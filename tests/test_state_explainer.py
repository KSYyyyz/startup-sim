"""Tests for Alpha 1.6 StateExplainer."""

from src.core.models import CompanyState
from src.core.state_explainer import StateExplainer


class TestExplainCash:
    """Cash and runway explanations."""

    def test_cash_zero_is_critical(self):
        """Zero cash should indicate company cannot operate."""
        state = CompanyState(cash=0, monthly_burn=100_000)
        result = StateExplainer.explain_cash(state)
        assert "耗尽" in result or "无法继续" in result

    def test_low_runway_is_danger(self):
        """Runway < 2 months should be flagged as extremely dangerous."""
        state = CompanyState(cash=150_000, monthly_burn=100_000)
        result = StateExplainer.explain_cash(state)
        assert "极度" in result or "危险" in result or "1." in result

    def test_tight_runway_warns(self):
        """Runway 2-4 months should warn of tight cash."""
        state = CompanyState(cash=300_000, monthly_burn=100_000)
        result = StateExplainer.explain_cash(state)
        assert "紧张" in result or "偏紧" in result or "建议" in result

    def test_healthy_runway_positive(self):
        """Healthy runway should be reassuring."""
        state = CompanyState(cash=1_000_000, monthly_burn=100_000)
        result = StateExplainer.explain_cash(state)
        assert "健康" in result or "充裕" in result or "缓冲" in result


class TestExplainProduct:
    """Product score maturity descriptions."""

    def test_very_low_product_is_prototype(self):
        """Product score < 15 is prototype stage."""
        state = CompanyState(product_score=10)
        result = StateExplainer.explain_product(state)
        assert "原型" in result

    def test_low_product_is_mvp(self):
        """Product score 15-30 is MVP stage."""
        state = CompanyState(product_score=25)
        result = StateExplainer.explain_product(state)
        assert "MVP" in result or "早期" in result

    def test_mid_product_is_usable(self):
        """Product score 45-60 is usable product."""
        state = CompanyState(product_score=55)
        result = StateExplainer.explain_product(state)
        assert "可用" in result or "完善" in result

    def test_high_product_is_mature(self):
        """Product score 75+ is mature/excellent."""
        state = CompanyState(product_score=80)
        result = StateExplainer.explain_product(state)
        assert "优秀" in result or "成熟" in result or "推荐" in result

    def test_top_product_is_benchmark(self):
        """Product score 90+ is top-tier."""
        state = CompanyState(product_score=95)
        result = StateExplainer.explain_product(state)
        assert "顶尖" in result or "标杆" in result or "标准" in result


class TestExplainUsersMRR:
    """User and MRR relationship explanations."""

    def test_zero_users_mrr_is_pre_launch(self):
        """Zero users and MRR should indicate pre-launch."""
        state = CompanyState(users=0, mrr=0)
        result = StateExplainer.explain_users_mrr(state)
        assert "暂无" in result or "没有" in result

    def test_many_users_low_mrr_is_conversion_issue(self):
        """Many users but low MRR indicates conversion problem."""
        state = CompanyState(users=200, mrr=20_000)
        result = StateExplainer.explain_users_mrr(state)
        assert "转化" in result or "定价" in result or "偏低" in result

    def test_high_product_few_users_is_marketing_issue(self):
        """High product but few users after month 5 means lack of marketing."""
        state = CompanyState(product_score=70, users=10, month=6)
        result = StateExplainer.explain_users_mrr(state)
        assert "获客" in result or "营销" in result or "没人用" in result

    def test_high_mrr_is_revenue_engine(self):
        """MRR > 30万 should indicate revenue engine running."""
        state = CompanyState(users=500, mrr=400_000)
        result = StateExplainer.explain_users_mrr(state)
        assert "门户" in result or "A轮" in result or "引擎" in result


class TestExplainEquity:
    """Equity and control explanations."""

    def test_high_equity_is_absolute_control(self):
        """Equity >= 95% is absolute control."""
        state = CompanyState(founder_equity=98, board_control=98)
        result = StateExplainer.explain_equity(state)
        assert "绝对" in result or "最好" in result

    def test_mid_equity_is_healthy(self):
        """Equity 70-95% is healthy control."""
        state = CompanyState(founder_equity=80, board_control=80)
        result = StateExplainer.explain_equity(state)
        assert "健康" in result or "充分" in result

    def test_low_equity_is_dilution_warning(self):
        """Equity 34-50% should warn about dilution."""
        state = CompanyState(founder_equity=40, board_control=40)
        result = StateExplainer.explain_equity(state)
        assert "否决" in result or "稀释" in result or "削弱" in result

    def test_very_low_equity_is_loss_of_control(self):
        """Equity < 34% means loss of veto power."""
        state = CompanyState(founder_equity=25, board_control=25)
        result = StateExplainer.explain_equity(state)
        assert "失去" in result or "更换" in result or "否决" in result


class TestExplainFull:
    """Full state explanation returns all dimensions."""

    def test_explain_full_returns_all_keys(self):
        """explain_full should return all 5 explanation dimensions."""
        state = CompanyState()
        result = StateExplainer.explain_full(state)
        assert "cash" in result
        assert "product" in result
        assert "users_mrr" in result
        assert "equity" in result
        assert "morale" in result

    def test_explain_full_all_nonempty(self):
        """All explanations should be non-empty strings."""
        state = CompanyState()
        result = StateExplainer.explain_full(state)
        for key, value in result.items():
            assert isinstance(value, str), f"{key} should be str"
            assert len(value) > 0, f"{key} should not be empty"


class TestExplainMorale:
    """Team morale explanations."""

    def test_very_low_morale_is_collapse(self):
        """Morale < 30 is near collapse."""
        state = CompanyState(team_morale=20)
        result = StateExplainer.explain_morale(state)
        assert "崩溃" in result or "流失" in result or "解体" in result

    def test_low_morale_is_concerning(self):
        """Morale 30-50 is concerning."""
        state = CompanyState(team_morale=40)
        result = StateExplainer.explain_morale(state)
        assert "低落" in result or "消极" in result

    def test_high_morale_is_energized(self):
        """Morale > 85 is highly energized."""
        state = CompanyState(team_morale=90)
        result = StateExplainer.explain_morale(state)
        assert "高涨" in result or "爆表" in result or "极强" in result
