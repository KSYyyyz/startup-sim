"""Competitor agents (竞品Agent) — rule engines with persistent state.

Alpha 1.3: Each competitor now has CompetitorState (product_score, cash,
market_share, strategy_cooldown) and a periodic_action() method, so
competitors act on their own initiative every turn, not just in response.

Two competitors:
- 快答科技 (QuickAnswer Tech): price_war — aggressive price competition
- 灵犀客服云 (Lingxi CS Cloud): premium_enterprise — high-end differentiation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from src.core.models import ActionPlan, CompanyState, StateDelta


@dataclass
class CompetitorState:
    """Persistent state for a single competitor."""

    product_score: int = 25
    cash: int = 2_000_000
    market_share: int = 15
    strategy_cooldown: int = 0  # turns until next major action


class CompetitorAgent:
    """Base class for competitor agents with persistent state."""

    def __init__(self, name: str, strategy: str, aggression_multiplier: float = 1.0) -> None:
        self.name = name
        self.strategy = strategy
        self.aggression_multiplier = aggression_multiplier
        self._state = CompetitorState()

    @property
    def product_score(self) -> int:
        return self._state.product_score

    @property
    def market_share(self) -> int:
        return self._state.market_share

    def get_state(self) -> CompetitorState:
        return self._state

    def periodic_action(self, player_state: CompanyState) -> Optional[Dict[str, Any]]:
        """Executed every turn — competitor's own initiative, not a response.

        Returns a competitor_move dict (same shape as respond()), or None
        if the competitor takes no independent action this turn.
        """
        return None

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        """Respond to the player's actions and return a competitor_move dict."""
        raise NotImplementedError


class KuaiDaTech(CompetitorAgent):
    """快答科技 — price_war strategy.

    Periodic behavior: slowly improves product (slower than player),
    occasionally does aggressive price cuts.

    Response rules:
    - If player product_score > 快答的产品分 → 降价抢市场
    - If player does marketing → 跟降
    - Default → steady growth
    """

    def __init__(self, aggression_multiplier: float = 1.0) -> None:
        super().__init__(name="快答科技", strategy="price_war", aggression_multiplier=aggression_multiplier)
        self._state = CompetitorState(
            product_score=25,
            cash=2_000_000,
            market_share=15,
            strategy_cooldown=0,
        )

    def periodic_action(self, player_state: CompanyState) -> Optional[Dict[str, Any]]:
        """快答科技周期性行为：缓慢产品提升 + 偶尔激进降价."""
        agg = self.aggression_multiplier

        # Slow organic product improvement: +1 every 2 turns on average
        if player_state.month % 2 == 0:
            self._state.product_score = min(100, self._state.product_score + 1)

        # Cooldown tick
        if self._state.strategy_cooldown > 0:
            self._state.strategy_cooldown -= 1

        # Price cut every ~4 turns, independent of player
        if self._state.strategy_cooldown == 0 and player_state.month % 4 == 0:
            self._state.strategy_cooldown = 4
            return {
                "name": self.name,
                "action": "initiative_price_cut",
                "narrative": (
                    f"快答科技主动发起新一轮价格战，将基础版降价30%，"
                    f"以低价策略抢占中低端市场份额。"
                ),
                "delta": {"market_share": int(-1 * agg)},
            }

        # If快答 has decent product, try to grow market share
        if self._state.product_score >= 30 and player_state.month % 3 == 0:
            self._state.market_share = min(30, self._state.market_share + 1)
            return {
                "name": self.name,
                "action": "organic_growth",
                "narrative": (
                    f"快答科技产品分提升至{self._state.product_score}，"
                    f"依靠低价优势自然蚕食市场份额（+1%）。"
                ),
                "delta": {"market_share": 0, "users": int(-3 * agg)},
            }

        return None

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        kuai_product = self._state.product_score
        has_marketing = any(a.type == "marketing" for a in plan.actions)
        agg = self.aggression_multiplier

        if state.product_score > kuai_product:
            return {
                "name": self.name,
                "action": "price_cut",
                "narrative": (
                    f"快答科技发现玩家产品分({state.product_score})高于自己({kuai_product})，"
                    "立即启动价格战，大幅降价抢夺客户。你的市场份额受到冲击。"
                ),
                "delta": {"market_share": int(-2 * agg)},
            }
        elif has_marketing:
            return {
                "name": self.name,
                "action": "follow_price_cut",
                "narrative": (
                    "快答科技监测到你在加大市场投放，随即跟进降价策略，"
                    "以低价吸引价格敏感客户。部分客户被分流。"
                ),
                "delta": {"market_share": int(-1 * agg)},
            }
        else:
            return {
                "name": self.name,
                "action": "steady_growth",
                "narrative": "快答科技本月维持常规运营，依靠价格优势缓慢蚕食中低端市场。",
                "delta": {"market_share": 0},
            }


class LingxiCSCloud(CompetitorAgent):
    """灵犀客服云 — premium_enterprise strategy.

    Periodic behavior: invests in enterprise features, grows steadily in
    high-end segment. Slower growth but higher quality.

    Response rules:
    - If player product_score > 70 → upgrade enterprise features
    - If player does marketing → differentiate on quality
    - Default → steady premium growth
    """

    def __init__(self, aggression_multiplier: float = 1.0) -> None:
        super().__init__(name="灵犀客服云", strategy="premium_enterprise", aggression_multiplier=aggression_multiplier)
        self._state = CompetitorState(
            product_score=35,
            cash=5_000_000,
            market_share=12,
            strategy_cooldown=0,
        )

    def periodic_action(self, player_state: CompanyState) -> Optional[Dict[str, Any]]:
        """灵犀客服云周期性行为：稳步研发企业功能 + 高端市场增长."""
        agg = self.aggression_multiplier

        # Steady product improvement: +1 every 2 turns
        if player_state.month % 2 == 0:
            self._state.product_score = min(100, self._state.product_score + 1)

        # Cooldown tick
        if self._state.strategy_cooldown > 0:
            self._state.strategy_cooldown -= 1

        # Enterprise feature push every ~5 turns
        if self._state.strategy_cooldown == 0 and player_state.month % 5 == 0:
            self._state.strategy_cooldown = 5
            self._state.market_share = min(25, self._state.market_share + 1)
            return {
                "name": self.name,
                "action": "enterprise_feature_launch",
                "narrative": (
                    f"灵犀客服云发布新企业版功能模块，产品分提升至{self._state.product_score}，"
                    f"进一步巩固高端市场地位。你的部分高端客户开始关注灵犀方案。"
                ),
                "delta": {"reputation": int(-1 * agg)},
            }

        # Slow but steady premium market growth
        if self._state.product_score >= 40 and player_state.month % 4 == 0:
            self._state.market_share = min(25, self._state.market_share + 1)
            return {
                "name": self.name,
                "action": "premium_growth",
                "narrative": (
                    f"灵犀客服云在高端企业市场持续增长（产品分{self._state.product_score}，"
                    f"市场份额{self._state.market_share}%），吸引对服务质量敏感的大客户。"
                ),
                "delta": {"users": int(-2 * agg)},
            }

        return None

    def respond(self, state: CompanyState, plan: ActionPlan) -> Dict[str, Any]:
        has_price_related = any(
            a.type == "marketing" or a.type == "strategy"
            for a in plan.actions
        )
        agg = self.aggression_multiplier

        if state.product_score > 70:
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
                    "mrr": int(30000 * agg),
                    "reputation": int(-1 * agg),
                },
            }
        elif has_price_related:
            return {
                "name": self.name,
                "action": "differentiate",
                "narrative": (
                    "灵犀客服云表示「我们不参与价格战」，"
                    "转而发布企业白皮书强调服务质量和AI能力差异化。"
                    "高端客户更看重服务稳定性而非价格。"
                ),
                "delta": {"reputation": int(-1 * agg)},
            }
        else:
            return {
                "name": self.name,
                "action": "steady_premium",
                "narrative": "灵犀客服云持续深耕高端企业市场，稳步获取新客户。",
                "delta": {},
            }


def get_competitor_summary(competitor: CompetitorAgent) -> str:
    """Return a one-line summary of competitor state for monthly reports."""
    cs = competitor.get_state()
    return (
        f"{competitor.name}: 产品分{cs.product_score} "
        f"市场份额{cs.market_share}% "
        f"策略冷却{cs.strategy_cooldown}回合"
    )
