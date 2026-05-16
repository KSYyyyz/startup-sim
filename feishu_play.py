"""飞书路由 — 薄适配层：命令路由 + TurnEngine.process_turn_raw()

飞书入口只做：
  1. 命令识别：开始 / 状态 / 决策
  2. user_id -> session_id 映射（通过 DB repository）
  3. 调用 TurnEngine.process_turn_raw(raw_input)
  4. 格式化 TurnResult 输出

所有游戏规则只存在于 TurnEngine、ActionParser、StateGuard、EventEngine、Agent 模块里。
状态持久化通过 src.db.repository 完成，不再使用 JSON 文件。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.models import CompanyState, TurnResult, EndingType
from src.core.turn_engine import TurnEngine
from src.core.difficulty import Difficulty, get_difficulty
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending
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
    sid = _session_map.get(user_id)
    if sid is not None:
        repository.reset_session(sid, state)
    else:
        sid = repository.create_session(user_id)
        repository.init_session_state(sid, state)
        _session_map[user_id] = sid

    return _render_state(state, difficulty)


# ── Command: 决策 ─────────────────────────────────────────────────────────────

def turn(user_id: str, raw_input: str) -> str:
    """Process one turn. All game logic delegated to TurnEngine.process_turn_raw()."""
    # Ensure DB is initialized
    init_db()

    sid = _session_map.get(user_id)
    if sid is None:
        return "❌ 游戏还没开始。说「创业模拟器 开始」来开局。"

    # Load state from DB
    state = repository.load_state(sid)

    # Check if game already ended
    ending = eval_ending(state)
    if ending:
        return (
            f"🎮 游戏已结束：{describe_ending(ending, state)}\n"
            "说「创业模拟器 开始」重新开局。"
        )

    # Get difficulty from session metadata
    session_status = repository.get_session_status(sid)
    diff_name = session_status.get("difficulty", "normal") if session_status else "normal"
    difficulty = get_difficulty(diff_name)

    # Delegate ALL game logic to TurnEngine
    result: TurnResult = TurnEngine.process_turn_raw(state, raw_input, difficulty)

    # Persist state via DB
    with repository.transaction() as conn:
        repository.save_state(sid, result.state_after, conn=conn)
        repository.update_session_month(
            sid, result.state_after.month,
            "active" if result.ending == EndingType.NONE else result.ending.value,
            conn=conn,
        )
        repository.save_snapshot(sid, result.state_after.month, result.state_after, conn=conn)

        # Persist action log (consistent with TurnEngine.process_turn)
        repository.save_action(
            sid, result.month,
            raw_input,
            result.action_plan.model_dump_json(),
            result.delta.model_dump_json(),
            conn=conn,
        )

        # Persist event logs
        for event in result.events:
            repository.save_event(
                sid, result.month,
                event.event_type, event.description,
                "high" if event.event_type == "board_coup_risk" else "medium",
                event.delta.model_dump_json(),
                conn=conn,
            )

    return _format_result(result)


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
    return _render_state(state, diff_name)


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
    if result.delta.reasons:
        for r in result.delta.reasons:
            lines.append(f"• {r}")
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
        lines.extend(["", f"🏁 **结局：{result.ending_description}**"])

    return "\n".join(lines)


def _render_state(state: CompanyState, difficulty: str = "") -> str:
    """Render current game state as Feishu Markdown."""
    diff_str = f" | {difficulty}模式" if difficulty else ""
    return "\n".join([
        f"🏢 AI客服SaaS | 第{state.month}月{diff_str}",
        f"💰 现金:{state.cash//10000}万 | 🔥 烧钱:{state.monthly_burn//10000}万/月 | MRR:{state.mrr//10000}万",
        f"👥 用户:{state.users} | 👨‍💻 员工:{state.employee_count}人 | 💰 单价:{state.price}元/月",
        f"📦 产品:{state.product_score} | 💪 士气:{state.team_morale} | ⭐ 声誉:{state.reputation}",
        f"📊 股权:创始人{state.founder_equity}% | 投资人{100 - state.founder_equity}% | 董事会控制:{state.board_control}%",
        f"🏦 估值:{state.valuation//10000}万 | ⏳ 跑道:{state.runway_months:.1f}月",
    ])
