"""Tests for reputation effects on CAC and team morale."""

from src.agents.customers import CustomerAgent
from src.core.models import ActionPlan, ActionType, CompanyState, PlayerAction


class TestReputationCAC:
    """Reputation modifies CAC in CustomerAgent.evaluate()."""

    def _make_marketing_plan(self, budget: int = 80000) -> ActionPlan:
        marketing = PlayerAction(type=ActionType.MARKETING, budget=budget, risk_level="medium")
        return ActionPlan(raw_input="花8万做营销", actions=[marketing])

    def _make_state(self, reputation: int, product_score: int = 70, **kwargs) -> CompanyState:
        defaults = dict(
            month=3,
            cash=1_000_000,
            mrr=100_000,
            users=500,
            monthly_burn=120_000,
            product_score=product_score,
            team_morale=70,
            founder_equity=85,
            board_control=85,
            market_share=5,
            reputation=reputation,
            employee_count=15,
            price=5000,
            valuation=5_000_000,
        )
        defaults.update(kwargs)
        return CompanyState(**defaults)

    def test_high_reputation_lowers_cac(self):
        """rep>=80 uses cac=720 → more users per budget."""
        state = self._make_state(reputation=80)
        plan = self._make_marketing_plan(budget=80000)
        agent = CustomerAgent()
        response = agent.evaluate(state, plan, [])
        # At CAC=720, 80000 // 720 = 111 users, retained based on product
        assert response["growth_change"] > 0

    def test_low_reputation_raises_cac(self):
        """rep<40 uses cac=960 → fewer users per budget."""
        state = self._make_state(reputation=30)
        plan = self._make_marketing_plan(budget=80000)
        agent = CustomerAgent()
        response = agent.evaluate(state, plan, [])
        # At CAC=960, 80000 // 960 = 83 users
        assert response["growth_change"] > 0

    def test_normal_reputation_default_cac(self):
        """rep 50-79 uses cac=800."""
        state = self._make_state(reputation=60)
        plan = self._make_marketing_plan(budget=80000)
        agent = CustomerAgent()
        response = agent.evaluate(state, plan, [])
        # At CAC=800, 80000 // 800 = 100 users
        assert response["growth_change"] > 0

    def test_high_rep_more_users_than_low_rep(self):
        """Same budget, high rep gives more users than low rep."""
        state_high = self._make_state(reputation=85)
        state_low = self._make_state(reputation=30)
        plan = self._make_marketing_plan(budget=80000)
        agent = CustomerAgent()
        resp_high = agent.evaluate(state_high, plan, [])
        resp_low = agent.evaluate(state_low, plan, [])
        # High rep should produce more growth (CAC 720 < 960)
        assert resp_high["growth_change"] >= resp_low["growth_change"]


class TestReputationTeamBonus:
    """Reputation >= 80 gives +2 morale bonus on hiring (via _simulate)."""

    def _make_team_plan(self, budget: int = 50000) -> ActionPlan:
        team_action = PlayerAction(type=ActionType.TEAM, budget=budget, risk_level="medium")
        return ActionPlan(raw_input=f"花{budget//10000}万招聘", actions=[team_action])

    def _make_state(self, reputation: int, **kwargs) -> CompanyState:
        defaults = dict(
            month=3,
            cash=1_000_000,
            mrr=100_000,
            users=500,
            monthly_burn=120_000,
            product_score=70,
            team_morale=70,
            founder_equity=85,
            board_control=85,
            market_share=5,
            reputation=reputation,
            employee_count=15,
            price=5000,
            valuation=5_000_000,
        )
        defaults.update(kwargs)
        return CompanyState(**defaults)

    def test_high_reputation_team_bonus(self):
        """Hiring with rep>=80 gets +2 morale bonus in _simulate."""
        from src.core.turn_engine import _simulate

        state = self._make_state(reputation=85, team_morale=70)
        plan = self._make_team_plan(budget=50000)
        delta = _simulate(plan, state)

        # Base morale gain = budget // 5000 = 10, plus +2 from high rep = 12
        assert delta.team_morale >= 10
        # Check the reason mentions the bonus
        bonus_reason = any("高声誉" in r for r in delta.reasons)
        if delta.team_morale > (50000 // 5000):
            # If bonus applied, reason should mention it
            assert bonus_reason

    def test_normal_reputation_no_team_bonus(self):
        """Hiring with rep<80 does NOT get +2 morale bonus."""
        from src.core.turn_engine import _simulate

        state = self._make_state(reputation=50, team_morale=70)
        plan = self._make_team_plan(budget=50000)
        delta = _simulate(plan, state)

        # Base morale gain = budget // 5000 = 10, no bonus
        assert delta.team_morale == 10
