"""StateGuard: validates and sanitizes state changes before they are applied.

Rules:
- Max 2 actions per turn
- Total action budget cannot exceed available cash
- When runway < 2 months, forbid high-risk marketing spend
- Single-month cash change <= 65% of previous cash
- product_score delta <= 18 per turn
- team_morale delta <= 15 per turn
- All values clamped to [0, 100] for percentage fields, [0, +inf) for cash/users/mrr
"""

from __future__ import annotations

from src.core.models import ActionPlan, ActionType, CompanyState, StateDelta
from config import MAX_ACTIONS_PER_TURN


class StateGuardError(Exception):
    """Raised when an action plan violates guard rules."""
    pass


def validate_action_plan(plan: ActionPlan, state: CompanyState) -> None:
    """Validate that an action plan is legal for the current state.

    Raises StateGuardError on violation.
    """
    # Rule 1: max 2 actions
    if len(plan.actions) > MAX_ACTIONS_PER_TURN:
        raise StateGuardError(
            f"Too many actions: {len(plan.actions)} (max {MAX_ACTIONS_PER_TURN})"
        )

    # Rule 2: total budget of non-fundraising actions <= cash
    total_budget = sum(a.budget for a in plan.actions if a.type != ActionType.FUNDRAISING)
    if total_budget > state.cash:
        raise StateGuardError(
            f"Total budget {total_budget} exceeds available cash {state.cash}"
        )

    # Rule 3: runway < 2 months → no high-risk marketing
    if state.runway_months < 2:
        for action in plan.actions:
            if action.type == "marketing" and action.risk_level == "high":
                raise StateGuardError(
                    f"Runway is only {state.runway_months:.1f} months — "
                    f"high-risk marketing spend is forbidden"
                )


def sanitize_delta(delta: StateDelta, state_before: CompanyState) -> StateDelta:
    """Sanitize a StateDelta to ensure no single-turn change exceeds limits.
    Returns a new (possibly modified) StateDelta.
    """
    # Cash change: max ±65% of previous cash
    prev_cash = max(state_before.cash, 1)  # avoid div-by-zero
    max_cash_delta = int(prev_cash * 0.65)

    return StateDelta(
        cash=max(-max_cash_delta, min(max_cash_delta, delta.cash)),
        monthly_burn=delta.monthly_burn,
        mrr=delta.mrr,
        users=delta.users,
        product_score=max(-18, min(18, delta.product_score)),
        team_morale=max(-15, min(15, delta.team_morale)),
        founder_equity=delta.founder_equity,
        board_control=delta.board_control,
        market_share=delta.market_share,
        reputation=delta.reputation,
        employee_count=delta.employee_count,
        price=delta.price,
        valuation=delta.valuation,
        reasons=delta.reasons,
    )


def apply_delta(state: CompanyState, delta: StateDelta) -> CompanyState:
    """Apply a delta to a state, then clamp all values to legal ranges."""
    new = CompanyState(
        month=state.month,
        cash=max(0, state.cash + delta.cash),
        monthly_burn=max(0, state.monthly_burn + delta.monthly_burn),
        mrr=max(0, state.mrr + delta.mrr),
        users=max(0, state.users + delta.users),
        product_score=max(0, min(100, state.product_score + delta.product_score)),
        team_morale=max(0, min(100, state.team_morale + delta.team_morale)),
        founder_equity=max(0, min(100, state.founder_equity + delta.founder_equity)),
        board_control=max(0, min(100, state.board_control + delta.board_control)),
        market_share=max(0, min(100, state.market_share + delta.market_share)),
        reputation=max(0, min(100, state.reputation + delta.reputation)),
        employee_count=max(0, state.employee_count + delta.employee_count),
        price=max(0, state.price + delta.price),
        valuation=max(0, state.valuation + delta.valuation),
    )
    return new


def clamp_state(state: CompanyState) -> CompanyState:
    """Ensure all state values are within legal bounds."""
    return CompanyState(
        month=max(1, min(12, state.month)),
        cash=max(0, state.cash),
        monthly_burn=max(0, state.monthly_burn),
        mrr=max(0, state.mrr),
        users=max(0, state.users),
        product_score=max(0, min(100, state.product_score)),
        team_morale=max(0, min(100, state.team_morale)),
        founder_equity=max(0, min(100, state.founder_equity)),
        board_control=max(0, min(100, state.board_control)),
        market_share=max(0, min(100, state.market_share)),
        reputation=max(0, min(100, state.reputation)),
        employee_count=max(0, state.employee_count),
        price=max(0, state.price),
        valuation=max(0, state.valuation),
    )
