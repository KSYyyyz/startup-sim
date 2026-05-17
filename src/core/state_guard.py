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
from src.core.models import ActionPlan, ActionType, CompanyState, CrisisGuidance, StateDelta


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


def generate_crisis_guidance(
    crisis_type: str,
    state: CompanyState,
    extra_info: dict | None = None,
) -> CrisisGuidance:
    """Alpha 1.9: Generate crisis explanation and copiable recovery inputs.

    Covers: budget_overrun, fundraising_rejected, runway_critical,
    cash_below_burn, equity_warning.
    """
    info = extra_info or {}
    cash_w = state.cash // 10000
    burn_w = state.monthly_burn // 10000
    runway = state.runway_months
    equity = state.founder_equity
    product = state.product_score

    if crisis_type == "budget_overrun":
        available = info.get("available_cash", state.cash)
        avail_w = available // 10000
        safe_w = max(1, available // 3) // 10000
        recovery = [
            f"花{safe_w}万研发产品",
        ]
        if equity >= 75:
            recovery.append(
                f"融资{max(200, (state.monthly_burn * 6) // 10000)}万出让8%股权，花{safe_w}万研发产品"
            )
        if product >= 40:
            recovery.append(f"花{safe_w}万做营销推广")
        return CrisisGuidance(
            crisis_type="budget_overrun",
            explanation=(
                f"预算超限：你的非融资支出超过了可用现金（{avail_w}万）。"
                f"在跑道{runway:.1f}个月的情况下，必须控制支出节奏。"
            ),
            severity="high",
            recovery_inputs=recovery[:3],
        )

    elif crisis_type == "fundraising_rejected":
        rejection_reason = info.get("reason", "估值预期与公司实际表现不匹配")
        investor_msg = info.get("investor_response", "提升核心指标后再来")
        recovery = [
            f"花{max(1, cash_w // 3)}万研发产品",
        ]
        if product < 50:
            recovery.append(f"花{max(1, cash_w // 5)}万研发产品，专注提升产品竞争力")
        if state.users < 100:
            recovery.append(f"花{max(1, cash_w // 4)}万做营销，扩大用户基础后再融资")
        return CrisisGuidance(
            crisis_type="fundraising_rejected",
            explanation=(
                f"融资被拒：{rejection_reason}。投资人反馈：{investor_msg}。"
                f"当前产品分{product}、MRR{state.mrr//10000}万、用户{state.users}人——"
                f"这些指标还不足以支撑你的估值预期。"
            ),
            severity="high",
            recovery_inputs=recovery[:3],
        )

    elif crisis_type == "runway_critical":
        recovery = [
            f"融资{max(200, (state.monthly_burn * 6) // 10000)}万出让10%股权",
            f"花{max(1, cash_w // 5)}万研发产品，暂停其他所有支出",
        ]
        if equity < 60:
            recovery.append("暂停所有非核心支出，寻求被收购或过桥贷款")
        return CrisisGuidance(
            crisis_type="runway_critical",
            explanation=(
                f"跑道危急：现金仅够{runway:.1f}个月。"
                f"每月消耗{burn_w}万，这意味着你只有{runway:.1f}个月的时间找到出路。"
                f"SaaS公司融资通常需要2-3个月——时间已经不多了。"
            ),
            severity="critical",
            recovery_inputs=recovery[:3],
        )

    elif crisis_type == "cash_below_burn":
        recovery = [
            f"融资{max(200, (state.monthly_burn * 6) // 10000)}万出让8%股权",
            f"花{max(1, cash_w // 4)}万研发产品，严格控制其他支出",
        ]
        return CrisisGuidance(
            crisis_type="cash_below_burn",
            explanation=(
                f"现金不足支撑当月运营：当前现金{cash_w}万，月消耗{burn_w}万。"
                f"如果不采取行动，公司将在本月内耗尽现金。"
            ),
            severity="critical",
            recovery_inputs=recovery[:2],
        )

    elif crisis_type == "equity_warning":
        recovery = [
            f"花{max(1, cash_w // 4)}万研发产品，暂不融资保护股权",
        ]
        if state.product_score >= 50 and state.mrr >= 50000:
            recovery.append("专注提升MRR到30万，用业绩支撑更高估值再融资")
        recovery.append("考虑债权融资或可转债，代替股权融资")
        return CrisisGuidance(
            crisis_type="equity_warning",
            explanation=(
                f"股权稀释警告：创始人股权仅剩{equity}%。"
                f"再融资一轮可能让你失去对公司重大事项的否决权（低于34%）。"
                f"现在需要更聪明地使用资金，而不是简单地用股权换钱。"
            ),
            severity="medium",
            recovery_inputs=recovery[:3],
        )

    # Default fallback
    return CrisisGuidance(
        crisis_type=crisis_type,
        explanation=f"当前{state.month}月，需要关注经营状况。",
        severity="medium",
        recovery_inputs=[f"花{max(1, cash_w // 3)}万研发产品"],
    )
