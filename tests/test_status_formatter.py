"""Tests for status_formatter: full and short status panels."""

from src.core.models import CompanyState
from src.core.status_formatter import format_status_panel, format_status_panel_short


def _make_state(**kwargs) -> CompanyState:
    defaults = dict(
        month=5,
        cash=1_500_000,
        mrr=300_000,
        users=1500,
        monthly_burn=150_000,
        product_score=65,
        team_morale=72,
        founder_equity=85,
        board_control=85,
        market_share=8,
        reputation=65,
        employee_count=18,
        price=5000,
        valuation=12_000_000,
    )
    defaults.update(kwargs)
    return CompanyState(**defaults)


class TestFullPanel:
    """Tests for format_status_panel()."""

    REQUIRED_FIELDS = [
        "现金",
        "月消耗",
        "MRR",
        "用户",
        "产品评分",
        "团队士气",
        "员工数",
        "声誉",
        "创始人股权",
        "董事会",
        "市场份额",
        "估值",
        "现金流可支撑时间",
    ]

    def test_full_panel_includes_all_metrics(self):
        """Check all 14 required fields in output."""
        state = _make_state()
        panel = format_status_panel(state)
        for field in self.REQUIRED_FIELDS:
            assert field in panel, f"Full panel missing field: {field}"

        # Also verify it shows the month
        assert f"第 {state.month} 个月" in panel

    def test_full_panel_handles_zero_values(self):
        """All zeros should still display."""
        state = _make_state(
            cash=0,
            mrr=0,
            users=0,
            monthly_burn=0,
            product_score=0,
            team_morale=0,
            founder_equity=0,
            board_control=0,
            market_share=0,
            reputation=0,
            employee_count=0,
            price=0,
            valuation=0,
        )
        panel = format_status_panel(state)
        for field in self.REQUIRED_FIELDS:
            assert field in panel, f"Full panel missing field with zeros: {field}"


class TestShortPanel:
    """Tests for format_status_panel_short()."""

    def test_short_panel_includes_equity(self):
        """Check 创始人股权."""
        state = _make_state()
        panel = format_status_panel_short(state)
        assert "创始人" in panel
        assert str(state.founder_equity) in panel

    def test_short_panel_includes_valuation(self):
        """Check 估值."""
        state = _make_state()
        panel = format_status_panel_short(state)
        assert "估值" in panel

    def test_short_panel_includes_reputation(self):
        """Check 声誉."""
        state = _make_state()
        panel = format_status_panel_short(state)
        assert "声誉" in panel

    def test_short_panel_handles_zero_values(self):
        """All zeros display in short form."""
        state = _make_state(
            cash=0,
            mrr=0,
            users=0,
            monthly_burn=0,
            product_score=0,
            team_morale=0,
            founder_equity=0,
            board_control=0,
            market_share=0,
            reputation=0,
            employee_count=0,
            price=0,
            valuation=0,
        )
        panel = format_status_panel_short(state)
        # Should not crash and should include key labels
        assert "现金" in panel
        assert "MRR" in panel
        assert "产品" in panel
        assert "士气" in panel
        assert "员工" in panel
        assert "股权" in panel
        assert "估值" in panel
        assert "声誉" in panel
