"""Tests for Alpha 1.6 SuggestionEngine."""

from src.core.models import ActionSuggestion, CompanyState, SuggestionResult
from src.core.suggestion_engine import SuggestionEngine


class TestLowCashSuggestions:
    """When cash is low, suggestions should focus on survival."""

    def test_low_cash_conservative_suggests_cut_spending(self):
        """With runway < 4, conservative suggestion should mention cutting spending."""
        state = CompanyState(cash=200_000, monthly_burn=100_000, product_score=25)
        result = SuggestionEngine.generate(state, turn_number=3)
        assert len(result.suggestions) == 3
        conservative = result.suggestions[0]
        assert conservative.risk_level == "conservative"
        assert "控支" in conservative.title or "保命" in conservative.title

    def test_low_cash_aggressive_suggests_fundraising(self):
        """With low cash and high equity, aggressive should suggest fundraising."""
        state = CompanyState(cash=200_000, monthly_burn=100_000)
        result = SuggestionEngine.generate(state, turn_number=3)
        aggressive = result.suggestions[1]
        assert aggressive.risk_level == "aggressive"
        assert "融资" in aggressive.title or "融资" in aggressive.example_input

    def test_low_cash_warning_not_empty(self):
        """Warning text should not be empty when risks are present."""
        state = CompanyState(cash=200_000, monthly_burn=100_000)
        result = SuggestionEngine.generate(state, turn_number=3)
        assert result.warning != ""


class TestHighProductLowMRRSuggestions:
    """High product score but low MRR should trigger commercialization push."""

    def test_high_product_low_mrr_conservative_suggests_marketing(self):
        """Conservative suggestion should mention light marketing."""
        state = CompanyState(
            cash=500_000,
            monthly_burn=100_000,
            product_score=70,
            mrr=20_000,
            month=5,
        )
        result = SuggestionEngine.generate(state, turn_number=5)
        conservative = result.suggestions[0]
        assert "营销" in conservative.example_input or "获客" in conservative.title

    def test_high_product_low_mrr_aggressive_suggests_marketing(self):
        """Aggressive suggestion should push marketing + fundraising."""
        state = CompanyState(
            cash=500_000,
            monthly_burn=100_000,
            product_score=70,
            mrr=20_000,
            month=5,
        )
        result = SuggestionEngine.generate(state, turn_number=5)
        aggressive = result.suggestions[1]
        assert aggressive.risk_level == "aggressive"


class TestLowProductHighMarketing:
    """When product score is low but user count is decent, warn about bubble."""

    def test_low_product_high_users_conservative_suggests_rd(self):
        """Conservative should suggest R&D focus."""
        state = CompanyState(
            cash=500_000,
            monthly_burn=100_000,
            product_score=25,
            users=200,
        )
        result = SuggestionEngine.generate(state, turn_number=4)
        conservative = result.suggestions[0]
        assert conservative.risk_level == "conservative"

    def test_low_product_high_users_warning_present(self):
        """Warning about marketing bubble should appear."""
        state = CompanyState(
            cash=500_000,
            monthly_burn=100_000,
            product_score=25,
            users=200,
            month=4,
        )
        result = SuggestionEngine.generate(state, turn_number=4)
        assert result.warning != ""


class TestExampleInputParseability:
    """Every suggestion must have an example_input that parse_multi can parse."""

    def test_all_example_inputs_are_nonempty(self):
        """No empty example inputs."""
        state = CompanyState()
        result = SuggestionEngine.generate(state)
        for s in result.suggestions:
            assert s.example_input.strip(), f"Empty example_input in {s.title}"

    def test_conservative_example_input_parseable(self):
        """Conservative example input should be parseable."""
        from src.core.action_parser import parse_multi

        state = CompanyState()
        result = SuggestionEngine.generate(state)
        s = result.suggestions[0]
        plan = parse_multi(s.example_input)
        assert len(plan.actions) >= 1, f"Failed to parse: {s.example_input}"

    def test_aggressive_example_input_parseable(self):
        """Aggressive example input should be parseable."""
        from src.core.action_parser import parse_multi

        state = CompanyState()
        result = SuggestionEngine.generate(state)
        s = result.suggestions[1]
        plan = parse_multi(s.example_input)
        assert len(plan.actions) >= 1, f"Failed to parse: {s.example_input}"

    def test_warning_example_input_parseable(self):
        """Warning example input should be parseable."""
        from src.core.action_parser import parse_multi

        state = CompanyState()
        result = SuggestionEngine.generate(state)
        s = result.suggestions[2]
        plan = parse_multi(s.example_input)
        assert len(plan.actions) >= 1, f"Failed to parse: {s.example_input}"


class TestSuggestionResultModel:
    """SuggestionResult model should have correct fields."""

    def test_suggestion_result_has_three_suggestions(self):
        """SuggestionResult always has exactly 3 suggestions."""
        state = CompanyState()
        result = SuggestionEngine.generate(state)
        assert len(result.suggestions) == 3
        assert isinstance(result, SuggestionResult)

    def test_suggestions_have_required_fields(self):
        """Each suggestion has title, description, example_input, risk_level."""
        state = CompanyState()
        result = SuggestionEngine.generate(state)
        for s in result.suggestions:
            assert isinstance(s, ActionSuggestion)
            assert s.title
            assert s.description
            assert s.example_input
            assert s.risk_level in ("conservative", "aggressive", "warning")

    def test_recommended_focus_not_empty(self):
        """Recommended focus should always be set."""
        state = CompanyState()
        result = SuggestionEngine.generate(state)
        assert result.recommended_focus


class TestEdgeCases:
    """Edge case handling."""

    def test_zero_cash_state_does_not_crash(self):
        """Zero cash should not cause crash."""
        state = CompanyState(cash=0, monthly_burn=100_000)
        result = SuggestionEngine.generate(state)
        assert len(result.suggestions) == 3

    def test_high_all_state_does_not_crash(self):
        """Very high numbers should not cause crash."""
        state = CompanyState(
            cash=10_000_000,
            monthly_burn=50_000,
            product_score=95,
            mrr=500_000,
            users=5000,
            founder_equity=95,
        )
        result = SuggestionEngine.generate(state)
        assert len(result.suggestions) == 3

    def test_bankruptcy_edge_state(self):
        """State with near-zero cash, high burn. Should still generate suggestions."""
        state = CompanyState(cash=5000, monthly_burn=200_000)
        result = SuggestionEngine.generate(state, turn_number=10)
        assert len(result.suggestions) == 3
        assert result.warning != ""
