"""Mock board member agents (董事会会议) using rule + template generation.

Alpha 1.3: Enhanced with conflicting perspectives. Each board member examines
the same CompanyState and ActionPlan but focuses on different concerns:
- CFO: cash flow / burn / runway — warns about overspending
- CTO: product score / R&D investment / tech debt — wants more resources
- COO: user growth / MRR / team efficiency — cares about execution
- Investor: valuation / equity / exit path — pushes for growth or exit

Alpha 1.9.1: Named investment firms with distinct styles and personalities.
"""

from __future__ import annotations

import hashlib

from src.agents.base_agent import BaseAgent
from src.core.models import ActionPlan, CompanyState

# ── Named investors ──────────────────────────────────────────────────────────

INVESTOR_POOL = [
    {
        "name": "红杉中国",
        "full_name": "红杉中国 — 创始合伙人 周逵",
        "type": "VC",
        "check_range": "2000万–1亿",
        "focus_stage": "A轮/B轮",
        "style": "激进增长",
        "personality": "只看增长斜率，能接受高烧钱率换取市场领先地位。常说的话：'不增长就是等死。'",
    },
    {
        "name": "经纬中国",
        "full_name": "经纬中国 — 合伙人 万浩基",
        "type": "VC",
        "check_range": "1000万–5000万",
        "focus_stage": "早期/A轮",
        "style": "产品技术导向",
        "personality": "对技术壁垒有执念，认为产品好自然增长。常说的话：'先把产品打磨到让人无法拒绝。'",
    },
    {
        "name": "高瓴资本",
        "full_name": "高瓴资本 — 执行董事 李岳",
        "type": "PE/VC",
        "check_range": "5000万–5亿",
        "focus_stage": "成长期/B轮+",
        "style": "长期价值投资",
        "personality": "不急于退出，关注商业模式的可持续性。常说的话：'做时间的朋友，不要为了融资而融资。'",
    },
    {
        "name": "真格基金",
        "full_name": "真格基金 — 合伙人 方爱之",
        "type": "天使/VC",
        "check_range": "300万–2000万",
        "focus_stage": "天使/种子/A轮",
        "style": "创始人友好",
        "personality": "对创始人有天然的信任和耐心，重视团队文化和愿景。常说的话：'我们投的是你这个人，相信你能做出对的事。'",
    },
    {
        "name": "源码资本",
        "full_name": "源码资本 — 合伙人 黄云刚",
        "type": "VC",
        "check_range": "1000万–8000万",
        "focus_stage": "早期/成长期",
        "style": "精实均衡",
        "personality": "关注单位经济模型，强调健康增长而非盲目扩张。常说的话：'验证了PMF再放量，数据不会骗人。'",
    },
    {
        "name": "险峰长青",
        "full_name": "险峰长青 — 合伙人 赵阳",
        "type": "VC",
        "check_range": "500万–3000万",
        "focus_stage": "早期/A轮",
        "style": "务实稳健",
        "personality": "偏保守，强调现金流管理和生存优先。常说的话：'活下来是第一位的，增长是第二位的。'",
    },
    {
        "name": "蓝驰创投",
        "full_name": "蓝驰创投 — 管理合伙人 陈维广",
        "type": "VC",
        "check_range": "1000万–6000万",
        "focus_stage": "早期/A轮",
        "style": "技术+增长双驱",
        "personality": "相信技术驱动增长的复利效应，愿意在技术上有耐心的同时推动商业化。常说的话：'技术底座扎实了，增长只是时间问题。'",
    },
    {
        "name": "沈南鹏",
        "full_name": "沈南鹏 — 个人天使投资人",
        "type": "个人",
        "check_range": "300万–2000万",
        "focus_stage": "天使/早期",
        "style": "精英主义",
        "personality": "看人极准，只投最优秀的创始人。对创业者要求极高但一旦投资就全力支持。常说的话：'创始人决定天花板，团队决定能不能走到天花板。'",
    },
]


def pick_investor_for_session(session_id: int, founder_equity: int) -> dict | None:
    """Pick a named investor for this session. Returns None if no investment taken."""
    if founder_equity >= 100:
        return None
    # Deterministic pick based on session_id
    idx = int(hashlib.md5(f"investor_{session_id}".encode()).hexdigest(), 16) % len(INVESTOR_POOL)
    return INVESTOR_POOL[idx]


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
                f"现金流仅够支撑{runway:.1f}个月，我强烈反对这个预算。砍掉非核心开支，活下来再说。"
            )

        # MRR growth check
        if state.mrr > 0 and state.mrr < 300_000:
            return (
                f"📈【CFO】收入增长不错（MRR {state.mrr//10000}万/月），但毛利率需要关注。"
                f"持续控制获客成本，确保LTV/CAC > 3。不建议大规模扩团队。"
            )

        # Default — healthy
        return (
            f"✅【CFO】本月现金流正常（可支撑{runway:.1f}个月），"
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
                "👥【CTO】扩团队要注意技术债积累。新老人配比1:2，"
                "新人前2个月以熟悉代码库和修bug为主。另外需要同步升级CI/CD基础设施。"
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
                f"⚠️【COO】现金流紧张（可支撑{runway:.1f}个月），"
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
            "📋【COO】日常运营稳定。关注交付质量和客户满意度，"
            "定期复盘各项目进度，识别瓶颈及时调整。用户反馈要每条都回。"
        )


class InvestorDirector(BaseAgent):
    """Investor Director — now named and styled based on which firm invested.

    Alpha 1.9.1: Uses named investment firms from INVESTOR_POOL with distinct
    personalities that influence their board feedback.
    """

    def __init__(self, investor_profile: dict | None = None) -> None:
        if investor_profile:
            name = investor_profile["name"]
            role = investor_profile["full_name"]
            self.investor_style = investor_profile["style"]
            self._personality = investor_profile["personality"]
        else:
            name = "投资方董事"
            role = "投资方董事"
            self.investor_style = "重视增长"
            self._personality = ""
        super().__init__(name=name, role=role, stance=self.investor_style)

    def speak(self, state: CompanyState, plan: ActionPlan) -> str:
        tag = f"【{self.name}】"

        # Founder losing control
        if state.founder_equity < 50:
            return (
                f"⚠️{tag}创始人持股已降至{state.founder_equity}%，"
                f"下轮融资后可能失去控制权。现在必须证明增长曲线，否则我们会"
                f"认真考虑管理层调整。建议立即聚焦增长：砍掉无效开支，all-in一条主线。"
            )

        # Slow growth
        if state.mrr < 100_000 and state.month >= 6:
            return (
                f"📉{tag}增长太慢了——MRR仅{state.mrr//10000}万/月，"
                f"月{state.month}了还没有PMF信号。投资委员会已经开始质疑。"
                f"需要在3个月内证明可规模化的增长模型，否则下一轮融不到钱。"
            )

        # Board control weak
        if state.board_control < 60:
            return (
                f"⚡{tag}董事会控制力偏弱（{state.board_control}%），"
                f"暂缓融资是对的。先通过业绩提升增加谈判筹码，"
                f"否则下轮融资条款会很苛刻。当前第一要务：把数字做漂亮。"
            )

        # Growth pressure — style-dependent
        if state.mrr < 200_000 and state.month <= 6:
            if "增长" in self.investor_style or "激进" in self.investor_style:
                return (
                    f"🚀{tag}早期阶段最重要的是增长斜率。"
                    f"不要太关注利润率，现在的每一分钱都应该用来换增长。"
                    f"如果这个月MRR增长不到20%，建议重新审视策略。"
                )
            elif "产品" in self.investor_style or "技术" in self.investor_style:
                return (
                    f"🔧{tag}产品技术是根基。MRR{state.mrr//10000}万/月还不够，"
                    f"但与其烧钱买量不如打磨产品。产品做好了，用户自然会来。"
                )
            elif "长期" in self.investor_style or "价值" in self.investor_style:
                return (
                    f"📊{tag}不用太焦虑短期增长节奏。"
                    f"关键是把商业模式跑通，确保单位经济模型健康。"
                    f"我们有耐心，但需要看到明确的PMF方向。"
                )
            else:
                return (
                    f"📋{tag}MRR{state.mrr//10000}万/月，继续稳步推进。"
                    f"保持现金纪律，不要为了增长而牺牲财务健康。"
                )

        # Default — style-dependent
        if self.investor_style == "激进增长":
            return (
                f"📈{tag}市场关注度高，保持增长势头。"
                f"下一个里程碑是MRR 50万/月，达到后可以启动A轮融资。"
                f"不要减速——现在正是抢市场的窗口期。"
            )
        elif self.investor_style == "产品技术导向":
            return (
                f"👍{tag}产品口碑不错（{state.product_score}分），继续深耕。"
                f"技术壁垒才是真正的护城河。建议每季度做一次技术评审。"
            )
        elif self.investor_style == "长期价值投资":
            return (
                f"📊{tag}保持节奏，我们不急于退出。"
                f"重点验证商业模式的长期可持续性，别被短期数字绑架。"
            )
        elif self.investor_style == "创始人友好":
            return (
                f"🤝{tag}状态不错，继续按你的节奏走。"
                f"我们投的是你这个人，有问题随时沟通，别自己扛。"
            )
        elif "均衡" in self.investor_style or "稳健" in self.investor_style:
            return f"📋{tag}保持现有节奏，稳扎稳打。" f"建议准备月度投资人更新邮件，主动管理预期。"
        else:
            return (
                f"📈{tag}市场关注度高，保持增长势头。"
                f"建议准备月度投资人更新邮件，主动管理预期。"
                f"下一个里程碑是MRR 50万/月。"
            )


# ── Board meeting minutes generator ─────────────────────────────────────────────


def generate_board_minutes(
    state: CompanyState,
    plan: ActionPlan,
    board_feedback: dict[str, str],
) -> str:
    """Generate formatted board meeting minutes with conflict highlights.

    Highlights where board members disagree based on their roles.
    """
    lines: list[str] = []
    lines.append("=" * 60)
    lines.append(f"  第{state.month}月度董事会会议记录")
    lines.append("=" * 60)
    lines.append("")

    # ── State snapshot ──────────────────────────────────────────────────────
    lines.append("【公司现状】")
    lines.append(f"  现金: {state.cash//10000}万  可支撑: {state.runway_months:.1f}月")
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
    for _name, speech in board_feedback.items():
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
    _feedback: dict[str, str],
) -> list[str]:
    """Detect conflicts between board members based on state and actions."""
    conflicts: list[str] = []

    has_marketing = any(a.type == "marketing" for a in plan.actions)
    has_product = any(a.type == "product" for a in plan.actions)
    has_fundraising = any(a.type == "fundraising" for a in plan.actions)
    has_team = any(a.type == "team" for a in plan.actions)

    total_spend = sum(a.budget for a in plan.actions if a.type.value != "fundraising")

    # CFO vs CTO: cut budget vs invest in product
    if state.runway_months < 6 and has_product:
        conflicts.append(
            f"CFO要求控制烧钱（可支撑{state.runway_months:.1f}月） vs "
            f"CTO坚持研发投入（产品分{state.product_score}）。两者立场截然相反。"
        )

    # CFO vs COO: conserve cash vs grow users
    if state.cash < 500_000 and has_marketing:
        conflicts.append(
            f"CFO警告现金流紧张（仅剩{state.cash//10000}万）vs " f"COO认为不投营销就失去增长窗口。"
        )

    # CFO vs Investor: raise now vs conserve equity
    if state.runway_months < 4 and not has_fundraising:
        conflicts.append("CFO可能建议立即融资保命 vs 投资方董事担心融资条款过于不利。")

    # CTO vs Investor: long-term tech moat vs short-term growth
    if state.product_score < 40 and state.mrr < 100_000:
        conflicts.append(
            "CTO主张先打磨产品再推广 vs 投资方董事要求先证明增长再谈产品。"
            "这是一场经典的'增长还是产品'之争。"
        )

    # COO vs CTO: hire vs build
    if has_team and has_product and state.cash < 1_000_000:
        conflicts.append("COO要扩团队提效率 vs CTO要加研发预算，" "但资源有限，二者难以同时满足。")

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
