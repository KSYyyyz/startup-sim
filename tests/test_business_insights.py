"""Alpha 1.9: Test InsightEngine — business insights per turn."""

from src.core.insight_engine import InsightEngine
from src.core.models import (
    ActionPlan,
    ActionType,
    BusinessInsight,
    CompanyState,
    PlayerAction,
    StateDelta,
)


def make_state(**overrides) -> CompanyState:
    defaults = {
        "month": 1,
        "cash": 1_000_000,
        "monthly_burn": 120_000,
        "mrr": 0,
        "users": 0,
        "product_score": 20,
        "team_morale": 70,
        "founder_equity": 100,
        "board_control": 100,
        "market_share": 0,
        "reputation": 50,
        "employee_count": 10,
        "price": 5000,
        "valuation": 5_000_000,
    }
    defaults.update(overrides)
    return CompanyState(**defaults)


def make_plan(actions: list) -> ActionPlan:
    return ActionPlan(raw_input="test", actions=actions)


def make_delta(**overrides) -> StateDelta:
    defaults = {
        "cash": 0,
        "monthly_burn": 0,
        "mrr": 0,
        "users": 0,
        "product_score": 0,
        "team_morale": 0,
        "founder_equity": 0,
        "board_control": 0,
        "market_share": 0,
        "reputation": 0,
        "employee_count": 0,
        "price": 0,
        "valuation": 0,
        "reasons": [],
        "fundraising_cash": 0,
    }
    defaults.update(overrides)
    return StateDelta(**defaults)


class TestBusinessInsights:
    def test_fundraising_accepted(self):
        s = make_state(product_score=50, mrr=100_000, month=4)
        plan = make_plan(
            [
                PlayerAction(
                    type=ActionType.FUNDRAISING, fundraise_amount=3_000_000, equity_offered=10
                ),
            ]
        )
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 4, fundraising_accepted=True)
        assert insight.category == "fundraising_win"
        assert "融资成功" in insight.title

    def test_fundraising_rejected(self):
        s = make_state(product_score=30, mrr=50000, month=5)
        plan = make_plan(
            [
                PlayerAction(
                    type=ActionType.FUNDRAISING, fundraise_amount=5_000_000, equity_offered=15
                ),
            ]
        )
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 5, fundraising_rejected=True)
        assert insight.category == "fundraising_fail"
        assert "融资被拒" in insight.title
        assert len(insight.action_advice) > 0

    def test_high_marketing_low_product(self):
        s = make_state(product_score=25, month=3)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.MARKETING, budget=200_000),
            ]
        )
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 3)
        assert insight.category == "marketing_efficiency"
        assert "产品" in insight.description or "营销" in insight.description

    def test_high_rd_low_cash(self):
        s = make_state(product_score=40, cash=500_000, monthly_burn=120_000, month=4)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.PRODUCT, budget=150_000),
            ]
        )
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 4)
        assert insight.category == "cash_warning"
        assert "研发" in insight.description or "现金" in insight.description

    def test_cash_dangerously_low(self):
        s = make_state(cash=200_000, monthly_burn=120_000, month=5)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.PRODUCT, budget=30000),
            ]
        )
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 5)
        assert insight.category == "cash_warning"
        assert "现金" in insight.description or "跑道" in insight.description

    def test_mrr_growth_signal(self):
        s = make_state(mrr=100_000, month=6, product_score=55)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.MARKETING, budget=50000),
            ]
        )
        delta = make_delta(mrr=50000)
        insight = InsightEngine.generate(s, plan, delta, 6)
        assert insight.category == "growth_signal"
        assert "MRR" in insight.title or "增长" in insight.title

    def test_reputation_damage(self):
        s = make_state(reputation=60, month=7)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.PRODUCT, budget=50000),
            ]
        )
        delta = make_delta(reputation=-5)
        insight = InsightEngine.generate(s, plan, delta, 7)
        assert insight.category == "risk_alert"
        assert "声誉" in insight.title or "品牌" in insight.description

    def test_team_morale_drop(self):
        s = make_state(team_morale=60, month=8)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.TEAM, budget=20000),
            ]
        )
        delta = make_delta(team_morale=-8)
        insight = InsightEngine.generate(s, plan, delta, 8)
        assert insight.category == "team_health"
        assert "士气" in insight.title or "团队" in insight.description

    def test_default_observation_with_budget(self):
        s = make_state(product_score=50, mrr=100_000, month=3)
        plan = make_plan(
            [
                PlayerAction(type=ActionType.PRODUCT, budget=50000),
            ]
        )
        delta = make_delta(product_score=5, mrr=10000)
        insight = InsightEngine.generate(s, plan, delta, 3)
        assert isinstance(insight.title, str) and len(insight.title) > 0
        assert isinstance(insight.description, str) and len(insight.description) > 0

    def test_no_action_taken(self):
        s = make_state(month=4)
        plan = make_plan([])
        delta = make_delta()
        insight = InsightEngine.generate(s, plan, delta, 4)
        assert insight.category == "risk_alert"
        assert "无动作" in insight.title or "没有" in insight.description


class TestSelectTopInsights:
    def test_selects_top_3_by_priority(self):
        insights = [
            BusinessInsight(month=1, category="growth_signal", title="t1", description="d1"),
            BusinessInsight(month=2, category="cash_warning", title="t2", description="d2"),
            BusinessInsight(month=3, category="fundraising_win", title="t3", description="d3"),
            BusinessInsight(month=4, category="team_health", title="t4", description="d4"),
            BusinessInsight(month=5, category="risk_alert", title="t5", description="d5"),
        ]
        top = InsightEngine.select_top_insights(insights, top_n=3)
        assert len(top) == 3
        # fundraising_win has highest priority (10)
        assert top[0].category == "fundraising_win"

    def test_selects_empty_list(self):
        top = InsightEngine.select_top_insights([], top_n=3)
        assert top == []

    def test_selects_fewer_than_n(self):
        insights = [
            BusinessInsight(month=1, category="growth_signal", title="t1", description="d1"),
        ]
        top = InsightEngine.select_top_insights(insights, top_n=3)
        assert len(top) == 1
