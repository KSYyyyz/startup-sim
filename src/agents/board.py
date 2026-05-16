"""Mock board member agents (董事会会议) using rule + template generation.

Phase 1B: no real LLM calls. Each board member examines CompanyState and
ActionPlan and returns a pre-canned suggestion based on thresholds.
"""

from __future__ import annotations

from src.agents.base_agent import BaseAgent
from src.core.models import ActionPlan, CompanyState


class CFO(BaseAgent):
    """Chief Financial Officer — conservative, cash-flow focused."""

    def __init__(self) -> None:
        super().__init__(name="CFO", role="首席财务官", stance="保守")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        runway = state.runway_months

        # Emergency: less than 4 months of runway
        if runway < 4:
            return (
                f"⚠️ 现金只够{runway:.1f}个月，强烈建议立即融资或大幅削减开支。"
                f"当前月消耗{state.monthly_burn:,}元，现金余额{state.cash:,}元。"
            )

        # Check for fundraising action
        has_fundraising = any(a.type == "fundraising" for a in plan.actions)
        if has_fundraising:
            return (
                "按当前估值，A轮投资人会要求至少20%股权。"
                "建议在融资前先提升MRR到50万/月以上以获得更好条款。"
            )

        # MRR growth check — we use a heuristic based on MRR absolute value
        if state.mrr > 0 and state.mrr < 300_000:
            return (
                f"收入增长不错（MRR {state.mrr:,}元），但需要关注毛利率。"
                "建议控制获客成本，确保LTV/CAC > 3。"
            )

        # Default — healthy
        return (
            f"📊 本月现金流正常（跑道{runway:.1f}个月），"
            "建议保持现有节奏，预留至少6个月的安全垫。"
        )


class CTO(BaseAgent):
    """Chief Technology Officer — product & long-term moat focused."""

    def __init__(self) -> None:
        super().__init__(name="CTO", role="首席技术官", stance="重视产品")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        # Product quality is weak
        if state.product_score < 30:
            return (
                f"🔧 产品还太弱（产品分{state.product_score}），"
                "建议至少投入研发把产品分推到50以上，否则用户留存会很差。"
            )

        # Product is strong
        if state.product_score > 70:
            return (
                f"👍 产品口碑不错（产品分{state.product_score}），"
                "可以考虑做企业级功能增加客单价，或者申请技术专利建立壁垒。"
            )

        # Team expansion action
        has_team = any(a.type == "team" for a in plan.actions)
        if has_team:
            return (
                "扩团队要注意技术债积累，建议新老人配比1:2，"
                "新人前2个月以熟悉代码库和修bug为主。"
            )

        # Default
        return (
            f"💻 技术路线稳健（产品分{state.product_score}），"
            "继续按计划迭代即可。关注系统可扩展性，为增长做准备。"
        )


class COO(BaseAgent):
    """Chief Operating Officer — execution & team focused."""

    def __init__(self) -> None:
        super().__init__(name="COO", role="首席运营官", stance="重视执行")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        # Low morale
        if state.team_morale < 50:
            return (
                f"😟 团队士气偏低（{state.team_morale}），"
                "建议做团建活动或考虑期权激励计划，核心员工流失风险较高。"
            )

        # High morale
        if state.team_morale > 80:
            return (
                f"🎯 团队状态很好（士气{state.team_morale}），"
                "现在推关键项目效率最高，建议趁热打铁推进重要里程碑。"
            )

        # Marketing with low runway
        runway = state.runway_months
        has_marketing = any(a.type == "marketing" for a in plan.actions)
        if has_marketing and runway < 3:
            return (
                f"⚠️ 现金流紧张（跑道{runway:.1f}个月），"
                "不建议此时大举投放市场费用，优先保证核心产品交付。"
            )

        # Default
        return (
            "📋 日常运营稳定，关注交付质量和客户满意度。"
            "定期复盘各项目进度，识别瓶颈及时调整。"
        )


class InvestorDirector(BaseAgent):
    """Investor Director (投资方董事) — growth & control focused."""

    def __init__(self) -> None:
        super().__init__(name="投资方董事", role="投资方董事", stance="重视增长")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        # Founder losing control
        if state.founder_equity < 50:
            return (
                f"⚠️ 创始人持股已降至{state.founder_equity}%，"
                "下轮融资后可能失去控制权。建议考虑AB股结构或暂缓稀释。"
            )

        # Slow growth
        if state.mrr < 100_000:
            return (
                f"📉 增长太慢（MRR仅{state.mrr:,}元），"
                "投资人会质疑PMF。需要在3个月内证明可规模化的增长模型。"
            )

        # Board control weak
        if state.board_control < 60:
            return (
                f"⚡ 董事会控制力偏弱（{state.board_control}），"
                "建议暂缓融资，先通过业绩提升增加谈判筹码。"
            )

        # Default
        return (
            "📈 市场关注度高，保持增长势头。"
            "建议准备月度投资人更新邮件，主动管理预期。"
        )
