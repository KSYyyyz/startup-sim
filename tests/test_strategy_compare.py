"""Tests for Alpha 1.5 StrategyCompare."""

from __future__ import annotations

import pytest

from src.core.models import (
    CompanyState,
    FounderProfile,
    GameReview,
    StrategyComparison,
    StrategyScore,
)
from src.core.strategy_compare import StrategyCompare


def _make_review(
    label: str,
    overall: int,
    product: int = 50,
    growth: int = 50,
    finance: int = 50,
    control: int = 50,
    risk: int = 50,
    ending_status: str = "survived_but_average",
    founder_type: str = "balanced_leader",
) -> GameReview:
    """Create a minimal GameReview for comparison."""
    return GameReview(
        session_id=hash(label) % 1000,
        ending_status=ending_status,
        ending_title=label,
        ending_summary=f"{label} summary",
        founder_profile=FounderProfile(
            profile_type=founder_type,
            profile_title=f"{label} CEO",
            description="Test",
        ),
        strategy_scores=StrategyScore(
            product_score=product,
            growth_score=growth,
            finance_score=finance,
            control_score=control,
            risk_score=risk,
            overall_score=overall,
        ),
    )


# ── Comparison generation ────────────────────────────────────────────────────


class TestComparisonBasics:
    def test_compare_returns_strategy_comparison(self):
        """Should return a StrategyComparison with all fields."""
        reviews = [
            _make_review("策略A", 80, product=70),
            _make_review("策略B", 60, growth=80),
            _make_review("策略C", 90, finance=85),
        ]
        result = StrategyCompare.compare(reviews)
        assert isinstance(result, StrategyComparison)
        assert len(result.strategies) == 3
        assert result.best_overall != ""
        assert result.conclusion != ""

    def test_compare_ranks_by_overall(self):
        """Highest overall score should be ranked first."""
        reviews = [
            _make_review("C", 60),
            _make_review("A", 90),
            _make_review("B", 75),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.summary_table[0]["strategy"] == "A"
        assert result.summary_table[0]["rank"] == 1
        assert result.summary_table[1]["strategy"] == "B"
        assert result.summary_table[2]["strategy"] == "C"

    def test_compare_best_overall_is_highest(self):
        """best_overall should be the strategy with highest overall score."""
        reviews = [
            _make_review("弱", 40),
            _make_review("强", 95),
            _make_review("中", 70),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_overall == "强"

    def test_compare_best_product(self):
        """best_product should be the strategy with highest product score."""
        reviews = [
            _make_review("A", 70, product=90),
            _make_review("B", 70, product=50),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_product == "A"

    def test_compare_best_growth(self):
        """best_growth should be the strategy with highest growth score."""
        reviews = [
            _make_review("A", 70, growth=95),
            _make_review("B", 70, growth=60),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_growth == "A"

    def test_compare_best_finance(self):
        """best_finance should be the strategy with highest finance score."""
        reviews = [
            _make_review("A", 70, finance=88),
            _make_review("B", 70, finance=55),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_finance == "A"

    def test_compare_best_control(self):
        """best_control should be the strategy with highest control score."""
        reviews = [
            _make_review("A", 70, control=99),
            _make_review("B", 70, control=60),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_control == "A"

    def test_compare_worst_risk(self):
        """worst_risk should be the strategy with lowest risk score."""
        reviews = [
            _make_review("A", 70, risk=20),
            _make_review("B", 70, risk=80),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.worst_risk == "A"  # A has lower (worse) risk score


# ── Summary table ────────────────────────────────────────────────────────────


class TestSummaryTable:
    def test_summary_table_not_empty(self):
        """Summary table should have one row per strategy."""
        reviews = [
            _make_review("S1", 80),
            _make_review("S2", 70),
            _make_review("S3", 85),
            _make_review("S4", 65),
            _make_review("S5", 75),
        ]
        result = StrategyCompare.compare(reviews)
        assert len(result.summary_table) == 5
        for row in result.summary_table:
            assert "rank" in row
            assert "strategy" in row
            assert "product" in row
            assert "growth" in row
            assert "finance" in row
            assert "control" in row
            assert "risk" in row
            assert "overall" in row

    def test_summary_table_ranks_unique(self):
        """Each rank should be unique."""
        reviews = [
            _make_review("A", 80),
            _make_review("B", 70),
            _make_review("C", 60),
        ]
        result = StrategyCompare.compare(reviews)
        ranks = [row["rank"] for row in result.summary_table]
        assert ranks == [1, 2, 3]


# ── Edge cases ───────────────────────────────────────────────────────────────


class TestEdgeCases:
    def test_empty_reviews(self):
        """Empty input should return a StrategyComparison without crashing."""
        result = StrategyCompare.compare([])
        assert isinstance(result, StrategyComparison)
        assert result.strategies == []
        assert result.conclusion != ""

    def test_single_review(self):
        """Single review should be best in everything."""
        review = _make_review("唯一", 75)
        result = StrategyCompare.compare([review])
        assert result.best_overall == "唯一"
        assert result.best_product == "唯一"
        assert result.best_growth == "唯一"
        assert result.best_finance == "唯一"
        assert result.best_control == "唯一"
        assert result.worst_risk == "唯一"

    def test_comparison_with_different_endings(self):
        """Reviews with different ending types should be comparable."""
        reviews = [
            _make_review("A轮成功", 85, ending_status="series_a_success"),
            _make_review("破产", 25, ending_status="bankruptcy", founder_type="chaotic_survivor"),
            _make_review("存活", 55, ending_status="survived_but_average"),
        ]
        result = StrategyCompare.compare(reviews)
        assert result.best_overall == "A轮成功"
        assert result.summary_table[0]["overall"] == 85
        assert result.summary_table[2]["overall"] == 25


# ── Conclusion ───────────────────────────────────────────────────────────────


class TestConclusion:
    def test_conclusion_mentions_best_overall(self):
        """Conclusion should mention the best overall strategy."""
        reviews = [
            _make_review("胜利者", 90),
            _make_review("失败者", 30),
        ]
        result = StrategyCompare.compare(reviews)
        assert "胜利者" in result.conclusion

    def test_conclusion_is_not_empty(self):
        """Conclusion should always be a non-empty string."""
        for n in [0, 1, 3]:
            reviews = [_make_review(f"S{i}", 50 + i * 10) for i in range(n)]
            result = StrategyCompare.compare(reviews)
            assert isinstance(result.conclusion, str)
