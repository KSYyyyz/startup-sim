"""StateGuard: validates and sanitizes state changes before they are applied.

Rules:
- MAX_ACTIONS_PER_TURN (default 5) actions per turn
- Total action budget cannot exceed available cash
- When runway < 2 months, forbid high-risk marketing spend
- Single-month cash change <= 65% of previous cash
- product_score delta <= 18 per turn
- team_morale delta <= 15 per turn
- All values clamped to [0, 100] for percentage fields, [0, +inf) for cash/users/mrr
"""

from __future__ import annotations

from config import MAX_ACTIONS_PER_TURN
from src.core.models import ActionPlan, ActionType, CompanyState, StateDelta


class StateGuardError(Exception):
    """Raised when an action plan violates guard rules."""

    pass


def validate_action_plan(plan: ActionPlan, state: CompanyState) -> None:
    """Validate that an action plan is legal for the current state.

    Raises StateGuardError with detailed Chinese error messages including
    what went wrong, current limits, how to fix, and copiable example inputs.
    """
    # Rule 1: Max MAX_ACTIONS_PER_TURN actions
    if len(plan.actions) > MAX_ACTIONS_PER_TURN:
        raise StateGuardError(
            f"❌ 每回合最多 {MAX_ACTIONS_PER_TURN} 个决策，"
            f"当前输入了 {len(plan.actions)} 个。\n"
            f"💡 请合并相关操作或减少决策数量。\n"
            f"📝 示例：把「招人研发营销」合并为「花10万研发产品，花5万做营销」"
        )

    # Rule 2: total budget of non-fundraising actions <= cash + fundraising inflow
    # Fundraising cash arrives in the same turn, so it's available for spending.
    total_budget = sum(a.budget for a in plan.actions if a.type != ActionType.FUNDRAISING)
    fundraising_inflow = sum(
        a.fundraise_amount
        for a in plan.actions
        if a.type == ActionType.FUNDRAISING and a.fundraise_amount > 0 and a.equity_offered > 0
    )
    available_cash = state.cash + fundraising_inflow
    if total_budget > available_cash:
        spend_w = total_budget // 10000
        cash_w = state.cash // 10000
        fundraising_w = fundraising_inflow // 10000
        deficit_w = (total_budget - available_cash) // 10000

        msg = f"❌ 预算超限：本回合非融资支出 {spend_w} 万，" f"但可用现金仅 {cash_w} 万"
        if fundraising_w > 0:
            msg += f"（含本回合融资到账 {fundraising_w} 万）"
        msg += f"，缺口 {deficit_w} 万。\n"

        # How to fix
        msg += "\n💡 解决方法（选一种）：\n"
        msg += f"  1) 降低预算到 {available_cash//10000} 万以内\n"
        if state.founder_equity >= 75:
            msg += "  2) 增加融资额度，出让更多股权换取现金\n"
        msg += "  3) 减少本回合投入，分多回合执行\n"

        # Example inputs — dynamic based on state
        examples = []

        # Always: scaled-down version
        safe_budget = max(1, available_cash // 3) // 10000
        examples.append(f"「花{safe_budget}万研发产品」")

        # If enough equity, fundraising option
        if state.founder_equity >= 75:
            fund_amount = (deficit_w + 5) * 100 if deficit_w > 0 else 300
            examples.append(f"「融资{fund_amount}万出让8%股权，花{safe_budget}万研发产品」")

        # Marketing option if product is decent
        if state.product_score >= 40:
            examples.append(f"「花{safe_budget}万做营销推广」")

        # Cut spending option
        if deficit_w > 5:
            cut_budget = max(1, available_cash // 4) // 10000
            examples.append(f"「花{cut_budget}万研发产品，暂停营销控制支出」")

        if examples:
            msg += "\\n📝 可复制输入（选一条试试）：\\n"
            for i, ex in enumerate(examples[:3], 1):
                msg += f"  {i}) {ex}\\n"

        raise StateGuardError(msg)

    # Rule 3: runway < 2 months → no high-risk marketing
    if state.runway_months < 2:
        for action in plan.actions:
            if action.type == "marketing" and action.risk_level == "high":
                runway = state.runway_months
                raise StateGuardError(
                    f"❌ 跑道仅 {runway:.1f} 个月，禁止高风险营销支出。\n"
                    f"💡 跑道不足2个月时，生存是第一优先级。\n"
                    f"📝 请改用低风险营销，或优先融资/削减开支：\n"
                    f"  「花1万做基础营销」\n"
                    f"  「融资300万出让8%股权」"
                )


def sanitize_delta(delta: StateDelta, state_before: CompanyState) -> StateDelta:
    """Sanitize a StateDelta to ensure no single-turn change exceeds limits.

    Returns a new (possibly modified) StateDelta.

    P0-2: Cash outflow capped at -65% of previous cash, but cash inflow
    from fundraising is never capped. Fundraising cash is tracked via
    delta.fundraising_cash and excluded from the cap.
    """
    # P0-2: Cash outflow cap at -65% of previous cash.
    # Fundraising inflow passes through uncapped.
    prev_cash = max(state_before.cash, 1)
    max_cash_delta = int(prev_cash * 0.65)

    fundraising_inflow = delta.fundraising_cash
    spending_cash = delta.cash - fundraising_inflow
    if spending_cash < 0:
        spending_cash = max(spending_cash, -max_cash_delta)
    cash_out = fundraising_inflow + spending_cash

    return StateDelta(
        cash=cash_out,
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
        fundraising_cash=delta.fundraising_cash,
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
