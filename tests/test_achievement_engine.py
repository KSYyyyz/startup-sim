"""Tests for Alpha 1.5 AchievementEngine."""

from __future__ import annotations

import pytest

from src.core.models import (
    Achievement,
    AchievementResult,
    CompanyState,
    FounderProfile,
    GameReview,
    StrategyScore,
)
from src.core.achievement_engine import AchievementEngine


def _snapshot(month: int, state: CompanyState) -> dict:
    return {"month": month, "state_json": state.model_dump()}


def _dummy_review(ending_status: str, final: CompanyState) -> GameReview:
    """Create a minimal GameReview for achievement evaluation."""
    return GameReview(
        session_id=1,
        ending_status=ending_status,
        ending_title="Test",
        ending_summary="Test summary",
        founder_profile=FounderProfile(
            profile_type="balanced_leader",
            profile_title="均衡型CEO",
            description="Test",
        ),
        strategy_scores=StrategyScore(
            product_score=final.product_score,
            growth_score=min(100, final.users // 10),
            finance_score=min(100, final.cash // 10000),
            control_score=final.founder_equity,
            risk_score=50,
            overall_score=50,
        ),
    )


# ── Common achievements ──────────────────────────────────────────────────────


class TestCommonAchievements:
    def test_product_believer(self):
        """product_score >= 80 should unlock 产品信仰者."""
        final = CompanyState(month=12, product_score=85)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "product_believer" in codes

    def test_product_believer_not_unlocked_below_80(self):
        """product_score < 80 should NOT unlock 产品信仰者."""
        final = CompanyState(month=12, product_score=60)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "product_believer" not in codes

    def test_growth_machine_by_users(self):
        """users >= 1000 should unlock 增长机器."""
        final = CompanyState(month=12, users=1200)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "growth_machine" in codes

    def test_growth_machine_by_mrr(self):
        """mrr >= 500k should unlock 增长机器."""
        final = CompanyState(month=12, mrr=600_000)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "growth_machine" in codes

    def test_series_a_winner(self):
        """series_a_success should unlock A轮赢家."""
        final = CompanyState(month=12, cash=3_000_000, mrr=350_000)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="series_a_success",
            review=_dummy_review("series_a_success", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "series_a_winner" in codes

    def test_near_death(self):
        """Cash dropped below 50k but didn't go bankrupt."""
        final = CompanyState(month=12, cash=200000, mrr=100000)
        snapshots = [
            _snapshot(1, CompanyState(month=1, cash=40000)),  # below 50k
            _snapshot(2, CompanyState(month=2, cash=200000)),
        ]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "near_death" in codes

    def test_cash_guardian(self):
        """Cash never dropped below 500k."""
        final = CompanyState(month=12, cash=600000)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=600000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "cash_guardian" in codes

    def test_control_master(self):
        """Equity >= 95% should unlock 控制权大师."""
        final = CompanyState(month=12, founder_equity=96)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "control_master" in codes

    def test_dilute_for_growth(self):
        """Equity < 80% + MRR >= 150k = 稀释换增长."""
        final = CompanyState(month=12, founder_equity=75, mrr=200_000)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "dilute_for_growth" in codes


# ── Rare achievements ────────────────────────────────────────────────────────


class TestRareAchievements:
    def test_slow_death(self):
        """slow_death ending = 慢性死亡."""
        final = CompanyState(month=12, cash=30000, product_score=30)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=100000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="slow_death",
            review=_dummy_review("slow_death", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "slow_death" in codes

    def test_rd_trap(self):
        """product >= 70 + bankruptcy = 研发陷阱."""
        final = CompanyState(month=4, cash=0, product_score=75)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=100000)) for m in range(1, 5)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="bankruptcy",
            review=_dummy_review("bankruptcy", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "rd_trap" in codes

    def test_marketing_bubble(self):
        """users >= 500 + product < 40 = 营销泡沫."""
        final = CompanyState(month=12, users=600, product_score=30)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "marketing_bubble" in codes

    def test_small_and_beautiful(self):
        """survived_but_average + product >= 75 = 小而美."""
        final = CompanyState(month=12, product_score=78)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=100000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "small_and_beautiful" in codes

    def test_capital_player_rare(self):
        """equity < 70% + valuation > 25M = 资本玩家."""
        final = CompanyState(month=12, founder_equity=60, valuation=30_000_000)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "capital_player_rare" in codes


# ── Epic achievements ────────────────────────────────────────────────────────


class TestEpicAchievements:
    def test_crisis_handler(self):
        """>=3 risky months + series_a_success = 危机处理者."""
        final = CompanyState(month=12, cash=3_000_000, mrr=350_000)
        snapshots = [
            _snapshot(1, CompanyState(month=1, cash=50000)),  # risky
            _snapshot(2, CompanyState(month=2, cash=30000)),  # risky
            _snapshot(3, CompanyState(month=3, cash=80000)),  # risky
            _snapshot(4, CompanyState(month=4, cash=3_000_000)),  # recovered
        ]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="series_a_success",
            review=_dummy_review("series_a_success", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "crisis_handler" in codes

    def test_steady_operator(self):
        """0 risky months + series_a_success = 稳健经营者."""
        final = CompanyState(month=12, cash=3_000_000, mrr=350_000)
        snapshots = [
            _snapshot(m, CompanyState(month=m, cash=1_000_000, monthly_burn=30000))
            for m in range(1, 13)
        ]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="series_a_success",
            review=_dummy_review("series_a_success", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "steady_operator" in codes


# ── Legendary achievements ───────────────────────────────────────────────────


class TestLegendaryAchievements:
    def test_legendary_founder(self):
        """series_a_success + product >= 85 + users >= 1000 + equity >= 80."""
        final = CompanyState(
            month=12, cash=5_000_000, mrr=600_000, product_score=90,
            users=1500, founder_equity=85,
        )
        snapshots = [_snapshot(m, CompanyState(month=m, cash=1_000_000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="series_a_success",
            review=_dummy_review("series_a_success", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "legendary_founder" in codes

    def test_legendary_not_unlocked_without_a_round(self):
        """Should not unlock legendary without series_a_success."""
        final = CompanyState(
            month=12, cash=500000, product_score=90, users=1500, founder_equity=85
        )
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        codes = [a.code for a in result.achievements]
        assert "legendary_founder" not in codes


# ── Rarity validation ────────────────────────────────────────────────────────


class TestRarityValidation:
    def test_all_rarities_are_legal(self):
        """Every achievement should have a valid rarity."""
        for ending in ["series_a_success", "survived_but_average", "bankruptcy", "slow_death", "founder_removed"]:
            final = CompanyState(month=12, cash=500000)
            snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
            result = AchievementEngine.evaluate(
                final_state=final,
                ending_status=ending,
                review=_dummy_review(ending, final),
                snapshots=snapshots,
            )
            for a in result.achievements:
                assert a.rarity in ("common", "rare", "epic", "legendary"), \
                    f"Bad rarity '{a.rarity}' for {a.code}"

    def test_rarity_counts(self):
        """total_count and rare_count should be consistent."""
        final = CompanyState(
            month=12, cash=5_000_000, mrr=600_000, product_score=90,
            users=1500, founder_equity=96,
        )
        snapshots = [_snapshot(m, CompanyState(month=m, cash=1_000_000, monthly_burn=30000))
                     for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="series_a_success",
            review=_dummy_review("series_a_success", final),
            snapshots=snapshots,
        )
        assert result.total_count == len(result.achievements)
        rare_count = sum(1 for a in result.achievements if a.rarity != "common")
        assert result.rare_count == rare_count


# ── Result model integrity ───────────────────────────────────────────────────


class TestResultIntegrity:
    def test_achievement_result_fields(self):
        """AchievementResult should have all required fields."""
        final = CompanyState(month=1)
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="slow_death",
            review=_dummy_review("slow_death", final),
            snapshots=[],
        )
        assert isinstance(result, AchievementResult)
        assert isinstance(result.achievements, list)
        assert isinstance(result.total_count, int)
        assert isinstance(result.rare_count, int)
        assert isinstance(result.summary, str)
        assert result.summary != ""

    def test_empty_snapshots_does_not_crash(self):
        """Empty snapshots should not crash evaluation."""
        final = CompanyState(month=1)
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="bankruptcy",
            review=_dummy_review("bankruptcy", final),
            snapshots=[],
        )
        assert isinstance(result, AchievementResult)

    def test_achievement_model_fields(self):
        """Each Achievement should have code, title, description, rarity."""
        final = CompanyState(month=12, product_score=90)
        snapshots = [_snapshot(m, CompanyState(month=m, cash=500000)) for m in range(1, 13)]
        result = AchievementEngine.evaluate(
            final_state=final,
            ending_status="survived_but_average",
            review=_dummy_review("survived_but_average", final),
            snapshots=snapshots,
        )
        for a in result.achievements:
            assert a.code != ""
            assert a.title != ""
            assert a.description != ""
            assert a.rarity != ""
