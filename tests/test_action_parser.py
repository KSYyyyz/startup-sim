"""Tests for action_parser module — parse_multi() and helpers."""

from src.core.action_parser import _extract_budget_per_segment, parse, parse_multi
from src.core.models import ActionType


class TestExtractBudgetPerSegment:
    """Test budget extraction from single clauses."""

    def test_wan_unit(self):
        """'30万' should return 300,000."""
        assert _extract_budget_per_segment("研发花30万") == 300_000

    def test_no_budget(self):
        """Text without 万 should return 0."""
        assert _extract_budget_per_segment("降价到3000元抢市场") == 0

    def test_multiple_wan_takes_first(self):
        """Only the first 万 pattern is captured."""
        # "20万" and "30万" → takes first
        assert _extract_budget_per_segment("先花20万再花30万") == 200_000


class TestParseMultiFundraising:
    """Test parse_multi fundraising extraction."""

    def test_fundraising_with_multiple_actions(self):
        """融资500万出让10%，花200万研发，100万招聘，50万投放 → 4 actions."""
        plan = parse_multi("融资500万出让10%，花200万研发，100万招聘，50万投放")
        assert len(plan.actions) == 4

        # Find fundraising action
        fundraising = [a for a in plan.actions if a.type == ActionType.FUNDRAISING]
        assert len(fundraising) == 1
        f = fundraising[0]
        assert f.fundraise_amount == 5_000_000
        assert f.equity_offered == 10
        assert f.budget == 0  # fundraising doesn't have budget spend

        # Find product action
        product = [a for a in plan.actions if a.type == ActionType.PRODUCT]
        assert len(product) == 1
        assert product[0].budget == 2_000_000  # 200万

        # Find team action
        team = [a for a in plan.actions if a.type == ActionType.TEAM]
        assert len(team) == 1
        assert team[0].budget == 1_000_000  # 100万

        # Find marketing action
        marketing = [a for a in plan.actions if a.type == ActionType.MARKETING]
        assert len(marketing) == 1
        assert marketing[0].budget == 500_000  # 50万

    def test_single_product_action(self):
        """研发产品花30万 → 1 action, product budget=300,000."""
        plan = parse_multi("研发产品花30万")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.PRODUCT
        assert plan.actions[0].budget == 300_000  # 30万

    def test_marketing_no_budget(self):
        """降价到3000元抢市场 → marketing, budget=0."""
        plan = parse_multi("降价到3000元抢市场")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.MARKETING
        assert plan.actions[0].budget == 0

    def test_fundraising_only(self):
        """Pure fundraising input."""
        plan = parse_multi("融资800万出让15%")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.FUNDRAISING
        assert plan.actions[0].fundraise_amount == 8_000_000
        assert plan.actions[0].equity_offered == 15

    def test_no_duplicate_types(self):
        """Each action type appears at most once."""
        plan = parse_multi("研发核心功能花20万，开发新特性花10万")
        # Both are product type, only first should match
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.PRODUCT

    def test_raw_input_preserved(self):
        """The raw_input field is preserved."""
        raw = "融资500万出让10%，花100万推广"
        plan = parse_multi(raw)
        assert plan.raw_input == raw


class TestParseMultiBackwardCompat:
    """Ensure old parse() still works."""

    def test_old_parse_still_works(self):
        """Old parse() should still return valid results."""
        plan = parse("研发产品花20万")
        assert len(plan.actions) >= 1
        assert plan.actions[0].type == ActionType.PRODUCT


class TestParseMultiComplexSentences:
    """Test parse_multi with complex multi-clause input sentences (P0-4)."""

    def test_complex_sentence_four_actions(self):
        """融资500万出让10%，花200万研发产品，100万招聘，50万做营销 → 4 actions with correct budgets."""
        plan = parse_multi("融资500万出让10%，花200万研发产品，100万招聘，50万做营销")
        assert len(plan.actions) == 4

        fundraising = [a for a in plan.actions if a.type == ActionType.FUNDRAISING]
        assert len(fundraising) == 1
        assert fundraising[0].fundraise_amount == 5_000_000
        assert fundraising[0].equity_offered == 10.0
        assert fundraising[0].post_money_valuation == 50_000_000

        product = [a for a in plan.actions if a.type == ActionType.PRODUCT]
        assert len(product) == 1
        assert product[0].budget == 2_000_000

        team = [a for a in plan.actions if a.type == ActionType.TEAM]
        assert len(team) == 1
        assert team[0].budget == 1_000_000

        marketing = [a for a in plan.actions if a.type == ActionType.MARKETING]
        assert len(marketing) == 1
        assert marketing[0].budget == 500_000

    def test_semicolon_separator(self):
        """Semicolons split clauses: 研发花20万；营销花10万 → 2 actions."""
        plan = parse_multi("研发花20万；营销花10万")
        assert len(plan.actions) == 2
        types = {a.type for a in plan.actions}
        assert ActionType.PRODUCT in types
        assert ActionType.MARKETING in types

    def test_dunhao_separator(self):
        """顿号 splits clauses: 研发花30万、招聘花15万 → 2 actions."""
        plan = parse_multi("研发花30万、招聘花15万")
        assert len(plan.actions) == 2
        types = {a.type for a in plan.actions}
        assert ActionType.PRODUCT in types
        assert ActionType.TEAM in types

    def test_english_comma_separator(self):
        """English commas split: 研发花20万, 营销花10万 → 2 actions."""
        plan = parse_multi("研发花20万, 营销花10万")
        assert len(plan.actions) == 2

    def test_mixed_separators(self):
        """Mixed separators: 研发30万，营销20万；招人10万、策略5万 → 4 actions."""
        plan = parse_multi("研发30万，营销20万；招人10万、策略5万")
        assert len(plan.actions) == 4

    def test_max_five_actions(self):
        """ActionPlan max_length=5: extra clauses are dropped."""
        raw = (
            "融资200万出让5%，"
            "研发花50万，"
            "营销花30万，"
            "招人花20万，"
            "策略花10万，"
            "降价花5万"
        )
        plan = parse_multi(raw)
        # Fundraising + 5 other clauses, but max 5 actions total
        assert len(plan.actions) <= 5

    def test_clause_without_budget(self):
        """Clause without budget still detected via keywords."""
        plan = parse_multi("降价抢市场，招聘工程师")
        assert len(plan.actions) == 2
        marketing = [a for a in plan.actions if a.type == ActionType.MARKETING]
        team = [a for a in plan.actions if a.type == ActionType.TEAM]
        assert len(marketing) == 1
        assert len(team) == 1
        assert marketing[0].budget == 0  # no 万 pattern
        assert team[0].budget == 0

    def test_fundraising_with_equity_in_different_order(self):
        """出让15%融资800万 → fundraising with amount and equity."""
        plan = parse_multi("出让15%融资800万")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.FUNDRAISING
        assert plan.actions[0].fundraise_amount == 8_000_000
        assert plan.actions[0].equity_offered == 15.0

    def test_fundraising_only_no_other_actions(self):
        """Pure fundraising text yields only fundraising action."""
        plan = parse_multi("我要融资1000万，出让20%股权给投资人")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.FUNDRAISING
        assert plan.actions[0].fundraise_amount == 10_000_000
        assert plan.actions[0].equity_offered == 20.0

    def test_strategy_action_detected(self):
        """Strategy keywords like 转型/战略 should be detected."""
        plan = parse_multi("转型新市场花100万")
        assert len(plan.actions) == 1
        assert plan.actions[0].type == ActionType.STRATEGY
        assert plan.actions[0].budget == 1_000_000

    def test_empty_input_returns_empty_plan(self):
        """Empty input yields ActionPlan with no actions."""
        plan = parse_multi("")
        assert plan.raw_input == ""
        assert len(plan.actions) == 0

    def test_raw_input_with_only_separators(self):
        """Input with only separators yields empty plan."""
        plan = parse_multi("，；、,")
        assert len(plan.actions) == 0
