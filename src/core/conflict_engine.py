"""Alpha 1.9 Conflict Engine: generates the monthly core conflict.

Each turn, the engine examines the company state and identifies the single
most pressing tension — the "核心矛盾" that defines the player's current
strategic situation. This gives the player a clear经营判断 every month.
"""

from __future__ import annotations

from src.core.models import CompanyState, ConflictSummary


class ConflictEngine:
    """Stateless engine that identifies the core monthly conflict.

    Pressure types: cash / pmf / growth / equity / delivery / competition / team
    Severity: low / medium / high
    """

    @staticmethod
    def identify(state: CompanyState) -> ConflictSummary:
        """Identify the single most pressing core conflict for the current state.

        Priority order (higher = more urgent):
        1. cash — runway < 3 or cash < monthly_burn
        2. pmf — low MRR despite high users or low product despite high spend
        3. equity — founder_equity < 50%
        4. growth — users < 50 after month 3
        5. delivery — high users, low product (quality risk)
        6. competition — market_share < 5 after month 3
        7. team — low morale
        """
        runway = state.runway_months
        cash = state.cash
        burn = state.monthly_burn
        product = state.product_score
        users = state.users
        mrr = state.mrr
        equity = state.founder_equity
        market_share = state.market_share
        morale = state.team_morale
        month = state.month

        # 1. Cash crisis (highest priority)
        if cash <= 0:
            return ConflictSummary(
                title="现金断裂",
                description="公司现金已耗尽，无法继续运营。这是最危急的时刻。",
                pressure_type="cash",
                severity="high",
                next_focus="立即融资或寻求收购，生存是第一位的。",
            )
        if runway < 2:
            return ConflictSummary(
                title="现金流危急",
                description=f"按当前烧钱速度，现金仅够撑{runway:.1f}个月。公司命悬一线，必须立刻行动。",
                pressure_type="cash",
                severity="high",
                next_focus="立即融资或大幅削减开支（建议月支出降至{burn//2//10000}万以下）。",
            )
        if cash < burn:
            return ConflictSummary(
                title="现金不足支撑当月运营",
                description=f"当前现金（{cash//10000}万）不足覆盖本月消耗（{burn//10000}万）。",
                pressure_type="cash",
                severity="high",
                next_focus="必须在本回合内获得融资或紧急削减成本。",
            )
        if runway < 4:
            return ConflictSummary(
                title="现金流紧张",
                description=f"现金流仅够支撑{runway:.1f}个月，公司需要在资金耗尽前找到出路。",
                pressure_type="cash",
                severity="medium",
                next_focus="启动融资准备或控制烧钱速度，争取更多时间。",
            )

        # 2. PMF / product-market fit
        if product >= 60 and mrr < 50000 and month >= 4:
            return ConflictSummary(
                title="产品好但商业化不足",
                description=f"产品分已达{product}，但MRR仅{mrr//10000}万。好产品没有换来好收入——这是PMF的典型信号。",
                pressure_type="pmf",
                severity="high",
                next_focus="加大营销投入，把产品优势转化为用户和收入增长。",
            )
        if product < 30 and month >= 4:
            return ConflictSummary(
                title="产品根基薄弱",
                description=f"产品分仅{product}，远低于竞品水平。用户来了也留不住，营销花再多也是浪费。",
                pressure_type="pmf",
                severity="high",
                next_focus="暂缓营销，集中资源打磨产品。产品是1，营销是后面的0。",
            )
        if product < 50 and users > 200:
            return ConflictSummary(
                title="高速增长下的产品债务",
                description=f"用户已达{users}，但产品分仅{product}。大量用户在用不够好的产品，口碑风险正在积累。",
                pressure_type="delivery",
                severity="medium",
                next_focus="在增长的同时加大研发投入，防止产品体验崩塌。",
            )

        # 3. Equity / control
        if equity < 34:
            return ConflictSummary(
                title="控制权危机",
                description=f"创始人股权仅剩{equity}%，已丧失重大事项否决权。公司名义上还是你的，实际上已经不属于你了。",
                pressure_type="equity",
                severity="high",
                next_focus="后续融资优先考虑债权或可转债，保护剩余股权。",
            )
        if equity < 50:
            return ConflictSummary(
                title="股权持续稀释",
                description=f"创始人股权降至{equity}%，再融资一轮可能失去绝对控制权。",
                pressure_type="equity",
                severity="medium",
                next_focus="慎重考虑下一轮融资的条款和估值，优先展示增长数据以获得更好的条件。",
            )

        # 4. Growth stagnation
        if users < 50 and month >= 6:
            return ConflictSummary(
                title="增长停滞",
                description=f"第{month}个月了，用户仅{users}人。市场对你的产品几乎没有反应——要么产品方向错了，要么获客渠道完全不通。",
                pressure_type="growth",
                severity="high",
                next_focus="重新审视产品定位和获客策略，考虑是否需要进行战略转型。",
            )
        if users < 100 and month >= 4:
            return ConflictSummary(
                title="用户增长缓慢",
                description=f"第{month}个月用户仅{users}人，增长速度远低于投资人预期。",
                pressure_type="growth",
                severity="medium",
                next_focus="增加营销投入或探索新的获客渠道，同时检查产品是否有留存问题。",
            )

        # 5. Competition
        if market_share < 5 and month >= 4:
            return ConflictSummary(
                title="市场份额被挤压",
                description=f"市场份额仅{market_share}%，竞品正在吞噬你的生存空间。",
                pressure_type="competition",
                severity="medium",
                next_focus="分析竞品策略，找到差异化定位或加大竞争性投入。",
            )

        # 6. Team morale
        if morale < 30:
            return ConflictSummary(
                title="团队士气崩溃",
                description=f"团队士气仅{morale}，核心员工正在流失。没有好的团队，一切计划都是空谈。",
                pressure_type="team",
                severity="high",
                next_focus="立即关注团队状态：安排团建、期权激励或调整工作节奏。",
            )
        if morale < 50:
            return ConflictSummary(
                title="团队士气偏低",
                description=f"团队士气{morale}，虽然还没到危机级别，但需要关注。",
                pressure_type="team",
                severity="medium",
                next_focus="适当投入团队建设，高士气能提升研发效率和人才吸引力。",
            )

        # 7. Healthy / no major conflict
        if product >= 60 and mrr >= 100000 and runway >= 6:
            return ConflictSummary(
                title="战略窗口期",
                description=f"公司状态良好：产品分{product}、MRR{mrr//10000}万、可支撑{runway:.1f}个月。你有选择的余地去思考下一步大动作。",
                pressure_type="growth",
                severity="low",
                next_focus="利用这段窗口期加速增长或准备A轮融资，不要浪费好状态。",
            )
        if product < 60 and month <= 3:
            return ConflictSummary(
                title="早期打磨期",
                description=f"第{month}个月，产品分{product}。现在是打磨产品的最佳窗口，你有时间和资源把产品做好。",
                pressure_type="pmf",
                severity="low",
                next_focus="专注研发，在竞品反应过来之前建立产品壁垒。",
            )

        # Default: moderate caution
        return ConflictSummary(
            title="稳健推进期",
            description=f"第{month}个月，各项指标在正常范围内。保持当前节奏，但也要警惕潜在风险。",
            pressure_type="growth",
            severity="low",
            next_focus="关注竞品动态和市场变化，为下一阶段增长做好准备。",
        )
