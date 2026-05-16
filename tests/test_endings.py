"""Tests for ending_evaluator module."""

import pytest
from src.core.models import CompanyState, EndingType
from src.core.ending_evaluator import evaluate, describe_ending


class TestEndingEvaluator:
    """Test game ending conditions."""

    def test_bankruptcy(self):
        """cash=0 → bankruptcy."""
        state = CompanyState(cash=0, month=3)
        result = evaluate(state)
        assert result == EndingType.BANKRUPTCY

    def test_founder_removed(self):
        """equity < 34, board < 45, runway < 4 → founder_removed."""
        state = CompanyState(
            founder_equity=30, board_control=40,
            cash=500_000, monthly_burn=200_000,  # runway = 2.5
            month=7,
        )
        result = evaluate(state)
        assert result == EndingType.FOUNDER_REMOVED

    def test_founder_not_removed_adequate_runway(self):
        """equity < 34, board < 45 but runway >= 4 → no ending."""
        state = CompanyState(
            founder_equity=30, board_control=40,
            cash=1_000_000, monthly_burn=200_000,  # runway = 5
            month=7,
        )
        result = evaluate(state)
        assert result is None

    def test_series_a_success(self):
        """month >= 12, mrr >= 500k, product >= 70, equity >= 50 → series_a."""
        state = CompanyState(
            month=12, cash=1_000_000,
            mrr=600_000, product_score=75, founder_equity=55,
        )
        result = evaluate(state)
        assert result == EndingType.SERIES_A_SUCCESS

    def test_survived_but_average(self):
        """month >= 12, mrr >= 200k, cash > 0 → survived_but_average."""
        state = CompanyState(
            month=12, cash=100_000,
            mrr=250_000, product_score=60, founder_equity=40,
        )
        result = evaluate(state)
        assert result == EndingType.SURVIVED_BUT_AVERAGE

    def test_slow_death(self):
        """month >= 12, doesn't meet other thresholds → slow_death."""
        state = CompanyState(
            month=12, cash=50_000,
            mrr=50_000, product_score=30, founder_equity=30,
        )
        result = evaluate(state)
        assert result == EndingType.SLOW_DEATH

    def test_continue_game(self):
        """Early month, healthy state → None (continue)."""
        state = CompanyState(
            month=5, cash=1_000_000,
            monthly_burn=100_000, mrr=100_000,
        )
        result = evaluate(state)
        assert result is None

    def test_immediate_endings_priority(self):
        """Bankruptcy takes priority over founder_removed."""
        state = CompanyState(
            cash=0, founder_equity=30, board_control=40,
            monthly_burn=200_000, month=5,
        )
        result = evaluate(state)
        assert result == EndingType.BANKRUPTCY


class TestDescribeEnding:
    """Test ending descriptions."""

    def test_bankruptcy_description(self):
        desc = describe_ending(EndingType.BANKRUPTCY, CompanyState(month=4))
        assert "破产" in desc

    def test_series_a_description(self):
        desc = describe_ending(EndingType.SERIES_A_SUCCESS, CompanyState(mrr=500_000, product_score=80))
        assert "A轮" in desc or "融资" in desc
