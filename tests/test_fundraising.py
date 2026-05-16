"""Tests for fundraising logic in _simulate().

Fundraising: 500万出让10% → cash+500万, equity-10%, board_control-10%, valuation=5000万.
"""

import pytest
from src.core.models import (
    ActionPlan, CompanyState, PlayerAction, ActionType,
)
from src.core.turn_engine import _simulate
from src.core.state_guard import apply_delta


class TestFundraising:
    """Test fundraising logic via _simulate + apply_delta."""

    def test_fundraising_delta_cash_increases(self):
        """Fundraising 500万 at 10% → delta.cash is positive (includes fundraise minus burn)."""
        state = CompanyState(
            cash=1_000_000,
            founder_equity=100,
            board_control=100,
            valuation=5_000_000,
        )
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)

        # Cash delta = fundraise_amount - budget(=0) - monthly_burn(=180000)
        assert delta.cash > 0
        assert delta.cash == 5_000_000 - 180_000  # 4,820,000

    def test_fundraising_delta_equity_decreases(self):
        """Fundraising at 10% equity → delta.founder_equity = -10."""
        state = CompanyState()
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        assert delta.founder_equity == -10

    def test_fundraising_delta_board_control_decreases(self):
        """Fundraising at 10% equity → delta.board_control = -10."""
        state = CompanyState()
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        assert delta.board_control == -10

    def test_fundraising_delta_valuation_post_money(self):
        """Fundraising 500万/10% → post-money valuation = 5000万 (50,000,000)."""
        state = CompanyState()
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        assert delta.valuation == 50_000_000  # post-money = 500万 / 10%

    def test_fundraising_apply_delta_state_equity(self):
        """After apply_delta: founder_equity = 100 - 10 = 90."""
        state = CompanyState(
            founder_equity=100,
            board_control=100,
            valuation=0,
        )
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        new_state = apply_delta(state, delta)

        assert new_state.founder_equity == 90
        assert new_state.board_control == 90

    def test_fundraising_apply_delta_state_valuation(self):
        """After apply_delta with initial valuation=0: valuation = 5000万."""
        state = CompanyState(valuation=0)
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        new_state = apply_delta(state, delta)

        assert new_state.valuation == 50_000_000  # 5000万

    def test_fundraising_cash_increases_after_apply(self):
        """After apply_delta: cash = 1M + 5M - 180k(burn) = 5.82M."""
        state = CompanyState(cash=1_000_000)
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)
        new_state = apply_delta(state, delta)

        assert new_state.cash == 1_000_000 + 5_000_000 - 180_000

    def test_fundraising_zero_params_falls_back_to_legacy(self):
        """When fundraise_amount=0 or equity_offered=0, uses legacy budget*2 logic."""
        state = CompanyState(cash=1_000_000, founder_equity=100, board_control=100)
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=0,  # no specific params
            equity_offered=0,
            budget=200_000,
        )
        plan = ActionPlan(raw_input="融资", actions=[action])
        delta = _simulate(plan, state)

        # Legacy: cash += budget * 2, equity -= 5, board -= 3
        assert delta.founder_equity == -5
        assert delta.board_control == -3
        # Cash: budget*2 - budget - burn = 400k - 200k - 180k = 20k
        assert delta.cash == 200_000 * 2 - 200_000 - 180_000
