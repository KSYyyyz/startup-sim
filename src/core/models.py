"""Pydantic data models for Startup Sim — the single source of truth for state shape."""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, computed_field


# ── Action types ──────────────────────────────────────────────────────────────

class ActionType(str, Enum):
    PRODUCT = "product"
    MARKETING = "marketing"
    FUNDRAISING = "fundraising"
    TEAM = "team"
    STRATEGY = "strategy"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PlayerAction(BaseModel):
    """A single action the player wants to take this turn."""
    type: ActionType
    intent: str = ""  # natural-language description
    budget: int = Field(default=0, ge=0, description="Budget allocated in 元")
    risk_level: RiskLevel = RiskLevel.MEDIUM
    fundraise_amount: int = Field(default=0, ge=0, description="Amount raised in 元 (fundraising only)")
    equity_offered: int = Field(default=0, ge=0, le=100, description="Equity percentage offered (fundraising only)")


class ActionPlan(BaseModel):
    """Parsed action plan from player's natural-language input."""
    raw_input: str
    actions: List[PlayerAction] = Field(default_factory=list, max_length=5)


# ── Company state (single source of truth) ────────────────────────────────────

class CompanyState(BaseModel):
    """The authoritative game state. Database is the storage layer; this model
    defines validation and computed properties."""
    month: int = Field(default=1, ge=1, le=12)
    cash: int = Field(default=1_000_000, ge=0)
    monthly_burn: int = Field(default=180_000, ge=0)
    mrr: int = Field(default=0, ge=0)
    users: int = Field(default=0, ge=0)
    product_score: int = Field(default=20, ge=0, le=100)
    team_morale: int = Field(default=70, ge=0, le=100)
    founder_equity: int = Field(default=100, ge=0, le=100)
    board_control: int = Field(default=100, ge=0, le=100)
    market_share: int = Field(default=0, ge=0, le=100)
    reputation: int = Field(default=50, ge=0, le=100)
    employee_count: int = Field(default=10, ge=0, description="团队人数")
    price: int = Field(default=5000, ge=0, description="产品月单价(元)")
    valuation: int = Field(default=5_000_000, ge=0, description="公司估值(元)")

    @computed_field
    @property
    def runway_months(self) -> float:
        """How many months until cash runs out at current burn rate."""
        if self.monthly_burn <= 0:
            return float("inf")
        return self.cash / self.monthly_burn

    @computed_field
    @property
    def mrr_growth_rate(self) -> float:
        """MRR growth rate as a fraction (0.0 - 1.0). Requires tracking
        previous MRR externally; here we default to 0."""
        return 0.0  # set externally by engine using historical data


# ── Delta (changes to apply) ──────────────────────────────────────────────────

class StateDelta(BaseModel):
    """Describes changes to apply to CompanyState, with reasons for each change."""
    cash: int = 0
    monthly_burn: int = 0
    mrr: int = 0
    users: int = 0
    product_score: int = 0
    team_morale: int = 0
    founder_equity: int = 0
    board_control: int = 0
    market_share: int = 0
    reputation: int = 0
    employee_count: int = 0
    price: int = 0
    valuation: int = 0
    reasons: List[str] = Field(default_factory=list)

    def is_empty(self) -> bool:
        return all(v == 0 for k, v in self.model_dump().items() if k != "reasons")


# ── Event ─────────────────────────────────────────────────────────────────────

class GameEvent(BaseModel):
    """A narrative event triggered by game rules."""
    event_type: str
    description: str
    delta: StateDelta = Field(default_factory=StateDelta)


# ── Turn result ───────────────────────────────────────────────────────────────

class EndingType(str, Enum):
    NONE = "none"  # game continues
    BANKRUPTCY = "bankruptcy"
    FOUNDER_REMOVED = "founder_removed"
    SERIES_A_SUCCESS = "series_a_success"
    SURVIVED_BUT_AVERAGE = "survived_but_average"
    SLOW_DEATH = "slow_death"


class TurnResult(BaseModel):
    """Complete result after processing one turn."""
    month: int
    action_plan: ActionPlan
    state_before: CompanyState
    state_after: CompanyState
    delta: StateDelta
    events: List[GameEvent] = Field(default_factory=list)
    board_feedback: Dict[str, str] = Field(default_factory=dict)
    competitor_moves: List[Dict[str, Any]] = Field(default_factory=list)
    customer_response: Dict[str, Any] = Field(default_factory=dict)
    ending: EndingType = EndingType.NONE
    ending_description: str = ""
    snapshots_saved: int = 0
