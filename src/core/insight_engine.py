"""Alpha 1.9 Insight Engine: generates one business insight per turn.

Each turn, the engine examines the player's actions and their results,
producing a concise经营洞察 that helps the player understand WHY their
actions had the effects they did. The insights are categorized and the
top 3 are preserved for the final review.
"""

from __future__ import annotations

from src.core.models import (
    ActionPlan,
    ActionType,
    BusinessInsight,
    CompanyState,
    StateDelta,
)


class InsightEngine:
    """Stateless engine that generates business insights from turn results."""

    @staticmethod
    def generate(
        state_before: CompanyState,
        action_plan: ActionPlan,
        delta: StateDelta,
        month: int,
        fundraising_accepted: bool = None,
        fundraising_rejected: bool = False,
    ) -> BusinessInsight:
        """Generate one business insight for the current turn.

        Priority order for insight generation:
        1. Fundraising result (accepted or rejected)
        2. High marketing spend with low product
        3. High R&D spend with low cash
        4. Cash dangerously low
        5. MRR growth signal
        6. Risk alerts
        7. Team health
        8. Generic observation
        """
        total_budget = sum(a.budget for a in action_plan.actions)
        has_marketing = any(a.type == ActionType.MARKETING for a in action_plan.actions)
        has_product = any(a.type == ActionType.PRODUCT for a in action_plan.actions)
        marketing_budget = sum(
            a.budget for a in action_plan.actions if a.type == ActionType.MARKETING
        )
        product_budget = sum(a.budget for a in action_plan.actions if a.type == ActionType.PRODUCT)

        product = state_before.product_score
        mrr = state_before.mrr
        runway = state_before.runway_months

        # 1. Fundraising result
        if fundraising_accepted:
            amount_w = (
                sum(
                    a.fundraise_amount
                    for a in action_plan.actions
                    if a.type == ActionType.FUNDRAISING and a.fundraise_amount > 0
                )
                // 10000
            )
            equity_used = sum(
                a.equity_offered
                for a in action_plan.actions
                if a.type == ActionType.FUNDRAISING and a.equity_offered > 0
            )
            return BusinessInsight(
                month=month,
                category="fundraising_win",
                title="融资成功",
                description=(
                    f"本轮成功融资{amount_w}万，出让{equity_used}%股权。"
                    f"这笔资金为公司争取了宝贵的运营时间，但也意味着未来决策需要考虑投资人的期望。"
                ),
                action_advice="用这笔钱建立真正的竞争壁垒，不要只是烧钱续命。",
            )

        if fundraising_rejected:
            return BusinessInsight(
                month=month,
                category="fundraising_fail",
                title="融资被拒",
                description=(
                    f"投资人拒绝了本轮融资提案。通常原因是估值期望与公司实际表现不匹配。"
                    f"当前产品分{product}、MRR{mrr//10000}万、跑道{runway:.1f}个月。"
                ),
                action_advice="提升核心指标（产品分、MRR、用户数）后再尝试融资，或降低融资额度和估值期望。",
            )

        # 2. High marketing, low product
        if has_marketing and marketing_budget >= 100_000 and product < 40:
            return BusinessInsight(
                month=month,
                category="marketing_efficiency",
                title="营销效率警告：产品不足时营销ROI极低",
                description=(
                    f"本回合营销投入{marketing_budget//10000}万，但产品分仅{product}。"
                    f"用户被营销吸引来，却因为产品体验差而流失——每花1元营销，可能只收回0.3元。"
                ),
                action_advice="暂缓大规模营销，把预算转投研发。产品分至少到50以上再启动营销。",
            )

        # 3. High R&D, low cash
        if has_product and product_budget >= 100_000 and runway < 5:
            return BusinessInsight(
                month=month,
                category="cash_warning",
                title="研发投入过高，现金流承压",
                description=(
                    f"本回合研发投入{product_budget//10000}万，但跑道仅{runway:.1f}个月。"
                    f"研发是长期投资，但如果死在产品完成之前，一切都没有意义。"
                ),
                action_advice="考虑适当降低研发单月投入，分多个月执行；或启动融资补充现金流。",
            )

        # 4. Cash dangerously low
        if runway < 3 and runway > 0:
            return BusinessInsight(
                month=month,
                category="cash_warning",
                title=f"现金流危急：跑道仅{runway:.1f}个月",
                description=(
                    f"公司现金仅够维持{runway:.1f}个月运营。"
                    f"在SaaS行业，重新融资通常需要2-3个月的准备和谈判周期——你已经在死亡线上了。"
                ),
                action_advice="立即启动紧急融资，同时将所有非核心支出削减至零。",
            )

        # 5. MRR growth signal
        mrr_growth = delta.mrr
        if mrr_growth >= 30000:
            return BusinessInsight(
                month=month,
                category="growth_signal",
                title=f"MRR显著增长：+{mrr_growth//10000}万",
                description=(
                    f"本月经常性收入增长{mrr_growth//10000}万，说明之前的投入开始产生复利效应。"
                    f"MRR的增长质量远高于一次性收入，这是投资人最看重的信号。"
                ),
                action_advice="保持增长势头，考虑适度追加投入以加速飞轮。",
            )

        # 6. Risk alert: reputation damage
        if delta.reputation < -3:
            return BusinessInsight(
                month=month,
                category="risk_alert",
                title="声誉显著下滑",
                description=(
                    f"本月声誉变化{delta.reputation}，市场对公司品牌信心下降。"
                    f"声誉影响融资估值、用户获取成本和团队招聘，是一个容易被忽视的隐性指标。"
                ),
                action_advice="排查声誉下滑原因（竞品攻击？产品质量问题？），尽快修复品牌形象。",
            )

        # 7. Team health
        if delta.team_morale <= -5:
            return BusinessInsight(
                month=month,
                category="team_health",
                title="团队士气明显下降",
                description=(
                    f"本月团队士气变化{delta.team_morale}。"
                    f"士气下降会拖累研发效率和客户服务质量，且核心员工流失风险上升。"
                ),
                action_advice="安排一次团队建设或考虑期权激励方案，防止核心人才流失。",
            )

        # 8. Default: observation based on what changed
        if total_budget > 0:
            return BusinessInsight(
                month=month,
                category="growth_signal",
                title=f"第{month}月经营观察",
                description=(
                    f"本回合总投入{total_budget//10000}万。"
                    f"产品分{product}→{product + delta.product_score}，"
                    f"MRR{mrr//10000}万→{(mrr + delta.mrr)//10000}万。"
                ),
                action_advice="持续关注产品-市场匹配和现金流健康度。",
            )

        # No action taken
        return BusinessInsight(
            month=month,
            category="risk_alert",
            title=f"第{month}月无动作",
            description="本回合没有做出任何决策。在竞争激烈的市场中，原地踏步就是退步。",
            action_advice="下回合至少投入一些资源推进产品或营销。",
        )

    @staticmethod
    def select_top_insights(
        insights: list[BusinessInsight], top_n: int = 3
    ) -> list[BusinessInsight]:
        """Select the top N most important insights for the final review.

        Priority categories: fundraising_win, fundraising_fail, cash_warning,
        risk_alert, team_health, marketing_efficiency, product_gap,
        growth_signal
        """
        priority = {
            "fundraising_win": 10,
            "fundraising_fail": 10,
            "cash_warning": 9,
            "risk_alert": 8,
            "team_health": 7,
            "marketing_efficiency": 6,
            "product_gap": 6,
            "growth_signal": 5,
        }
        sorted_insights = sorted(insights, key=lambda i: priority.get(i.category, 0), reverse=True)
        return sorted_insights[:top_n]
