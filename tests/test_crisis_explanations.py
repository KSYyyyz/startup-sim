"""Alpha 1.9: Test crisis guidance with copiable recovery inputs."""

from src.core.models import CompanyState, CrisisGuidance
from src.core.state_guard import generate_crisis_guidance


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


class TestCrisisGuidance:
    def test_budget_overrun_with_equity(self):
        s = make_state(cash=500_000, founder_equity=80, monthly_burn=120_000)
        guidance = generate_crisis_guidance("budget_overrun", s, {"available_cash": 500_000})
        assert isinstance(guidance, CrisisGuidance)
        assert guidance.crisis_type == "budget_overrun"
        assert guidance.severity == "high"
        assert len(guidance.recovery_inputs) >= 1
        assert any("万" in inp for inp in guidance.recovery_inputs)

    def test_budget_overrun_low_equity(self):
        s = make_state(cash=300_000, founder_equity=40, monthly_burn=100_000)
        guidance = generate_crisis_guidance("budget_overrun", s, {"available_cash": 300_000})
        assert guidance.crisis_type == "budget_overrun"
        # Low equity should not include fundraising option
        has_fundraising = any("融资" in inp for inp in guidance.recovery_inputs)
        assert not has_fundraising

    def test_fundraising_rejected_basic(self):
        s = make_state(product_score=30, mrr=50000, users=50, month=5)
        guidance = generate_crisis_guidance(
            "fundraising_rejected", s, {"reason": "估值偏高", "investor_response": "数据不支撑估值"}
        )
        assert guidance.crisis_type == "fundraising_rejected"
        assert guidance.severity == "high"
        assert len(guidance.recovery_inputs) >= 1
        assert "估值" in guidance.explanation or "数据" in guidance.explanation

    def test_fundraising_rejected_low_product(self):
        s = make_state(product_score=25, mrr=20000, users=20, month=6)
        guidance = generate_crisis_guidance(
            "fundraising_rejected",
            s,
            {"reason": "产品不够成熟", "investor_response": "需要看到更多用户反馈"},
        )
        assert guidance.crisis_type == "fundraising_rejected"
        # Low product should suggest product focus
        has_product = any("产品" in inp for inp in guidance.recovery_inputs)
        assert has_product

    def test_fundraising_rejected_low_users(self):
        s = make_state(product_score=50, mrr=80000, users=30, month=7)
        guidance = generate_crisis_guidance(
            "fundraising_rejected",
            s,
            {"reason": "用户基数太小", "investor_response": "需要验证PMF"},
        )
        # Low users should suggest marketing
        has_marketing = any("营销" in inp for inp in guidance.recovery_inputs)
        assert has_marketing

    def test_runway_critical_with_equity(self):
        s = make_state(cash=200_000, monthly_burn=120_000, founder_equity=70, month=8)
        guidance = generate_crisis_guidance("runway_critical", s)
        assert guidance.crisis_type == "runway_critical"
        assert guidance.severity == "critical"
        assert len(guidance.recovery_inputs) >= 2
        assert any("融资" in inp for inp in guidance.recovery_inputs)

    def test_runway_critical_low_equity(self):
        s = make_state(cash=150_000, monthly_burn=120_000, founder_equity=40, month=9)
        guidance = generate_crisis_guidance("runway_critical", s)
        assert guidance.crisis_type == "runway_critical"
        # Low equity should suggest acquisition or bridge loan
        has_alternative = any("收购" in inp or "贷款" in inp for inp in guidance.recovery_inputs)
        assert has_alternative

    def test_cash_below_burn(self):
        s = make_state(cash=100_000, monthly_burn=120_000, month=6)
        guidance = generate_crisis_guidance("cash_below_burn", s)
        assert guidance.crisis_type == "cash_below_burn"
        assert guidance.severity == "critical"
        assert len(guidance.recovery_inputs) >= 2

    def test_equity_warning(self):
        s = make_state(founder_equity=35, product_score=60, mrr=100_000, month=8)
        guidance = generate_crisis_guidance("equity_warning", s)
        assert guidance.crisis_type == "equity_warning"
        assert guidance.severity == "medium"
        assert len(guidance.recovery_inputs) >= 1
        assert any("股权" in inp or "暂不融资" in inp for inp in guidance.recovery_inputs)

    def test_equity_warning_with_strong_product(self):
        s = make_state(founder_equity=30, product_score=65, mrr=80000, month=7)
        guidance = generate_crisis_guidance("equity_warning", s)
        assert guidance.crisis_type == "equity_warning"
        # Strong product+MRR should suggest growing MRR first
        has_mrr_advice = any("MRR" in inp or "业绩" in inp for inp in guidance.recovery_inputs)
        assert has_mrr_advice

    def test_unknown_crisis_type(self):
        s = make_state()
        guidance = generate_crisis_guidance("unknown_crisis", s)
        assert isinstance(guidance, CrisisGuidance)
        assert guidance.crisis_type == "unknown_crisis"
        assert len(guidance.recovery_inputs) >= 1

    def test_recovery_inputs_are_copiable(self):
        """All recovery inputs should be actionable single-line commands."""
        s = make_state(
            cash=500_000,
            founder_equity=80,
            monthly_burn=120_000,
            product_score=40,
            mrr=50000,
            users=100,
        )
        for crisis_type in [
            "budget_overrun",
            "fundraising_rejected",
            "runway_critical",
            "cash_below_burn",
            "equity_warning",
        ]:
            extra = {"available_cash": s.cash} if crisis_type == "budget_overrun" else None
            if crisis_type == "fundraising_rejected":
                extra = {"reason": "测试", "investor_response": "测试"}
            guidance = generate_crisis_guidance(crisis_type, s, extra)
            assert len(guidance.recovery_inputs) >= 1, f"{crisis_type} has no recovery inputs"
            for inp in guidance.recovery_inputs:
                assert len(inp) > 0, f"{crisis_type} has empty recovery input"
                assert len(inp) < 200, f"{crisis_type} recovery input too long"
