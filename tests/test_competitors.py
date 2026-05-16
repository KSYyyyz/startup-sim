"""Tests for competitor agents and customer agent (Phase 1C)."""

import pytest
from src.core.models import ActionPlan, CompanyState, PlayerAction, ActionType
from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.agents.customers import CustomerAgent


def make_plan(*actions: PlayerAction) -> ActionPlan:
    """Helper to create an ActionPlan from PlayerActions."""
    return ActionPlan(raw_input="test", actions=list(actions))


# ── 快答科技 (price_war) tests ────────────────────────────────────────────────

class TestKuaiDaTech:
    """快答科技 — price_war 竞品测试."""

    def test_price_war_responds_to_better_product(self):
        """When player product_score is high, 快答 undercuts on price."""
        kuai = KuaiDaTech()
        # state with high product score in month 1
        state = CompanyState(product_score=60, month=1)
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        result = kuai.respond(state, plan)

        assert result["name"] == "快答科技"
        assert result["action"] == "price_cut"
        assert "降价" in result["narrative"] or "价格" in result["narrative"]
        assert result["delta"]["market_share"] == -2

    def test_price_war_responds_to_marketing(self):
        """When player does marketing, 快答 follows with price cut."""
        kuai = KuaiDaTech()
        # product_score <= 快答's product_score, but has marketing action
        state = CompanyState(product_score=20, month=1)
        plan = make_plan(PlayerAction(type=ActionType.MARKETING, budget=50000))
        result = kuai.respond(state, plan)

        assert result["name"] == "快答科技"
        assert result["action"] == "follow_price_cut"
        assert "降价" in result["narrative"] or "投放" in result["narrative"]
        assert result["delta"]["market_share"] == -1

    def test_price_war_default_behavior(self):
        """Default: 快答 grows steadily when no trigger."""
        kuai = KuaiDaTech()
        state = CompanyState(product_score=20, month=1)
        plan = make_plan(PlayerAction(type=ActionType.TEAM, budget=10000))
        result = kuai.respond(state, plan)

        assert result["name"] == "快答科技"
        assert result["action"] == "steady_growth"
        assert result["delta"].get("market_share", 0) == 0


class TestLingxiCSCloud:
    """灵犀客服云 — premium_enterprise 竞品测试."""

    def test_premium_responds_to_high_product_score(self):
        """When player product_score > 70, 灵犀 upgrades enterprise features."""
        lingxi = LingxiCSCloud()
        state = CompanyState(product_score=85, month=3)
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        result = lingxi.respond(state, plan)

        assert result["name"] == "灵犀客服云"
        assert result["action"] == "enterprise_upgrade"
        assert "企业" in result["narrative"] or "高端" in result["narrative"]
        # Should have negative delta for the player
        assert result["delta"]["users"] == -30
        assert result["delta"]["mrr"] == 30000

    def test_premium_ignores_price_cut(self):
        """灵犀 does not follow price cuts; emphasizes differentiation."""
        lingxi = LingxiCSCloud()
        state = CompanyState(product_score=60, month=2)
        # marketing action → price_related trigger
        plan = make_plan(PlayerAction(type=ActionType.MARKETING, budget=50000))
        result = lingxi.respond(state, plan)

        assert result["name"] == "灵犀客服云"
        assert result["action"] == "differentiate"
        assert "价格战" in result["narrative"] or "差异化" in result["narrative"]
        # Should not steal market share
        assert "market_share" not in result.get("delta", {})

    def test_premium_default_behavior(self):
        """Default: 灵犀 steadily grows in premium market."""
        lingxi = LingxiCSCloud()
        state = CompanyState(product_score=40, month=2)
        plan = make_plan(PlayerAction(type=ActionType.TEAM, budget=10000))
        result = lingxi.respond(state, plan)

        assert result["name"] == "灵犀客服云"
        assert result["action"] == "steady_premium"
        assert result["delta"] == {}


class TestBothCompetitors:
    """Tests validating both competitors together."""

    def test_both_return_valid_move_format(self):
        """Both competitors return dicts with required keys."""
        state = CompanyState(
            product_score=50, month=3,
            cash=1_000_000, users=200, mrr=50_000,
        )
        plan = make_plan(
            PlayerAction(type=ActionType.PRODUCT, budget=100_000),
            PlayerAction(type=ActionType.MARKETING, budget=50_000),
        )

        for comp in [KuaiDaTech(), LingxiCSCloud()]:
            result = comp.respond(state, plan)
            assert isinstance(result, dict), f"{comp.name} returned {type(result)}"
            assert "name" in result, f"{comp.name} missing 'name'"
            assert "action" in result, f"{comp.name} missing 'action'"
            assert "narrative" in result, f"{comp.name} missing 'narrative'"
            assert "delta" in result, f"{comp.name} missing 'delta'"
            assert isinstance(result["delta"], dict)
            assert isinstance(result["narrative"], str)
            assert len(result["narrative"]) > 0

    def test_competitors_have_distinct_names(self):
        """Competitors have distinct names."""
        comps = [KuaiDaTech(), LingxiCSCloud()]
        names = [c.name for c in comps]
        assert len(names) == len(set(names)), f"Duplicate names: {names}"

    def test_competitors_have_different_strategies(self):
        """Competitors have different strategies."""
        kuai = KuaiDaTech()
        lingxi = LingxiCSCloud()
        assert kuai.strategy != lingxi.strategy


# ── CustomerAgent tests ────────────────────────────────────────────────────────

class TestCustomerAgent:
    """客户群体Agent 测试."""

    def test_growth_with_high_product_score(self):
        """Product score > 70 → accelerated growth."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=85, month=3,
            cash=1_000_000, users=200, mrr=50_000,
            team_morale=70,
        )
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        assert result["growth_change"] > 0, f"Expected positive growth, got {result['growth_change']}"
        assert "口碑" in result["narrative"] or "增长" in result["narrative"]
        assert "growth_change" in result
        assert "revenue_change" in result

    def test_churn_with_low_product_score(self):
        """Product score < 30 → customer churn."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=15, month=2,
            cash=500_000, users=200, mrr=30_000,
            team_morale=60,
        )
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=10000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        assert result["growth_change"] < 0, f"Expected churn, got {result['growth_change']}"
        assert "流失" in result["narrative"]

    def test_churn_on_competitor_undercut(self):
        """Competitor price cut → customer churn (net negative when product is weak)."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=15, month=3,
            cash=1_000_000, users=500, mrr=100_000,
            team_morale=70,
        )
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        competitor_moves = [
            {
                "name": "快答科技",
                "action": "price_cut",
                "narrative": "快答降价抢市场",
                "delta": {"market_share": -2},
            },
        ]

        result = agent.evaluate(state, plan, competitor_moves)

        # Low product → baseline churn, plus competitor undercut → net negative
        assert result["growth_change"] < 0, f"Expected churn from competitor price cut, got {result['growth_change']}"
        assert "快答" in result["narrative"] or "竞品" in result["narrative"]

    def test_marketing_drives_growth(self):
        """Marketing action → user growth but margin pressure."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=50, month=2,
            cash=1_000_000, users=200, mrr=50_000,
            team_morale=70,
        )
        plan = make_plan(PlayerAction(type=ActionType.MARKETING, budget=50000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        # Marketing should bring users
        assert result["growth_change"] > 0 or "投放" in result["narrative"]
        # Revenue change exists (may be positive from baseline MRR or negative from discount)

    def test_high_morale_boosts_retention(self):
        """Team morale >= 80 → better customer retention."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=50, month=3,
            cash=1_000_000, users=200, mrr=50_000,
            team_morale=85,
        )
        plan = make_plan(PlayerAction(type=ActionType.TEAM, budget=20000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        assert "士气" in result["narrative"]
        # High morale should contribute positively
        assert result["growth_change"] > 0

    def test_low_morale_causes_churn(self):
        """Team morale < 40 → delivery issues → customer churn."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=50, month=3,
            cash=1_000_000, users=200, mrr=50_000,
            team_morale=25,
        )
        plan = make_plan(PlayerAction(type=ActionType.TEAM, budget=20000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        assert "士气" in result.get("narrative", "")
        # Low morale should cause churn or negative effects
        narrative = result.get("narrative", "")
        assert "流失" in narrative or "离开" in narrative or "下降" in narrative

    def test_enterprise_competitor_causes_churn(self):
        """Competitor enterprise upgrade → premium customers switch."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=25, month=4,  # low product → baseline already churn
            cash=1_000_000, users=300, mrr=80_000,
            team_morale=70,
        )
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        competitor_moves = [
            {
                "name": "灵犀客服云",
                "action": "enterprise_upgrade",
                "narrative": "灵犀升级企业版",
                "delta": {"users": -30, "mrr": 30000, "reputation": -1},
            },
        ]

        result = agent.evaluate(state, plan, competitor_moves)

        # Low product → baseline churn, competitor enterprise upgrade adds more churn
        assert result["growth_change"] < 0, f"Expected churn, got {result['growth_change']}"
        assert "灵犀" in result["narrative"] or "高端" in result["narrative"]

    def test_returns_valid_format(self):
        """Customer response always has required keys."""
        agent = CustomerAgent()
        state = CompanyState(
            product_score=50, month=2,
            cash=1_000_000, users=200, mrr=50_000,
            team_morale=70,
        )
        plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50000))
        competitor_moves = []

        result = agent.evaluate(state, plan, competitor_moves)

        assert isinstance(result, dict)
        assert "growth_change" in result
        assert "revenue_change" in result
        assert "narrative" in result
        assert isinstance(result["growth_change"], int)
        assert isinstance(result["revenue_change"], int)
        assert isinstance(result["narrative"], str)
        assert len(result["narrative"]) > 0
