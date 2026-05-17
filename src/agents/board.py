"""Mock board member agents (董事会会议) using rule + template generation.

Alpha 1.3: Enhanced with conflicting perspectives. Each board member examines
the same CompanyState and ActionPlan but focuses on different concerns:
- CFO: cash flow / burn / runway — warns about overspending
- CTO: product score / R&D investment / tech debt — wants more resources
- COO: user growth / MRR / team efficiency — cares about execution
- Investor: valuation / equity / exit path — pushes for growth or exit
"""

from __future__ import annotations

from typing import Dict, List, Optional, Tuple

from src.agents.base_agent import BaseAgent
from src.core.models import ActionPlan, CompanyState, PlayerAction


class CFO(BaseAgent):
    """Chief Financial Officer — conservative, cash-flow focused."""

    def __init__(self) -> None:
        super().__init__(name="CFO", role="首席财务官", stance="保守")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        runway = state.runway_months
        total_spend = sum(a.budget for a in plan.actions if a.budget > 0)

        # Emergency: less than 4 months of runway
        if runway < 4:
            return (
                f"⚠️【CFO】现金只够{runway:.1f}个月！强烈建议立即融资或大幅削减开支。"
                f"当前月消耗{state.monthly_burn//10000}万，现金余额{state.cash//10000}万。"
                f"如果这个月烧钱不控制，下个月现金流就断了。"
            )

        # Check for fundraising action
        has_fundraising = any(a.type == "fundraising" for a in plan.actions)
        if has_fundraising:
            return (
                f"📊【CFO】按当前估值{state.valuation//10000}万，A轮投资人会要求至少20%股权。"
                f"建议在融资前先把MRR推到50万/月以上以获得更好条款，否则稀释太快。"
            )

        # High burn alert
        if total_spend > state.cash * 0.3 and state.runway_months < 8:
            return (
                f"🔴【CFO】本回合支出{total_spend//10000}万，占现金的{total_spend*100//state.cash}%。"
                f"跑道仅剩{runway:.1f}个月，我强烈反对这个预算。砍掉非核心开支，活下来再说。"
            )

        # MRR growth check
        if state.mrr > 0 and state.mrr < 300_000:
            return (
                f"📈【CFO】收入增长不错（MRR {state.mrr//10000}万/月），但毛利率需要关注。"
                f"持续控制获客成本，确保LTV/CAC > 3。不建议大规模扩团队。"
            )

        # Default — healthy
        return (
            f"✅【CFO】本月现金流正常（跑道{runway:.1f}个月），"
            f"月烧{state.monthly_burn//10000}万。保持现有节奏，预留至少6个月安全垫。"
        )


class CTO(BaseAgent):
    """Chief Technology Officer — product & long-term moat focused."""

    def __init__(self) -> None:
        super().__init__(name="CTO", role="首席技术官", stance="重视产品")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        has_product = any(a.type == "product" for a in plan.actions)
        has_team = any(a.type == "team" for a in plan.actions)
        product_budget = sum(a.budget for a in plan.actions if a.type == "product")

        # Product quality is weak
        if state.product_score < 30:
            if not has_product:
                return (
                    f"🔧【CTO】产品还太弱（产品分{state.product_score}），你居然这回合不做研发？"
                    f"产品是根本，没有好产品一切增长都是空中楼阁。强烈要求至少投入5万做产品。"
                )
            return (
                f"🔧【CTO】产品分仅{state.product_score}，现在这点投入远远不够。"
                f"建议大幅增加研发预算，把产品分推到50以上，否则用户留存会越来越差。"
            )

        # Product is strong
        if state.product_score > 70:
            return (
                f"👍【CTO】产品口碑不错（产品分{state.product_score}），"
                f"可以考虑做企业级功能增加客单价，或者申请技术专利建立壁垒。"
                f"现在正是加大研发投入、拉开差距的时候，别松懈。"
            )

        # Team expansion — check before product budget complaint
        if has_team:
            return (
                f"👥【CTO】扩团队要注意技术债积累。新老人配比1:2，"
                f"新人前2个月以熟悉代码库和修bug为主。另外需要同步升级CI/CD基础设施。"
            )

        # Need more R&D budget
        if product_budget < 50_000 and state.product_score < 60:
            return (
                f"💡【CTO】研发投入不足（本回合仅{product_budget//10000}万）。"
                f"产品分{state.product_score}离优秀还有距离，继续省钱只会被竞品追上。"
                f"建议把研发预算至少加3倍。"
            )

        # Default
        return (
            f"💻【CTO】技术路线稳健（产品分{state.product_score}），"
            f"继续按计划迭代。关注系统可扩展性，为增长做准备。建议每周代码评审。"
        )


class COO(BaseAgent):
    """Chief Operating Officer — execution & team focused."""

    def __init__(self) -> None:
        super().__init__(name="COO", role="首席运营官", stance="重视执行")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        has_marketing = any(a.type == "marketing" for a in plan.actions)

        # Low morale
        if state.team_morale < 50:
            return (
                f"😟【COO】团队士气偏低（{state.team_morale}），这是最大的风险。"
                f"建议立即做团建活动或考虑期权激励计划。核心员工流失风险非常高，"
                f"一旦关键人走了，产品交付和客户服务都会受影响。"
            )

        # High morale
        if state.team_morale > 80:
            return (
                f"🎯【COO】团队状态很好（士气{state.team_morale}），"
                f"现在推关键项目效率最高。建议趁热打铁：要么推营销抢占市场，"
                f"要么加研发打磨产品。不要错过团队战斗力的窗口期。"
            )

        # Marketing with low runway — direct conflict with CTO
        runway = state.runway_months
        if has_marketing and runway < 4:
            return (
                f"⚠️【COO】现金流紧张（跑道{runway:.1f}个月），"
                f"此时投放市场ROI很难回正。建议暂停营销投入，优先保证核心产品交付。"
                f"用户增长可以等等，但现金断了就什么都没了。"
            )

        # User growth concern
        if state.users < 100 and state.month >= 3:
            return (
                f"📋【COO】用户数仅{state.users}，月{state.month}了还在这个量级是个危险信号。"
                f"不管是通过营销还是自然增长，必须在接下来3个月内证明增长能力。"
                f"建议把本回合预算至少一半用于获客。"
            )

        # Default
        return (
            f"📋【COO】日常运营稳定。关注交付质量和客户满意度，"
            f"定期复盘各项目进度，识别瓶颈及时调整。用户反馈要每条都回。"
        )


class InvestorDirector(BaseAgent):
    """Investor Director (投资方董事) — growth & control focused."""

    def __init__(self) -> None:
        super().__init__(name="投资方董事", role="投资方董事", stance="重视增长")

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        # Founder losing control
        if state.founder_equity < 50:
            return (
                f"⚠️【投资方】创始人持股已降至{state.founder_equity}%，"
                f"下轮融资后可能失去控制权。现在必须证明增长曲线，否则我们投资方"
                f"会认真考虑管理层调整。建议立即聚焦增长：砍掉无效开支，all-in一条主线。"
            )

        # Slow growth
        if state.mrr < 100_000 and state.month >= 6:
            return (
                f"📉【投资方】增长太慢了——MRR仅{state.mrr//10000}万/月，"
                f"月{state.month}了还没有PMF信号。投资委员会已经开始质疑。"
                f"需要在3个月内证明可规模化的增长模型，否则下一轮融不到钱。"
            )

        # Board control weak
        if state.board_control < 60:
            return (
                f"⚡【投资方】董事会控制力偏弱（{state.board_control}%），"
                f"暂缓融资是对的。先通过业绩提升增加谈判筹码，"
                f"否则下轮融资条款会很苛刻。当前第一要务：把数字做漂亮。"
            )

        # Growth pressure
        if state.mrr < 200_000 and state.month <= 6:
            return (
                f"🚀【投资方】早期阶段最重要的是增长斜率。"
                f"不要太关注利润率，现在的每一分钱都应该用来换增长。"
                f"如果这个月MRR增长不到20%，建议重新审视策略。"
            )

        # Default
        return (
            f"📈【投资方】市场关注度高，保持增长势头。"
            f"建议准备月度投资人更新邮件，主动管理预期。"
            f"下一个里程碑是MRR 50万/月，达到后可以启动A轮融资。"
        )


# ── Board meeting minutes generator ─────────────────────────────────────────────

def generate_board_minutes(
    state: CompanyState,
    plan: ActionPlan,
    board_feedback: Dict[str, str],
) -> str:
    """Generate formatted board meeting minutes with conflict highlights.

    Highlights where board members disagree based on their roles.
    """
    lines: List[str] = []
    lines.append("=" * 60)
    lines.append(f"  第{state.month}月度董事会会议记录")
    lines.append("=" * 60)
    lines.append("")

    # ── State snapshot ──────────────────────────────────────────────────────
    lines.append("【公司现状】")
    lines.append(f"  现金: {state.cash//10000}万  跑道: {state.runway_months:.1f}月")
    lines.append(f"  MRR: {state.mrr//10000}万  用户: {state.users}")
    lines.append(f"  产品分: {state.product_score}  士气: {state.team_morale}")
    lines.append(f"  股权: {state.founder_equity}%  董事会: {state.board_control}%")
    lines.append(f"  估值: {state.valuation//10000}万  市场份额: {state.market_share}%")
    lines.append("")

    # ── Action summary ──────────────────────────────────────────────────────
    if plan.actions:
        lines.append("【本回合行动】")
        for a in plan.actions:
            desc = f"  {a.type.value}: 预算{a.budget//10000}万"
            if a.type.value == "fundraising" and a.fundraise_amount > 0:
                desc += f" 融资{a.fundraise_amount//10000}万 出让{a.equity_offered}%"
            lines.append(desc)
        lines.append("")

    # ── Each board member's speech ──────────────────────────────────────────
    lines.append("【董事发言】")
    for name, speech in board_feedback.items():
        lines.append(f"  {speech}")
    lines.append("")

    # ── Conflict detection ──────────────────────────────────────────────────
    conflicts = _detect_conflicts(state, plan, board_feedback)
    if conflicts:
        lines.append("【⚠️ 分歧焦点】")
        for conflict in conflicts:
            lines.append(f"  ⚡ {conflict}")
        lines.append("")

    lines.append("=" * 60)
    return "\n".join(lines)


def _detect_conflicts(
    state: CompanyState,
    plan: ActionPlan,
    _feedback: Dict[str, str],
) -> List[str]:
    """Detect conflicts between board members based on state and actions."""
    conflicts: List[str] = []

    has_marketing = any(a.type == "marketing" for a in plan.actions)
    has_product = any(a.type == "product" for a in plan.actions)
    has_fundraising = any(a.type == "fundraising" for a in plan.actions)
    has_team = any(a.type == "team" for a in plan.actions)

    total_spend = sum(a.budget for a in plan.actions if a.type.value != "fundraising")

    # CFO vs CTO: cut budget vs invest in product
    if state.runway_months < 6 and has_product:
        conflicts.append(
            f"CFO要求控制烧钱（跑道{state.runway_months:.1f}月） vs "
            f"CTO坚持研发投入（产品分{state.product_score}）。两者立场截然相反。"
        )

    # CFO vs COO: conserve cash vs grow users
    if state.cash < 500_000 and has_marketing:
        conflicts.append(
            f"CFO警告现金流紧张（仅剩{state.cash//10000}万）vs "
            f"COO认为不投营销就失去增长窗口。"
        )

    # CFO vs Investor: raise now vs conserve equity
    if state.runway_months < 4 and not has_fundraising:
        conflicts.append(
            f"CFO可能建议立即融资保命 vs 投资方董事担心融资条款过于不利。"
        )

    # CTO vs Investor: long-term tech moat vs short-term growth
    if state.product_score < 40 and state.mrr < 100_000:
        conflicts.append(
            f"CTO主张先打磨产品再推广 vs 投资方董事要求先证明增长再谈产品。"
            f"这是一场经典的'增长还是产品'之争。"
        )

    # COO vs CTO: hire vs build
    if has_team and has_product and state.cash < 1_000_000:
        conflicts.append(
            f"COO要扩团队提效率 vs CTO要加研发预算，"
            f"但资源有限，二者难以同时满足。"
        )

    # High total spend with limited cash
    if total_spend > state.cash * 0.4 and state.runway_months >= 4:
        conflicts.append(
            f"本回合非融资支出{total_spend//10000}万，"
            f"占现金{total_spend*100//max(state.cash,1)}%。"
            f"多个董事对支出规模有争议。"
        )

    # Low product with fundraising focus
    if has_fundraising and state.product_score < 40:
        conflicts.append(
            f"投资方支持融资但CTO指出产品分仅{state.product_score}，"
            f"融资后估值可能不理想。需要先提升产品吗？"
        )

    return conflicts
