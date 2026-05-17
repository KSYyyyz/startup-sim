"""Fundraising valuation engine — evaluates fundraising offers with realistic
valuation logic, counter-offers, and risk warnings.

Uses dataclasses (not Pydantic) to avoid circular imports with models.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.core.models import CompanyState


@dataclass
class FundraisingOffer:
    """Result of evaluating a fundraising request."""

    requested_amount: int  # 玩家要求的融资额
    requested_equity: float  # 玩家出价的股权%
    implied_valuation: int  # 隐含估值 = amount / (equity/100)
    fair_valuation_min: int  # 合理估值下限
    fair_valuation_max: int  # 合理估值上限
    suggested_amount: int  # 反报价金额
    suggested_equity: float  # 反报价股权
    investor_response: str  # 投资人反馈文本
    accepted: bool  # 是否接受
    accepted_amount: int  # 实际到账金额
    accepted_equity: float  # 实际出让股权
    reason: str  # 原因说明
    warnings: list = field(default_factory=list)


def calculate_fair_valuation(state: CompanyState) -> int:
    """Calculate the midpoint fair valuation based on company metrics.

    Used for both the status display and the fundraising negotiation baseline.
    Formula: base = max(mrr*60, users*3000, 3,000,000), then product/reputation/runway modifiers.
    """
    base_valuation = max(state.mrr * 60, state.users * 3000, 3_000_000)

    modifier = 1.0
    if state.product_score >= 80:
        modifier *= 1.30
    elif state.product_score >= 60:
        modifier *= 1.15
    elif state.product_score < 40:
        modifier *= 0.80

    if state.reputation >= 80:
        modifier *= 1.15
    elif state.reputation >= 50:
        pass
    elif state.reputation >= 30:
        modifier *= 0.90
    else:
        modifier *= 0.75

    runway = state.runway_months
    if runway < 2:
        modifier *= 0.80
    elif runway > 6:
        modifier *= 1.10

    return int(base_valuation * modifier)


def evaluate_fundraising(
    state: CompanyState,
    requested_amount: int,
    requested_equity: float,
) -> FundraisingOffer:
    """Evaluate a fundraising request against the company's current state.

    Valuation formula:
        base_valuation = max(mrr * 60, users * 3000, 3,000,000)
        Then apply modifiers for product_score, reputation, and runway.

    Returns a FundraisingOffer with acceptance decision, counter-offer, and warnings.
    """
    base_valuation = calculate_fair_valuation(state)

    fair_valuation_min = int(base_valuation * 0.7)
    fair_valuation_max = int(base_valuation * 1.3)

    # ── Implied valuation from player's offer ─────────────────────────────
    if requested_equity <= 0:
        # Can't compute implied valuation; reject outright
        return FundraisingOffer(
            requested_amount=requested_amount,
            requested_equity=requested_equity,
            implied_valuation=0,
            fair_valuation_min=fair_valuation_min,
            fair_valuation_max=fair_valuation_max,
            suggested_amount=0,
            suggested_equity=0.0,
            investor_response="投资人无法评估0%股权的报价，请重新出价。",
            accepted=False,
            accepted_amount=0,
            accepted_equity=0.0,
            reason="股权出价无效（≤0%）。",
        )

    implied_valuation = int(requested_amount / (requested_equity / 100))

    # ── Decision logic ────────────────────────────────────────────────────
    # Case 1: Severely overvalued → REJECTED
    if implied_valuation > fair_valuation_max * 1.5:
        suggested_amount = min(requested_amount, int(fair_valuation_max * 0.12))
        suggested_equity = 0.0
        if fair_valuation_max > 0:
            suggested_equity = round(suggested_amount / fair_valuation_max * 100, 1)

        overvaluation_pct = int((implied_valuation / fair_valuation_max - 1) * 100)
        investor_msg = (
            f"投资人认为公司估值过高。你报价的隐含估值是{implied_valuation // 10000}万，"
            f"但合理估值上限为{fair_valuation_max // 10000}万（溢价{overvaluation_pct}%）。"
        )
        return FundraisingOffer(
            requested_amount=requested_amount,
            requested_equity=requested_equity,
            implied_valuation=implied_valuation,
            fair_valuation_min=fair_valuation_min,
            fair_valuation_max=fair_valuation_max,
            suggested_amount=suggested_amount,
            suggested_equity=suggested_equity,
            investor_response=investor_msg,
            accepted=False,
            accepted_amount=0,
            accepted_equity=0.0,
            reason=f"估值过高（{implied_valuation//10000}万 > 上限{fair_valuation_max//10000}万×1.5），投资人拒绝。",
        )

    # Case 2: Severely undervalued → WARNING but ACCEPT
    if implied_valuation < fair_valuation_min * 0.5:
        undervaluation_pct = int((1 - implied_valuation / fair_valuation_min) * 100)
        warnings_list = [
            f"⚠️ 严重贱卖：估值仅{implied_valuation//10000}万，低于合理下限"
            f"{fair_valuation_min//10000}万的50%。董事会控制权面临风险。"
        ]
        return FundraisingOffer(
            requested_amount=requested_amount,
            requested_equity=requested_equity,
            implied_valuation=implied_valuation,
            fair_valuation_min=fair_valuation_min,
            fair_valuation_max=fair_valuation_max,
            suggested_amount=requested_amount,
            suggested_equity=requested_equity,
            investor_response=(
                f"投资人乐于接受低价入股。但你以{implied_valuation//10000}万估值"
                f"出让{requested_equity}%股权，低于合理下限{undervaluation_pct}%。"
            ),
            accepted=True,
            accepted_amount=requested_amount,
            accepted_equity=requested_equity,
            reason=f"估值偏低但投资人接受（{implied_valuation//10000}万）。注意股权稀释风险。",
            warnings=warnings_list,
        )

    # Case 3: Reasonable range → ACCEPT
    return FundraisingOffer(
        requested_amount=requested_amount,
        requested_equity=requested_equity,
        implied_valuation=implied_valuation,
        fair_valuation_min=fair_valuation_min,
        fair_valuation_max=fair_valuation_max,
        suggested_amount=requested_amount,
        suggested_equity=requested_equity,
        investor_response=(
            f"投资人对{implied_valuation//10000}万估值表示认可，"
            f"同意以{requested_amount//10000}万换取{requested_equity}%股权。"
        ),
        accepted=True,
        accepted_amount=requested_amount,
        accepted_equity=requested_equity,
        reason=f"估值合理（{implied_valuation//10000}万），投资人接受。",
    )
