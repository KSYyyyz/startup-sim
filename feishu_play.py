"""飞书路由 — 精简版：命令路由 + TurnEngine.process_turn_raw()

飞书入口只做：
  1. 命令识别：开始 / 状态 / 决策
  2. user_id -> session_id 映射
  3. 调用 TurnEngine.process_turn_raw(raw_input)
  4. 格式化 TurnResult 输出

所有游戏规则只存在于 TurnEngine、ActionParser、StateGuard、EventEngine、Agent 模块里。
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.models import CompanyState, TurnResult, EndingType
from src.core.turn_engine import TurnEngine
from src.core.difficulty import Difficulty, get_difficulty
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "feishu_state.json")

# ── Global state (single-user MVP, persisted across processes via JSON) ──────
_game_state: CompanyState = None
_difficulty: Difficulty = None


def _save() -> None:
    """Save game state to JSON file."""
    if _game_state:
        data = {
            "state": _game_state.model_dump(),
            "difficulty": _difficulty.model_dump() if _difficulty else None,
        }
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def _load() -> bool:
    """Load game state from JSON file. Returns True if loaded."""
    global _game_state, _difficulty
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        _game_state = CompanyState(**data["state"])
        if data.get("difficulty"):
            _difficulty = Difficulty(**data["difficulty"])
        return True
    return False


# ── Command: 开始 ─────────────────────────────────────────────────────────────

def start(track: str = "AI客服SaaS", difficulty: str = "normal") -> str:
    """Start a new game with the given track and difficulty."""
    global _game_state, _difficulty

    diff_map = {"easy": Difficulty.easy(), "hard": Difficulty.hard()}
    _difficulty = diff_map.get(difficulty, Difficulty.normal())

    _game_state = CompanyState(
        cash=int(1_000_000 * _difficulty.cash_multiplier),
        monthly_burn=180_000,
        mrr=0,
        users=0,
        product_score=max(0, 20 + _difficulty.product_score_add),
        team_morale=max(0, 70 + _difficulty.team_morale_add),
        founder_equity=100,
        board_control=100,
        market_share=0,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
        month=1,
    )
    _save()
    return _render_state()


# ── Command: 决策 ─────────────────────────────────────────────────────────────

def turn(raw_input: str) -> str:
    """Process one turn. All game logic delegated to TurnEngine.process_turn_raw()."""
    global _game_state

    if not _game_state:
        _load()
    if not _game_state:
        return "❌ 游戏还没开始。说「创业模拟器 开始」来开局。"

    # Check if game already ended
    ending = eval_ending(_game_state)
    if ending:
        return (
            f"🎮 游戏已结束：{describe_ending(ending, _game_state)}\n"
            "说「创业模拟器 开始」重新开局。"
        )

    # Delegate ALL game logic to TurnEngine
    result: TurnResult = TurnEngine.process_turn_raw(
        _game_state, raw_input, _difficulty
    )

    # Update persisted state
    _game_state = result.state_after
    _save()

    return _format_result(result)


# ── Command: 状态 ─────────────────────────────────────────────────────────────

def status() -> str:
    """Return the current game state."""
    global _game_state
    if not _game_state:
        _load()
    if not _game_state:
        return "🎮 游戏还没开始。说「创业模拟器 开始」来开局。"
    return _render_state()


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
    lines.append(_render_state())

    # Events
    if result.events:
        lines.append("")
        for e in result.events:
            lines.append(f"⚡ [{e.event_type}] {e.description}")

    # Ending
    if result.ending != EndingType.NONE:
        lines.extend(["", f"🏁 **结局：{result.ending_description}**"])

    return "\n".join(lines)


def _render_state() -> str:
    """Render current game state as Feishu Markdown."""
    if not _game_state:
        return ""
    s = _game_state
    diff_name = _difficulty.name if _difficulty else "normal"
    return "\n".join([
        f"🏢 AI客服SaaS | 第{s.month}月 | {diff_name}模式",
        f"💰 现金:{s.cash//10000}万 | 🔥 烧钱:{s.monthly_burn//10000}万/月 | MRR:{s.mrr//10000}万",
        f"👥 用户:{s.users} | 👨‍💻 员工:{s.employee_count}人 | 💰 单价:{s.price}元/月",
        f"📦 产品:{s.product_score} | 💪 士气:{s.team_morale} | ⭐ 声誉:{s.reputation}",
        f"📊 股权:创始人{s.founder_equity}% | 投资人{100 - s.founder_equity}% | 董事会控制:{s.board_control}%",
        f"🏦 估值:{s.valuation//10000}万 | ⏳ 跑道:{s.runway_months:.1f}月",
    ])
