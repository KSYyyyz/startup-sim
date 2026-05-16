"""Competitor agents (竞品Agent) — mock rule engines for Phase 1C.

Two competitors:
- 快答科技 (QuickAnswer Tech): price_war strategy — aggressive price competition
- 灵犀客服云 (Lingxi CS Cloud): premium_enterprise strategy — high-end differentiation
"""

from __future__ import annotations

from typing import Any, Dict

from src.core.models import ActionPlan, CompanyState, StateDelta


class CompetitorAgent:
    """Base class for competitor agents."""

    def __init__(self, name: str, strategy: str, aggression_multiplier: float = 1.0) -> None:
        self.name = name
        self.strategy = strategy
        self.aggression_multiplier = aggression_multiplier

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        """Respond to the player's actions and return a competitor_move dict.

        Returns:
            dict with keys: name, action, narrative, delta (StateDelta-compatible dict)
        """
        raise NotImplementedError


class KuaiDaTech(CompetitorAgent):
    """快答科技 — price_war strategy.

    Rules:
    - If player product_score > 快答的 product_score → 快答降价抢市场 (market_share -2 for player)
    - If player does marketing → 快答跟降 (market_share -1 for player)
    - Default → small growth for 快答 (minor market_share shift)
    """

    # 快答科技 has its own implied product score (grows over time)
    _base_product_score = 25

    def __init__(self, aggression_multiplier: float = 1.0) -> None:
        super().__init__(name="快答科技", strategy="price_war", aggression_multiplier=aggression_multiplier)

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        # 快答科技's product score grows slowly over time
        kuai_product = self._base_product_score + (state.month - 1) * 2

        has_marketing = any(a.type == "marketing" for a in plan.actions)
        agg = self.aggression_multiplier

        if state.product_score > kuai_product:
            # 玩家产品更好 → 快答降价抢市场
            return {
                "name": self.name,
                "action": "price_cut",
                "narrative": (
                    f"快答科技发现玩家产品分({state.product_score})高于自己({kuai_product})，"
                    "立即启动价格战，大幅降价抢夺客户。你的市场份额受到冲击。"
                ),
                "delta": {
                    "market_share": int(-2 * agg),
                },
            }
        elif has_marketing:
            # 玩家做营销 → 快答跟降
            return {
                "name": self.name,
                "action": "follow_price_cut",
                "narrative": (
                    "快答科技监测到你在加大市场投放，随即跟进降价策略，"
                    "以低价吸引价格敏感客户。部分客户被分流。"
                ),
                "delta": {
                    "market_share": int(-1 * agg),
                },
            }
        else:
            # Default — 快答缓慢增长
            return {
                "name": self.name,
                "action": "steady_growth",
                "narrative": (
                    "快答科技本月维持常规运营，依靠价格优势缓慢蚕食中低端市场。"
                ),
                "delta": {
                    "market_share": 0,
                },
            }


class LingxiCSCloud(CompetitorAgent):
    """灵犀客服云 — premium_enterprise strategy.

    Rules:
    - If player product_score > 70 → 灵犀也做企业级功能 (user growth slows but 客单价 rises)
    - If player 降价 → 灵犀不跟降，强调差异化
    - Default → 灵犀稳步增长高端市场
    """

    def __init__(self, aggression_multiplier: float = 1.0) -> None:
        super().__init__(name="灵犀客服云", strategy="premium_enterprise", aggression_multiplier=aggression_multiplier)

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        has_price_related = any(
            a.type == "marketing" or a.type == "strategy"
            for a in plan.actions
        )
        agg = self.aggression_multiplier

        if state.product_score > 70:
            # 玩家产品好 → 灵犀做企业级功能，用户增长微降但客单价升
            return {
                "name": self.name,
                "action": "enterprise_upgrade",
                "narrative": (
                    f"灵犀客服云注意到你的产品分已达{state.product_score}，"
                    "立即升级企业版功能包，瞄准大型客户。"
                    "高端客户开始转向灵犀，但你的客单价受到一定压力。"
                ),
                "delta": {
                    "users": int(-30 * agg),
                    "mrr": int(30000 * agg),  # 客单价提升，对灵犀有利
                    "reputation": int(-1 * agg),
                },
            }
        elif has_price_related:
            # 玩家降价/营销 → 灵犀不跟降，强调差异化
            return {
                "name": self.name,
                "action": "differentiate",
                "narrative": (
                    "灵犀客服云表示「我们不参与价格战」，"
                    "转而发布企业白皮书强调服务质量和AI能力差异化。"
                    "高端客户更看重服务稳定性而非价格。"
                ),
                "delta": {
                    "reputation": int(-1 * agg),
                },
            }
        else:
            # Default — 灵犀稳步增长
            return {
                "name": self.name,
                "action": "steady_premium",
                "narrative": (
                    "灵犀客服云持续深耕高端企业市场，稳步获取新客户。"
                ),
                "delta": {},
            }
