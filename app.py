#!/usr/bin/env python3
"""Startup Sim — CLI entry point.

Usage:
    python app.py new --name "玩家名" [--scenario ai_customer_service_saas]
    python app.py new --name "玩家名" --difficulty hard

Start a new game and play interactively through 12 months of startup life.
"""

from __future__ import annotations

import argparse

import yaml

from config import MAX_TURNS, SCENARIOS_PATH
from src.core.achievement_engine import AchievementEngine
from src.core.models import CompanyState, EndingType
from src.core.replay_engine import ReplayEngine
from src.core.review_engine import ReviewEngine
from src.core.state_explainer import StateExplainer
from src.core.suggestion_engine import SuggestionEngine
from src.core.turn_engine import TurnEngine
from src.core.tutorial import TutorialEngine
from src.db import repository
from src.db.connection import init_db

# ── Display helpers ────────────────────────────────────────────────────────────


def _money(v: int) -> str:
    """Format integer money to readable string."""
    if abs(v) >= 10_000:
        return f"{v/10000:.1f}万"
    return str(v)


def display_state(state: CompanyState, title: str = "📊 公司状态") -> None:
    """Pretty-print the company state with human-readable insights."""
    from src.core.status_formatter import format_status_panel

    print()
    print(format_status_panel(state))
    print()

    # Alpha 1.6: Human-readable state insights
    explanations = StateExplainer.explain_full(state)
    print(f"  💬 {explanations['cash']}")
    if state.product_score > 0 or state.month > 1:
        print(f"  💬 {explanations['product']}")
    if state.users > 0 or state.mrr > 0:
        print(f"  💬 {explanations['users_mrr']}")
    if state.founder_equity < 100:
        print(f"  💬 {explanations['equity']}")
    print()


def display_events(events) -> None:
    """Display triggered events."""
    if not events:
        return
    print(f"\n⚡ 事件触发 ({len(events)}):")
    for e in events:
        print(f"  [{e.event_type}] {e.description}")


def print_review(
    session_id: int,
    initial_state: CompanyState,
    final_state: CompanyState,
    ending_status: str,
) -> None:
    """Generate and print the post-game review report."""
    snapshots = repository.list_snapshots(session_id)
    actions = repository.list_actions(session_id)
    events_db = repository.list_events(session_id)

    review = ReviewEngine.generate_review(
        initial_state=initial_state,
        snapshots=snapshots,
        action_logs=actions,
        event_logs=events_db,
        final_state=final_state,
        ending_status=ending_status,
        session_id=session_id,
    )

    scores = review.strategy_scores
    fm = review.final_metrics

    print(f"\n{'='*60}")
    print("  🏁 创业复盘报告")
    print(f"{'='*60}")
    print(f"  🎯 结局：{review.ending_title}")
    print(f"  💬 {review.ending_summary}")
    print()
    print("  📊 最终指标")
    print(
        f"    现金:{_money(fm.get('cash',0))} | MRR:{_money(fm.get('mrr',0))} | "
        f"产品:{fm.get('product_score',0)} | 用户:{fm.get('users',0)} | "
        f"股权:{fm.get('founder_equity',0)}%"
    )
    print()
    print("  🎯 策略评分")
    print(
        f"    产品力:{scores.product_score:>3} | 增长力:{scores.growth_score:>3} | "
        f"财务力:{scores.finance_score:>3}"
    )
    print(
        f"    控制力:{scores.control_score:>3} | 风控力:{scores.risk_score:>3} | "
        f"综合:{scores.overall_score:>3}"
    )
    print()
    print("  🔑 关键转折点")
    for m in review.key_moments:
        print(f"    [M{m.month:>2}] {m.title} — {m.description}")
    print()
    print(f"  👤 创始人画像：{review.founder_profile.profile_title}")
    print(f"    {review.founder_profile.description}")
    print()
    print("  💡 下局建议")
    print(f"    {review.advice_for_next_run}")
    print(f"{'='*60}")

    # ── Alpha 1.5: Replay ──
    print_replay(session_id, snapshots, actions, events_db, final_state, ending_status)

    # ── Alpha 1.5: Achievements ──
    achievements = AchievementEngine.evaluate(
        final_state=final_state,
        ending_status=ending_status,
        review=review,
        snapshots=snapshots,
    )
    print_achievements(achievements)


def print_replay(
    session_id: int,
    snapshots: list,
    actions: list,
    events: list,
    final_state: CompanyState,
    ending_status: str,
) -> None:
    """Print the monthly replay timeline (5 key months)."""
    replay = ReplayEngine.generate_replay(
        snapshots=snapshots,
        actions=actions,
        events=events,
        final_state=final_state,
        ending_status=ending_status,
        session_id=session_id,
    )

    if not replay.months:
        return

    # Identify 5 key months: M1, climax, most risky, max growth, final
    key_indices = set()
    key_indices.add(0)  # month 1
    key_indices.add(len(replay.months) - 1)  # final month

    if replay.climax_month:
        for i, m in enumerate(replay.months):
            if m.month == replay.climax_month:
                key_indices.add(i)
                break

    # Most risky month (max risk_level)
    risk_order = {"critical": 3, "high": 2, "normal": 1, "low": 0}
    most_risky_i = max(
        range(len(replay.months)),
        key=lambda i: risk_order.get(replay.months[i].risk_level, 0),
    )
    key_indices.add(most_risky_i)

    # Max MRR growth month
    max_growth_i = max(
        range(len(replay.months)),
        key=lambda i: replay.months[i].metric_changes.get("mrr", 0),
    )
    key_indices.add(max_growth_i)

    key_months = sorted(key_indices)

    tags_str = " | ".join(replay.replay_tags) if replay.replay_tags else "无"
    print(f"\n{'='*60}")
    print(f"  🎬 回放：{replay.title}")
    print(f"  🏷️  {tags_str}")
    print(f"{'='*60}")
    print(f"  📖 {replay.opening_summary}")
    print()
    for i in key_months:
        m = replay.months[i]
        marker = "⭐" if m.month == replay.climax_month else "  "
        print(
            f"  {marker} M{m.month:>2} | {m.title:20s} | "
            f"风险:{m.risk_level:8s} | "
            f"现金:{m.metric_changes.get('cash',0):+5d} "
            f"MRR:{m.metric_changes.get('mrr',0):+5d}"
        )
        if i == 0 or m.month == replay.climax_month or m.risk_level in ("critical", "high"):
            print(f"      {m.summary}")
        if m.major_events:
            for evt in m.major_events[:2]:
                print(f"      ⚡ {evt}")
    print("  ...")
    print(f"  🏁 {replay.ending_summary}")
    print(f"{'='*60}")


def print_achievements(achievement_result) -> None:
    """Print achievement badges."""
    ach = achievement_result
    if not ach.achievements:
        print(f"\n🏅 成就：{ach.summary}")
        return

    rarity_icon = {"common": "🟢", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
    print(f"\n{'='*60}")
    print(f"  🏅 成就系统 — {ach.summary}")
    print(f"{'='*60}")
    for a in ach.achievements:
        icon = rarity_icon.get(a.rarity, "⚪")
        print(f"  {icon} [{a.rarity}] {a.title}")
        print(f"     {a.description}")
    print(f"{'='*60}")


def display_result(result) -> None:
    """Display turn result summary."""
    print(f"\n--- 第{result.month}月结果 ---")

    # Show delta summary
    d = result.delta
    changes = []
    for field, label in [
        ("cash", "💰现金"),
        ("mrr", "📈MRR"),
        ("users", "👥用户"),
        ("product_score", "🛠️产品"),
        ("team_morale", "💪士气"),
        ("founder_equity", "📊股权"),
        ("reputation", "⭐声誉"),
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


def display_suggestions(state: CompanyState) -> None:
    """Alpha 1.6: Display 3 action suggestions for the current state."""
    result = SuggestionEngine.generate(state, state.month)

    print(f"{'='*60}")
    print("  💡 本月建议")
    print(f"{'='*60}")

    labels = {"conservative": "🟢 稳健路线", "aggressive": "🔶 激进路线", "warning": "🔴 风险提示"}
    for s in result.suggestions:
        label = labels.get(s.risk_level, "📌")
        print(f"  {label}：{s.title}")
        print(f"     {s.description}")
        print(f"     📝 可输入：「{s.example_input}」")
        print()

    if result.warning:
        print(f"  ⚠️  {result.warning}")
        print()

    if result.recommended_focus:
        print(f"  🎯 建议聚焦：{result.recommended_focus}")
        print()

    print(f"{'='*60}")


def display_tutorial() -> None:
    """Alpha 1.6: Display onboarding tutorial on first turn."""
    steps = TutorialEngine.get_first_turn_tutorial()
    print(f"\n{'='*60}")
    print("  🎓 新手引导")
    print(f"{'='*60}")
    for step in steps:
        print(f"\n  📖 {step.title}")
        for line in step.description.split("\n"):
            print(f"     {line.strip()}")
        if step.example_input:
            print(f"     📝 试试输入：「{step.example_input}」")
    print(f"\n{'='*60}")


def show_help() -> None:
    """Alpha 1.6: Display help / command reference."""
    print(f"\n{'='*60}")
    print("  📖 创业模拟器 — 帮助")
    print(f"{'='*60}")
    print()
    print("  🎯 游戏目标：")
    print("     12个月内带领AI客服SaaS公司完成A轮融资。")
    print("     A轮条件：MRR≥30万、产品分≥60、用户规模可观。")
    print()
    print("  🎮 常用指令：")
    print("     status  — 查看当前公司状态")
    print("     help    — 显示本帮助信息")
    print("     quit    — 退出游戏")
    print()
    print("  📝 决策输入格式：")
    print("     用自然语言描述你的决策，系统会自动解析。")
    print("     支持同时输入多个决策，用逗号/顿号/分号分隔。")
    print()
    print("  🛠️ 五种决策类型：")
    print('     研发(product)    — "花20万研发产品"')
    print('     营销(marketing)  — "花15万做营销推广"')
    print('     融资(fundraising) — "融资500万出让10%股权"')
    print('     团队(team)       — "花10万招聘扩充团队"')
    print('     战略(strategy)   — "花5万做战略规划"')
    print()
    print("  📊 关键指标：")
    print("     💰 现金     — 公司的命脉，耗尽则破产")
    print("     📈 MRR      — 月度经常性收入，A轮关键门槛")
    print("     🛠️ 产品分   — 产品竞争力(0-100)，影响用户留存")
    print("     👥 用户     — 付费客户数")
    print("     📊 股权     — 创始人对公司的控制权")
    print("     ⏳ 跑道     — 现金/月消耗，剩余生存月数")
    print()
    print("  💡 示例输入：")
    print('     "花20万研发产品，花10万做营销"')
    print('     "融资500万出让10%股权，花30万研发"')
    print('     "花5万招聘，花10万做营销推广"')
    print(f"{'='*60}")
    print()
    print("  📖 快速开始：查看 QUICKSTART.md")
    print("  📋 样例局：examples/")
    print("  🔧 遇到问题：docs/troubleshooting.md")
    print()


def load_scenario(scenario_id: str) -> CompanyState:
    """Load initial state from scenarios.yaml."""
    if not SCENARIOS_PATH.exists():
        raise FileNotFoundError(f"Scenarios file not found: {SCENARIOS_PATH}")

    with open(SCENARIOS_PATH, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    scenarios = data.get("scenarios", {})
    if scenario_id not in scenarios:
        available = ", ".join(scenarios.keys())
        raise ValueError(f"Unknown scenario '{scenario_id}'. Available: {available}")

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

    print("🚀 Startup Sim — 新游戏")
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

    # Alpha 1.6: Show onboarding tutorial
    display_tutorial()

    # Create turn engine
    engine = TurnEngine(session_id)

    # Alpha 1.6: Track shown tutorial hints to avoid repeats
    shown_hints: set = set()

    # Main game loop
    print(f"\n🎮 输入你的决策 (最多{MAX_TURNS}个月)。输入 'help' 查看帮助，'quit' 退出。")
    print("   示例: 花20万研发产品, 花10万做营销\n")

    while True:
        try:
            raw = input(f"👉 第{repository.load_state(session_id).month}月决策: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 再见！")
            break

        if not raw:
            print("  ⚠️ 请输入决策内容")
            continue

        if raw.lower() in ("quit", "exit", "q"):
            print("👋 再见！")
            break

        if raw.lower() in ("help", "帮助", "怎么玩", "指令"):
            show_help()
            continue

        if raw.lower() == "status":
            state = repository.load_state(session_id)
            display_state(state)
            # Alpha 1.6: Show suggestions after status
            display_suggestions(state)
            # Alpha 1.6: Show tutorial hints
            hints = TutorialEngine.check_hints(state, shown_hints)
            for hint in hints:
                print(f"\n  💡 [{hint.title}] {hint.message}")
                if hint.example_inputs:
                    print(f"     📝 可尝试：「{'」 或 「'.join(hint.example_inputs)}」")
            continue

        try:
            result = engine.process_turn(raw)
            display_result(result)

            if result.ending != EndingType.NONE:
                display_state(result.state_after, "📊 最终状态")
                print_review(session_id, scenario_state, result.state_after, result.ending.value)
                break

            # Show updated state
            display_state(result.state_after)

            # Alpha 1.6: Show suggestions and tutorial hints after each turn
            display_suggestions(result.state_after)
            hints = TutorialEngine.check_hints(result.state_after, shown_hints)
            for hint in hints:
                print(f"\n  💡 [{hint.title}] {hint.message}")
                if hint.example_inputs:
                    print(f"     📝 可尝试：「{'」 或 「'.join(hint.example_inputs)}」")

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
    new_parser.add_argument(
        "--scenario", type=str, default="ai_customer_service_saas", help="剧本名称"
    )
    new_parser.add_argument(
        "--difficulty",
        type=str,
        default="normal",
        choices=["easy", "normal", "hard"],
        help="游戏难度",
    )

    args = parser.parse_args()

    if args.command == "new":
        cmd_new(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
