#!/usr/bin/env python3
"""AI创业模拟器 Phase 0 — 终端交互版

Fixes applied:
  - Track definitions imported from shared tracks.py (no duplication)
  - state_row_to_dict() replaces fragile numeric indices (state[2], state[3], …)
  - All imports at top of file
"""

from db import (
    init_db,
    get_state,
    get_investors,
    update_state,
    state_row_to_dict,
    investor_row_to_dict,
)
from pipeline import process
from tracks import TRACKS, DEFAULT_TRACK, resolve_track


def show_state(state: dict) -> None:
    """Display current company state."""
    runway = state["cash"] / state["burn_rate"] if state["burn_rate"] > 0 else 999
    print()
    print("=" * 50)
    print(
        f"🏢 {state['company_name']} | 第{state['turn']}回合 | "
        f"阶段: {state['product_stage']} | 市场: {state['market_sentiment']}"
    )
    print(
        f"💰 现金: {state['cash']}万 | 烧钱: {state['burn_rate']}万/月 | "
        f"MRR: {state['revenue_mrr']}万/月"
    )
    print(f"👥 团队: {state['team_size']}人 | 士气: {state['team_morale']}/100")
    print(
        f"📊 创始人持股: {state['founder_equity'] * 100:.0f}% | "
        f"投资人: {state['investor_equity'] * 100:.0f}% | "
        f"期权池: {state['option_pool'] * 100:.0f}%"
    )
    print(f"🏦 当前轮次: {state['round']}")
    print(f"⏳ 跑道: {runway:.1f}个月")
    print("=" * 50)


def show_investors() -> None:
    """Display investor list."""
    investors = get_investors()
    print("\n📋 市场投资人:")
    for row in investors:
        inv = investor_row_to_dict(row)
        print(
            f"  {inv['name']} ({inv['type']}) — "
            f"{inv['check_size_min']}-{inv['check_size_max']}万, "
            f"偏好{inv['focus_stage']}轮, 信任度{inv['trust_score']:.0f}"
        )


def main() -> None:
    print("🚀 AI创业模拟器 Phase 0")
    print("你是CEO。输入你的战略决策，AI世界引擎会推演后果。")
    print("试试: '我要融资500万天使轮' / '招2个工程师' / '降价20%抢市场' / '裁员降本'")
    print("输入 'q' 退出, 'god 如果...' 进入上帝模式\n")

    init_db()

    # Track selection
    print("📌 选择你的创业赛道:")
    for k, (name, desc) in TRACKS.items():
        print(f"  {k}. {name} — {desc}")
    print("  5. 自定义（输入赛道名称）")

    choice = input("\n> ").strip()
    if choice == "5":
        track_name = input("输入赛道名称: ").strip() or DEFAULT_TRACK
    else:
        track_name = resolve_track(choice)

    update_state(track=track_name)
    print(f"\n✅ 选定赛道: {track_name}\n")

    while True:
        raw_state = get_state()
        state = state_row_to_dict(raw_state)

        show_state(state)

        if state["cash"] <= 0:
            print("\n💀 现金耗尽！游戏结束。")
            break

        user_input = input("\n> ").strip()
        if not user_input:
            continue
        if user_input.lower() == "q":
            break

        # God mode
        if user_input.startswith("god "):
            what_if = user_input[4:]
            print(f"\n🔮 上帝模式: {what_if}")
            print("（此模式下不改变真实状态，仅推演可能性）")
            result = process(what_if)
            print(f"\n{result['narrative']}")
            continue

        print("\n⏳ AI世界引擎推演中...")
        result = process(user_input)
        print(f"\n{result['narrative']}")

        # Advance turn
        update_state(turn=state["turn"] + 1)


if __name__ == "__main__":
    main()
