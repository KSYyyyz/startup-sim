"""Event engine: triggers narrative events based on state transitions.

Three event types:
- runway_warning: cash runway drops to <= 3 from above 3
- board_coup_risk: equity < 34, board < 50, MRR growth < 5%
- product_breakthrough: product_score crosses 75 threshold upward

Phase 1C enhancements:
- Event priority: critical > high > medium > positive > low
- Event dedup: same type won't trigger again once already triggered
- Event stacking: multiple events can fire in same turn, deltas accumulate
"""

from __future__ import annotations

from typing import List, Optional, Set

from src.core.models import CompanyState, GameEvent, StateDelta
from src.core.difficulty import Difficulty, get_difficulty


# ── Priority constants ────────────────────────────────────────────────────────

EVENT_PRIORITY = {
    "runway_warning": 1,       # critical
    "board_coup_risk": 1,      # critical
    "product_breakthrough": 3,  # positive
}

# Priority names for display
PRIORITY_NAMES = {
    1: "critical",
    2: "high",
    3: "positive",
    4: "low",
}


class EventEngine:
    """Evaluates game state transitions and triggers narrative events."""

    def __init__(self, difficulty: Difficulty = None):
        self._prev_state: Optional[CompanyState] = None
        self._triggered_events: Set[str] = set()  # events already fired this session
        self._difficulty = difficulty or get_difficulty("normal")
        self._runway_warning_delay_counter: int = 0

    def set_previous_state(self, state: CompanyState) -> None:
        """Store the state before this turn's delta was applied, for comparison."""
        self._prev_state = state

    def reset_triggered(self) -> None:
        """Reset the set of already-triggered events (for a new session)."""
        self._triggered_events.clear()

    def evaluate(self, current: CompanyState) -> List[GameEvent]:
        """Evaluate the current state (possibly against previous state) and return
        a list of triggered GameEvent objects.

        Events can stack — multiple events may fire in the same turn.
        Events that have already been triggered are skipped (dedup).
        Events are sorted by priority (most critical first).
        """
        events: List[GameEvent] = []

        # Event 1: runway_warning (priority: critical)
        if "runway_warning" not in self._triggered_events:
            if current.runway_months <= 3.0 and (
                self._prev_state is None or self._prev_state.runway_months > 3.0
            ):
                # Easy mode delays the warning by N turns
                delay_turns = self._difficulty.runway_warning_delay_turns
                if delay_turns > 0 and self._runway_warning_delay_counter < delay_turns:
                    self._runway_warning_delay_counter += 1
                else:
                    self._triggered_events.add("runway_warning")
                    events.append(GameEvent(
                        event_type="runway_warning",
                        description=(
                            f"⚠️ 现金跑道仅剩 {current.runway_months:.1f} 个月！"
                            f"投资者开始担忧，团队士气受挫。"
                        ),
                        delta=StateDelta(
                            team_morale=-5,
                            reputation=-2,
                            reasons=["现金跑道降至3个月以下，触发 runway_warning"],
                        ),
                    ))

        # Event 2: board_coup_risk (priority: critical)
        if "board_coup_risk" not in self._triggered_events:
            mrr_growth = getattr(current, 'mrr_growth_rate', 0.0) or 0.0
            equity_threshold = self._difficulty.board_coup_equity_threshold
            board_threshold = self._difficulty.board_coup_board_threshold
            if (current.founder_equity < equity_threshold
                    and current.board_control < board_threshold
                    and mrr_growth < 0.05):
                self._triggered_events.add("board_coup_risk")
                events.append(GameEvent(
                    event_type="board_coup_risk",
                    description=(
                        f"🔴 董事会危机！创始人股权仅 {current.founder_equity}%，"
                        f"董事会控制力 {current.board_control}%，"
                        f"MRR增长率仅 {mrr_growth*100:.1f}%。"
                        f"董事会开始讨论更换CEO。"
                    ),
                    delta=StateDelta(
                        team_morale=-10,
                        reputation=-5,
                        reasons=[f"股权<{equity_threshold}%且董事会<{board_threshold}%且MRR增长率<5%，触发 board_coup_risk"],
                    ),
                ))

        # Event 3: product_breakthrough (priority: positive)
        if "product_breakthrough" not in self._triggered_events:
            if current.product_score >= 75 and (
                self._prev_state is None or self._prev_state.product_score < 75
            ):
                self._triggered_events.add("product_breakthrough")
                events.append(GameEvent(
                    event_type="product_breakthrough",
                    description=(
                        f"🚀 产品突破！产品评分达到 {current.product_score}，"
                        f"市场反响热烈，MRR增长5万元，声誉大幅提升。"
                    ),
                    delta=StateDelta(
                        reputation=8,
                        mrr=50_000,
                        reasons=["产品评分突破75，触发 product_breakthrough"],
                    ),
                ))

        # Sort by priority: critical first
        events.sort(key=lambda e: EVENT_PRIORITY.get(e.event_type, 4))

        return events

    def apply_event_deltas(self, state: CompanyState, events: List[GameEvent]) -> CompanyState:
        """Apply all event deltas to state and return the new state.

        Events can stack — all event deltas are accumulated and applied.
        Uses StateDelta accumulation to combine all event effects.
        """
        from src.core.state_guard import apply_delta

        current = state
        for event in events:
            current = apply_delta(current, event.delta)
        return current
