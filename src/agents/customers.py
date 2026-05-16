"""Customer agent (客户群体Agent) — mock rule engine for Phase 1C.

Evaluates how the customer base responds to:
- Product quality changes
- Pricing / marketing decisions
- Competitor moves
- Team morale (delivery quality)
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.models import ActionPlan, CompanyState


class CustomerAgent:
    """客户群体Agent — evaluates customer response each turn."""

    def __init__(self, churn_multiplier: float = 1.0):
        self.churn_multiplier = churn_multiplier

    def evaluate(
        self,
        state: CompanyState,
        plan: ActionPlan,
        competitor_moves: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Evaluate customer response based on state, player actions, and competitor moves.

        Returns:
            dict with keys: growth_change (int, user count), revenue_change (int, MRR),
            narrative (str)
        """
        growth_change = 0
        revenue_change = 0
        narratives: List[str] = []
        cm = self.churn_multiplier

        # ── 1. Product quality → growth ──────────────────────────────────────
        # product_score < 30: slow growth (or churn)
        # product_score 30-70: moderate growth
        # product_score > 70: accelerated growth
        if state.product_score < 30:
            churn = max(1, (30 - state.product_score) // 5)
            churn = int(churn * cm)
            growth_change -= churn
            narratives.append(
                f"产品体验不佳（产品分{state.product_score}），"
                f"部分客户流失（{-churn}人）"
            )
        elif state.product_score > 70:
            bonus = (state.product_score - 70) // 5 + 1
            growth_change += bonus * 10
            narratives.append(
                f"产品口碑优秀（产品分{state.product_score}），"
                f"自然增长加速（+{bonus * 10}人）"
            )
        else:
            # 30-70: baseline organic growth
            baseline = state.product_score // 10
            growth_change += baseline * 5
            if baseline > 0:
                narratives.append(
                    f"产品稳定（产品分{state.product_score}），"
                    f"自然增长{baseline * 5}人"
                )

        # -- 2. Player marketing → user growth via CAC + retention modifier --
        has_marketing = any(a.type == "marketing" for a in plan.actions)
        if has_marketing:
            marketing_budget = sum(
                a.budget for a in plan.actions if a.type == "marketing"
            )
            # CAC = 1000元/用户 (base acquisition cost)
            new_users = max(1, marketing_budget // 1000)
            # Product-score-based retention modifier
            if state.product_score < 30:
                retention = 0.4   # 产品太差，获客留存打4折
            elif state.product_score < 60:
                retention = 0.8   # 产品一般，留存打8折
            else:
                retention = 1.0 + (state.product_score - 60) / 200  # 1.0→1.2
            retained_users = max(1, int(new_users * retention))
            growth_change += retained_users
            # MRR from retained users (same conversion-rate logic as baseline)
            if state.product_score < 30:
                conv = 0.02
            elif state.product_score < 50:
                conv = 0.05
            elif state.product_score < 70:
                conv = 0.10
            else:
                conv = 0.18
            new_mrr = int(retained_users * conv * state.price)
            revenue_change += new_mrr
            narratives.append(
                f"市场投放带来{retained_users}个留存用户"
                f"（CAC={marketing_budget // retained_users}元/人，留存率{retention*100:.0f}%），"
                f"新增MRR≈{new_mrr//10000}万"
            )

        # ── 3. Competitor moves → customer response ──────────────────────────
        for move in competitor_moves:
            competitor_name = move.get("name", "未知竞品")
            action = move.get("action", "")

            if action == "price_cut" or action == "follow_price_cut":
                # Competitor undercutting → some customers switch
                churn = int(5 * cm) if action == "price_cut" else int(3 * cm)
                churn = max(1, churn)
                growth_change -= churn
                narratives.append(
                    f"{competitor_name}降价吸引走{churn}个价格敏感客户"
                )
            elif action == "enterprise_upgrade":
                # Competitor improving enterprise features
                churn = max(1, int(5 * cm))
                revenue_loss = int(5000 * cm)
                growth_change -= churn
                revenue_change -= revenue_loss
                narratives.append(
                    f"{competitor_name}企业版功能升级，{churn}个高端客户转向竞品"
                )

        # ── 4. Team morale → delivery quality → retention ────────────────────
        if state.team_morale >= 80:
            retention_bonus = 3
            growth_change += retention_bonus
            narratives.append(
                f"团队士气高涨（{state.team_morale}），"
                f"交付质量提升，客户留存率提高（+{retention_bonus}人）"
            )
        elif state.team_morale < 40:
            churn = (40 - state.team_morale) // 10
            churn = max(1, int(churn * cm))
            growth_change -= churn
            revenue_change -= churn * 1000
            narratives.append(
                f"团队士气低落（{state.team_morale}），"
                f"交付质量下降，{churn}个客户因服务不佳离开"
            )

        # ── 5. Baseline MRR from user base ────────────────────────────────────
        # Users generate MRR based on product quality (conversion rate)
        if state.users > 0:
            if state.product_score < 30:
                conv_rate = 0.02  # 2% pay
            elif state.product_score < 50:
                conv_rate = 0.05  # 5% pay
            elif state.product_score < 70:
                conv_rate = 0.10  # 10% pay
            else:
                conv_rate = 0.18  # 18% pay
            
            paying_users = int(state.users * conv_rate)
            new_mrr = paying_users * state.price
            # Only report if MRR actually changes significantly
            if new_mrr > state.mrr:
                revenue_change += (new_mrr - state.mrr)
                narratives.append(
                    f"付费转化率{conv_rate*100:.0f}%，{paying_users}个付费用户，"
                    f"MRR={new_mrr//10000}万"
                )

        # ── Assemble response ─────────────────────────────────────────────────
        full_narrative = "；".join(narratives) if narratives else "客户群体表现平稳，无显著变化。"

        return {
            "growth_change": growth_change,
            "revenue_change": revenue_change,
            "narrative": full_narrative,
        }
