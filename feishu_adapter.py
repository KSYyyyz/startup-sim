#!/usr/bin/env python3
"""飞书适配层 — 在对话中玩创业模拟器

Fixes applied:
  - Track definitions imported from shared tracks.py (removed inline duplicate)
  - state_row_to_dict() / investor_row_to_dict() replace fragile numeric indices
  - Imports organised at top, no sys.path hack
"""

import os
import sys

# Let sibling imports work regardless of how this file is invoked
_srcdir = os.path.dirname(os.path.abspath(__file__))
if _srcdir not in sys.path:
    sys.path.insert(0, _srcdir)

from db import (
    DB_PATH,
    get_investors,
    get_state,
    init_db,
    investor_row_to_dict,
    state_row_to_dict,
    update_state,
)
from pipeline import process as pipeline_process
from tracks import TRACKS

# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------


def get_game_state() -> dict:
    """Return a display-ready dict for the current company state, or
    {'status': 'not_started'} if no game exists."""
    row = get_state()
    if not row:
        return {"status": "not_started"}

    state = state_row_to_dict(row)
    runway = state["cash"] / state["burn_rate"] if state["burn_rate"] > 0 else 999

    return {
        "status": "active",
        "company": state["company_name"],
        "track": state["track"],
        "cash": state["cash"],
        "burn_rate": state["burn_rate"],
        "mrr": state["revenue_mrr"],
        "team_size": state["team_size"],
        "team_morale": state["team_morale"],
        "product_stage": state["product_stage"],
        "founder_equity": round(state["founder_equity"] * 100),
        "investor_equity": round(state["investor_equity"] * 100),
        "option_pool": round(state["option_pool"] * 100),
        "round": state["round"],
        "turn": state["turn"],
        "market": state["market_sentiment"],
        "runway": round(runway, 1),
    }


def format_state_for_feishu(state: dict) -> str:
    """Format game state as a Feishu markdown message."""
    if state.get("status") == "not_started":
        return "🎮 游戏还没开始。说「开始创业」来选择赛道吧！"

    lines = [
        f"🏢 **{state['company']}** | 第{state['turn']}回合",
        f"📌 赛道: {state['track']} | 市场: {state['market']}",
        f"💰 现金: {state['cash']}万 | 烧钱: {state['burn_rate']}万/月",
        f"📈 MRR: {state['mrr']}万/月 | ⏳ 跑道: {state['runway']}个月",
        f"👥 团队: {state['team_size']}人 | 士气: {state['team_morale']}/100",
        f"📊 股权: 创始人{state['founder_equity']}% "
        f"| 投资人{state['investor_equity']}% "
        f"| 期权池{state['option_pool']}%",
        f"🏦 轮次: {state['round']} | 阶段: {state['product_stage']}",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Game lifecycle
# ---------------------------------------------------------------------------


def start_game(track_name: str) -> str:
    """Delete old save, initialise a fresh game with the given track."""
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    init_db()
    update_state(track=track_name)
    state = get_game_state()

    return (
        f"✅ **创业开始！赛道: {track_name}**\n\n"
        f"{format_state_for_feishu(state)}\n\n"
        "💡 试试: 「我要融资500万天使轮」 / 「招2个工程师」 / 「降价20%抢市场」"
    )


def handle_command(user_input: str) -> str:
    """Process one turn of user input, returning a Feishu-formatted message."""
    try:
        result = pipeline_process(user_input)
        narrative = result.get("narrative", "（无输出）")
        state = get_game_state()

        msg = narrative + "\n\n" + format_state_for_feishu(state)

        if state.get("cash", 0) <= 0:
            msg += "\n\n💀 **现金耗尽！游戏结束。** 说「开始创业」重新来。"

        return msg
    except Exception as exc:
        return f"❌ 出错: {exc}"


def show_investors() -> str:
    """Return a Feishu-formatted investor list."""
    invs = get_investors()
    lines = ["📋 **市场投资人:**"]
    for row in invs:
        inv = investor_row_to_dict(row)
        lines.append(
            f"• {inv['name']} ({inv['type']}) — "
            f"{inv['check_size_min']}-{inv['check_size_max']}万, "
            f"偏好{inv['focus_stage']}轮, 信任度{inv['trust_score']:.0f}"
        )
    return "\n".join(lines)


def show_tracks() -> str:
    """Return a Feishu-formatted track-selection prompt."""
    lines = ["📌 **选择赛道:**"]
    for k, (name, desc) in TRACKS.items():
        lines.append(f"  {k}. {name} — {desc}")
    lines.append("  5. 自定义（输入名称）")
    lines.append("\n回复数字或赛道名。")
    return "\n".join(lines)
