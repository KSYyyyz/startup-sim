"""Alpha 1.9: Test StateGuard intercepts and insights in game review."""

from src.core.models import (
    BusinessInsight,
    CompanyState,
    GameReview,
)
from src.core.review_engine import ReviewEngine


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


def make_snapshot(month: int, state: CompanyState) -> dict:
    return {"month": month, "state_json": state.model_dump_json()}


class TestReviewStateGuardIntercepts:
    def test_intercept_added_as_key_moment(self):
        initial = make_state(month=1)
        final = make_state(month=6, cash=200_000, mrr=100_000, product_score=45, users=200)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 7)]
        action_logs = [{"month": 3, "raw_input": "花200万研发产品", "action_plan_json": "{}"}]

        intercepts = [{"month": 3, "reason": "预算超限：非融资支出200万但可用现金仅100万"}]

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="cash_out",
            session_id=1,
            stateguard_intercepts=intercepts,
        )

        assert isinstance(review, GameReview)
        # Find the intercept key moment
        intercept_moments = [m for m in review.key_moments if "预算计划超限" in m.title]
        assert len(intercept_moments) >= 1
        assert intercept_moments[0].impact_type == "negative"
        assert (
            "超现" in intercept_moments[0].description or "超限" in intercept_moments[0].description
        )

    def test_multiple_intercepts(self):
        initial = make_state(month=1)
        final = make_state(month=8, cash=500_000, mrr=200_000, product_score=55, users=500)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 9)]
        action_logs = []

        intercepts = [
            {"month": 2, "reason": "第一次超限"},
            {"month": 5, "reason": "第二次超限"},
            {"month": 7, "reason": "第三次超限"},
        ]

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
            session_id=2,
            stateguard_intercepts=intercepts,
        )

        intercept_moments = [m for m in review.key_moments if "预算计划超限" in m.title]
        assert len(intercept_moments) == 3

    def test_duplicate_intercept_not_added(self):
        initial = make_state(month=1)
        final = make_state(month=5, cash=300_000, mrr=50000, product_score=40, users=100)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 6)]
        action_logs = []

        # Two intercepts for the same month should only produce one key moment
        intercepts = [
            {"month": 3, "reason": "超限A"},
            {"month": 3, "reason": "超限B"},
        ]

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="neutral",
            session_id=3,
            stateguard_intercepts=intercepts,
        )

        intercept_moments = [m for m in review.key_moments if "预算计划超限" in m.title]
        # Duplicate (month=3, "预算计划超限") should only appear once
        assert len(intercept_moments) == 1

    def test_no_intercepts_no_extra_moments(self):
        initial = make_state(month=1)
        final = make_state(month=4, cash=800_000, product_score=50, users=150, mrr=80000)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 5)]
        action_logs = []

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="neutral",
            session_id=4,
            stateguard_intercepts=[],
        )

        intercept_moments = [m for m in review.key_moments if "预算计划超限" in m.title]
        assert len(intercept_moments) == 0


class TestReviewInsightsInAdvice:
    def test_top_insights_in_advice(self):
        initial = make_state(month=1)
        final = make_state(month=6, cash=800_000, mrr=150_000, product_score=60, users=300)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 7)]
        action_logs = []

        top_insights = [
            BusinessInsight(
                month=3, category="cash_warning", title="现金流危急", description="跑道仅2个月"
            ),
            BusinessInsight(
                month=4,
                category="marketing_efficiency",
                title="营销效率警告",
                description="产品分低时营销ROI低",
            ),
            BusinessInsight(
                month=5, category="growth_signal", title="MRR增长", description="MRR增长3万"
            ),
        ]

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
            session_id=5,
            top_insights=top_insights,
        )

        # Advice should mention relevant insight categories
        assert (
            "现金流管理" in review.advice_for_next_run or "营销效率" in review.advice_for_next_run
        )

    def test_insights_none_does_not_break(self):
        initial = make_state(month=1)
        final = make_state(month=6, cash=800_000, mrr=150_000, product_score=60, users=300)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 7)]
        action_logs = []

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
            session_id=6,
            top_insights=None,
        )

        assert isinstance(review, GameReview)
        assert len(review.advice_for_next_run) > 0

    def test_combined_intercepts_and_insights(self):
        initial = make_state(month=1)
        final = make_state(month=7, cash=600_000, mrr=200_000, product_score=65, users=400)

        snapshots = [make_snapshot(m, make_state(month=m)) for m in range(1, 8)]
        action_logs = []

        intercepts = [
            {"month": 4, "reason": "预算超限150万"},
        ]
        top_insights = [
            BusinessInsight(
                month=5, category="risk_alert", title="声誉下滑", description="竞品攻击导致声誉下降"
            ),
            BusinessInsight(
                month=6,
                category="team_health",
                title="团队士气下降",
                description="过度加班导致士气下降",
            ),
        ]

        review = ReviewEngine.generate_review(
            initial_state=initial,
            snapshots=snapshots,
            action_logs=action_logs,
            event_logs=[],
            final_state=final,
            ending_status="neutral",
            session_id=7,
            stateguard_intercepts=intercepts,
            top_insights=top_insights,
        )

        # Should have intercept key moment
        intercept_moments = [m for m in review.key_moments if "预算计划超限" in m.title]
        assert len(intercept_moments) == 1
        # Should have insight-augmented advice
        assert "风险意识" in review.advice_for_next_run or "团队管理" in review.advice_for_next_run
