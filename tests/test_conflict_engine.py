"""Alpha 1.9: Test ConflictEngine — monthly core conflict identification."""

from src.core.conflict_engine import ConflictEngine
from src.core.models import CompanyState


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


class TestConflictEngine:
    def test_healthy_state_low_conflict(self):
        s = make_state(product_score=60, mrr=200_000, users=500, market_share=15, month=8)
        cs = ConflictEngine.identify(s)
        assert cs.severity == "low"

    def test_cash_crisis_high_severity(self):
        s = make_state(cash=200_000, monthly_burn=120_000)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "cash"
        assert cs.severity == "high"

    def test_runway_critical(self):
        s = make_state(cash=100_000, monthly_burn=120_000)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "cash"

    def test_product_good_but_no_mrr(self):
        s = make_state(product_score=65, mrr=10000, month=6)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "pmf"
        assert cs.severity == "high"

    def test_product_weak_late_game(self):
        s = make_state(product_score=25, month=6)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "pmf"

    def test_high_users_low_product(self):
        s = make_state(product_score=40, users=300)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "delivery"
        assert cs.severity == "medium"

    def test_equity_crisis(self):
        s = make_state(founder_equity=30)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "equity"
        assert cs.severity == "high"

    def test_equity_warning(self):
        s = make_state(founder_equity=45)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "equity"
        assert cs.severity == "medium"

    def test_growth_stagnation(self):
        s = make_state(users=30, product_score=40, month=7)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "growth"
        assert cs.severity == "high"

    def test_competition_pressure(self):
        s = make_state(market_share=3, product_score=40, users=100, month=5)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "competition"

    def test_team_morale_crash(self):
        s = make_state(team_morale=25)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "team"
        assert cs.severity == "high"

    def test_early_game_pmf_focus(self):
        s = make_state(product_score=30, month=1)
        cs = ConflictEngine.identify(s)
        assert cs.pressure_type == "pmf"
        assert cs.severity == "low"

    def test_structural_fields(self):
        s = make_state()
        cs = ConflictEngine.identify(s)
        assert isinstance(cs.title, str) and len(cs.title) > 0
        assert isinstance(cs.description, str) and len(cs.description) > 0
        assert cs.pressure_type in (
            "cash",
            "pmf",
            "growth",
            "equity",
            "delivery",
            "competition",
            "team",
        )
        assert cs.severity in ("low", "medium", "high")
        assert isinstance(cs.next_focus, str) and len(cs.next_focus) > 0
