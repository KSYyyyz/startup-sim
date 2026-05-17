"""飞书路由 — 薄适配层：命令路由 + TurnEngine.process_turn_raw()

飞书入口只做：
  1. 命令识别：开始 / 重新开始 / 状态 / 决策 / 会话诊断
  2. external_user_id -> session_id 映射（通过 DB external_sessions 表）
  3. 调用 TurnEngine.process_turn_raw(raw_input)
  4. 格式化 TurnResult 输出

所有游戏规则只存在于 TurnEngine、ActionParser、StateGuard、EventEngine、Agent 模块里。
状态持久化通过 src.db.repository 完成，进程重启后会话不丢失。
"""

import logging
import os
import sys
from pathlib import Path

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
from src.db.connection import get_connection, init_db

# ── Debug logging ────────────────────────────────────────────────────────────

_log_dir = Path(__file__).resolve().parent / "logs"
_log_dir.mkdir(exist_ok=True)
_session_logger = logging.getLogger("feishu_session")
_session_logger.setLevel(logging.DEBUG)
_fh = logging.FileHandler(_log_dir / "feishu_session.log", encoding="utf-8")
_fh.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
_session_logger.addHandler(_fh)


def _log(msg: str) -> None:
    _session_logger.info(msg)


# ── External user identity ───────────────────────────────────────────────────

FEISHU_SOURCE = "feishu"
DEFAULT_EXTERNAL_USER_ID = "feishu:ou_10e6039f2c4e1c22280a0a7eb4c25542"


def extract_feishu_identity(event: dict | None = None) -> str:
    """Return a unified external_user_id string from a feishu event.

    Format: feishu:{open_id} (private chat) or feishu:{chat_id}:{open_id} (group chat).

    When no real event is available, falls back to the default test user.
    """
    if event is None:
        return DEFAULT_EXTERNAL_USER_ID
    open_id = event.get("sender", {}).get("open_id", "")
    chat_type = event.get("message", {}).get("chat_type", "private")
    if chat_type == "group" and open_id:
        chat_id = event.get("message", {}).get("chat_id", "")
        return f"{FEISHU_SOURCE}:{chat_id}:{open_id}" if chat_id else f"{FEISHU_SOURCE}:{open_id}"
    return f"{FEISHU_SOURCE}:{open_id}" if open_id else DEFAULT_EXTERNAL_USER_ID


# ── Session management (DB-backed, survives process restarts) ────────────────


def _resolve_session(external_user_id: str) -> tuple[int, bool]:
    """Resolve session from external_sessions table. Returns (session_id, is_new)."""
    init_db()
    sid, is_new = repository.get_or_create_external_session(FEISHU_SOURCE, external_user_id)
    repository.update_external_session_time(FEISHU_SOURCE, external_user_id)
    return sid, is_new


def _resolve_session_readonly(external_user_id: str) -> int | None:
    """Resolve session without creating a new one. Returns session_id or None."""
    init_db()
    return repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)


def _reset_session(external_user_id: str, state: CompanyState) -> int:
    """Delete old binding and create a new session. Returns new session_id."""
    init_db()
    repository.delete_external_session(FEISHU_SOURCE, external_user_id)
    sid = repository.create_session(external_user_id)
    repository.init_session_state(sid, state)
    repository.bind_external_session(FEISHU_SOURCE, external_user_id, sid)
    _log(
        f"reset | user={external_user_id} | new_session={sid} | "
        f"cash={state.cash} | month={state.month}"
    )
    return sid


# ── Command: 开始 ─────────────────────────────────────────────────────────────


def start(user_id: str, track: str = "AI客服SaaS", difficulty: str = "normal") -> str:
    """Start a new game — only if the user has no active session."""
    external_user_id = user_id or extract_feishu_identity()
    init_db()
    existing_sid = repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)
    if existing_sid is not None:
        status_info = repository.get_session_status(existing_sid)
        month_info = status_info.get("current_month", "?") if status_info else "?"
        session_status = status_info.get("status", "unknown") if status_info else "unknown"
        if session_status == "active":
            _log(
                f"start_rejected | user={external_user_id} | "
                f"existing_session={existing_sid} | month={month_info}"
            )
            return (
                f"🎮 你已经有一个进行中的游戏（第{month_info}月）。\n"
                "继续输入决策即可推进回合。\n"
                "输入「重新开始」可以放弃当前进度开始新游戏。"
            )

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

    sid = repository.create_session(external_user_id)
    repository.init_session_state(sid, state)
    repository.bind_external_session(FEISHU_SOURCE, external_user_id, sid)
    _log(f"start | user={external_user_id} | new_session={sid} | month=1")

    msg = _render_state(state, difficulty)
    msg += (
        "\n\n💡 这是你的第一次创业之旅。输入决策开始吧！\n"
        "试试：「花20万研发产品，花10万做营销」\n"
        "输入「帮助」查看完整指南。"
    )
    return msg


# ── Command: 重新开始 ─────────────────────────────────────────────────────────


def restart(user_id: str, track: str = "AI客服SaaS", difficulty: str = "normal") -> str:
    """Force-create a new game, overwriting any existing session binding."""
    external_user_id = user_id or extract_feishu_identity()
    init_db()
    old_sid = repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)
    repository.delete_external_session(FEISHU_SOURCE, external_user_id)

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

    sid = repository.create_session(external_user_id)
    repository.init_session_state(sid, state)
    repository.bind_external_session(FEISHU_SOURCE, external_user_id, sid)
    _log(
        f"restart | user={external_user_id} | old_session={old_sid} | "
        f"new_session={sid} | month=1"
    )

    msg = "🔄 已重新开始新游戏。\n\n"
    msg += _render_state(state, difficulty)
    msg += "\n\n💡 输入决策开始新的创业之旅！"
    return msg


# ── Command: 决策 ─────────────────────────────────────────────────────────────


def turn(user_id: str, raw_input: str) -> str:
    """Process one turn. All game logic delegated to TurnEngine.process_turn_raw()."""
    init_db()

    # Help command routing
    if raw_input.strip().lower() in ("help", "帮助", "怎么玩", "指令", "？", "?"):
        return help_text()

    # Restart command routing
    if raw_input.strip() in ("重新开始", "重开", "restart"):
        return restart(user_id)

    # Session diagnostic command
    if raw_input.strip().lower() in ("会话", "session", "debug session", "debug_session"):
        return session_diag(user_id)

    external_user_id = user_id or extract_feishu_identity()
    sid = repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)
    if sid is None:
        _log(f"turn_rejected_no_session | user={external_user_id} | input={raw_input[:60]}")
        return "❌ 游戏还没开始。说「创业模拟器 开始」来开局。"

    state = repository.load_state(sid)
    month_before = state.month

    # Check if game already ended
    ending = eval_ending(state)
    if ending:
        _log(
            f"turn_rejected_ended | user={external_user_id} | "
            f"session={sid} | month={month_before}"
        )
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
        repository.save_snapshot(sid, result.state_after.month, result.state_after, conn=conn)
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
        repository.update_external_session_time(FEISHU_SOURCE, external_user_id, conn=conn)

    _log(
        f"turn | user={external_user_id} | session={sid} | "
        f"month_before={month_before} | month_after={result.state_after.month} | "
        f"ending={result.ending.value} | is_new=False"
    )

    msg = _format_result(result)
    msg += "\n\n" + _format_suggestions_compact(result.state_after)

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
    """Return the current game state. Read-only: does not create a new session."""
    external_user_id = user_id or extract_feishu_identity()
    init_db()
    sid = repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)
    if sid is None:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"

    session_status = repository.get_session_status(sid)
    if session_status is None:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"

    state = repository.load_state(sid)
    diff_name = session_status.get("difficulty", "normal")
    msg = _render_state(state, diff_name)
    msg += "\n\n" + _format_suggestions_compact(state)
    return msg


# ── Command: 会话诊断 ─────────────────────────────────────────────────────────


def session_diag(user_id: str) -> str:
    """Return session diagnostic info for the current external user."""
    external_user_id = user_id or extract_feishu_identity()
    init_db()
    sid = repository.find_session_by_external_user(FEISHU_SOURCE, external_user_id)
    if sid is None:
        return (
            f"🔍 **会话诊断**\n\n"
            f"external_user_id: `{external_user_id}`\n"
            f"状态: 无绑定会话\n"
            f"提示: 输入「创业模拟器 开始」开局"
        )

    session_info = repository.get_session_status(sid)
    state = repository.load_state(sid)
    binding_row = None
    conn = get_connection()
    try:
        binding_row = conn.execute(
            "SELECT created_at, updated_at FROM external_sessions "
            "WHERE source=? AND external_user_id=?",
            (FEISHU_SOURCE, external_user_id),
        ).fetchone()
    finally:
        conn.close()

    created = binding_row["created_at"] if binding_row else "?"
    updated = binding_row["updated_at"] if binding_row else "?"
    current_month = session_info.get("current_month", "?") if session_info else state.month
    status_str = session_info.get("status", "active") if session_info else "active"

    return (
        f"🔍 **会话诊断**\n\n"
        f"external_user_id: `{external_user_id}`\n"
        f"session_id: {sid}\n"
        f"当前月份: 第{current_month}月\n"
        f"状态: {status_str}\n"
        f"绑定创建: {created}\n"
        f"最近活动: {updated}\n"
        f"现金: {state.cash//10000}万 | 产品分: {state.product_score} | MRR: {state.mrr//10000}万"
    )


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
        "• 直接输入决策即可\n\n"
        "📖 快速开始：QUICKSTART.md\n"
        "📋 样例局：examples/\n"
        "🔧 问题排查：docs/troubleshooting.md"
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

    # Board feedback — always shown
    lines.append("**👔 董事会：**")
    if result.board_feedback:
        for name, msg in result.board_feedback.items():
            lines.append(f"  [{name}] {msg}")
    else:
        lines.append("  本月无重大分歧，董事会意见基本一致。")
    lines.append("")

    # Competitor moves — always shown
    lines.append("**🏪 竞品：**")
    if result.competitor_moves:
        for m in result.competitor_moves:
            lines.append(f"  [{m['name']}] {m['action']} — {m['narrative']}")
    else:
        lines.append("  本月竞品无明显动作，但市场竞争仍在持续。")
    lines.append("")

    # Customer response — always shown
    lines.append("**👥 客户：**")
    if result.customer_response:
        narrative = result.customer_response.get("narrative", "")
        if narrative:
            lines.append(f"  {narrative[:150]}")
        else:
            lines.append("  客户群体表现平稳。")
    else:
        lines.append("  客户群体表现平稳。")
    lines.append("")

    # Delta reasons
    for reason in result.delta.reasons:
        lines.append(f"• {reason}")
    if result.delta.reasons:
        lines.append("")

    # Current state
    lines.append(_render_state(result.state_after, ""))

    # Events — always shown
    lines.append("")
    lines.append("**📢 本月事件：**")
    if result.events:
        for e in result.events:
            lines.append(f"⚡ [{e.event_type}] {e.description}")
    else:
        lines.append("  本月无重大外部事件，但市场竞争仍在持续。")

    # Ending
    if result.ending != EndingType.NONE:
        lines.append("")
        lines.append(f"🏁 **结局：{result.ending_description}**")

    return "\n".join(lines)


def _render_state(state: CompanyState, difficulty: str = "") -> str:
    """Render current game state as Feishu Markdown."""
    from src.core.status_formatter import format_status_panel_short

    header = f"🏢 AI客服SaaS | 第{state.month}月"
    if difficulty:
        header += f" | {difficulty}模式"
    return header + "\n" + format_status_panel_short(state)


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
