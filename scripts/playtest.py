#!/usr/bin/env python3
"""12回合自动试玩脚本 — 5种策略跑满12回合，输出结局/现金/MRR/产品分/股权。

Alpha 1.1 平衡验证：走完整 TurnEngine.process_turn_raw 流程，
覆盖 parse_multi / StateGuard / 竞品 / 客户 / 事件 / 结局。
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src is importable
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.models import CompanyState, EndingType
from src.core.turn_engine import TurnEngine
from src.core.state_guard import StateGuardError
from src.core.difficulty import get_difficulty


# ── Strategy definitions (generate raw_input strings) ──────────────────────────


def strategy_all_rnd(month: int, state: CompanyState) -> str:
    """策略1: 全研发 — 每回合10万研发产品，不融资不营销。"""
    budget_wan = min(10, state.cash // 10000)
    if budget_wan <= 0:
        return ""
    return f"花{budget_wan}万研发产品"


def strategy_all_marketing(month: int, state: CompanyState) -> str:
    """策略2: 全营销 — 每回合5万营销，不研发不融资。"""
    budget_wan = min(5, state.cash // 10000)
    if budget_wan <= 0:
        return ""
    return f"花{budget_wan}万做营销"


def strategy_fundraise_then_growth(month: int, state: CompanyState) -> str:
    """策略3: 先融资再增长 — 首回合融资500万/10%，然后产品→营销。"""
    if month == 1:
        return "融资500万出让10%"
    elif month <= 4:
        budget_wan = min(10, state.cash // 10000)
        if budget_wan <= 0:
            return ""
        return f"花{budget_wan}万研发产品"
    else:
        budget_wan = min(15, state.cash // 10000)
        if budget_wan <= 0:
            return ""
        return f"花{budget_wan}万做营销"


def strategy_conservative(month: int, state: CompanyState) -> str:
    """策略4: 保守现金流 — 每回合仅5千研发，尽量延长跑道。"""
    if state.cash < 5000:
        return ""
    return "花5千研发产品"


def strategy_balanced(month: int, state: CompanyState) -> str:
    """策略5: 均衡 — 首回合小融资200万/8%，交替研发+营销。"""
    if month == 1:
        return "融资200万出让8%"
    budget_wan = min(3, state.cash // 10000)
    if budget_wan <= 0:
        return ""
    if month % 2 == 0:
        return f"花{budget_wan}万研发产品"
    else:
        return f"花{budget_wan}万做营销"


STRATEGIES = [
    ("全研发", strategy_all_rnd),
    ("全营销", strategy_all_marketing),
    ("先融资再增长", strategy_fundraise_then_growth),
    ("保守现金流", strategy_conservative),
    ("均衡", strategy_balanced),
]


def run_one_strategy(name: str, strat_fn, difficulty=None) -> dict:
    """Run a single strategy for up to 12 months via TurnEngine.process_turn_raw.

    Each turn: generate raw_input → process_turn_raw → use result.state_after.
    Covers parse_multi, StateGuard, competitors, CustomerAgent, events, endings.
    """
    state = CompanyState()
    difficulty = difficulty or get_difficulty("normal")

    for month in range(1, 13):
        raw_input = strat_fn(month, state)
        if not raw_input or not raw_input.strip():
            # Strategy has nothing to do this turn (empty = pass)
            raw_input = ""

        try:
            result = TurnEngine.process_turn_raw(state, raw_input, difficulty)
        except StateGuardError:
            # Overspending caught by StateGuard — treat as forced end
            state.month = month
            return {
                "strategy": name,
                "ending": "bankruptcy",
                "ending_desc": f"第{month}月现金流断裂，无法继续运营。",
                "month": state.month,
                "cash": state.cash,
                "mrr": state.mrr,
                "product_score": state.product_score,
                "users": state.users,
                "founder_equity": state.founder_equity,
                "valuation": state.valuation,
                "events": [],
            }

        state = result.state_after

        if result.ending and result.ending != EndingType.NONE:
            return {
                "strategy": name,
                "ending": result.ending.value,
                "ending_desc": result.ending_description,
                "month": state.month,
                "cash": state.cash,
                "mrr": state.mrr,
                "product_score": state.product_score,
                "users": state.users,
                "founder_equity": state.founder_equity,
                "valuation": state.valuation,
                "events": [e.event_type for e in result.events],
            }

    return {
        "strategy": name,
        "ending": "none",
        "ending_desc": "游戏继续",
        "month": state.month,
        "cash": state.cash,
        "mrr": state.mrr,
        "product_score": state.product_score,
        "users": state.users,
        "founder_equity": state.founder_equity,
        "valuation": state.valuation,
        "events": [],
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
    print("  Flow: TurnEngine.process_turn_raw → parse_multi/StateGuard/竞品/客户/事件/结局")
    print("=" * 90)
    print()
    print(f"{'策略':<10} | {'结局':<22} | {'回合':>4} | {'现金':>6} | {'MRR':>6} | "
          f"{'产品':>4} | {'用户':>6} | {'股权':>4} | {'估值':>7}")
    print("-" * 90)

    difficulty = get_difficulty("normal")
    results = []
    endings = set()

    for name, strat_fn in STRATEGIES:
        r = run_one_strategy(name, strat_fn, difficulty)
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
        if r.get("events"):
            print(f"   事件: {', '.join(r['events'])}")
        print()


if __name__ == "__main__":
    main()
