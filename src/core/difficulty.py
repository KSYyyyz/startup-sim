"""Difficulty system: affects initial state, event triggers, and agent behavior.

Three levels:
- easy:   generous starting position, forgiving events, weak competitors
- normal: balanced defaults
- hard:   tight starting position, aggressive events/competitors/churn
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Difficulty:
    """Preset difficulty configuration. Use class methods to get presets."""

    name: str

    # ── Initial state overrides (applied on top of scenario defaults) ────
    cash_multiplier: float = 1.0  # multiplier on scenario cash
    product_score_add: int = 0  # additive product_score adjustment
    team_morale_add: int = 0  # additive team_morale adjustment

    # ── Event trigger modifiers ──────────────────────────────────────────
    runway_warning_delay_turns: int = 0  # turns to delay runway_warning after threshold
    board_coup_equity_threshold: int = 34  # equity below this → board_coup_risk triggers
    board_coup_board_threshold: int = 50  # board_control below this threshold

    # ── Competitor aggression modifier ───────────────────────────────────
    competitor_aggression: float = 1.0  # 0.5 = half effects, 2.0 = double effects

    # ── Customer churn modifier ──────────────────────────────────────────
    customer_churn_multiplier: float = 1.0  # applied to churn calculations

    # ── Other ────────────────────────────────────────────────────────────
    description: str = ""

    @classmethod
    def easy(cls) -> Difficulty:
        return cls(
            name="easy",
            cash_multiplier=1.5,  # 1,000,000 → 1,500,000
            product_score_add=10,  # 20 → 30
            team_morale_add=0,
            runway_warning_delay_turns=1,  # warning delayed by 1 turn
            board_coup_equity_threshold=34,
            board_coup_board_threshold=50,
            competitor_aggression=0.5,  # half effects
            customer_churn_multiplier=1.0,
            description="轻松模式：充裕资金，温和竞品，适合新手体验",
        )

    @classmethod
    def normal(cls) -> Difficulty:
        return cls(
            name="normal",
            cash_multiplier=1.0,
            product_score_add=0,
            team_morale_add=0,
            runway_warning_delay_turns=0,
            board_coup_equity_threshold=34,
            board_coup_board_threshold=50,
            competitor_aggression=1.0,
            customer_churn_multiplier=1.0,
            description="标准模式：平衡的挑战",
        )

    @classmethod
    def hard(cls) -> Difficulty:
        return cls(
            name="hard",
            cash_multiplier=0.6,  # 1,000,000 → 600,000
            product_score_add=-10,  # 20 → 10
            team_morale_add=-15,  # 70 → 55
            runway_warning_delay_turns=0,
            board_coup_equity_threshold=40,  # higher threshold → triggers sooner
            board_coup_board_threshold=55,  # higher threshold → triggers sooner
            competitor_aggression=2.0,  # double effects
            customer_churn_multiplier=1.3,  # +30% churn
            description="困难模式：资金紧张，激进竞品，高流失率，适合挑战者",
        )

    def apply_to_scenario(self, scenario_dict: dict[str, Any]) -> dict[str, Any]:
        """Apply difficulty modifiers to a scenario's initial_state dict.

        Returns a *copy* with modifications.
        """
        import copy

        result = copy.deepcopy(scenario_dict)
        init = result.setdefault("initial_state", {})

        # Cash multiplier
        if "cash" in init:
            init["cash"] = int(init["cash"] * self.cash_multiplier)

        # Product score additive
        if "product_score" in init:
            init["product_score"] = max(0, min(100, init["product_score"] + self.product_score_add))

        # Team morale additive
        if "team_morale" in init:
            init["team_morale"] = max(0, min(100, init["team_morale"] + self.team_morale_add))

        result["_difficulty"] = self.name
        return result


# ── Convenience factory ────────────────────────────────────────────────────────


def get_difficulty(name: str) -> Difficulty:
    """Get a Difficulty instance by name ('easy', 'normal', 'hard')."""
    presets = {
        "easy": Difficulty.easy,
        "normal": Difficulty.normal,
        "hard": Difficulty.hard,
    }
    if name not in presets:
        raise ValueError(f"Unknown difficulty '{name}'. Available: easy, normal, hard")
    return presets[name]()
