"""飞书路由 — 薄适配层：命令路由 + TurnEngine.process_turn_raw()

飞书入口只做：
  1. 命令识别：开始 / 状态 / 决策
  2. user_id -> session_id 映射（通过 DB repository）
  3. 调用 TurnEngine.process_turn_raw(raw_input)
  4. 格式化 TurnResult 输出

所有游戏规则只存在于 TurnEngine、ActionParser、StateGuard、EventEngine、Agent 模块里。
状态持久化通过 src.db.repository 完成，不再使用 JSON 文件。
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.achievement_engine import AchievementEngine
from src.core.difficulty import Difficulty, get_difficulty
from src.core.ending_evaluator import describe_ending
from src.core.ending_evaluator import evaluate as eval_ending
from src.core.models import CompanyState, EndingType, TurnResult
from src.core.replay_engine import ReplayEngine
from src.core.review_engine import ReviewEngine
from src.core.suggestion_engine import SuggestionEngine
from src.core.turn_engine import TurnEngine
from src.db import repository
from src.db.connection import init_db

# ── Session mapping: user_id (str) → session_id (int) ─────────────────────────


def _get_or_create_session(user_id: str, player_name: str = "") -> int:
    """Map a user_id to a session_id. DB-first: queries for active session by player_name.
    Falls back to in-memory map, then creates a new session."""
    # 1) Check in-memory cache first (fast path)
    sid = _session_map.get(user_id)
    if sid is not None:
        status = repository.get_session_status(sid)
        if status:
            return sid
        else:
            del _session_map[user_id]

    # 2) Query DB for active session (handles process restarts)
    init_db()
    name = player_name or user_id
    sid = repository.find_active_session_by_player_name(name)
    if sid is not None:
        _session_map[user_id] = sid
        return sid

    # 3) Create new session
    sid = repository.create_session(name)
    _session_map[user_id] = sid
    return sid


# In-memory session map (lives only for process lifetime; acceptable for MVP)
_session_map: dict[str, int] = {}


# ── Command: 开始 ─────────────────────────────────────────────────────────────


def start(user_id: str, track: str = "AI客服SaaS", difficulty: str = "normal") -> str:
    """Start a new game with the given track and difficulty."""
    diff_map = {"easy": Difficulty.easy(), "hard": Difficulty.hard()}
    diff = diff_map.get(difficulty, Difficulty.normal())

    state = CompanyState(
        cash=int(1_000_000 * diff.cash_multiplier),
        monthly_burn=180_000,
        mrr=0,
        users=0,
        product_score=max(0, 20 + diff.product_score_add),
        team_morale=max(0, 70 + diff.team_morale_add),
        founder_equity=100,
        board_control=100,
        market_share=0,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
        month=1,
    )

    # Create or reset session
    is_new = False
    sid = _session_map.get(user_id)
    if sid is not None:
        repository.reset_session(sid, state)
    else:
        sid = repository.create_session(user_id)
        repository.init_session_state(sid, state)
        _session_map[user_id] = sid
        is_new = True

    msg = _render_state(state, difficulty)

    # Alpha 1.6: Tutorial hint only for brand-new sessions
    if is_new:
        msg += (
            "\n\n💡 这是你的第一次创业之旅。输入决策开始吧！\n"
            "试试：「花20万研发产品，花10万做营销」\n"
            "输入「帮助」查看完整指南。"
        )

    return msg


# ── Command: 决策 ─────────────────────────────────────────────────────────────


def turn(user_id: str, raw_input: str) -> str:
    """Process one turn. All game logic delegated to TurnEngine.process_turn_raw()."""
    init_db()

    # Alpha 1.6: Help command routing
    if raw_input.strip().lower() in ("help", "帮助", "怎么玩", "指令", "？", "?"):
        return help_text()

    sid = _session_map.get(user_id)
    if sid is None:
        return "❌ 游戏还没开始。说「创业模拟器 开始」来开局。"

    state = repository.load_state(sid)

    # Check if game already ended
    ending = eval_ending(state)
    if ending:
        return (
            f"🎮 游戏已结束：{describe_ending(ending, state)}\n" "说「创业模拟器 开始」重新开局。"
        )

    session_status = repository.get_session_status(sid)
    diff_name = session_status.get("difficulty", "normal") if session_status else "normal"
    difficulty = get_difficulty(diff_name)

    result: TurnResult = TurnEngine.process_turn_raw(state, raw_input, difficulty)

    with repository.transaction() as conn:
        repository.save_state(sid, result.state_after, conn=conn)
        repository.update_session_month(
            sid,
            result.state_after.month,
            "active" if result.ending == EndingType.NONE else result.ending.value,
            conn=conn,
        )
        repository.save_snapshot(
            sid,
            result.state_after.month,
            result.state_after,
            conn=conn,
        )

        repository.save_action(
            sid,
            result.month,
            raw_input,
            result.action_plan.model_dump_json(),
            result.delta.model_dump_json(),
            conn=conn,
        )

        for event in result.events:
            severity = "high" if event.event_type == "board_coup_risk" else "medium"
            repository.save_event(
                sid,
                result.month,
                event.event_type,
                event.description,
                severity,
                event.delta.model_dump_json(),
                conn=conn,
            )

    msg = _format_result(result)

    # Alpha 1.6: Compact suggestions after turn
    msg += "\n\n" + _format_suggestions_compact(result.state_after)

    # Alpha 1.4: Append review when game ends
    if result.ending != EndingType.NONE:
        msg += "\n\n" + _format_review_short(sid, result)

    return msg


def turn_safe(user_id: str, raw_input: str) -> str:
    """Process one turn with error handling for feishu message handler."""
    try:
        return turn(user_id, raw_input)
    except Exception as exc:
        return f"❌ 出错: {exc}"


# ── Command: 状态 ─────────────────────────────────────────────────────────────


def status(user_id: str) -> str:
    """Return the current game state."""
    sid = _session_map.get(user_id)
    if sid is None:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"

    session_status = repository.get_session_status(sid)
    if session_status is None:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"

    state = repository.load_state(sid)
    diff_name = session_status.get("difficulty", "normal")
    msg = _render_state(state, diff_name)

    # Alpha 1.6: Compact suggestions
    msg += "\n\n" + _format_suggestions_compact(state)

    return msg


# ── Command: 帮助 ─────────────────────────────────────────────────────────────


def help_text() -> str:
    """Alpha 1.6: Return compact help message for Feishu."""
    return (
        "📖 **创业模拟器 帮助**\n\n"
        "🎯 目标：12个月完成A轮融资（MRR≥30万、产品分≥60）\n\n"
        "🛠️ 五种决策类型：\n"
        '• 研发 — "花20万研发产品"\n'
        '• 营销 — "花15万做营销推广"\n'
        '• 融资 — "融资500万出让10%股权"\n'
        '• 团队 — "花10万招聘扩充团队"\n'
        '• 战略 — "花5万做战略规划"\n\n'
        "📊 关键指标：\n"
        "💰现金 💰月消耗 📈MRR 👥用户 🛠️产品分 💪士气 📊股权 ⏳跑道\n\n"
        "💡 示例：\n"
        "• 花20万研发产品，花10万做营销\n"
        "• 融资500万出让10%股权，花30万研发产品\n\n"
        "📌 常用指令：\n"
        "• 创业模拟器 开始 / 状态 / 帮助\n"
        "• 直接输入决策即可"
    )


def _format_suggestions_compact(state: CompanyState) -> str:
    """Alpha 1.6: Generate compact suggestion line for Feishu."""
    result = SuggestionEngine.generate(state, state.month)
    lines = []

    # Only show the risk warning line + recommended focus
    if result.warning:
        lines.append(f"⚠️ {result.warning}")
    if result.recommended_focus:
        lines.append(f"🎯 {result.recommended_focus}")

    # Show top 2 example inputs
    examples = []
    for s in result.suggestions[:2]:
        examples.append(f"「{s.example_input}」")
    if examples:
        lines.append(f"💡 {'  '.join(examples)}")

    return "\n".join(lines)


# ── Formatting ────────────────────────────────────────────────────────────────


def _format_result(result: TurnResult) -> str:
    """Format a TurnResult into a Feishu Markdown message."""
    lines = [f"📅 第{result.month}月结果", ""]

    # Board feedback
    if result.board_feedback:
        lines.append("**👔 董事会：**")
        for name, msg in result.board_feedback.items():
            lines.append(f"  [{name}] {msg}")
        lines.append("")

    # Competitor moves
    if result.competitor_moves:
        lines.append("**🏪 竞品：**")
        for m in result.competitor_moves:
            lines.append(f"  [{m['name']}] {m['action']} — {m['narrative']}")
        lines.append("")

    # Customer response
    if result.customer_response:
        narrative = result.customer_response.get("narrative", "")
        lines.append(f"**👥 客户：** {narrative[:150]}")
        lines.append("")

    # Delta reasons
    for reason in result.delta.reasons:
        lines.append(f"• {reason}")
    if result.delta.reasons:
        lines.append("")

    # Current state
    lines.append(_render_state(result.state_after, ""))

    # Events
    if result.events:
        lines.append("")
        for e in result.events:
            lines.append(f"⚡ [{e.event_type}] {e.description}")

    # Ending
    if result.ending != EndingType.NONE:
        lines.append("")
        lines.append(f"🏁 **结局：{result.ending_description}**")

    return "\n".join(lines)


def _render_state(state: CompanyState, difficulty: str = "") -> str:
    """Render current game state as Feishu Markdown."""
    diff_str = f" | {difficulty}模式" if difficulty else ""

    line1 = f"🏢 AI客服SaaS | 第{state.month}月{diff_str}"
    line2 = (
        f"💰 现金:{state.cash//10000}万 | "
        f"🔥 烧钱:{state.monthly_burn//10000}万/月 | "
        f"MRR:{state.mrr//10000}万"
    )
    line3 = (
        f"👥 用户:{state.users} | "
        f"👨‍💻 员工:{state.employee_count}人 | "
        f"💰 单价:{state.price}元/月"
    )
    line4 = (
        f"📦 产品:{state.product_score} | "
        f"💪 士气:{state.team_morale} | "
        f"⭐ 声誉:{state.reputation}"
    )
    line5 = (
        f"📊 股权:创始人{state.founder_equity}% | "
        f"投资人{100 - state.founder_equity}% | "
        f"董事会控制:{state.board_control}%"
    )
    line6 = f"🏦 估值:{state.valuation//10000}万 | " f"⏳ 跑道:{state.runway_months:.1f}月"

    return "\n".join([line1, line2, line3, line4, line5, line6])


def _format_review_short(session_id: int, result: TurnResult) -> str:
    """Generate a compact review for Feishu chat window."""
    snapshots = repository.list_snapshots(session_id)
    actions = repository.list_actions(session_id)
    events_db = repository.list_events(session_id)

    # Reconstruct initial state from session difficulty
    session_status = repository.get_session_status(session_id)
    diff_name = session_status.get("difficulty", "normal") if session_status else "normal"
    diff = get_difficulty(diff_name)
    initial_state = CompanyState(
        cash=int(1_000_000 * diff.cash_multiplier),
        product_score=max(0, 20 + diff.product_score_add),
        team_morale=max(0, 70 + diff.team_morale_add),
        month=1,
    )

    review = ReviewEngine.generate_review(
        initial_state=initial_state,
        snapshots=snapshots,
        action_logs=actions,
        event_logs=events_db,
        final_state=result.state_after,
        ending_status=result.ending.value,
        session_id=session_id,
    )

    scores = review.strategy_scores
    lines = [
        "🏁 **创业复盘**",
        f"结局：{review.ending_title}",
        f"💬 {review.ending_summary}",
        "",
        f"📊 评分：产品{scores.product_score} | 增长{scores.growth_score} | "
        f"财务{scores.finance_score} | 控制{scores.control_score} | "
        f"风控{scores.risk_score} | 综合{scores.overall_score}",
        "",
        "🔑 关键转折：",
    ]
    for m in review.key_moments[:3]:
        lines.append(f"• M{m.month} {m.title}")
    lines.append("")
    lines.append(f"💡 {review.advice_for_next_run}")

    # Alpha 1.5: Replay (compact — 2-3 key months)
    replay = ReplayEngine.generate_replay(
        snapshots=snapshots,
        actions=actions,
        events=events_db,
        final_state=result.state_after,
        ending_status=result.ending.value,
        session_id=session_id,
    )
    if replay.months:
        climax_m = next((m for m in replay.months if m.month == replay.climax_month), None)
        final_m = replay.months[-1] if replay.months else None
        lines.append("")
        lines.append("🎬 **月历回放**")
        if climax_m:
            lines.append(f"⭐ M{climax_m.month} {climax_m.title} — {climax_m.summary}")
        if final_m and final_m != climax_m:
            lines.append(f"🏁 M{final_m.month} {final_m.title} — {final_m.summary}")
        if replay.replay_tags:
            lines.append(f"🏷️ {' · '.join(replay.replay_tags)}")

    # Alpha 1.5: Achievements (top 3)
    achievements = AchievementEngine.evaluate(
        final_state=result.state_after,
        ending_status=result.ending.value,
        review=review,
        snapshots=snapshots,
    )
    if achievements.achievements:
        lines.append("")
        lines.append(f"🏅 **成就** ({achievements.summary})")
        for a in achievements.achievements[:3]:
            lines.append(f"• {a.title} — {a.description}")

    return "\n".join(lines)
