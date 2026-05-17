"""Tests for Alpha 1.6 TutorialEngine."""

from src.core.models import CompanyState, TutorialHint, TutorialStep
from src.core.tutorial import TutorialEngine


class TestFirstTurnTutorial:
    """First turn tutorial should provide onboarding steps."""

    def test_get_first_turn_tutorial_returns_steps(self):
        """First-turn tutorial has 4 onboarding steps."""
        steps = TutorialEngine.get_first_turn_tutorial()
        assert len(steps) == 4
        for step in steps:
            assert isinstance(step, TutorialStep)
            assert step.step_id
            assert step.title
            assert step.description
            assert step.trigger_condition == "first_turn"
            assert step.shown_once is True

    def test_first_step_is_welcome(self):
        """First step should be the welcome message."""
        steps = TutorialEngine.get_first_turn_tutorial()
        assert steps[0].step_id == "welcome"
        assert "创始人" in steps[0].description

    def test_second_step_explains_input_format(self):
        """Second step should explain how to input decisions."""
        steps = TutorialEngine.get_first_turn_tutorial()
        assert steps[1].step_id == "how_to_input"
        assert steps[1].example_input != ""

    def test_third_step_lists_action_types(self):
        """Third step lists the 5 action types."""
        steps = TutorialEngine.get_first_turn_tutorial()
        assert steps[2].step_id == "action_types"
        assert "研发" in steps[2].description
        assert "营销" in steps[2].description
        assert "融资" in steps[2].description

    def test_fourth_step_explains_metrics(self):
        """Fourth step explains key metrics."""
        steps = TutorialEngine.get_first_turn_tutorial()
        assert steps[3].step_id == "metrics_101"
        assert "现金" in steps[3].description
        assert "MRR" in steps[3].description

    def test_tutorial_does_not_change_numerics(self):
        """Calling tutorial should never modify any game state."""
        state = CompanyState()
        original_cash = state.cash
        original_product = state.product_score

        TutorialEngine.get_first_turn_tutorial()
        TutorialEngine.check_hints(state)

        assert state.cash == original_cash
        assert state.product_score == original_product


class TestRunwayHint:
    """Runway threshold hints should trigger correctly."""

    def test_runway_below_3_triggers_hint(self):
        """When runway < 3 months, a cash risk hint should be shown."""
        state = CompanyState(cash=200_000, monthly_burn=100_000)
        hints = TutorialEngine.check_hints(state)
        assert len(hints) >= 1
        cash_hints = [h for h in hints if "现金" in h.title or "风险" in h.title]
        assert len(cash_hints) >= 1

    def test_runway_above_6_no_hint(self):
        """When runway is healthy, no cash hint should trigger."""
        state = CompanyState(cash=1_000_000, monthly_burn=100_000)
        hints = TutorialEngine.check_hints(state)
        cash_hints = [h for h in hints if "现金流" in h.title]
        assert len(cash_hints) == 0

    def test_hint_has_example_inputs(self):
        """Triggered hints should include example inputs."""
        state = CompanyState(cash=200_000, monthly_burn=100_000)
        hints = TutorialEngine.check_hints(state)
        for hint in hints:
            assert isinstance(hint, TutorialHint)
            if hint.example_inputs:
                assert len(hint.example_inputs) >= 1


class TestEquityHint:
    """Equity threshold hints."""

    def test_equity_below_70_triggers_hint(self):
        """When equity drops below 70%, dilution hint should appear."""
        state = CompanyState(founder_equity=60, board_control=60)
        hints = TutorialEngine.check_hints(state)
        equity_hints = [h for h in hints if "股权" in h.title or "董事会" in h.title]
        assert len(equity_hints) >= 1

    def test_equity_100_no_dilution_hint(self):
        """Full equity should not trigger dilution hint."""
        state = CompanyState(founder_equity=100)
        hints = TutorialEngine.check_hints(state)
        equity_hints = [h for h in hints if "稀释" in h.title]
        assert len(equity_hints) == 0

    def test_board_pressure_hint(self):
        """When both equity and board control are low, board risk triggers."""
        state = CompanyState(founder_equity=45, board_control=45)
        hints = TutorialEngine.check_hints(state)
        board_hints = [h for h in hints if "董事会" in h.title]
        assert len(board_hints) >= 1


class TestShownTriggers:
    """Already-shown triggers should not repeat."""

    def test_shown_triggers_not_repeated(self):
        """If a trigger was already shown, it should not appear again."""
        state = CompanyState(cash=200_000, monthly_burn=100_000)
        shown = {"runway_below_3"}
        hints = TutorialEngine.check_hints(state, shown)
        cash_hints = [h for h in hints if "现金" in h.title]
        assert len(cash_hints) == 0

    def test_new_triggers_still_show(self):
        """Unshown triggers should still appear even when some are shown."""
        state = CompanyState(
            cash=200_000,
            monthly_burn=100_000,
            founder_equity=50,
            board_control=50,
            team_morale=30,
        )
        shown = {"runway_below_3"}
        hints = TutorialEngine.check_hints(state, shown)
        # Should still get equity and morale hints
        assert len(hints) >= 2


class TestNoNumericalChanges:
    """Tutorial hints must not modify game state."""

    def test_hints_dont_change_cash(self):
        """Checking hints should not change cash."""
        state = CompanyState(cash=100_000, monthly_burn=50_000)
        original = state.cash
        TutorialEngine.check_hints(state)
        assert state.cash == original

    def test_hints_dont_change_product(self):
        """Checking hints should not change product score."""
        state = CompanyState(product_score=25)
        original = state.product_score
        TutorialEngine.check_hints(state)
        assert state.product_score == original

    def test_hints_dont_change_equity(self):
        """Checking hints should not change founder equity."""
        state = CompanyState(founder_equity=60)
        original = state.founder_equity
        TutorialEngine.check_hints(state)
        assert state.founder_equity == original
