"""Agent modules for Startup Sim.

Board member agents (董事会会议) — Phase 1B.
Competitor agents (竞品Agent) — Phase 1C.
Customer agent (客户群体Agent) — Phase 1C.
"""

from src.agents.base_agent import BaseAgent
from src.agents.board import CFO, CTO, COO, InvestorDirector
from src.agents.competitors import KuaiDaTech, LingxiCSCloud, CompetitorAgent
from src.agents.customers import CustomerAgent

__all__ = [
    "BaseAgent",
    "CFO", "CTO", "COO", "InvestorDirector",
    "CompetitorAgent", "KuaiDaTech", "LingxiCSCloud",
    "CustomerAgent",
]
