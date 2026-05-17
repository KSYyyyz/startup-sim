"""Alpha 1.9: Test competitor visibility in monthly reports.

Covers: non-empty competitor moves, market share estimation, impact formatting,
and the enhanced competitor landscape section of generate_monthly_report.
"""

from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.core.models import (
    ActionPlan,
    CompanyState,
    StateDelta,
    TurnResult,
)
from src.core.turn_engine import generate_monthly_report


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


def make_result(**overrides) -> TurnResult:
    defaults = {
        "month": 1,
        "state_before": make_state(),
        "state_after": make_state(),
        "action_plan": make_plan([]),
        "delta": StateDelta(
            cash=0,
            monthly_burn=0,
            mrr=0,
            users=0,
            product_score=0,
            team_morale=0,
            founder_equity=0,
            board_control=0,
            market_share=0,
            reputation=0,
            employee_count=0,
            price=0,
            valuation=0,
            reasons=[],
            fundraising_cash=0,
        ),
        "board_feedback": {},
        "customer_response": {},
        "competitor_moves": [],
        "event_triggered": None,
        "is_game_over": False,
        "conflict_summary": None,
        "insight": None,
        "stateguard_intercepted": False,
    }
    defaults.update(overrides)
    return TurnResult(**defaults)


class TestCompetitorVisibility:
    def test_empty_competitor_moves_shows_no_action(self):
        state = make_state(month=3)
        result = make_result(
            month=3,
            state_before=state,
            state_after=state,
            competitor_moves=[],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        assert "无显著动作" in report

    def test_non_empty_competitor_moves_in_report(self):
        state = make_state(month=4, users=500, market_share=10)
        result = make_result(
            month=4,
            state_before=state,
            state_after=state,
            competitor_moves=[
                {
                    "name": "快答科技",
                    "action": "price_cut",
                    "narrative": "快答科技降价20%抢客户",
                    "delta": {"market_share": -2, "users": -50},
                },
            ],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        assert "快答科技" in report
        assert "price_cut" in report or "降价" in report

    def test_competitor_impact_formatting(self):
        state = make_state(month=5, users=300, market_share=8)
        result = make_result(
            month=5,
            state_before=state,
            state_after=state,
            competitor_moves=[
                {
                    "name": "灵犀客服云",
                    "action": "enterprise_upgrade",
                    "narrative": "灵犀升级企业版功能",
                    "delta": {"market_share": -1, "users": -30},
                },
            ],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        assert "灵犀客服云" in report
        assert "对你影响" in report

    def test_multiple_competitor_moves(self):
        state = make_state(month=6, users=800, market_share=15)
        result = make_result(
            month=6,
            state_before=state,
            state_after=state,
            competitor_moves=[
                {
                    "name": "快答科技",
                    "action": "price_cut",
                    "narrative": "快答降价",
                    "delta": {"market_share": -2},
                },
                {
                    "name": "灵犀客服云",
                    "action": "differentiate",
                    "narrative": "灵犀差异化",
                    "delta": {},
                },
            ],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        assert "快答科技" in report
        assert "灵犀客服云" in report

    def test_market_share_estimation_in_report(self):
        state = make_state(month=4, users=500, market_share=10)
        result = make_result(
            month=4,
            state_before=state,
            state_after=state,
            competitor_moves=[],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        assert "市场格局" in report
        assert "份额" in report

    def test_competitor_section_with_real_competitors(self):
        kuai = KuaiDaTech()
        lingxi = LingxiCSCloud()
        state = make_state(month=5, users=600, market_share=12)
        result = make_result(
            month=5,
            state_before=state,
            state_after=state,
            competitor_moves=[
                {
                    "name": "快答科技",
                    "action": "steady_growth",
                    "narrative": "快答稳定增长",
                    "delta": {},
                },
            ],
        )
        report = generate_monthly_report(result, state, state, competitors=[kuai, lingxi])
        assert "竞品状态" in report
        assert "快答科技" in report
        assert "灵犀客服云" in report
        # Competitor summaries should show product score and market share info
        assert "产品分" in report
        assert "市场份额" in report

    def test_competitor_impact_zero_delta_not_shown(self):
        state = make_state(month=3, users=200)
        result = make_result(
            month=3,
            state_before=state,
            state_after=state,
            competitor_moves=[
                {
                    "name": "快答科技",
                    "action": "steady_growth",
                    "narrative": "稳定增长中",
                    "delta": {},
                },
            ],
        )
        report = generate_monthly_report(result, state, state, competitors=None)
        # With empty delta, impact line should not appear
        assert "对你影响" not in report
