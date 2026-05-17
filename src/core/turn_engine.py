"""Turn engine: orchestrates the full turn processing pipeline.

Flow per turn:
1. action_parser.parse(raw_input) → ActionPlan
2. board members speak(state, plan) → board_feedback
3. state_guard.validate_action_plan(plan, state)
4. simulate(plan, state) → StateDelta (simple rules)
5. competitor agents respond(state, plan) → competitor_moves
6. customer agent evaluates(state, plan, competitor_moves) → customer_response
7. Merge competitor & customer deltas into raw_delta
8. state_guard.sanitize_delta(delta, state)
9. state_guard.apply_delta(state, delta) → new state
10. event_engine.evaluate(new_state) → events
11. event_engine.apply_event_deltas(state, events) → final state
12. ending_evaluator.evaluate(final_state) → ending
13. Save snapshot, action, events → TurnResult

All DB writes are wrapped in repository.transaction().
"""

from __future__ import annotations

from src.core.difficulty import Difficulty, get_difficulty
from src.core.models import (
    ActionPlan, CompanyState, EndingType, GameEvent, StateDelta, TurnResult,
)
from src.core.action_parser import parse_multi
from src.core.state_guard import (
    validate_action_plan, sanitize_delta, apply_delta,
)
from src.core.event_engine import EventEngine
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending
from src.agents import CFO, CTO, COO, InvestorDirector
from src.agents.board import generate_board_minutes
from src.agents.competitors import KuaiDaTech, LingxiCSCloud, get_competitor_summary
from src.agents.customers import CustomerAgent
from src.db import repository


def _simulate(plan: ActionPlan, state: CompanyState) -> StateDelta:
    """Simple rule-based simulation: compute delta from action plan.

    Rules:
    - product action: budget//80k + employee_count//3 + team_morale//10 → +product_score, cost deducted
    - marketing action: each 10,000 budget → reputation + burn; users/MRR via CustomerAgent CAC (CAC=800)
    - team action: each 10,000 budget → +2 team_morale, burn +2,000, cost deducted
    - organic: +1 product_score/turn from team learning (min 5 employees)
    - fundraising action: if fundraise_amount>0 & equity_offered>0:
        cash += fundraise_amount, equity -= equity_offered,
        board_control -= equity_offered, valuation = post_money
        (legacy fallback: budget*2 to cash, -5 equity, -3 board)
    - strategy action: each 10,000 budget → +1 market_share, +3 reputation, cost deducted
    """
    delta = StateDelta()

    for action in plan.actions:
        budget = action.budget
        # Fundraising with explicit fundraise_amount and equity_offered doesn't need budget
        if budget <= 0 and not (
            action.type == "fundraising"
            and action.fundraise_amount > 0
            and action.equity_offered > 0
        ):
            continue

        # All actions consume budget (fundraising with budget=0 doesn't subtract)
        if budget > 0:
            delta.cash -= budget

        if action.type == "product":
            product_gain = budget // 80_000 + state.employee_count // 3 + state.team_morale // 10
            delta.product_score += max(1, product_gain)
            delta.monthly_burn += budget // 30  # dev costs increase burn
        elif action.type == "marketing":
            delta.monthly_burn += budget // 12
            delta.reputation += max(0, budget // 50_000)
            # User growth and MRR handled by CustomerAgent (CAC-based retention)
        elif action.type == "team":
            delta.team_morale += max(1, budget // 5_000)
            delta.monthly_burn += budget // 5  # team costs increase burn (lowered for Alpha 1.2)
        elif action.type == "fundraising":
            if action.fundraise_amount > 0 and action.equity_offered > 0:
                delta.cash += action.fundraise_amount
                delta.fundraising_cash += action.fundraise_amount  # track for sanitize cap exemption
                delta.founder_equity -= int(action.equity_offered)
                delta.board_control -= int(action.equity_offered)
                post_money = int(action.fundraise_amount / (action.equity_offered / 100))
                delta.valuation = post_money
                delta.reasons.append(
                    f"融资{action.fundraise_amount}出让{action.equity_offered}%股权"
                )
            else:
                # Legacy: no specific fundraising params, use budget * 2
                delta.cash += budget * 2
                delta.founder_equity -= 5
                delta.board_control -= 3
                delta.reputation += max(0, budget // 100_000)
        elif action.type == "strategy":
            delta.market_share += max(0, budget // 100_000)
            delta.reputation += max(1, budget // 20_000)

        delta.reasons.append(
            f"{action.type.value}: 预算={budget}, 风险={action.risk_level.value}"
        )

    # Monthly burn is always applied
    delta.cash -= state.monthly_burn
    delta.reasons.append(f"月度消耗: -{state.monthly_burn}")

    # Natural MRR churn (5% monthly)
    if state.mrr > 0:
        churn = max(1, state.mrr // 20)
        delta.mrr -= churn
        delta.reasons.append(f"MRR自然流失: -{churn}")

    # Organic product improvement from team learning (Alpha 1.2)
    if state.employee_count >= 5:
        delta.product_score += 1
        delta.reasons.append("团队自然学习: 产品分+1")

    return delta


def _merge_competitor_customer_delta(
    delta: StateDelta,
    competitor_moves: list,
    customer_response: dict,
) -> StateDelta:
    """Merge competitor and customer effects into the main state delta."""
    # Apply competitor deltas
    for move in competitor_moves:
        comp_delta = move.get("delta", {})
        delta.market_share += comp_delta.get("market_share", 0)
        delta.users += comp_delta.get("users", 0)
        delta.mrr += comp_delta.get("mrr", 0)
        delta.reputation += comp_delta.get("reputation", 0)
        if comp_delta:
            delta.reasons.append(
                f"竞品{move.get('name', '未知')}: {move.get('action', '')}"
            )

    # Apply customer response
    growth = customer_response.get("growth_change", 0)
    revenue = customer_response.get("revenue_change", 0)
    delta.users += growth
    delta.mrr += revenue
    if growth or revenue:
        delta.reasons.append(
            f"客户响应: 用户{'增长' if growth >= 0 else '减少'}{growth}, "
            f"收入变化{revenue}"
        )

    return delta


class TurnEngine:
    """Orchestrates one full turn of the game."""

    def __init__(self, session_id: int, difficulty: Difficulty = None):
        self.session_id = session_id
        self.difficulty = difficulty or get_difficulty("normal")
        self.event_engine = EventEngine(difficulty=self.difficulty)
        self.board_members = [
            CFO(),
            CTO(),
            COO(),
            InvestorDirector(),
        ]
        self.competitors = [
            KuaiDaTech(aggression_multiplier=self.difficulty.competitor_aggression),
            LingxiCSCloud(aggression_multiplier=self.difficulty.competitor_aggression),
        ]
        self.customer_agent = CustomerAgent(
            churn_multiplier=self.difficulty.customer_churn_multiplier,
        )

    def process_turn(self, raw_input: str) -> TurnResult:
        """Process one turn from raw player input. Returns TurnResult."""
        # Load current state
        state_before = repository.load_state(self.session_id)
        month = state_before.month

        # Step 1: Parse input (multi-segment parser)
        action_plan = parse_multi(raw_input)

        # Step 2: Collect board feedback (董事会会议发言)
        board_feedback: dict[str, str] = {}
        for member in self.board_members:
            board_feedback[member.name] = member.speak(state_before, action_plan)

        # Step 3: Validate
        validate_action_plan(action_plan, state_before)

        # Step 4: Simulate (player actions)
        delta = _simulate(action_plan, state_before)

        # Step 5a: Competitor periodic actions (independent initiative)
        competitor_moves = []
        for comp in self.competitors:
            periodic_move = comp.periodic_action(state_before)
            if periodic_move:
                competitor_moves.append(periodic_move)

        # Step 5b: Competitor agents respond to player
        for comp in self.competitors:
            move = comp.respond(state_before, action_plan)
            competitor_moves.append(move)

        # Step 6: Customer agent evaluates
        customer_response = self.customer_agent.evaluate(
            state_before, action_plan, competitor_moves
        )

        # Step 7: Merge competitor & customer effects into delta
        delta = _merge_competitor_customer_delta(delta, competitor_moves, customer_response)

        # Step 8: Sanitize delta
        delta = sanitize_delta(delta, state_before)

        # Step 9: Apply delta
        state_after_delta = apply_delta(state_before, delta)

        # Step 10: Evaluate events (need previous state for threshold crossing)
        self.event_engine.set_previous_state(state_before)
        events = self.event_engine.evaluate(state_after_delta)

        # Step 11: Apply event deltas
        state_after = self.event_engine.apply_event_deltas(state_after_delta, events)
        state_after.month = month + 1  # advance month

        # Step 12: Evaluate ending
        ending = eval_ending(state_after)
        ending_desc = describe_ending(ending, state_after) if ending and ending != EndingType.NONE else ""

        # Step 13: Persist everything in a transaction
        snapshots_saved = 0
        with repository.transaction() as conn:
            repository.save_state(self.session_id, state_after, conn=conn)

            status = "active"
            if ending and ending != EndingType.NONE:
                status = ending.value
            repository.update_session_month(
                self.session_id, state_after.month, status, conn=conn,
            )

            repository.save_snapshot(
                self.session_id, state_after.month, state_after, conn=conn,
            )
            snapshots_saved = 1

            repository.save_action(
                self.session_id, month,
                raw_input,
                action_plan.model_dump_json(),
                delta.model_dump_json(),
                conn=conn,
            )

            for event in events:
                repository.save_event(
                    self.session_id, month,
                    event.event_type, event.description,
                    "high" if event.event_type == "board_coup_risk" else "medium",
                    event.delta.model_dump_json(),
                    conn=conn,
                )

        return TurnResult(
            month=month,
            action_plan=action_plan,
            state_before=state_before,
            state_after=state_after,
            delta=delta,
            events=events,
            board_feedback=board_feedback,
            competitor_moves=competitor_moves,
            customer_response=customer_response,
            ending=ending or EndingType.NONE,
            ending_description=ending_desc,
            snapshots_saved=snapshots_saved,
        )

    @classmethod
    def process_turn_raw(cls, state: CompanyState, raw_input: str, difficulty=None) -> TurnResult:
        """Stateless turn: no DB, no session. For testing and batch simulation."""
        diff = difficulty or get_difficulty("normal")
        engine = cls(session_id=0, difficulty=diff)  # dummy session_id
        state_before = state
        month = state_before.month

        action_plan = parse_multi(raw_input)

        board_feedback: dict[str, str] = {}
        for member in engine.board_members:
            board_feedback[member.name] = member.speak(state_before, action_plan)

        validate_action_plan(action_plan, state_before)

        delta = _simulate(action_plan, state_before)

        competitor_moves = []
        for c in engine.competitors:
            periodic_move = c.periodic_action(state_before)
            if periodic_move:
                competitor_moves.append(periodic_move)
        for c in engine.competitors:
            competitor_moves.append(c.respond(state_before, action_plan))

        customer_response = engine.customer_agent.evaluate(
            state_before, action_plan, competitor_moves
        )

        delta = _merge_competitor_customer_delta(delta, competitor_moves, customer_response)
        delta = sanitize_delta(delta, state_before)
        state_after_delta = apply_delta(state_before, delta)

        engine.event_engine.set_previous_state(state_before)
        events = engine.event_engine.evaluate(state_after_delta)
        state_after = engine.event_engine.apply_event_deltas(state_after_delta, events)
        state_after.month = month + 1

        ending = eval_ending(state_after)
        ending_desc = describe_ending(ending, state_after) if ending and ending != EndingType.NONE else ""

        return TurnResult(
            month=month,
            action_plan=action_plan,
            state_before=state_before,
            state_after=state_after,
            delta=delta,
            events=events,
            board_feedback=board_feedback,
            competitor_moves=competitor_moves,
            customer_response=customer_response,
            ending=ending or EndingType.NONE,
            ending_description=ending_desc,
            snapshots_saved=0,
        )


# ── Monthly Report Generator (Alpha 1.3) ────────────────────────────────────────

def generate_monthly_report(
    result: TurnResult,
    state_before: CompanyState,
    state_after: CompanyState,
    competitors: list | None = None,
) -> str:
    """Generate a formatted monthly battle report.

    Used by both CLI and Feishu output. Covers:
    - Key changes this month
    - Board disagreements
    - Competitor actions
    - Customer feedback
    - Risk alerts
    - Next-month suggestions
    """
    month = state_after.month

    lines: list[str] = []
    lines.append("")
    lines.append("#" * 64)
    lines.append(f"  📊 第{month}月度战报")
    lines.append("#" * 64)
    lines.append("")

    # ── 1. Key changes ───────────────────────────────────────────────────
    lines.append("## 📈 本月关键变化")
    lines.append("")
    changes = _compute_changes(state_before, state_after)
    for label, before, after in changes:
        direction = "↑" if after > before else ("↓" if after < before else "→")
        lines.append(f"  {label}: {before} → {after} {direction}")
    lines.append("")

    # ── 2. Board disagreements ────────────────────────────────────────────
    lines.append("## 🏛️ 董事会争议")
    lines.append("")
    if result.board_feedback:
        board_minutes = generate_board_minutes(
            state_before, result.action_plan, result.board_feedback,
        )
        # Extract just the conflict section
        for line in board_minutes.split("\n"):
            if "分歧焦点" in line or "⚡" in line:
                lines.append(f"  {line.strip()}")
        if not any("⚡" in l for l in lines[-5:]):
            lines.append("  本轮无显著争议，董事会意见基本一致。")
    else:
        lines.append("  （无董事会记录）")
    lines.append("")

    # ── 3. Competitor actions ─────────────────────────────────────────────
    lines.append("## 🎯 竞品动作")
    lines.append("")
    if result.competitor_moves:
        for move in result.competitor_moves:
            action = move.get("action", "未知")
            name = move.get("name", "未知竞品")
            narrative = move.get("narrative", "")
            lines.append(f"  [{name}] {action}")
            if narrative:
                lines.append(f"    {narrative[:120]}")
        lines.append("")
    else:
        lines.append("  本月竞品无显著动作。")
        lines.append("")

    # If competitors with state were passed, show their status
    if competitors:
        lines.append("  **竞品状态:**")
        for comp in competitors:
            lines.append(f"    {get_competitor_summary(comp)}")
        lines.append("")

    # ── 4. Customer feedback ──────────────────────────────────────────────
    lines.append("## 💬 客户反馈")
    lines.append("")
    if result.customer_response:
        narrative = result.customer_response.get("narrative", "客户群体表现平稳。")
        lines.append(f"  {narrative[:200]}")
    else:
        lines.append("  （无客户反馈数据）")
    lines.append("")

    # ── 5. Risk alerts ───────────────────────────────────────────────────
    lines.append("## ⚠️ 风险提醒")
    lines.append("")
    risks = _identify_risks(state_after)
    if risks:
        for risk in risks:
            lines.append(f"  🔴 {risk}")
    else:
        lines.append("  ✅ 暂无明显风险信号。")
    lines.append("")

    # ── 6. Next-month suggestions ─────────────────────────────────────────
    lines.append("## 💡 下月建议")
    lines.append("")
    suggestions = _generate_suggestions(state_after, result)
    for s in suggestions:
        lines.append(f"  → {s}")
    lines.append("")

    # ── Events this turn ─────────────────────────────────────────────────
    if result.events:
        lines.append("## 📢 本月事件")
        lines.append("")
        for event in result.events:
            lines.append(f"  [{event.event_type}] {event.description[:150]}")
        lines.append("")

    lines.append("#" * 64)
    return "\n".join(lines)


def _compute_changes(
    before: CompanyState, after: CompanyState,
) -> list[tuple[str, str, str]]:
    """Compute formatted key changes between two states."""
    changes: list[tuple[str, str, str]] = []

    def fmt_val(k: str, v: int) -> str:
        if k in ("cash", "mrr", "valuation", "monthly_burn"):
            return f"{v//10000}万"
        return str(v)

    fields = [
        ("现金", "cash"),
        ("MRR", "mrr"),
        ("用户", "users"),
        ("产品分", "product_score"),
        ("士气", "team_morale"),
        ("创始人股权", "founder_equity"),
        ("市场份额", "market_share"),
        ("估值", "valuation"),
        ("月消耗", "monthly_burn"),
    ]

    for label, field in fields:
        b = getattr(before, field, 0)
        a = getattr(after, field, 0)
        if b != a:
            changes.append((label, fmt_val(field, b), fmt_val(field, a)))

    return changes


def _identify_risks(state: CompanyState) -> list[str]:
    """Identify risk factors from current state."""
    risks: list[str] = []

    if state.runway_months <= 3:
        risks.append(f"现金流危急：跑道仅{state.runway_months:.1f}个月，需立即融资或大幅削减开支。")
    elif state.runway_months <= 5:
        risks.append(f"现金流紧张：跑道{state.runway_months:.1f}个月，建议启动融资准备。")

    if state.team_morale < 40:
        risks.append(f"团队士气极低（{state.team_morale}），核心员工流失风险高。")
    elif state.team_morale < 55:
        risks.append(f"团队士气偏低（{state.team_morale}），关注核心人员状态。")

    if state.founder_equity < 40:
        risks.append(f"创始人股权仅剩{state.founder_equity}%，下轮融资后可能失去控制权。")

    if state.product_score < 30:
        risks.append(f"产品分{state.product_score}太低，用户留存和口碑面临严重问题。")

    if state.market_share >= 10 and state.product_score < 40:
        risks.append("高市场份额但产品薄弱，竞品可能通过技术优势反超。")

    if state.mrr > 0 and state.mrr < 50_000 and state.month >= 6:
        risks.append(f"MRR仅{state.mrr//10000}万/月，月{state.month}未达PMF信号，投资人信心在流失。")

    return risks


def _generate_suggestions(state: CompanyState, result: TurnResult) -> list[str]:
    """Generate next-month suggestions based on current state."""
    suggestions: list[str] = []

    if state.runway_months < 4:
        suggestions.append("优先级#1：融资或大幅削减开支，活下来是第一位的。")
    elif state.runway_months < 6:
        suggestions.append("考虑启动融资准备，更新BP和投资人更新邮件。")

    if state.product_score < 40:
        suggestions.append("加大研发投入，产品是根基。建议至少连续3个月投入5万+研发。")
    elif state.product_score < 60:
        suggestions.append("产品有进步空间，建议保持研发节奏，同时开始做用户测试收集反馈。")

    if state.team_morale < 50:
        suggestions.append("团队士气需要关注：安排团建活动或期权激励，防止核心人员流失。")
    elif state.team_morale > 80:
        suggestions.append("团队状态极佳，适合推动关键里程碑或探索性项目。")

    if state.users < 100 and state.month >= 4:
        suggestions.append("用户基数偏小，建议增加营销投入或探索渠道合作加速获客。")

    if state.mrr >= 200_000 and state.product_score >= 60:
        suggestions.append("增长拐点已到：可以考虑A轮融资，为规模化扩张储备弹药。")

    if state.founder_equity < 50:
        suggestions.append("股权稀释较多，后续融资优先考虑债权或可转债，保护控制权。")

    if not suggestions:
        suggestions.append("保持当前节奏，关注竞品动态，稳扎稳打。")

    return suggestions[:5]  # cap at 5 suggestions
