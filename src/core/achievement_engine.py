"""Alpha 1.5 Achievement Engine: awards badges based on game performance.

Evaluates a completed game against 15 achievements across 4 rarity tiers:
  common(7) / rare(5) / epic(2) / legendary(1)

Pure functions — no DB, no LLM, no side effects.
"""

from __future__ import annotations

from typing import Any

from src.core.models import Achievement, AchievementResult, CompanyState, GameReview


class AchievementEngine:
    """Stateless achievement evaluator."""

    # ── Achievement definitions ──────────────────────────────────────────────

    _ACHIEVEMENTS = [
        # ── Common (7) ──
        {
            "code": "product_believer",
            "title": "产品信仰者",
            "description": "最终产品分达到80分以上——你用代码改变世界。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: s.product_score >= 80,
        },
        {
            "code": "growth_machine",
            "title": "增长机器",
            "description": "用户数突破1000人或MRR突破50万——规模是你的名片。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: s.users >= 1000 or s.mrr >= 500_000,
        },
        {
            "code": "series_a_winner",
            "title": "A轮赢家",
            "description": "成功完成A轮融资——你拿到了通往下一关的门票。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: e == "series_a_success",
        },
        {
            "code": "near_death",
            "title": "死里逃生",
            "description": "现金一度跌破5万但最终没有破产——心跳回忆。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: _had_cash_below(snaps, 50_000) and e != "bankruptcy",
        },
        {
            "code": "cash_guardian",
            "title": "现金守门员",
            "description": "现金从未跌破50万——你把现金流当信仰。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: not _had_cash_below(snaps, 500_000),
        },
        {
            "code": "control_master",
            "title": "控制权大师",
            "description": "创始人股权始终保持在95%以上——公司是你的城堡。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: s.founder_equity >= 95,
        },
        {
            "code": "dilute_for_growth",
            "title": "稀释换增长",
            "description": "股权低于80%但MRR突破15万——用控制权换来了增长。",
            "rarity": "common",
            "check": lambda s, e, r, snaps: s.founder_equity < 80 and s.mrr >= 150_000,
        },
        # ── Rare (5) ──
        {
            "code": "slow_death",
            "title": "慢性死亡",
            "description": "公司没有剧变，却一点点从市场上消失——温水煮青蛙。",
            "rarity": "rare",
            "check": lambda s, e, r, snaps: e == "slow_death",
        },
        {
            "code": "rd_trap",
            "title": "研发陷阱",
            "description": "产品分达到70+却仍以失败告终——好产品也需要好时机。",
            "rarity": "rare",
            "check": lambda s, e, r, snaps: s.product_score >= 70
            and e in ("bankruptcy", "slow_death"),
        },
        {
            "code": "marketing_bubble",
            "title": "营销泡沫",
            "description": "用户数超500但产品分不足40——增长没有产品根基。",
            "rarity": "rare",
            "check": lambda s, e, r, snaps: s.users >= 500 and s.product_score < 40,
        },
        {
            "code": "small_and_beautiful",
            "title": "小而美",
            "description": "没有拿到A轮但产品分达到75——你有一门好生意。",
            "rarity": "rare",
            "check": lambda s, e, r, snaps: e == "survived_but_average" and s.product_score >= 75,
        },
        {
            "code": "capital_player_rare",
            "title": "资本玩家",
            "description": "股权低于70%但估值超过2500万——你深谙资本游戏。",
            "rarity": "rare",
            "check": lambda s, e, r, snaps: s.founder_equity < 70 and s.valuation > 25_000_000,
        },
        # ── Epic (2) ──
        {
            "code": "crisis_handler",
            "title": "危机处理者",
            "description": "经历3个以上危险月份仍完成A轮——在风暴中抵达彼岸。",
            "rarity": "epic",
            "check": lambda s, e, r, snaps: _count_risky_months(snaps) >= 3
            and e == "series_a_success",
        },
        {
            "code": "steady_operator",
            "title": "稳健经营者",
            "description": "零高风险月份并成功A轮——稳扎稳打的教科书。",
            "rarity": "epic",
            "check": lambda s, e, r, snaps: _count_risky_months(snaps) == 0
            and e == "series_a_success",
        },
        # ── Legendary (1) ──
        {
            "code": "legendary_founder",
            "title": "传奇创始人",
            "description": "A轮成功、产品85+、用户1000+、股权80%+——满贯。",
            "rarity": "legendary",
            "check": lambda s, e, r, snaps: (
                e == "series_a_success"
                and s.product_score >= 85
                and s.users >= 1000
                and s.founder_equity >= 80
            ),
        },
    ]

    # ── Public API ───────────────────────────────────────────────────────────

    @classmethod
    def evaluate(
        cls,
        final_state: CompanyState,
        ending_status: str,
        review: GameReview,
        snapshots: list[dict[str, Any]],
    ) -> AchievementResult:
        """Evaluate all 15 achievements against a completed game."""
        earned = []
        for ach_def in cls._ACHIEVEMENTS:
            try:
                if ach_def["check"](final_state, ending_status, review, snapshots):
                    earned.append(
                        Achievement(
                            code=ach_def["code"],
                            title=ach_def["title"],
                            description=ach_def["description"],
                            rarity=ach_def["rarity"],
                        )
                    )
            except Exception:
                pass  # skip buggy checks

        rare_count = sum(1 for a in earned if a.rarity in ("rare", "epic", "legendary"))
        total = len(earned)

        summary = cls._build_summary(earned, total, rare_count, ending_status)

        return AchievementResult(
            achievements=earned,
            total_count=total,
            rare_count=rare_count,
            summary=summary,
        )

    @classmethod
    def _build_summary(
        cls, earned: list[Achievement], total: int, rare_count: int, ending_status: str
    ) -> str:
        legendary = [a for a in earned if a.rarity == "legendary"]
        epic = [a for a in earned if a.rarity == "epic"]
        rare = [a for a in earned if a.rarity == "rare"]

        if legendary:
            return f"传奇创始人！你获得了{total}个成就（含{rare_count}个稀有+），满贯通关。"
        if epic:
            titles = "、".join(a.title for a in epic)
            return f"出色的表现！{titles}——你获得了{total}个成就。"
        if rare:
            return f"不错的一局！你获得了{total}个成就（含{rare_count}个稀有）。"
        if total > 0:
            return f"你获得了{total}个成就。继续尝试不同策略来解锁更多。"
        return "这次没有获得成就。换个策略再试一次吧！"


# ── Helper functions ─────────────────────────────────────────────────────────


def _had_cash_below(snapshots: list[dict[str, Any]], threshold: int) -> bool:
    """Check if cash ever dropped below threshold across snapshots."""
    for snap in snapshots:
        state_dict = snap.get("state_json", snap)
        if isinstance(state_dict, str):
            import json

            state_dict = json.loads(state_dict)
        if state_dict.get("cash", 1_000_000) < threshold:
            return True
    return False


def _count_risky_months(snapshots: list[dict[str, Any]]) -> int:
    """Count months where cash < 100k or runway < 6."""
    count = 0
    for snap in snapshots:
        state_dict = snap.get("state_json", snap)
        if isinstance(state_dict, str):
            import json

            state_dict = json.loads(state_dict)
        cash = state_dict.get("cash", 1_000_000)
        monthly_burn = state_dict.get("monthly_burn", 120_000)
        runway = cash / monthly_burn if monthly_burn > 0 else float("inf")
        if cash < 100_000 or runway < 6:
            count += 1
    return count
