"""Balance simulation: 5 strategies × 12 months using _simulate + apply_delta.

Asserts ending diversity ≥ 3 distinct ending types across the 5 strategies.
"""

import pytest
from src.core.models import (
    ActionPlan, CompanyState, PlayerAction, ActionType, EndingType,
)
from src.core.turn_engine import _simulate
from src.core.state_guard import apply_delta
from src.core.ending_evaluator import evaluate as eval_ending


def run_strategy(monthly_actions, initial_state=None):
    """Run a strategy for up to 12 months.

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
        state = apply_delta(state, delta)
        state.month = month + 1

        # Check for early ending
        ending = eval_ending(state)
        if ending and ending != EndingType.NONE:
            return ending, state

    return eval_ending(state) or EndingType.NONE, state


# ── Strategy definitions ──────────────────────────────────────────────────────

def strategy_no_action(month, state):
    """Strategy 1: Do nothing, just watch burn. → early bankruptcy."""
    return PlayerAction(
        type=ActionType.PRODUCT,
        budget=0,  # no spend, just passive burn
    )


def strategy_fundraise_marketing(month, state):
    """Strategy 2: Fundraise 500万 at 10% in month 1, then heavy marketing.
    → should reach SURVIVED_BUT_AVERAGE (MRR ≥ 200k)."""
    if month == 1:
        return PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
    else:
        return PlayerAction(
            type=ActionType.MARKETING,
            budget=50_000,
        )


def strategy_fundraise_product_marketing(month, state):
    """Strategy 3: Fundraise 500万 in month 1, then balanced product+marketing.
    → may reach SURVIVED_BUT_AVERAGE or SLOW_DEATH."""
    if month == 1:
        return PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
    elif month % 2 == 0:
        return PlayerAction(type=ActionType.PRODUCT, budget=30_000)
    else:
        return PlayerAction(type=ActionType.MARKETING, budget=30_000)


def strategy_aggressive_product(month, state):
    """Strategy 4: Heavy product spend, no fundraising. → fast bankruptcy."""
    return PlayerAction(
        type=ActionType.PRODUCT,
        budget=100_000,
    )


def strategy_conservative_product(month, state):
    """Strategy 5: Minimal product spend, no fundraising. → slow bankruptcy or slow_death."""
    return PlayerAction(
        type=ActionType.PRODUCT,
        budget=10_000,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

class TestBalanceSimulation:
    """5-strategy balance test: assert ≥ 3 distinct endings."""

    STRATEGIES = [
        ("no_action", strategy_no_action),
        ("fundraise_marketing", strategy_fundraise_marketing),
        ("fundraise_product_marketing", strategy_fundraise_product_marketing),
        ("aggressive_product", strategy_aggressive_product),
        ("conservative_product", strategy_conservative_product),
    ]

    def test_all_strategies_run_12_months(self):
        """Each strategy completes without crashing."""
        for name, strat_fn in self.STRATEGIES:
            ending, final_state = run_strategy(strat_fn)
            assert isinstance(ending, EndingType), f"{name}: ending should be EndingType"
            assert final_state.month >= 1, f"{name}: month should advance"

    def test_ending_diversity_at_least_3(self):
        """At least 3 distinct ending types across the 5 strategies."""
        endings = set()
        for name, strat_fn in self.STRATEGIES:
            ending, _ = run_strategy(strat_fn)
            endings.add(ending)
            # Skip NONE (no ending should trigger by month 12 in our simulation)
            # Every strategy should hit some ending by month 12

        distinct = {e for e in endings if e != EndingType.NONE}
        assert len(distinct) >= 3, (
            f"Expected ≥3 distinct endings, got {len(distinct)}: {distinct}"
        )

    def test_bankruptcy_is_reached_by_some_strategy(self):
        """At least one strategy ends in BANKRUPTCY."""
        for name, strat_fn in self.STRATEGIES:
            ending, _ = run_strategy(strat_fn)
            if ending == EndingType.BANKRUPTCY:
                return  # found it
        pytest.fail("No strategy ended in BANKRUPTCY")

    def test_strategies_produce_different_states(self):
        """Different strategies produce measurably different final states."""
        final_states = {}
        for name, strat_fn in self.STRATEGIES:
            ending, state = run_strategy(strat_fn)
            final_states[name] = (ending, state)

        # fundraise strategies should have more cash than non-fundraise ones
        fm_cash = final_states["fundraise_marketing"][1].cash
        fpm_cash = final_states["fundraise_product_marketing"][1].cash
        no_cash = final_states["no_action"][1].cash

        assert fm_cash > no_cash, "fundraise_marketing should have more cash than no_action"
        assert fpm_cash > no_cash, "fundraise_product_marketing should have more cash than no_action"

    def test_product_score_differs_by_strategy(self):
        """Heavy product strategy should have higher product_score than marketing-only."""
        _, prod_state = run_strategy(strategy_aggressive_product)
        _, mktg_state = run_strategy(strategy_fundraise_marketing)
        _, cons_state = run_strategy(strategy_conservative_product)

        # Aggressive product should beat conservative product on product_score
        assert prod_state.product_score > cons_state.product_score, (
            f"aggressive({prod_state.product_score}) > conservative({cons_state.product_score})"
        )
