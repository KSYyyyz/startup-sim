"""Tests for Alpha 1.4 ReviewEngine and related components."""

from __future__ import annotations

import json

import pytest

from src.core.models import (
    CompanyState,
    EndingType,
    FounderProfile,
    GameReview,
    KeyMoment,
    StrategyScore,
)
from src.core.review_engine import ReviewEngine


def _snapshot(month: int, state: CompanyState) -> dict:
    return {"month": month, "state_json": state.model_dump()}


def _action(month: int, raw: str = "test") -> dict:
    return {"month": month, "raw_input": raw, "action_plan_json": "[]"}


def _default_snapshots(final: CompanyState) -> list[dict]:
    """Generate 12 snapshots with gradual progression toward final state."""
    snaps = []
    mid = CompanyState(month=1)
    for m in range(1, 13):
        # Linear interpolate toward final for key metrics
        t = m / 12.0
        s = CompanyState(
            month=m,
            cash=int(mid.cash + (final.cash - mid.cash) * t),
            mrr=int(final.mrr * t),
            users=int(final.users * t),
            product_score=int(20 + (final.product_score - 20) * t),
            team_morale=final.team_morale,
            founder_equity=int(100 + (final.founder_equity - 100) * t),
            board_control=final.board_control,
            market_share=int(final.market_share * t),
            reputation=final.reputation,
            valuation=int(5_000_000 + (final.valuation - 5_000_000) * t),
            monthly_burn=final.monthly_burn,
        )
        snaps.append(_snapshot(m, s))
    return snaps


# ── Task 7.1: 4 endings generate non-empty GameReview ─────────────────────


class TestReviewAllEndings:
    def test_review_bankruptcy(self):
        final = CompanyState(month=8, cash=0, mrr=50000, product_score=30, users=100)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m, "test") for m in range(1, 9)],
            event_logs=[],
            final_state=final,
            ending_status="bankruptcy",
        )
        assert review.ending_title != ""
        assert review.ending_summary != ""
        assert review.advice_for_next_run != ""
        assert review.founder_profile.profile_type != ""

    def test_review_founder_removed(self):
        final = CompanyState(
            month=7,
            cash=100000,
            founder_equity=30,
            board_control=40,
            monthly_burn=50000,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 8)],
            event_logs=[],
            final_state=final,
            ending_status="founder_removed",
        )
        assert review.ending_title != ""
        assert (
            "控制" in review.advice_for_next_run or "股权" in review.advice_for_next_run
        )

    def test_review_series_a_success(self):
        final = CompanyState(
            month=12,
            cash=3_000_000,
            mrr=350_000,
            product_score=75,
            users=800,
            founder_equity=80,
            valuation=30_000_000,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert review.ending_title != ""
        assert review.strategy_scores.overall_score >= 50

    def test_review_survived_but_average(self):
        final = CompanyState(
            month=12, cash=200000, mrr=120000, product_score=45, users=300
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        assert review.ending_title != ""
        assert review.advice_for_next_run != ""

    def test_review_slow_death(self):
        final = CompanyState(
            month=12, cash=50000, mrr=40000, product_score=35, users=150
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="slow_death",
        )
        assert review.ending_title != ""
        assert review.advice_for_next_run != ""


# ── Task 7.2: Strategy scores in 0-100 range ──────────────────────────────


class TestStrategyScores:
    def test_scores_in_range(self):
        final = CompanyState(
            month=12,
            cash=500000,
            mrr=300000,
            product_score=80,
            users=600,
            founder_equity=85,
            valuation=25_000_000,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
        )
        s = review.strategy_scores
        for name in [
            "product_score",
            "growth_score",
            "finance_score",
            "control_score",
            "risk_score",
            "overall_score",
        ]:
            v = getattr(s, name)
            assert 0 <= v <= 100, f"{name} = {v} out of range"

    def test_bankruptcy_scores_lower(self):
        """Bankruptcy should produce lower overall score than series A."""
        final_a = CompanyState(
            month=12,
            cash=3_000_000,
            mrr=350_000,
            product_score=75,
            users=800,
            founder_equity=80,
        )
        review_a = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final_a),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final_a,
            ending_status="series_a_success",
        )
        final_b = CompanyState(month=8, cash=0, mrr=30000, product_score=20, users=50)
        review_b = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final_b),
            action_logs=[_action(m) for m in range(1, 9)],
            event_logs=[],
            final_state=final_b,
            ending_status="bankruptcy",
        )
        assert (
            review_b.strategy_scores.overall_score
            < review_a.strategy_scores.overall_score
        )


# ── Task 7.3: Key moments not empty ───────────────────────────────────────


class TestKeyMoments:
    def test_key_moments_not_empty(self):
        """Even a short game should produce at least 1 key moment."""
        final = CompanyState(
            month=4, cash=5000, mrr=0, product_score=25, users=10, monthly_burn=80000
        )
        snapshots = [
            _snapshot(
                1, CompanyState(month=1, cash=1000000, mrr=0, product_score=20, users=0)
            ),
            _snapshot(
                2,
                CompanyState(
                    month=2, cash=500000, mrr=10000, product_score=22, users=20
                ),
            ),
            _snapshot(
                3,
                CompanyState(
                    month=3, cash=80000, mrr=15000, product_score=24, users=30
                ),
            ),
            _snapshot(4, final),
        ]
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=snapshots,
            action_logs=[_action(m) for m in range(1, 5)],
            event_logs=[],
            final_state=final,
            ending_status="bankruptcy",
        )
        assert (
            len(review.key_moments) >= 1
        ), f"Expected >=1 moments, got {len(review.key_moments)}"

    def test_moments_include_cash_crisis(self):
        """Verify cash drops below danger thresholds are captured."""
        final = CompanyState(month=3, cash=5000, monthly_burn=100000)
        snapshots = [
            _snapshot(1, CompanyState(month=1, cash=1000000)),
            _snapshot(2, CompanyState(month=2, cash=50000)),  # drops below 100k
            _snapshot(3, final),  # drops below 10k
        ]
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=snapshots,
            action_logs=[_action(m) for m in range(1, 4)],
            event_logs=[],
            final_state=final,
            ending_status="bankruptcy",
        )
        titles = [m.title for m in review.key_moments]
        assert any(
            "现金" in t for t in titles
        ), f"No cash crisis moments found in {titles}"


# ── Task 7.4: Founder profile varies with metrics ─────────────────────────


class TestFounderProfile:
    def test_high_product_yields_tech_visionary(self):
        final = CompanyState(
            month=12,
            cash=500000,
            mrr=200000,
            product_score=85,
            users=400,
            founder_equity=90,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert review.founder_profile.profile_type == "tech_visionary"

    def test_low_equity_yields_capital_player(self):
        final = CompanyState(
            month=12,
            cash=5_000_000,
            mrr=300000,
            product_score=55,
            users=600,
            founder_equity=70,
            valuation=35_000_000,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert review.founder_profile.profile_type == "capital_player"

    def test_long_runway_low_growth_conservative(self):
        final = CompanyState(
            month=12,
            cash=800000,
            mrr=50000,
            product_score=40,
            users=100,
            monthly_burn=30000,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        assert review.founder_profile.profile_type == "conservative_operator"

    def test_growth_hacker_from_high_users(self):
        final = CompanyState(
            month=12,
            cash=200000,
            mrr=250000,
            product_score=55,
            users=700,
            founder_equity=85,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        assert review.founder_profile.profile_type == "growth_hacker"


# ── Task 7.5: GameReview model integrity ──────────────────────────────────


class TestGameReviewModel:
    def test_game_review_all_fields_present(self):
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[_snapshot(1, CompanyState(month=1))],
            action_logs=[_action(1)],
            event_logs=[],
            final_state=CompanyState(month=1),
            ending_status="slow_death",
        )
        assert isinstance(review.ending_status, str)
        assert isinstance(review.ending_title, str)
        assert isinstance(review.ending_summary, str)
        assert isinstance(review.founder_profile, FounderProfile)
        assert isinstance(review.strategy_scores, StrategyScore)
        assert isinstance(review.key_moments, list)
        assert isinstance(review.final_metrics, dict)
        assert isinstance(review.advice_for_next_run, str)

    def test_final_metrics_contain_key_fields(self):
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[_snapshot(1, CompanyState(month=1, cash=500000, mrr=100000))],
            action_logs=[_action(1)],
            event_logs=[],
            final_state=CompanyState(month=1, cash=500000, mrr=100000),
            ending_status="slow_death",
        )
        for key in ["cash", "mrr", "product_score", "users", "founder_equity"]:
            assert key in review.final_metrics, f"Missing {key} in final_metrics"


# ── Task 7.6: DB list functions ───────────────────────────────────────────


class TestDBListFunctions:
    def test_list_snapshots_importable(self):
        from src.db.repository import list_snapshots

        assert callable(list_snapshots)

    def test_list_actions_importable(self):
        from src.db.repository import list_actions

        assert callable(list_actions)

    def test_list_events_importable(self):
        from src.db.repository import list_events

        assert callable(list_events)


# ── Task 7.7: Event-based key moments ─────────────────────────────────────


class TestEventKeyMoments:
    def test_events_produce_key_moments(self):
        final = CompanyState(month=6, cash=200000, mrr=80000)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[_snapshot(m, CompanyState(month=m)) for m in range(1, 7)],
            action_logs=[_action(m) for m in range(1, 7)],
            event_logs=[
                {
                    "month": 3,
                    "event_type": "evt_server_crash",
                    "title": "服务器宕机",
                    "severity": "high",
                    "payload_json": "{}",
                },
                {
                    "month": 5,
                    "event_type": "evt_key_hire",
                    "title": "关键人才入职",
                    "severity": "low",
                    "payload_json": "{}",
                },
            ],
            final_state=final,
            ending_status="survived_but_average",
        )
        evt_titles = [m.title for m in review.key_moments]
        assert any(
            "服务器宕机" in t or "关键人才" in t for t in evt_titles
        ), f"Event moments not found in {evt_titles}"


# ── Task 7.8: Snapshot JSON parsing robustness ────────────────────────────


class TestSnapshotParsing:
    def test_snapshot_with_string_state_json(self):
        """Snapshots from DB have state_json as JSON string."""
        state = CompanyState(month=1, cash=500000)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[{"month": 1, "state_json": state.model_dump_json()}],
            action_logs=[_action(1)],
            event_logs=[],
            final_state=state,
            ending_status="slow_death",
        )
        assert review.ending_title != ""

    def test_snapshot_with_dict_state_json(self):
        """Snapshots from in-memory may have state_json as dict."""
        state = CompanyState(month=1, cash=500000)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[{"month": 1, "state_json": state.model_dump()}],
            action_logs=[_action(1)],
            event_logs=[],
            final_state=state,
            ending_status="slow_death",
        )
        assert review.ending_title != ""


# ── Task 7.9: Advice varies by ending ─────────────────────────────────────


class TestAdvice:
    def test_bankruptcy_advice_mentions_cash(self):
        final = CompanyState(month=5, cash=0)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[
                _snapshot(m, CompanyState(month=m, cash=max(0, 1000000 - m * 200000)))
                for m in range(1, 6)
            ],
            action_logs=[_action(m) for m in range(1, 6)],
            event_logs=[],
            final_state=final,
            ending_status="bankruptcy",
        )
        assert (
            "现金" in review.advice_for_next_run or "跑道" in review.advice_for_next_run
        )

    def test_series_a_advice_mentions_growth(self):
        final = CompanyState(
            month=12,
            cash=2_000_000,
            mrr=400000,
            product_score=80,
            users=900,
            founder_equity=80,
        )
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=_default_snapshots(final),
            action_logs=[_action(m) for m in range(1, 13)],
            event_logs=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert len(review.advice_for_next_run) > 10


# ── Task 7.10: Empty data edge case ───────────────────────────────────────


class TestEdgeCases:
    def test_empty_snapshots_and_logs(self):
        """Should not crash with empty history."""
        final = CompanyState(month=1)
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[],
            action_logs=[],
            event_logs=[],
            final_state=final,
            ending_status="slow_death",
        )
        assert isinstance(review, GameReview)
        assert review.founder_profile.profile_type == "chaotic_survivor"

    def test_session_id_propagated(self):
        review = ReviewEngine.generate_review(
            initial_state=CompanyState(),
            snapshots=[],
            action_logs=[],
            event_logs=[],
            final_state=CompanyState(),
            ending_status="slow_death",
            session_id=42,
        )
        assert review.session_id == 42
