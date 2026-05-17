"""Alpha 1.5 Strategy Comparison: compares multiple playthrough strategies.

Takes a list of GameReview objects and produces a StrategyComparison with
best-in-class rankings and a summary table.
"""

from __future__ import annotations

from typing import Any

from src.core.models import GameReview, StrategyComparison


class StrategyCompare:
    """Stateless strategy comparator."""

    @classmethod
    def compare(cls, reviews: list[GameReview]) -> StrategyComparison:
        """Compare multiple game reviews and rank strategies."""
        if not reviews:
            return StrategyComparison(conclusion="没有策略数据可供对比。")

        strategies: list[dict[str, Any]] = []
        best_overall = ""
        best_growth = ""
        best_product = ""
        best_finance = ""
        best_control = ""
        worst_risk = ""

        best_overall_val = -1
        best_growth_val = -1
        best_product_val = -1
        best_finance_val = -1
        best_control_val = -1
        worst_risk_val = 101

        for review in reviews:
            scores = review.strategy_scores
            profile = review.founder_profile
            label = review.ending_title or f"#{review.session_id}"

            strategy_entry = {
                "label": label,
                "ending_status": review.ending_status,
                "founder_type": profile.profile_type,
                "product_score": scores.product_score,
                "growth_score": scores.growth_score,
                "finance_score": scores.finance_score,
                "control_score": scores.control_score,
                "risk_score": scores.risk_score,
                "overall_score": scores.overall_score,
            }
            strategies.append(strategy_entry)

            if scores.overall_score > best_overall_val:
                best_overall_val = scores.overall_score
                best_overall = label
            if scores.growth_score > best_growth_val:
                best_growth_val = scores.growth_score
                best_growth = label
            if scores.product_score > best_product_val:
                best_product_val = scores.product_score
                best_product = label
            if scores.finance_score > best_finance_val:
                best_finance_val = scores.finance_score
                best_finance = label
            if scores.control_score > best_control_val:
                best_control_val = scores.control_score
                best_control = label
            if scores.risk_score < worst_risk_val:
                worst_risk_val = scores.risk_score
                worst_risk = label

        # Sort strategies by overall_score descending
        strategies.sort(key=lambda s: s["overall_score"], reverse=True)

        # Build summary table
        summary_table: list[dict[str, Any]] = []
        for i, s in enumerate(strategies):
            summary_table.append(
                {
                    "rank": i + 1,
                    "strategy": s["label"],
                    "product": s["product_score"],
                    "growth": s["growth_score"],
                    "finance": s["finance_score"],
                    "control": s["control_score"],
                    "risk": s["risk_score"],
                    "overall": s["overall_score"],
                }
            )

        conclusion = cls._build_conclusion(
            best_overall, best_product, best_growth, best_finance, best_control, worst_risk
        )

        return StrategyComparison(
            strategies=strategies,
            best_overall=best_overall,
            best_growth=best_growth,
            best_product=best_product,
            best_finance=best_finance,
            best_control=best_control,
            worst_risk=worst_risk,
            summary_table=summary_table,
            conclusion=conclusion,
        )

    @classmethod
    def _build_conclusion(
        cls,
        best_overall: str,
        best_product: str,
        best_growth: str,
        best_finance: str,
        best_control: str,
        worst_risk: str,
    ) -> str:
        parts = [f"综合最优：{best_overall}"]
        if best_product != best_overall:
            parts.append(f"产品最强：{best_product}")
        if best_growth != best_overall:
            parts.append(f"增长最快：{best_growth}")
        if best_finance != best_overall:
            parts.append(f"财务最佳：{best_finance}")
        if best_control != best_overall:
            parts.append(f"控制最稳：{best_control}")
        if worst_risk != best_overall:
            parts.append(f"风控最弱：{worst_risk}")
        return "。".join(parts) + "。"
