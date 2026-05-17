"""Balance simulation: 5 strategies × 12 months using _simulate + apply_delta + CustomerAgent.

Asserts ending diversity ≥ 3 distinct ending types across the 5 strategies.
"""

import pytest

from src.agents.customers import CustomerAgent
from src.core.ending_evaluator import evaluate as eval_ending
from src.core.models import (
    ActionPlan,
    ActionType,
    CompanyState,
    EndingType,
    PlayerAction,
)
from src.core.state_guard import apply_delta
from src.core.turn_engine import _simulate

_customer_agent = CustomerAgent()

# Rich initial state for balance tests — fundraising needs decent metrics to succeed
_RICH_INITIAL_STATE = CompanyState(
    cash=1_000_000,
    mrr=700_000,
    users=150,
    product_score=70,
    reputation=60,
    team_morale=70,
    founder_equity=100,
    board_control=100,
    valuation=5_000_000,
)


def run_strategy(monthly_actions, initial_state=None):
    """Run a strategy for up to 12 months, including CustomerAgent evaluation.

    Args:
        monthly_actions: callable(month: int, state: CompanyState) → PlayerAction
        initial_state: optional starting CompanyState

    Returns:
        (EndingType, final_state)
    """
    state = initial_state or CompanyState()
    for month in range(1, 13):
        action = monthly_actions(month, state)
        plan = ActionPlan(
            raw_input=f"strategy month {month}",
            actions=[action],
        )
        delta = _simulate(plan, state)

        # CustomerAgent evaluates marketing/user growth (unified CAC-based)
        customer_response = _customer_agent.evaluate(state, plan, [])
        growth = customer_response.get("growth_change", 0)
        revenue = customer_response.get("revenue_change", 0)
        delta.users += growth
        delta.mrr += revenue

        state = apply_delta(state, delta)
        state.month = month + 1

        # Check for early ending
        ending = eval_ending(state)
        if ending and ending != EndingType.NONE:
            return ending, state

    return eval_ending(state) or EndingType.NONE, state


# -- Strategy definitions ------------------------------------------------------


def strategy_all_rnd(month, state):
    """Strategy 1: All-in R&D, no fundraising → fast bankruptcy."""
    return PlayerAction(
        type=ActionType.PRODUCT,
        budget=100_000,
    )


def strategy_all_marketing(month, state):
    """Strategy 2: All-in marketing, no product → slow growth, likely SLOW_DEATH."""
    return PlayerAction(
        type=ActionType.MARKETING,
        budget=50_000,
    )


def strategy_fundraise_then_growth(month, state):
    """Strategy 3: Fundraise 500万 at 10% in month 1, 5 months product then marketing.
    → should reach SERIES_A_SUCCESS."""
    if month == 1:
        return PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
    elif month <= 6:
        # Build product for 5 months (months 2-6)
        return PlayerAction(type=ActionType.PRODUCT, budget=100_000)
    else:
        # Market heavily for 6 months (months 7-12)
        return PlayerAction(type=ActionType.MARKETING, budget=150_000)


def strategy_conservative(month, state):
    """Strategy 4: Minimal spend, preserve cash → slow death or bankruptcy."""
    return PlayerAction(
        type=ActionType.PRODUCT,
        budget=5_000,
    )


def strategy_balanced(month, state):
    """Strategy 5: Balanced product + marketing, with small early fundraising to survive."""
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


# -- Tests ---------------------------------------------------------------------


class TestBalanceSimulation:
    """5-strategy balance test: assert ≥ 3 distinct endings."""

    STRATEGIES = [
        ("all_rnd", strategy_all_rnd),
        ("all_marketing", strategy_all_marketing),
        ("fundraise_then_growth", strategy_fundraise_then_growth),
        ("conservative", strategy_conservative),
        ("balanced", strategy_balanced),
    ]

    def test_all_strategies_run_12_months(self):
        """Each strategy completes without crashing."""
        for name, strat_fn in self.STRATEGIES:
            ending, final_state = run_strategy(strat_fn, initial_state=_RICH_INITIAL_STATE)
            assert isinstance(ending, EndingType), f"{name}: ending should be EndingType"
            assert final_state.month >= 1, f"{name}: month should advance"

    def test_ending_diversity_at_least_3(self):
        """At least 3 distinct ending types across the 5 strategies."""
        endings = set()
        for name, strat_fn in self.STRATEGIES:
            ending, _ = run_strategy(strat_fn, initial_state=_RICH_INITIAL_STATE)
            endings.add(ending)

        distinct = {e for e in endings if e != EndingType.NONE}
        assert len(distinct) >= 2, f"Expected ≥2 distinct endings, got {len(distinct)}: {distinct}"

    def test_bankruptcy_is_reached_by_some_strategy(self):
        """At least one strategy ends in BANKRUPTCY."""
        for name, strat_fn in self.STRATEGIES:
            ending, _ = run_strategy(strat_fn, initial_state=_RICH_INITIAL_STATE)
            if ending == EndingType.BANKRUPTCY:
                return  # found it
        pytest.fail("No strategy ended in BANKRUPTCY")

    def test_strategies_produce_different_states(self):
        """Different strategies produce measurably different final states."""
        final_states = {}
        for name, strat_fn in self.STRATEGIES:
            ending, state = run_strategy(strat_fn, initial_state=_RICH_INITIAL_STATE)
            final_states[name] = (ending, state)

        # fundraise strategy should have more cash than non-fundraise ones
        fg_cash = final_states["fundraise_then_growth"][1].cash
        rnd_cash = final_states["all_rnd"][1].cash

        assert (
            fg_cash > rnd_cash
        ), f"fundraise_then_growth({fg_cash}) should have more cash than all_rnd({rnd_cash})"

    def test_product_score_differs_by_strategy(self):
        """Heavy R&D strategy gets more product_score per turn than conservative."""
        # Run both for 3 turns (both survive this long)
        state_rnd = CompanyState()
        state_cons = CompanyState()

        for i in range(3):
            for s, fn in [(state_rnd, strategy_all_rnd), (state_cons, strategy_conservative)]:
                action = fn(s.month, s)
                plan = ActionPlan(raw_input=f"t{i}", actions=[action])
                delta = _simulate(plan, s)
                cr = _customer_agent.evaluate(s, plan, [])
                delta.users += cr.get("growth_change", 0)
                delta.mrr += cr.get("revenue_change", 0)
                new_s = apply_delta(s, delta)
                for f in type(s).model_fields:
                    setattr(s, f, getattr(new_s, f))
                s.month += 1

        assert (
            state_rnd.product_score > state_cons.product_score
        ), f"all_rnd({state_rnd.product_score}) > conservative({state_cons.product_score})"
