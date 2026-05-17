"""Tests for Alpha 1.5 ReplayEngine."""

from __future__ import annotations

import pytest

from src.core.models import CompanyState, GameReplay, ReplayMonth
from src.core.replay_engine import ReplayEngine


def _snapshot(month: int, state: CompanyState) -> dict:
    return {"month": month, "state_json": state.model_dump()}


def _action(month: int, raw: str = "test") -> dict:
    return {"month": month, "raw_input": raw, "action_plan_json": "[]"}


def _default_snapshots(final: CompanyState) -> list[dict]:
    """Generate 12 snapshots with gradual progression toward final state."""
    snaps = []
    for m in range(1, 13):
        t = m / 12.0
        s = CompanyState(
            month=m,
            cash=max(0, int(1_000_000 + (final.cash - 1_000_000) * t)),
            mrr=int(final.mrr * t),
            users=int(final.users * t),
            product_score=int(20 + (final.product_score - 20) * t),
            team_morale=final.team_morale,
            founder_equity=int(100 + (final.founder_equity - 100) * t),
            valuation=int(5_000_000 + (final.valuation - 5_000_000) * t),
            monthly_burn=final.monthly_burn,
        )
        snaps.append(_snapshot(m, s))
    return snaps


# ── GameReplay generation ────────────────────────────────────────────────────


class TestReplayGeneration:
    def test_replay_has_all_fields(self):
        """Replay should have all required fields populated."""
        final = CompanyState(month=12, cash=500000, mrr=300000, product_score=75, users=600)
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="series_a_success",
            session_id=1,
        )
        assert replay.session_id == 1
        assert replay.title != ""
        assert replay.opening_summary != ""
        assert len(replay.months) == 12
        assert replay.climax_month > 0
        assert replay.ending_summary != ""
        assert len(replay.replay_tags) > 0

    def test_replay_months_not_empty(self):
        """Every ending should produce 12 months."""
        for ending in ["series_a_success", "survived_but_average", "bankruptcy", "slow_death", "founder_removed"]:
            final = CompanyState(month=12, cash=500000, mrr=100000, product_score=50, users=200)
            replay = ReplayEngine.generate_replay(
                snapshots=_default_snapshots(final),
                actions=[_action(m) for m in range(1, 13)],
                events=[],
                final_state=final,
                ending_status=ending,
            )
            assert len(replay.months) == 12, f"Expected 12 months for {ending}"

    def test_climax_is_reasonable(self):
        """Climax month should be between 1 and 12."""
        final = CompanyState(month=12, cash=100000, mrr=50000, product_score=30, users=100, monthly_burn=100000)
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="slow_death",
        )
        assert 1 <= replay.climax_month <= 12

    def test_tags_not_empty(self):
        """replay_tags should always have at least 1 tag."""
        final = CompanyState(month=12, cash=200000, mrr=100000, product_score=50, users=200)
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        assert len(replay.replay_tags) >= 1

    def test_tags_max_4(self):
        """replay_tags should be capped at 4."""
        # High ambition game that could earn many tags
        final = CompanyState(
            month=12, cash=3_000_000, mrr=500000, product_score=90,
            users=1500, founder_equity=96, valuation=40_000_000,
        )
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert len(replay.replay_tags) <= 4

    def test_bankruptcy_gets_burn_tag(self):
        """Bankruptcy ending should include relevant tag."""
        final = CompanyState(month=4, cash=0, mrr=5000, product_score=25, users=20)
        snapshots = [
            _snapshot(m, CompanyState(month=m, cash=max(0, 1000000 - m * 250000)))
            for m in range(1, 5)
        ]
        replay = ReplayEngine.generate_replay(
            snapshots=snapshots,
            actions=[_action(m) for m in range(1, 5)],
            events=[],
            final_state=final,
            ending_status="bankruptcy",
        )
        tags_str = " ".join(replay.replay_tags)
        assert "燃烧殆尽" in tags_str or "惊险" in tags_str

    def test_series_a_gets_winner_tag(self):
        """Series A success should get 'A轮赢家' tag."""
        final = CompanyState(
            month=12, cash=2_000_000, mrr=400000, product_score=80, users=900
        )
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="series_a_success",
        )
        assert "A轮赢家" in replay.replay_tags


# ── Risk levels ──────────────────────────────────────────────────────────────


class TestRiskLevels:
    def test_cash_critical_is_critical(self):
        """Cash <= 10k should be risk critical."""
        replay = ReplayEngine.generate_replay(
            snapshots=[_snapshot(1, CompanyState(month=1, cash=5000))],
            actions=[_action(1)],
            events=[],
            final_state=CompanyState(month=1, cash=5000),
            ending_status="bankruptcy",
        )
        assert replay.months[0].risk_level == "critical"

    def test_high_cash_is_low_risk(self):
        """High cash with good runway should be low risk."""
        replay = ReplayEngine.generate_replay(
            snapshots=[
                _snapshot(1, CompanyState(month=1, cash=1_000_000, monthly_burn=50000, mrr=100000, team_morale=80, founder_equity=100))
            ],
            actions=[_action(1)],
            events=[],
            final_state=CompanyState(month=1, cash=1_000_000),
            ending_status="series_a_success",
        )
        assert replay.months[0].risk_level == "low"


# ── Month titles ─────────────────────────────────────────────────────────────


class TestMonthTitles:
    def test_month_12_ending_has_finale(self):
        """Month 12 with an ending should include '大结局'."""
        final = CompanyState(month=12, cash=200000, mrr=100000)
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        assert "大结局" in replay.months[-1].title

    def test_cash_emergency_title(self):
        """Low cash should add '现金告急' to title."""
        replay = ReplayEngine.generate_replay(
            snapshots=[_snapshot(1, CompanyState(month=1, cash=30000))],
            actions=[_action(1)],
            events=[],
            final_state=CompanyState(month=1, cash=30000),
            ending_status="survived_but_average",
        )
        assert "现金告急" in replay.months[0].title


# ── Metric changes ───────────────────────────────────────────────────────────


class TestMetricChanges:
    def test_metric_changes_are_calculated(self):
        """Metric changes should be the delta from previous month."""
        final = CompanyState(month=12, cash=800000, mrr=100000, users=500, product_score=60)
        replay = ReplayEngine.generate_replay(
            snapshots=_default_snapshots(final),
            actions=[_action(m) for m in range(1, 13)],
            events=[],
            final_state=final,
            ending_status="survived_but_average",
        )
        for m in replay.months:
            assert isinstance(m.metric_changes, dict)
            for key in ["cash", "mrr", "users", "product"]:
                assert key in m.metric_changes


# ── Events in replay ─────────────────────────────────────────────────────────


class TestReplayEvents:
    def test_events_attached_to_correct_month(self):
        """Events should appear in the correct month."""
        events = [
            {"month": 3, "event_type": "evt_server_crash", "title": "服务器宕机"},
            {"month": 7, "event_type": "evt_key_hire", "title": "关键人才入职"},
        ]
        replay = ReplayEngine.generate_replay(
            snapshots=[_snapshot(m, CompanyState(month=m)) for m in range(1, 13)],
            actions=[_action(m) for m in range(1, 13)],
            events=events,
            final_state=CompanyState(month=12),
            ending_status="survived_but_average",
        )
        m3 = replay.months[2]  # index 2 = month 3
        m7 = replay.months[6]  # index 6 = month 7
        assert any("服务器宕机" in e for e in m3.major_events)
        assert any("关键人才入职" in e for e in m7.major_events)


# ── Snapshot JSON parsing ────────────────────────────────────────────────────


class TestSnapshotParsing:
    def test_string_state_json(self):
        """Snapshots with JSON string state_json should work."""
        state = CompanyState(month=1, cash=500000)
        replay = ReplayEngine.generate_replay(
            snapshots=[{"month": 1, "state_json": state.model_dump_json()}],
            actions=[_action(1)],
            events=[],
            final_state=state,
            ending_status="slow_death",
        )
        assert len(replay.months) == 1

    def test_dict_state_json(self):
        """Snapshots with dict state_json should work."""
        state = CompanyState(month=1, cash=500000)
        replay = ReplayEngine.generate_replay(
            snapshots=[{"month": 1, "state_json": state.model_dump()}],
            actions=[_action(1)],
            events=[],
            final_state=state,
            ending_status="slow_death",
        )
        assert len(replay.months) == 1


# ── Ending narratives ────────────────────────────────────────────────────────


class TestEndingNarratives:
    def test_all_endings_have_narrative(self):
        """Each ending type should produce a non-empty ending narrative."""
        for ending in ["series_a_success", "survived_but_average", "bankruptcy", "slow_death", "founder_removed"]:
            replay = ReplayEngine.generate_replay(
                snapshots=[_snapshot(1, CompanyState(month=1))],
                actions=[_action(1)],
                events=[],
                final_state=CompanyState(month=1),
                ending_status=ending,
            )
            assert replay.ending_summary != "", f"Empty ending summary for {ending}"
            assert replay.title != "", f"Empty title for {ending}"


# ── Empty data edge case ─────────────────────────────────────────────────────


class TestEdgeCases:
    def test_empty_snapshots(self):
        """Should not crash with empty data."""
        replay = ReplayEngine.generate_replay(
            snapshots=[],
            actions=[],
            events=[],
            final_state=CompanyState(month=1),
            ending_status="slow_death",
        )
        assert isinstance(replay, GameReplay)
        assert replay.months == []
        assert len(replay.replay_tags) > 0

    def test_one_month_game(self):
        """One-month game should still generate replay."""
        replay = ReplayEngine.generate_replay(
            snapshots=[_snapshot(1, CompanyState(month=1, cash=0))],
            actions=[_action(1)],
            events=[],
            final_state=CompanyState(month=1, cash=0),
            ending_status="bankruptcy",
        )
        assert len(replay.months) == 1
        assert replay.climax_month == 1
