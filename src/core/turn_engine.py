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
from src.core.action_parser import parse, parse_multi
from src.core.state_guard import (
    validate_action_plan, sanitize_delta, apply_delta,
)
from src.core.event_engine import EventEngine
from src.core.ending_evaluator import evaluate as eval_ending, describe_ending
from src.agents import CFO, CTO, COO, InvestorDirector
from src.agents.competitors import KuaiDaTech, LingxiCSCloud
from src.agents.customers import CustomerAgent
from src.db import repository


def _simulate(plan: ActionPlan, state: CompanyState) -> StateDelta:
    """Simple rule-based simulation: compute delta from action plan.

    Rules:
    - product action: each 10,000 budget → +1 product_score, cost deducted
    - marketing action: each 10,000 budget → +50 users, +5,000 mrr, cost deducted
    - team action: each 10,000 budget → +2 team_morale, burn +2,000, cost deducted
    - fundraising action: +budget * 2 to cash, -5 equity, cost deducted
    - strategy action: each 10,000 budget → +1 market_share, +3 reputation, cost deducted
    """
    delta = StateDelta()

    for action in plan.actions:
        budget = action.budget
        if budget <= 0:
            continue

        # All actions consume budget
        delta.cash -= budget

        if action.type == "product":
            delta.product_score += max(1, budget // 10_000)
            delta.monthly_burn += budget // 20  # dev costs increase burn
        elif action.type == "marketing":
            delta.users += budget // 200
            delta.mrr += budget // 2
            delta.monthly_burn += budget // 5
            delta.reputation += max(0, budget // 50_000)
        elif action.type == "team":
            delta.team_morale += max(1, budget // 5_000)
            delta.monthly_burn += budget // 3
        elif action.type == "fundraising":
            if action.fundraise_amount > 0 and action.equity_offered > 0:
                delta.cash += action.fundraise_amount
                delta.founder_equity -= action.equity_offered
                delta.board_control -= action.equity_offered
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

        # Step 1: Parse input
        action_plan = parse(raw_input)

        # Step 2: Collect board feedback (董事会会议发言)
        board_feedback: dict[str, str] = {}
        for member in self.board_members:
            board_feedback[member.name] = member.speak(state_before, action_plan)

        # Step 3: Validate
        validate_action_plan(action_plan, state_before)

        # Step 4: Simulate (player actions)
        delta = _simulate(action_plan, state_before)

        # Step 5: Competitor agents respond
        competitor_moves = []
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
        with repository.transaction():
            repository.save_state(self.session_id, state_after)

            status = "active"
            if ending and ending != EndingType.NONE:
                status = ending.value
            repository.update_session_month(self.session_id, state_after.month, status)

            repository.save_snapshot(self.session_id, state_after.month, state_after)
            snapshots_saved = 1

            repository.save_action(
                self.session_id, month,
                raw_input,
                action_plan.model_dump_json(),
                delta.model_dump_json(),
            )

            for event in events:
                repository.save_event(
                    self.session_id, month,
                    event.event_type, event.description,
                    "high" if event.event_type == "board_coup_risk" else "medium",
                    event.delta.model_dump_json(),
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
