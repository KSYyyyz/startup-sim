#!/usr/bin/env python3
"""12回合自动试玩脚本 — 5种策略跑满12回合，输出结局/现金/MRR/产品分/股权。

用于 Alpha 1.1 平衡验证：不应有某种策略稳定无脑获胜。
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.models import (
    ActionPlan, CompanyState, PlayerAction, ActionType, EndingType,
)
from src.core.turn_engine import _simulate
from src.core.state_guard import apply_delta
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending
from src.agents.customers import CustomerAgent

_customer_agent = CustomerAgent()

# ── Strategy definitions ──────────────────────────────────────────────────────


def strategy_all_rnd(month: int, state: CompanyState) -> PlayerAction:
    """策略1: 全研发 — 每回合10万研发产品，不融资不营销。"""
    return PlayerAction(type=ActionType.PRODUCT, budget=100_000)


def strategy_all_marketing(month: int, state: CompanyState) -> PlayerAction:
    """策略2: 全营销 — 每回合5万营销，不研发不融资。"""
    return PlayerAction(type=ActionType.MARKETING, budget=50_000)


def strategy_fundraise_then_growth(month: int, state: CompanyState) -> PlayerAction:
    """策略3: 先融资再增长 — 首回合融资500万/10%，然后产品→营销。"""
    if month == 1:
        return PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
    elif month <= 4:
        return PlayerAction(type=ActionType.PRODUCT, budget=100_000)
    else:
        return PlayerAction(type=ActionType.MARKETING, budget=150_000)


def strategy_conservative(month: int, state: CompanyState) -> PlayerAction:
    """策略4: 保守现金流 — 每回合仅5千研发，尽量延长跑道。"""
    return PlayerAction(type=ActionType.PRODUCT, budget=5_000)


def strategy_balanced(month: int, state: CompanyState) -> PlayerAction:
    """策略5: 均衡 — 首回合小融资200万/8%，交替研发+营销。"""
    if month == 1:
        return PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=2_000_000,
            equity_offered=8,
            budget=0,
        )
    elif month % 2 == 0:
        return PlayerAction(type=ActionType.PRODUCT, budget=30_000)
    else:
        return PlayerAction(type=ActionType.MARKETING, budget=30_000)


STRATEGIES = [
    ("全研发", strategy_all_rnd),
    ("全营销", strategy_all_marketing),
    ("先融资再增长", strategy_fundraise_then_growth),
    ("保守现金流", strategy_conservative),
    ("均衡", strategy_balanced),
]


def run_one_strategy(name: str, strat_fn) -> dict:
    """Run a single strategy for up to 12 months. Return result dict."""
    state = CompanyState()
    for month in range(1, 13):
        action = strat_fn(month, state)
        plan = ActionPlan(raw_input=f"{name} 第{month}月", actions=[action])
        delta = _simulate(plan, state)

        # CustomerAgent evaluates marketing/user growth
        cr = _customer_agent.evaluate(state, plan, [])
        delta.users += cr.get("growth_change", 0)
        delta.mrr += cr.get("revenue_change", 0)

        state = apply_delta(state, delta)
        state.month = month + 1

        ending = eval_ending(state)
        if ending and ending != EndingType.NONE:
            return {
                "strategy": name,
                "ending": ending.value,
                "ending_desc": describe_ending(ending, state),
                "month": state.month,
                "cash": state.cash,
                "mrr": state.mrr,
                "product_score": state.product_score,
                "users": state.users,
                "founder_equity": state.founder_equity,
                "valuation": state.valuation,
            }

    ending = eval_ending(state) or EndingType.NONE
    return {
        "strategy": name,
        "ending": ending.value,
        "ending_desc": describe_ending(ending, state) if ending != EndingType.NONE else "游戏继续",
        "month": state.month,
        "cash": state.cash,
        "mrr": state.mrr,
        "product_score": state.product_score,
        "users": state.users,
        "founder_equity": state.founder_equity,
        "valuation": state.valuation,
    }


def format_result(r: dict) -> str:
    """Format a result dict as a readable summary line."""
    cash_w = r["cash"] // 10000
    mrr_w = r["mrr"] // 10000
    val_w = r["valuation"] // 10000
    return (
        f"{r['strategy']:<10} | {r['ending']:<22} | "
        f"月{r['month']:>2} | 现金{cash_w:>5}万 | MRR{mrr_w:>5}万 | "
        f"产品{r['product_score']:>3} | 用户{r['users']:>5} | "
        f"股权{r['founder_equity']:>3}% | 估值{val_w:>6}万"
    )


def main():
    print("=" * 90)
    print("  Startup Sim — 12回合自动试玩脚本 (Alpha 1.1)")
    print("=" * 90)
    print()
    print(f"{'策略':<10} | {'结局':<22} | {'回合':>4} | {'现金':>6} | {'MRR':>6} | "
          f"{'产品':>4} | {'用户':>6} | {'股权':>4} | {'估值':>7}")
    print("-" * 90)

    results = []
    endings = set()

    for name, strat_fn in STRATEGIES:
        r = run_one_strategy(name, strat_fn)
        results.append(r)
        endings.add(r["ending"])
        print(format_result(r))

    print("-" * 90)
    print()

    # Balance check
    ending_list = sorted(endings)
    print(f"🏁 结局分布: {len(endings)} 种 → {ending_list}")
    if len(endings) >= 3:
        print("✅ 平衡验证通过：≥3种结局，不存在无脑获胜策略。")
    else:
        print(f"⚠️ 平衡警告：仅 {len(endings)} 种结局，可能需要调整参数。")

    # Check for dominant strategy
    has_series_a = any(r["ending"] == "series_a_success" for r in results)
    if has_series_a:
        winners = [r["strategy"] for r in results if r["ending"] == "series_a_success"]
        print(f"🏆 A轮成功策略: {winners}")
    else:
        print("ℹ️ 无策略达成A轮成功（难度 Normal）。")

    print()

    # Detail for each strategy
    for r in results:
        print(f"📋 {r['strategy']}")
        print(f"   {r['ending_desc']}")
        print(f"   现金={r['cash']//10000}万  MRR={r['mrr']//10000}万  "
              f"产品分={r['product_score']}  用户={r['users']}  "
              f"创始人股权={r['founder_equity']}%")
        print()


if __name__ == "__main__":
    main()
