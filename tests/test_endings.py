"""Tests for ending_evaluator module."""

from src.core.ending_evaluator import (
    PlayerPath,
    classify_player_path,
    describe_ending,
    describe_ending_with_seed,
    evaluate,
)
from src.core.models import CompanyState, EndingType


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
            founder_equity=30,
            board_control=40,
            cash=500_000,
            monthly_burn=200_000,  # runway = 2.5
            month=7,
        )
        result = evaluate(state)
        assert result == EndingType.FOUNDER_REMOVED

    def test_founder_not_removed_adequate_runway(self):
        """equity < 34, board < 45 but runway >= 4 → no ending."""
        state = CompanyState(
            founder_equity=30,
            board_control=40,
            cash=1_000_000,
            monthly_burn=200_000,  # runway = 5
            month=7,
        )
        result = evaluate(state)
        assert result is None

    def test_series_a_success(self):
        """month >= 12, mrr >= 500k, product >= 70, equity >= 50 → series_a."""
        state = CompanyState(
            month=12,
            cash=1_000_000,
            mrr=600_000,
            product_score=75,
            founder_equity=55,
        )
        result = evaluate(state)
        assert result == EndingType.SERIES_A_SUCCESS

    def test_survived_but_average(self):
        """month >= 12, mrr >= 200k, cash > 0 → survived_but_average."""
        state = CompanyState(
            month=12,
            cash=100_000,
            mrr=250_000,
            product_score=60,
            founder_equity=40,
            monthly_burn=50_000,
        )
        result = evaluate(state)
        assert result == EndingType.SURVIVED_BUT_AVERAGE

    def test_slow_death(self):
        """month >= 12, doesn't meet other thresholds → slow_death."""
        state = CompanyState(
            month=12,
            cash=50_000,
            mrr=50_000,
            product_score=30,
            founder_equity=30,
            monthly_burn=25_000,
        )
        result = evaluate(state)
        assert result == EndingType.SLOW_DEATH

    def test_continue_game(self):
        """Early month, healthy state → None (continue)."""
        state = CompanyState(
            month=5,
            cash=1_000_000,
            monthly_burn=100_000,
            mrr=100_000,
        )
        result = evaluate(state)
        assert result is None

    def test_immediate_endings_priority(self):
        """Bankruptcy takes priority over founder_removed."""
        state = CompanyState(
            cash=0,
            founder_equity=30,
            board_control=40,
            monthly_burn=200_000,
            month=5,
        )
        result = evaluate(state)
        assert result == EndingType.BANKRUPTCY


class TestDescribeEnding:
    """Test ending descriptions (Alpha 1.3: variant narratives)."""

    def test_bankruptcy_description_nonempty(self):
        desc = describe_ending(EndingType.BANKRUPTCY, CompanyState(month=4))
        assert len(desc) > 10

    def test_series_a_description_nonempty(self):
        desc = describe_ending(
            EndingType.SERIES_A_SUCCESS, CompanyState(mrr=500_000, product_score=80)
        )
        assert len(desc) > 10

    def test_describe_ending_with_seed_deterministic(self):
        """Seeded describe should return same variant every time."""
        state = CompanyState(month=4, cash=0)
        d1 = describe_ending_with_seed(EndingType.BANKRUPTCY, state, seed=1)
        d2 = describe_ending_with_seed(EndingType.BANKRUPTCY, state, seed=1)
        assert d1 == d2

    def test_different_seeds_may_differ(self):
        """Different seeds for same ending can produce different variants."""
        state = CompanyState(month=4, cash=0, product_score=75, founder_equity=30)
        path = classify_player_path(state)
        variants_for_path = len(
            __import__(
                "src.core.ending_evaluator", fromlist=["BANKRUPTCY_NARRATIVES"]
            ).BANKRUPTCY_NARRATIVES.get(path, [])
        )
        if variants_for_path > 1:
            d1 = describe_ending_with_seed(EndingType.BANKRUPTCY, state, seed=0)
            d2 = describe_ending_with_seed(EndingType.BANKRUPTCY, state, seed=1)
            # May or may not differ depending on path, but both should be non-empty
            assert len(d1) > 10 and len(d2) > 10

    def test_describe_ending_all_endings_nonempty(self):
        """Every ending type should produce a non-empty description."""
        for ending in EndingType:
            if ending == EndingType.NONE:
                continue
            desc = describe_ending(ending, CompanyState(month=4))
            assert len(desc) > 5, f"{ending} description too short: '{desc}'"

    def test_path_classification_rnd(self):
        state = CompanyState(product_score=80, users=100, founder_equity=60)
        assert classify_player_path(state) == PlayerPath.RND

    def test_path_classification_fundraise(self):
        state = CompanyState(founder_equity=30, product_score=40, users=100)
        assert classify_player_path(state) == PlayerPath.FUNDRAISE

    def test_path_classification_conservative(self):
        state = CompanyState(
            cash=2_000_000,
            monthly_burn=100_000,  # runway 20
            product_score=30,
            users=50,
            founder_equity=80,
        )
        assert classify_player_path(state) == PlayerPath.CONSERVATIVE

    def test_path_classification_balanced(self):
        state = CompanyState(
            product_score=50,
            users=300,
            founder_equity=60,
            cash=800_000,
            monthly_burn=150_000,  # runway ~5.3
        )
        assert classify_player_path(state) == PlayerPath.BALANCED
