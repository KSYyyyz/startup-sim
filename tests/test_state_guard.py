"""Tests for state_guard module."""

import pytest
from src.core.models import (
    ActionPlan, CompanyState, PlayerAction, ActionType, RiskLevel,
    StateDelta,
)
from src.core.state_guard import (
    validate_action_plan, sanitize_delta, apply_delta, StateGuardError,
)


class TestValidateActionPlan:
    """Test validation rules."""

    def test_too_many_actions(self):
        """Max 2 actions per turn."""
        state = CompanyState(cash=1_000_000)
        plan = ActionPlan(
            raw_input="test",
            actions=[
                PlayerAction(type=ActionType.PRODUCT, budget=10000),
                PlayerAction(type=ActionType.MARKETING, budget=20000),
                PlayerAction(type=ActionType.TEAM, budget=5000),
            ],
        )
        with pytest.raises(StateGuardError, match="Too many actions"):
            validate_action_plan(plan, state)

    def test_budget_exceeds_cash(self):
        """Total budget cannot exceed available cash."""
        state = CompanyState(cash=100_000)
        plan = ActionPlan(
            raw_input="test",
            actions=[
                PlayerAction(type=ActionType.MARKETING, budget=150_000),
                PlayerAction(type=ActionType.TEAM, budget=50_000),
            ],
        )
        with pytest.raises(StateGuardError, match="exceeds available cash"):
            validate_action_plan(plan, state)

    def test_high_risk_marketing_low_runway(self):
        """High-risk marketing forbidden when runway < 2 months."""
        state = CompanyState(cash=100_000, monthly_burn=90_000)  # runway ~1.1
        plan = ActionPlan(
            raw_input="test",
            actions=[
                PlayerAction(type=ActionType.MARKETING, budget=10_000, risk_level=RiskLevel.HIGH),
            ],
        )
        with pytest.raises(StateGuardError, match="high-risk marketing"):
            validate_action_plan(plan, state)

    def test_valid_plan_passes(self):
        """A legal plan should pass validation."""
        state = CompanyState(cash=1_000_000)
        plan = ActionPlan(
            raw_input="研发产品 花20万",
            actions=[
                PlayerAction(type=ActionType.PRODUCT, budget=200_000),
            ],
        )
        # Should not raise
        validate_action_plan(plan, state)


class TestSanitizeDelta:
    """Test delta sanitization."""

    def test_product_score_capped(self):
        """Product score delta capped at ±18."""
        state = CompanyState()
        delta = StateDelta(product_score=25)
        result = sanitize_delta(delta, state)
        assert result.product_score == 18

        delta2 = StateDelta(product_score=-25)
        result2 = sanitize_delta(delta2, state)
        assert result2.product_score == -18

    def test_team_morale_capped(self):
        """Team morale delta capped at ±15."""
        state = CompanyState()
        delta = StateDelta(team_morale=20)
        result = sanitize_delta(delta, state)
        assert result.team_morale == 15

        delta2 = StateDelta(team_morale=-20)
        result2 = sanitize_delta(delta2, state)
        assert result2.team_morale == -15

    def test_cash_delta_capped_at_65_percent(self):
        """Cash delta capped at ±65% of previous cash."""
        state = CompanyState(cash=100_000)
        delta = StateDelta(cash=80_000)  # 80%
        result = sanitize_delta(delta, state)
        assert result.cash == 65_000  # capped at 65%

        delta2 = StateDelta(cash=-80_000)
        result2 = sanitize_delta(delta2, state)
        assert result2.cash == -65_000

    def test_no_cap_small_delta(self):
        """Small deltas should pass through unchanged."""
        state = CompanyState(cash=100_000)
        delta = StateDelta(cash=10_000, product_score=5, team_morale=3)
        result = sanitize_delta(delta, state)
        assert result.cash == 10_000
        assert result.product_score == 5
        assert result.team_morale == 3


class TestApplyDelta:
    """Test delta application with clamping."""

    def test_apply_delta_basic(self):
        """Basic delta application."""
        state = CompanyState(cash=100_000, product_score=50)
        delta = StateDelta(cash=-20_000, product_score=10)
        result = apply_delta(state, delta)
        assert result.cash == 80_000
        assert result.product_score == 60

    def test_equity_clamp_bottom(self):
        """Equity cannot go below 0."""
        state = CompanyState(founder_equity=10)
        delta = StateDelta(founder_equity=-120)
        result = apply_delta(state, delta)
        assert result.founder_equity == 0

    def test_equity_clamp_top(self):
        """Equity cannot exceed 100."""
        state = CompanyState(founder_equity=95)
        delta = StateDelta(founder_equity=10)
        result = apply_delta(state, delta)
        assert result.founder_equity == 100

    def test_cash_clamp_bottom(self):
        """Cash cannot go below 0."""
        state = CompanyState(cash=5000)
        delta = StateDelta(cash=-10_000)
        result = apply_delta(state, delta)
        assert result.cash == 0

    def test_score_clamp_range(self):
        """Scores clamped to 0-100."""
        state = CompanyState(product_score=95)
        delta = StateDelta(product_score=10)
        result = apply_delta(state, delta)
        assert result.product_score == 100

        state2 = CompanyState(team_morale=3)
        delta2 = StateDelta(team_morale=-10)
        result2 = apply_delta(state2, delta2)
        assert result2.team_morale == 0
