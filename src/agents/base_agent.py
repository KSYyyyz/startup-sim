"""Base agent class for board member agents (董事会会议).

Phase 1B: mock board members that use rule + template to generate suggestions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.models import ActionPlan, CompanyState


class BaseAgent(ABC):
    """Abstract base for all board member agents (董事).

    Each agent has a name (display ID), role (e.g. "CFO"), and stance
    (e.g. "conservative").  The `speak` method takes the current company
    state and the player's action plan and returns a natural-language
    suggestion string (董事会发言).
    """

    def __init__(self, name: str, role: str, stance: str) -> None:
        self.name = name
        self.role = role
        self.stance = stance

    @abstractmethod
    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        """Generate a role-appropriate suggestion (在董事会上发言)."""
        ...
