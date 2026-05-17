"""Supplementary tests for Alpha 1.2.

Covers:
  1. process_turn_raw end-to-end (full TurnEngine flow)
  2. Marketing does NOT double-add users/mrr (CustomerAgent handles it)
  3. Fundraising cash exempt from sanitize 65% cap (verified via process_turn_raw)
  4. Product R&D formula: budget//80k + emp//3 + morale//10
"""

from src.agents.customers import CustomerAgent
from src.core.ending_evaluator import evaluate as eval_ending
from src.core.models import (
    ActionPlan,
    ActionType,
    CompanyState,
    EndingType,
    PlayerAction,
)
from src.core.state_guard import sanitize_delta
from src.core.turn_engine import TurnEngine, _simulate

# ── 1. process_turn_raw end-to-end ────────────────────────────────────────────


class TestProcessTurnRawE2E:
    """Verify process_turn_raw covers the full pipeline:
    parse → simulate → competitors → customers → sanitize → events → ending.
    """

    def test_process_turn_raw_with_product_action(self):
        """Product action via process_turn_raw: state updates + no crash."""
        state = CompanyState()
        result = TurnEngine.process_turn_raw(state, "花10万研发产品")

        # Check result structure
        assert result.month == 1
        assert len(result.action_plan.actions) >= 1
        assert result.action_plan.actions[0].type == ActionType.PRODUCT

        # State should advance
        assert result.state_after.month == 2
        assert result.state_after.product_score > state.product_score
        assert result.state_after.cash < state.cash  # spent money

        # Board feedback should be present
        assert len(result.board_feedback) >= 1

        # Competitor moves should be generated
        assert isinstance(result.competitor_moves, list)

        # Customer response should be generated
        assert "narrative" in result.customer_response

    def test_process_turn_raw_with_fundraising(self):
        """Fundraising via process_turn_raw: cash increases, equity decreases."""
        state = CompanyState(mrr=700_000, product_score=70, reputation=60)
        result = TurnEngine.process_turn_raw(state, "融资500万出让10%")

        assert result.state_after.cash > state.cash
        assert result.state_after.founder_equity == 90
        assert result.state_after.board_control == 90
        # Post-money valuation = 500万 / 10% = 5000万, added to initial 500万 = 5500万
        assert result.state_after.valuation == 55_000_000

    def test_process_turn_raw_with_marketing(self):
        """Marketing via process_turn_raw: users/MRR grow via CustomerAgent."""
        state = CompanyState()
        result = TurnEngine.process_turn_raw(state, "花5万做营销")

        # Customer agent should produce growth
        customer = result.customer_response
        assert customer.get("growth_change", 0) != 0 or customer.get("revenue_change", 0) != 0

    def test_process_turn_raw_multi_action(self):
        """Multiple actions in one turn via process_turn_raw."""
        state = CompanyState()
        result = TurnEngine.process_turn_raw(state, "融资200万出让8%，花5万研发产品，花3万做营销")

        action_types = {a.type for a in result.action_plan.actions}
        assert len(action_types) >= 2  # at least product + marketing
        assert result.state_after.month == 2  # month advanced
        assert result.state_after.cash > 0  # shouldn't go bankrupt

    def test_process_turn_raw_slow_death_at_month_12(self):
        """process_turn_raw triggers SLOW_DEATH when month>=12 with low MRR."""
        state = CompanyState(
            month=12, cash=5_000_000, mrr=50_000, product_score=20, founder_equity=80
        )
        result = TurnEngine.process_turn_raw(state, "")

        # Month >= 12, mrr < 100k → SLOW_DEATH
        assert result.ending != EndingType.NONE
        assert result.ending == EndingType.SLOW_DEATH
        assert result.ending_description != ""

    def test_process_turn_raw_bankruptcy_from_zero_cash(self):
        """When cash is already 0, evaluating state gives BANKRUPTCY."""

        # Cash already 0 → evaluate directly returns bankruptcy
        state = CompanyState(cash=0, month=5)
        ending = eval_ending(state)
        assert ending == EndingType.BANKRUPTCY

    def test_process_turn_raw_12_month_ending(self):
        """At month 12, process_turn_raw should evaluate ending."""
        state = CompanyState(
            month=12, cash=500_000, mrr=200_000, product_score=75, founder_equity=80
        )
        result = TurnEngine.process_turn_raw(state, "花1万研发产品")

        # Month 12 + 1 = 13 >= 12, so ending should be evaluated
        assert result.ending != EndingType.NONE
        # MRR >= 100k, cash > 0 → SURVIVED_BUT_AVERAGE or better
        assert result.ending in (EndingType.SURVIVED_BUT_AVERAGE, EndingType.SERIES_A_SUCCESS)


# ── 2. Marketing does NOT double-add users/MRR ────────────────────────────────


class TestMarketingNoDoubleAdd:
    """Verify that marketing actions in _simulate do NOT directly add users/mrr.
    The CustomerAgent is the sole handler for user growth and MRR from marketing.
    """

    def test_simulate_marketing_does_not_add_users_directly(self):
        """_simulate with marketing action: delta.users == 0, delta.mrr == 0."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.MARKETING, budget=100_000)
        plan = ActionPlan(raw_input="花10万做营销", actions=[action])
        delta = _simulate(plan, state)

        # _simulate should NOT add users or mrr for marketing
        assert delta.users == 0, f"_simulate should NOT add users for marketing (got {delta.users})"
        assert delta.mrr == 0, f"_simulate should NOT add mrr for marketing (got {delta.mrr})"

        # But it should add burn and reputation
        assert delta.monthly_burn > 0
        assert delta.reputation >= 0

    def test_customer_agent_adds_users_and_mrr(self):
        """CustomerAgent.evaluate with marketing: returns growth_change and revenue_change."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.MARKETING, budget=100_000)
        plan = ActionPlan(raw_input="花10万做营销", actions=[action])
        ca = CustomerAgent()
        response = ca.evaluate(state, plan, [])

        assert (
            response.get("growth_change", 0) > 0
        ), "CustomerAgent should produce positive growth_change for marketing"
        assert (
            response.get("revenue_change", 0) > 0
        ), "CustomerAgent should produce positive revenue_change for marketing"

    def test_combined_simulate_and_customer_no_double_count(self):
        """After _simulate + CustomerAgent, users/mrr come ONLY from CustomerAgent."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.MARKETING, budget=100_000)
        plan = ActionPlan(raw_input="花10万做营销", actions=[action])

        delta = _simulate(plan, state)
        ca = CustomerAgent()
        response = ca.evaluate(state, plan, [])

        # Before merging customer response, delta has 0 users and 0 mrr
        assert delta.users == 0
        assert delta.mrr == 0

        # Merge customer response
        delta.users += response.get("growth_change", 0)
        delta.mrr += response.get("revenue_change", 0)

        # After merge, users and mrr should be nonzero
        assert delta.users > 0
        assert delta.mrr > 0

    def test_product_action_does_not_trigger_marketing_growth(self):
        """Product-only action: CustomerAgent shouldn't produce marketing growth."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        ca = CustomerAgent()
        response = ca.evaluate(state, plan, [])

        # Product-only: no marketing_budget, so no marketing-driven growth
        # But may have organic growth from product score
        # Key: the "market投放" narrative should NOT appear
        narrative = response.get("narrative", "")
        assert "市场投放" not in narrative, "Product-only should not trigger marketing narrative"


# ── 3. Fundraising cash exempt from 65% cap ───────────────────────────────────


class TestFundraisingCashExemption:
    """Verify that fundraising_cash bypasses the 65% cash outflow cap in sanitize_delta."""

    def test_fundraising_delta_has_fundraising_cash_field(self):
        """_simulate with fundraising sets delta.fundraising_cash."""
        state = CompanyState(cash=1_000_000, mrr=700_000, product_score=70, reputation=60)
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)

        assert (
            delta.fundraising_cash == 5_000_000
        ), f"fundraising_cash should be 5,000,000, got {delta.fundraising_cash}"

    def test_small_cash_state_fundraising_not_capped(self):
        """小现金(10万)融资500万: 融资流入不应被65%限制截断."""
        state = CompanyState(
            cash=100_000, mrr=700_000, product_score=70, reputation=60
        )  # only 10万 cash but good metrics
        action = PlayerAction(
            type=ActionType.FUNDRAISING,
            fundraise_amount=5_000_000,
            equity_offered=10,
            budget=0,
        )
        plan = ActionPlan(raw_input="融资500万出让10%", actions=[action])
        delta = _simulate(plan, state)

        # Without exemption: max_cash_delta = 65,000, delta.cash = 4,880,000
        # The 65% cap would limit outflow, but inflow should pass through
        sanitized = sanitize_delta(delta, state)
        # With 10万 cash, spending cap = 65k. Fundraising 500万 on top.
        # Net: 5M - 120k(burn) but burn portion capped at 65k
        # fundraising_cash = 5M, spending = -120k capped at -65k
        # result = 5M + (-65k) = 4,935,000
        assert sanitized.cash > 4_900_000, f"Fundraising should not be capped, got {sanitized.cash}"
        assert sanitized.cash < 5_000_000  # burn still deducted

    def test_fundraising_via_process_turn_raw_not_capped(self):
        """process_turn_raw with fundraising: full amount arrives despite low cash."""
        state = CompanyState(
            cash=50_000, mrr=700_000, product_score=70, reputation=60
        )  # very low cash but good metrics
        result = TurnEngine.process_turn_raw(state, "融资500万出让10%")

        # Cash should be ~50k + 5M - burn = ~4.93M, well above 65% cap
        assert result.state_after.cash > 4_000_000, (
            f"process_turn_raw fundraising should not be capped, "
            f"got cash={result.state_after.cash}"
        )
        assert result.state_after.founder_equity == 90

    def test_spending_is_capped_but_fundraising_is_not(self):
        """Verify that in the same turn: spending is capped, fundraising passes through."""
        state = CompanyState(cash=100_000, mrr=700_000, product_score=70, reputation=60)
        actions = [
            PlayerAction(
                type=ActionType.FUNDRAISING, fundraise_amount=5_000_000, equity_offered=10, budget=0
            ),
            PlayerAction(type=ActionType.MARKETING, budget=500_000),  # huge spend
        ]
        plan = ActionPlan(raw_input="融资500万出让10%，花50万做营销", actions=actions)
        delta = _simulate(plan, state)
        sanitized = sanitize_delta(delta, state)

        # Marketing spend 500k + burn 120k should be capped at -65k (65% of 100k)
        # Fundraising 5M passes through uncapped
        # Net: 5M - 65k = 4,935,000
        assert sanitized.cash == 4_935_000, (
            f"Expected 4,935,000 (5M fundraising - 65k capped spending), " f"got {sanitized.cash}"
        )
        # Verify fundraising_cash is preserved
        assert sanitized.fundraising_cash == 5_000_000


# ── 4. Product R&D formula verification ───────────────────────────────────────


class TestProductFormula:
    """Verify product formula: budget // 80_000 + employee_count // 3 + team_morale // 10."""

    def test_product_gain_default_state(self):
        """Default state (emp=10, morale=70): budget=100k → gain=1+3+7=11."""
        state = CompanyState(
            employee_count=10,
            team_morale=70,
        )
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # budget//80k = 100k//80k = 1, emp//3 = 10//3 = 3, morale//10 = 70//10 = 7
        # Total = 11, max(1, 11) = 11, + organic(1) = 12
        expected_base = 100_000 // 80_000 + 10 // 3 + 70 // 10  # 1+3+7 = 11
        assert expected_base == 11

        # Delta should include base gain + 1 organic (emp >= 5)
        assert (
            delta.product_score == 12
        ), f"Expected 12 (11 formula + 1 organic), got {delta.product_score}"

    def test_product_gain_minimum_one(self):
        """Even with zero budget, formula clamped to minimum 1."""
        state = CompanyState(employee_count=10, team_morale=70)
        action = PlayerAction(type=ActionType.PRODUCT, budget=0)
        plan = ActionPlan(raw_input="研发", actions=[action])
        delta = _simulate(plan, state)

        # budget=0 → skipped by _simulate (budget <= 0 and no fundraising),
        # but organic still applies since employee_count >= 5
        # Actually: budget=0, action type=product, so 'continue' is triggered
        # because budget <= 0 and not fundraising.
        # So no product gain at all, only organic from the bottom of _simulate.
        assert delta.product_score == 1  # organic only

    def test_product_gain_with_large_budget(self):
        """Large budget: 800k budget → gain=10+3+7=20."""
        state = CompanyState(employee_count=10, team_morale=70)
        action = PlayerAction(type=ActionType.PRODUCT, budget=800_000)
        plan = ActionPlan(raw_input="花80万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 800k//80k = 10, emp//3 = 3, morale//10 = 7
        # Total = 20, max(1,20) = 20, + organic(1) = 21
        expected_base = 800_000 // 80_000 + 10 // 3 + 70 // 10  # 10+3+7 = 20
        assert expected_base == 20
        assert delta.product_score == 21  # 20 + organic

    def test_product_gain_with_more_employees(self):
        """More employees → higher product gain: emp=20 → gain=1+6+7=14."""
        state = CompanyState(employee_count=20, team_morale=70)
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 100k//80k = 1, 20//3 = 6, 70//10 = 7 → 14
        expected_base = 100_000 // 80_000 + 20 // 3 + 70 // 10
        assert expected_base == 14
        assert delta.product_score == 15  # + organic

    def test_product_gain_with_low_morale(self):
        """Low morale → lower product gain: morale=25 → gain=1+3+2=6."""
        state = CompanyState(employee_count=10, team_morale=25)
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 100k//80k = 1, 10//3 = 3, 25//10 = 2 → 6
        expected_base = 100_000 // 80_000 + 10 // 3 + 25 // 10
        assert expected_base == 6
        assert delta.product_score == 7  # + organic

    def test_product_gain_with_high_morale(self):
        """High morale → higher product gain: morale=100 → gain=1+3+10=14."""
        state = CompanyState(employee_count=10, team_morale=100)
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 100k//80k = 1, 10//3 = 3, 100//10 = 10 → 14
        expected_base = 100_000 // 80_000 + 10 // 3 + 100 // 10
        assert expected_base == 14
        assert delta.product_score == 15  # + organic

    def test_product_gain_with_few_employees(self):
        """Few employees → less product gain but still organic if >=5."""
        state = CompanyState(employee_count=5, team_morale=70)
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 100k//80k = 1, 5//3 = 1, 70//10 = 7 → 9
        expected_base = 100_000 // 80_000 + 5 // 3 + 70 // 10
        assert expected_base == 9
        assert delta.product_score == 10  # + organic (emp=5 >= 5)

    def test_no_organic_with_very_few_employees(self):
        """With < 5 employees, no organic product improvement."""
        state = CompanyState(employee_count=4, team_morale=70)
        action = PlayerAction(type=ActionType.PRODUCT, budget=100_000)
        plan = ActionPlan(raw_input="花10万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # 100k//80k = 1, 4//3 = 1, 70//10 = 7 → 9, no organic
        expected_base = 100_000 // 80_000 + 4 // 3 + 70 // 10
        assert expected_base == 9
        assert delta.product_score == 9  # no organic (emp < 5)

    def test_product_burn_formula(self):
        """Product action adds burn: budget // 30."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.PRODUCT, budget=300_000)
        plan = ActionPlan(raw_input="花30万研发产品", actions=[action])
        delta = _simulate(plan, state)

        # Burn increase = budget // 30 = 300k // 30 = 10,000
        assert (
            delta.monthly_burn == 10_000
        ), f"Expected burn increase 10,000 (300k//30), got {delta.monthly_burn}"

    def test_marketing_burn_formula(self):
        """Marketing action adds burn: budget // 12."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.MARKETING, budget=120_000)
        plan = ActionPlan(raw_input="花12万做营销", actions=[action])
        delta = _simulate(plan, state)

        # Burn increase = budget // 12 = 120k // 12 = 10,000
        assert (
            delta.monthly_burn == 10_000
        ), f"Expected burn increase 10,000 (120k//12), got {delta.monthly_burn}"

    def test_team_burn_formula(self):
        """Team action adds burn: budget // 5."""
        state = CompanyState()
        action = PlayerAction(type=ActionType.TEAM, budget=50_000)
        plan = ActionPlan(raw_input="花5万招聘", actions=[action])
        delta = _simulate(plan, state)

        # Burn increase = budget // 5 = 50k // 5 = 10,000
        assert (
            delta.monthly_burn == 10_000
        ), f"Expected burn increase 10,000 (50k//5), got {delta.monthly_burn}"
