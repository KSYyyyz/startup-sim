"""Tests for enhanced StateGuard error messages with copiable example inputs."""

from src.core.models import ActionPlan, ActionType, CompanyState, PlayerAction
from src.core.state_guard import StateGuardError, validate_action_plan


def _make_plan(*actions):
    return ActionPlan(raw_input="test", actions=list(actions))


def _state(**kwargs):
    defaults = dict(
        month=2,
        cash=300_000,
        monthly_burn=180_000,
        product_score=40,
        team_morale=70,
        founder_equity=85,
        board_control=85,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
    )
    defaults.update(kwargs)
    return CompanyState(**defaults)


class TestStateGuardExamples:
    """Test that StateGuard error messages include copiable example inputs."""

    def test_overflow_includes_examples(self):
        """Error message contains '可复制' or '示例'."""
        state = _state()
        excessive = PlayerAction(type=ActionType.PRODUCT, budget=500_000, risk_level="medium")
        plan = _make_plan(excessive)
        try:
            validate_action_plan(plan, state)
            assert False, "Should have raised StateGuardError"
        except StateGuardError as e:
            msg = str(e)
            assert "花" in msg and ("万" in msg), f"Expected parseable example in: {msg}"
            assert "可复制" in msg or "示例" in msg or "试试" in msg

    def test_examples_parseable(self):
        """Extract example input strings and verify they match expected pattern (contain 「」)."""
        state = _state()
        excessive = PlayerAction(type=ActionType.PRODUCT, budget=600_000, risk_level="medium")
        plan = _make_plan(excessive)
        try:
            validate_action_plan(plan, state)
            assert False, "Should have raised StateGuardError"
        except StateGuardError as e:
            msg = str(e)
            # Examples should contain 「」 bracketed suggestions
            if "可复制" in msg:
                assert "「" in msg, f"Expected 「 brackets in examples: {msg}"

    def test_overflow_with_fundraising_option(self):
        """When equity >= 75, error includes fundraising option."""
        state = _state(founder_equity=90)
        excessive = PlayerAction(type=ActionType.PRODUCT, budget=500_000, risk_level="medium")
        plan = _make_plan(excessive)
        try:
            validate_action_plan(plan, state)
            assert False, "Should have raised StateGuardError"
        except StateGuardError as e:
            msg = str(e)
            # With equity >= 75, the "融资" option should appear
            assert "融资" in msg, f"Expected fundraising option for high equity: {msg}"

    def test_overflow_without_fundraising_option_low_equity(self):
        """When equity < 75, error should NOT include fundraising option."""
        state = _state(founder_equity=50)
        excessive = PlayerAction(type=ActionType.PRODUCT, budget=500_000, risk_level="medium")
        plan = _make_plan(excessive)
        try:
            validate_action_plan(plan, state)
            assert False, "Should have raised StateGuardError"
        except StateGuardError as e:
            msg = str(e)
            # Fundraising option should NOT appear when equity < 75 (only 2) and 3) appear)
            # Actually the code checks founder_equity >= 75 before adding option 2
            assert (
                "增加融资额度" not in msg
            ), f"Should not suggest fundraising with low equity: {msg}"

    def test_overflow_includes_scaled_down_suggestion(self):
        """Error always includes a scaled-down version."""
        state = _state()
        excessive = PlayerAction(type=ActionType.PRODUCT, budget=500_000, risk_level="medium")
        plan = _make_plan(excessive)
        try:
            validate_action_plan(plan, state)
            assert False, "Should have raised StateGuardError"
        except StateGuardError as e:
            msg = str(e)
            # Should include at least one example with 研发
            assert "研发" in msg or "营销" in msg or "控制" in msg
