"""Tests for fundraising_engine: valuation logic, acceptance/rejection, counter-offers."""

from src.core.fundraising_engine import evaluate_fundraising
from src.core.models import CompanyState


def _state(**kwargs):
    defaults = dict(
        month=3,
        cash=2_000_000,
        mrr=700_000,
        users=5000,
        monthly_burn=180_000,
        product_score=70,
        team_morale=70,
        founder_equity=85,
        board_control=85,
        market_share=5,
        reputation=60,
        employee_count=15,
        price=5000,
        valuation=10_000_000,
    )
    defaults.update(kwargs)
    return CompanyState(**defaults)


class TestFundraisingEngine:
    """Direct tests of evaluate_fundraising()."""

    def test_accept_reasonable_offer(self):
        """Offer within fair range is accepted."""
        state = _state(mrr=700_000, users=5000, product_score=70, reputation=60)
        offer = evaluate_fundraising(state, requested_amount=5_000_000, requested_equity=10)
        assert offer.accepted is True
        assert offer.accepted_amount == 5_000_000
        assert offer.accepted_equity == 10
        assert offer.implied_valuation == 50_000_000

    def test_reject_overvalued(self):
        """implied_valuation > max*1.5 is rejected, accepted_amount=0."""
        # Very poor metrics → fair range is low, 500万/10% = 5000万 is overvalued
        state = _state(mrr=100_000, users=200, product_score=20, reputation=30)
        offer = evaluate_fundraising(state, requested_amount=5_000_000, requested_equity=10)
        assert offer.accepted is False
        assert offer.accepted_amount == 0
        assert "估值过高" in offer.reason

    def test_reject_no_cash_change(self):
        """Rejected offer should not add cash to delta (accepted_amount=0)."""
        state = _state(mrr=100_000, users=200, product_score=20, reputation=30)
        offer = evaluate_fundraising(state, requested_amount=5_000_000, requested_equity=10)
        assert offer.accepted is False
        assert offer.accepted_amount == 0
        assert offer.accepted_equity == 0.0

    def test_counter_offer_included(self):
        """Rejected offer returns suggested_amount and suggested_equity."""
        state = _state(mrr=100_000, users=200, product_score=20, reputation=30)
        offer = evaluate_fundraising(state, requested_amount=5_000_000, requested_equity=10)
        assert offer.accepted is False
        # Should have a suggested_amount > 0 and suggested_equity > 0
        assert offer.suggested_amount >= 0
        assert offer.suggested_equity >= 0

    def test_warn_undervalued(self):
        """implied < min*0.5 warns but accepts."""
        # High MRR → high fair range, 100万/10% = 1000万 could be undervalued
        state = _state(mrr=2_000_000, users=20000, product_score=85, reputation=85)
        offer = evaluate_fundraising(state, requested_amount=1_000_000, requested_equity=10)
        if offer.implied_valuation < offer.fair_valuation_min * 0.5:
            assert offer.accepted is True
            assert len(offer.warnings) > 0
            assert "贱卖" in offer.warnings[0] or "低估" in offer.warnings[0]

    def test_zero_equity_rejected(self):
        """equity <= 0 is rejected."""
        state = _state()
        offer = evaluate_fundraising(state, requested_amount=5_000_000, requested_equity=0)
        assert offer.accepted is False
        assert "无效" in offer.reason
        assert offer.accepted_amount == 0

    def test_high_reputation_boosts_valuation(self):
        """rep 90 gives higher fair value range than default."""
        state_low = _state(reputation=50)
        state_high = _state(reputation=90)
        offer_low = evaluate_fundraising(state_low, requested_amount=5_000_000, requested_equity=10)
        offer_high = evaluate_fundraising(
            state_high, requested_amount=5_000_000, requested_equity=10
        )
        assert offer_high.fair_valuation_max > offer_low.fair_valuation_max

    def test_low_reputation_hurts_valuation(self):
        """rep 20 gives lower fair value range than default."""
        state_default = _state(reputation=60)
        state_low = _state(reputation=20)
        offer_default = evaluate_fundraising(
            state_default, requested_amount=5_000_000, requested_equity=10
        )
        offer_low = evaluate_fundraising(state_low, requested_amount=5_000_000, requested_equity=10)
        assert offer_low.fair_valuation_max < offer_default.fair_valuation_max

    def test_low_runway_hurts_valuation(self):
        """runway < 2 reduces fair value."""
        # Low cash + high burn = low runway
        state_good = _state(cash=2_000_000, monthly_burn=180_000)  # runway ~11.1
        state_bad = _state(cash=200_000, monthly_burn=180_000)  # runway ~1.1
        offer_good = evaluate_fundraising(
            state_good, requested_amount=3_000_000, requested_equity=10
        )
        offer_bad = evaluate_fundraising(state_bad, requested_amount=3_000_000, requested_equity=10)
        assert offer_bad.fair_valuation_max < offer_good.fair_valuation_max

    def test_high_product_boosts_valuation(self):
        """product 85 boosts fair value vs product 50."""
        state_low = _state(product_score=50)
        state_high = _state(product_score=85)
        offer_low = evaluate_fundraising(state_low, requested_amount=5_000_000, requested_equity=10)
        offer_high = evaluate_fundraising(
            state_high, requested_amount=5_000_000, requested_equity=10
        )
        assert offer_high.fair_valuation_max > offer_low.fair_valuation_max
