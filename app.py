#!/usr/bin/env python3
"""Startup Sim — CLI entry point.

Usage:
    python app.py new --name "玩家名" [--scenario ai_customer_service_saas]
    python app.py new --name "玩家名" --difficulty hard

Start a new game and play interactively through 12 months of startup life.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

from config import SCENARIOS_PATH, MAX_TURNS
from src.db.connection import init_db
from src.db import repository
from src.core.models import CompanyState, EndingType
from src.core.turn_engine import TurnEngine
from src.core.difficulty import get_difficulty


# ── Display helpers ────────────────────────────────────────────────────────────

def _money(v: int) -> str:
    """Format integer money to readable string."""
    if abs(v) >= 10_000:
        return f"{v/10000:.1f}万"
    return str(v)


def display_state(state: CompanyState, title: str = "📊 公司状态") -> None:
    """Pretty-print the company state."""
    runway = state.runway_months
    runway_str = f"{runway:.1f}个月" if runway != float("inf") else "∞"

    print(f"\n{'='*60}")
    print(f"  {title}  —  第 {state.month} 个月")
    print(f"{'='*60}")
    print(f"  💰 现金:      {_money(state.cash):>10}     🔥 月消耗:   {_money(state.monthly_burn):>10}")
    print(f"  📈 MRR:       {_money(state.mrr):>10}     👥 用户:     {state.users:>10}")
    print(f"  🛠️  产品评分:  {state.product_score:>10}     💪 团队士气: {state.team_morale:>10}")
    print(f"  📊 创始人股权:{state.founder_equity:>10}%    🏛️  董事会:   {state.board_control:>10}%")
    print(f"  📈 市场份额:  {state.market_share:>10}%    ⭐ 声誉:     {state.reputation:>10}")
    print(f"  ⏳ 剩余跑道:  {runway_str:>10}")
    print(f"{'='*60}")


def display_events(events) -> None:
    """Display triggered events."""
    if not events:
        return
    print(f"\n⚡ 事件触发 ({len(events)}):")
    for e in events:
        print(f"  [{e.event_type}] {e.description}")


def display_result(result) -> None:
    """Display turn result summary."""
    print(f"\n--- 第{result.month}月结果 ---")

    # Show delta summary
    d = result.delta
    changes = []
    for field, label in [
        ("cash", "💰现金"), ("mrr", "📈MRR"), ("users", "👥用户"),
        ("product_score", "🛠️产品"), ("team_morale", "💪士气"),
        ("founder_equity", "📊股权"), ("reputation", "⭐声誉"),
    ]:
        v = getattr(d, field, 0)
        if v != 0:
            sign = "+" if v > 0 else ""
            changes.append(f"{label} {sign}{v}")
    if changes:
        print("  变化: " + " | ".join(changes))

    if result.delta.reasons:
        print("  原因:")
        for r in result.delta.reasons:
            print(f"    • {r}")

    display_events(result.events)

    # Ending
    if result.ending != EndingType.NONE:
        print(f"\n{'='*60}")
        print(f"  🏁 游戏结束: {result.ending.value}")
        print(f"  {result.ending_description}")
        print(f"{'='*60}")


def load_scenario(scenario_id: str) -> CompanyState:
    """Load initial state from scenarios.yaml."""
    if not SCENARIOS_PATH.exists():
        raise FileNotFoundError(f"Scenarios file not found: {SCENARIOS_PATH}")

    with open(SCENARIOS_PATH, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    scenarios = data.get("scenarios", {})
    if scenario_id not in scenarios:
        available = ", ".join(scenarios.keys())
        raise ValueError(
            f"Unknown scenario '{scenario_id}'. Available: {available}"
        )

    s = scenarios[scenario_id]
    init = s["initial_state"]
    return CompanyState(
        cash=init["cash"],
        monthly_burn=init["monthly_burn"],
        mrr=init["mrr"],
        users=init["users"],
        product_score=init["product_score"],
        team_morale=init["team_morale"],
        founder_equity=init["founder_equity"],
        board_control=init["board_control"],
        market_share=init["market_share"],
        reputation=init["reputation"],
        month=1,
    )


def cmd_new(args) -> None:
    """Start a new game."""
    scenario_id = args.scenario or "ai_customer_service_saas"

    print(f"🚀 Startup Sim — 新游戏")
    print(f"   玩家: {args.name}")
    print(f"   剧本: {scenario_id}")
    print(f"   难度: {args.difficulty}")
    print()

    # Initialize DB and load scenario
    init_db()
    scenario_state = load_scenario(scenario_id)

    # Create session
    session_id = repository.create_session(
        player_name=args.name,
        scenario_id=scenario_id,
        difficulty=args.difficulty,
    )
    repository.init_session_state(session_id, scenario_state)

    print(f"✅ 游戏已创建 (会话ID: {session_id})")
    display_state(scenario_state, "📊 初始状态")

    # Create turn engine
    engine = TurnEngine(session_id)

    # Main game loop
    print(f"\n🎮 输入你的决策 (最多{MAX_TURNS}个月)。输入 'quit' 退出。")
    print(f"   示例: 研发产品花20万, 招3个销售\n")

    while True:
        try:
            raw = input("👉 第{}月决策: ".format(
                repository.load_state(session_id).month
            )).strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not raw:
            print("  ⚠️ 请输入决策内容")
            continue

        if raw.lower() in ("quit", "exit", "q"):
            print("👋 再见！")
            break

        if raw.lower() == "status":
            state = repository.load_state(session_id)
            display_state(state)
            continue

        try:
            result = engine.process_turn(raw)
            display_result(result)

            if result.ending != EndingType.NONE:
                display_state(result.state_after, "📊 最终状态")
                break

            # Show updated state
            display_state(result.state_after)

        except Exception as e:
            print(f"  ❌ 错误: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Startup Sim — AI客服SaaS创业模拟器",
    )
    sub = parser.add_subparsers(dest="command", help="命令")

    # new command
    new_parser = sub.add_parser("new", help="开始新游戏")
    new_parser.add_argument("--name", type=str, default="创始人", help="玩家名称")
    new_parser.add_argument("--scenario", type=str, default="ai_customer_service_saas",
                            help="剧本名称")
    new_parser.add_argument("--difficulty", type=str, default="normal",
                            choices=["easy", "normal", "hard"],
                            help="游戏难度")

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
