"""Ending evaluator: determines if the game has reached an ending condition.

Five possible endings:
- bankruptcy: cash <= 0
- founder_removed: equity < 34 AND board < 45 AND runway < 4
- series_a_success: month >= 12 AND mrr >= 300,000 AND product >= 70 AND equity >= 50
- survived_but_average: month >= 12 AND mrr >= 100,000 AND cash > 0
- slow_death: month >= 12 (catch-all)
- None: game continues
"""

from __future__ import annotations

from typing import Optional

from src.core.models import CompanyState, EndingType


def evaluate(state: CompanyState) -> Optional[EndingType]:
    """Evaluate the current state and return an EndingType if the game is over,
    or None if the game should continue.
    """

    # Immediate endings (can happen any month)
    if state.cash <= 0:
        return EndingType.BANKRUPTCY

    if (state.founder_equity < 34
            and state.board_control < 45
            and state.runway_months < 4):
        return EndingType.FOUNDER_REMOVED

    # Terminal month endings (only evaluated at month 12)
    if state.month >= 12:
        if (state.mrr >= 300_000
                and state.product_score >= 70
                and state.founder_equity >= 50):
            return EndingType.SERIES_A_SUCCESS

        if state.mrr >= 100_000 and state.cash > 0:
            return EndingType.SURVIVED_BUT_AVERAGE

        return EndingType.SLOW_DEATH

    # Game continues
    return None


def describe_ending(ending: EndingType, state: CompanyState) -> str:
    """Return a human-readable description for an ending."""
    descriptions = {
        EndingType.BANKRUPTCY: (
            f"💸 资金耗尽！第{state.month}个月现金归零，公司破产。"
            f"MRR={state.mrr/10000:.0f}万, 用户={state.users}"
        ),
        EndingType.FOUNDER_REMOVED: (
            f"👋 创始人出局！股权仅{state.founder_equity}%，"
            f"董事会控制力{state.board_control}%，董事会投票罢免了你。"
        ),
        EndingType.SERIES_A_SUCCESS: (
            f"🎉 A轮融资成功！MRR={state.mrr/10000:.0f}万，"
            f"产品评分{state.product_score}，成功以优厚条款完成A轮融资！"
        ),
        EndingType.SURVIVED_BUT_AVERAGE: (
            f"😐 勉强存活。MRR={state.mrr/10000:.0f}万，"
            f"现金剩余{state.cash/10000:.0f}万。公司活下来了但未达高速增长预期。"
        ),
        EndingType.SLOW_DEATH: (
            f"🐌 慢性死亡。12个月后MRR仅{state.mrr/10000:.0f}万，"
            f"增长乏力，公司在慢慢耗尽资源。"
        ),
    }
    return descriptions.get(ending, f"游戏结束：{ending.value}")
