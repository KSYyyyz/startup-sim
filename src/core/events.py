"""Alpha 1.3 expanded event pool: 27 narrative events across 3 categories.

Categories:
- opportunity: 大客户签约、媒体报道、技术突破、政策利好、竞品失误
- crisis: 服务器宕机、核心员工离职、客户投诉爆发、竞品挖墙脚、数据泄露
- neutral: 行业展会、投资人主动接触、团队内部摩擦

Design:
- Each event has condition_fn based on CompanyState
- Each event delta ≤ ±3 product / ±5 morale / ±2 market share
- Events sampled at ~20% per turn → ~2.4 events per 12 turns
- No duplicates with existing fixed events (runway_warning, board_coup_risk, product_breakthrough)
"""

from __future__ import annotations

import random
from typing import Callable, List, Optional

from src.core.models import CompanyState, GameEvent, StateDelta


class EventDef:
    """Definition of a pool event with condition and delta."""

    __slots__ = (
        "event_type", "category", "title", "description",
        "condition_fn", "delta", "probability",
    )

    def __init__(
        self,
        event_type: str,
        category: str,
        title: str,
        description: str,
        condition_fn: Callable[[CompanyState], bool],
        delta: StateDelta,
        probability: float = 0.03,
    ) -> None:
        self.event_type = event_type
        self.category = category
        self.title = title
        self.description = description
        self.condition_fn = condition_fn
        self.delta = delta
        self.probability = probability

    def to_game_event(self) -> GameEvent:
        return GameEvent(
            event_type=self.event_type,
            description=f"{self.title}：{self.description}",
            delta=self.delta,
        )


# ── Event pool ──────────────────────────────────────────────────────────────────

EVENT_POOL: List[EventDef] = [
    # ═══ 机会类 (opportunity) ═══════════════════════════════════════════════════
    EventDef(
        event_type="evt_big_client",
        category="opportunity",
        title="🎯 大客户签约",
        description="一家中型企业决定采购你的产品，带来稳定的MRR增长。团队士气大振。",
        condition_fn=lambda s: s.product_score >= 40 and s.reputation >= 40,
        delta=StateDelta(mrr=30_000, reputation=2, users=20, reasons=["大客户签约: MRR+3万, 声誉+2, 用户+20"]),
    ),
    EventDef(
        event_type="evt_media_coverage",
        category="opportunity",
        title="📰 媒体报道",
        description="知名科技媒体发表了关于你产品的正面报道，自然流量暴涨。",
        condition_fn=lambda s: s.reputation >= 35 or s.product_score >= 60,
        delta=StateDelta(users=30, reputation=3, reasons=["媒体报道: 用户+30, 声誉+3"]),
    ),
    EventDef(
        event_type="evt_tech_insight",
        category="opportunity",
        title="💡 技术洞察",
        description="研发团队在架构评审中发现了一个关键优化点，产品体验将显著提升。",
        condition_fn=lambda s: s.product_score >= 30 and s.team_morale >= 50,
        delta=StateDelta(product_score=2, reasons=["技术洞察: 产品分+2"]),
    ),
    EventDef(
        event_type="evt_policy_boost",
        category="opportunity",
        title="🏛️ 政策利好",
        description="政府发布了支持SaaS行业的新政策，你的目标市场获得税收优惠和采购倾斜。",
        condition_fn=lambda s: True,
        delta=StateDelta(market_share=2, reputation=1, reasons=["政策利好: 市场份额+2, 声誉+1"]),
    ),
    EventDef(
        event_type="evt_competitor_stumble",
        category="opportunity",
        title="🎲 竞品失误",
        description="竞争对手的一次版本更新出现严重Bug，大量用户在社交媒体上吐槽并寻找替代方案。",
        condition_fn=lambda s: s.product_score >= 30,
        delta=StateDelta(users=15, market_share=1, reasons=["竞品失误: 用户+15, 市场份额+1"]),
    ),
    EventDef(
        event_type="evt_viral_organic",
        category="opportunity",
        title="🔥 自然裂变",
        description="一位行业KOL在社交媒体上自发推荐了你的产品，引发了小范围的病毒式传播。",
        condition_fn=lambda s: s.users >= 100 and s.reputation >= 40,
        delta=StateDelta(users=25, reputation=2, reasons=["自然裂变: 用户+25, 声誉+2"]),
    ),
    EventDef(
        event_type="evt_key_hire",
        category="opportunity",
        title="⭐ 关键人才入职",
        description="一位资深工程师被你的愿景打动，降薪加入团队。技术实力明显增强。",
        condition_fn=lambda s: s.reputation >= 50 and s.team_morale >= 60,
        delta=StateDelta(product_score=1, team_morale=4, reasons=["关键人才入职: 产品分+1, 士气+4"]),
    ),
    EventDef(
        event_type="evt_channel_partner",
        category="opportunity",
        title="🤝 渠道合作",
        description="一家咨询公司主动提出渠道合作，将你的产品打包进他们的解决方案。",
        condition_fn=lambda s: s.product_score >= 50 and s.reputation >= 40,
        delta=StateDelta(mrr=20_000, market_share=1, reasons=["渠道合作: MRR+2万, 市场份额+1"]),
    ),
    EventDef(
        event_type="evt_award_finalist",
        category="opportunity",
        title="🏆 行业奖项入围",
        description="你的产品入围了年度企业服务创新奖，行业认可度大幅提升。",
        condition_fn=lambda s: s.product_score >= 55,
        delta=StateDelta(reputation=3, team_morale=3, reasons=["行业奖项入围: 声誉+3, 士气+3"]),
    ),
    EventDef(
        event_type="evt_referral_wave",
        category="opportunity",
        title="📣 口碑推荐潮",
        description="老客户自发推荐带来了批量新用户，且转化率远高于市场投放。",
        condition_fn=lambda s: s.users >= 200 and s.product_score >= 50,
        delta=StateDelta(users=20, mrr=15_000, reasons=["口碑推荐潮: 用户+20, MRR+1.5万"]),
    ),

    # ═══ 危机类 (crisis) ═════════════════════════════════════════════════════════
    EventDef(
        event_type="evt_server_crash",
        category="crisis",
        title="💥 服务器宕机",
        description="云服务商区域性故障导致服务中断4小时，用户在社交媒体上抱怨不断。",
        condition_fn=lambda s: s.users >= 50,
        delta=StateDelta(reputation=-3, users=-15, reasons=["服务器宕机: 声誉-3, 用户-15"]),
    ),
    EventDef(
        event_type="evt_key_employee_quit",
        category="crisis",
        title="👋 核心员工离职",
        description="一位早期核心工程师接受了竞品的高薪挖角，临走前带走了大量隐性知识。",
        condition_fn=lambda s: s.team_morale < 60,
        delta=StateDelta(team_morale=-5, product_score=-1, reasons=["核心员工离职: 士气-5, 产品分-1"]),
    ),
    EventDef(
        event_type="evt_complaint_wave",
        category="crisis",
        title="📢 客户投诉潮",
        description="产品界面的一个改动引发了老用户的集体不满，社交媒体上出现了负面讨论。",
        condition_fn=lambda s: s.product_score < 50,
        delta=StateDelta(reputation=-3, users=-10, reasons=["客户投诉潮: 声誉-3, 用户-10"]),
    ),
    EventDef(
        event_type="evt_competitor_poach",
        category="crisis",
        title="🕵️ 竞品挖角",
        description="竞品以高出30%的薪资试图挖走你的核心团队成员。",
        condition_fn=lambda s: s.team_morale < 70 and s.product_score >= 40,
        delta=StateDelta(team_morale=-3, product_score=-2, reasons=["竞品挖角: 士气-3, 产品分-2"]),
    ),
    EventDef(
        event_type="evt_data_leak_rumor",
        category="crisis",
        title="🔓 数据安全传闻",
        description="行业论坛上出现了关于你产品数据安全的质疑帖，部分客户开始担忧。",
        condition_fn=lambda s: True,
        delta=StateDelta(reputation=-5, users=-20, reasons=["数据安全传闻: 声誉-5, 用户-20"]),
    ),
    EventDef(
        event_type="evt_payment_glitch",
        category="crisis",
        title="💳 支付系统故障",
        description="支付网关升级导致部分客户被重复扣款，客服电话被打爆。",
        condition_fn=lambda s: s.mrr > 50_000,
        delta=StateDelta(mrr=-15_000, reputation=-2, reasons=["支付系统故障: MRR-1.5万, 声誉-2"]),
    ),
    EventDef(
        event_type="evt_regulatory_inquiry",
        category="crisis",
        title="⚖️ 监管问询",
        description="行业监管机构对你的数据合规性提出问询，需要投入时间精力应对。",
        condition_fn=lambda s: s.market_share >= 8,
        delta=StateDelta(market_share=-1, reputation=-2, reasons=["监管问询: 市场份额-1, 声誉-2"]),
    ),
    EventDef(
        event_type="evt_infra_cost_spike",
        category="crisis",
        title="📈 基础设施涨价",
        description="云服务商突然调整计费模式，你的月度基础设施成本上涨。",
        condition_fn=lambda s: s.users >= 200,
        delta=StateDelta(monthly_burn=5_000, reasons=["基础设施涨价: 月度消耗+5000"]),
    ),
    EventDef(
        event_type="evt_investor_doubt",
        category="crisis",
        title="📉 投资人信心动摇",
        description="一位早期天使投资人私下表达了对增长速度的担忧，可能影响后续融资。",
        condition_fn=lambda s: s.valuation > 5_000_000 and s.runway_months < 6,
        delta=StateDelta(valuation=-500_000, team_morale=-2, reasons=["投资人信心动摇: 估值-50万, 士气-2"]),
    ),
    EventDef(
        event_type="evt_customer_churn_spike",
        category="crisis",
        title="📤 客户集中流失",
        description="一批中小客户在合同到期后未续约，据反馈是因为缺少某个关键功能。",
        condition_fn=lambda s: s.users >= 100 and s.mrr >= 100_000,
        delta=StateDelta(users=-25, mrr=-20_000, reasons=["客户集中流失: 用户-25, MRR-2万"]),
    ),

    # ═══ 中性类 (neutral) ════════════════════════════════════════════════════════
    EventDef(
        event_type="evt_industry_conference",
        category="neutral",
        title="🎤 行业大会",
        description="年度行业大会邀请你参展，展位费和差旅费需要一笔开支，但曝光价值可观。",
        condition_fn=lambda s: True,
        delta=StateDelta(reputation=2, cash=-30_000, reasons=["行业大会: 声誉+2, 现金-3万"]),
    ),
    EventDef(
        event_type="evt_investor_intro",
        category="neutral",
        title="🤝 投资人引荐",
        description="一位行业前辈主动引荐了几位A轮投资人，公司在投资圈的关注度上升。",
        condition_fn=lambda s: s.product_score >= 40 or s.mrr >= 100_000,
        delta=StateDelta(valuation=300_000, reasons=["投资人引荐: 估值+30万"]),
    ),
    EventDef(
        event_type="evt_team_conflict",
        category="neutral",
        title="⚡ 团队内部分歧",
        description="产品和技术团队在下一阶段优先级上产生了激烈争论，短期影响协作效率。",
        condition_fn=lambda s: s.employee_count >= 5,
        delta=StateDelta(team_morale=-3, reasons=["团队内部分歧: 士气-3"]),
    ),
    EventDef(
        event_type="evt_market_rumor",
        category="neutral",
        title="🌐 市场传闻",
        description="业界传闻某互联网大厂也看中了这个赛道，市场关注度提升但竞争阴影也浮现了。",
        condition_fn=lambda s: True,
        delta=StateDelta(reasons=["市场传闻: 无直接影响，但引发行业关注"]),
    ),
    EventDef(
        event_type="evt_user_feature_requests",
        category="neutral",
        title="💬 用户需求爆发",
        description="用户社区里出现了大量产品改进建议，虽然增加了噪音但也带来了有价值的洞察。",
        condition_fn=lambda s: s.users >= 50,
        delta=StateDelta(product_score=1, reasons=["用户需求反馈: 产品分+1（来自用户洞察）"]),
    ),
    EventDef(
        event_type="evt_acquihire_inquiry",
        category="neutral",
        title="📞 收购意向接触",
        description="一家上市公司通过猎头试探收购意向，团队内部人心浮动但估值参考价值上升。",
        condition_fn=lambda s: s.product_score >= 60 and s.team_morale >= 50,
        delta=StateDelta(team_morale=-2, reputation=1, reasons=["收购意向接触: 士气-2, 声誉+1"]),
    ),
    EventDef(
        event_type="evt_tech_paradigm_shift",
        category="neutral",
        title="🔮 技术范式变化",
        description="开源社区发布了一个可能与你的核心功能重叠的框架，需要评估影响。",
        condition_fn=lambda s: s.product_score < 40,
        delta=StateDelta(product_score=-1, reasons=["技术范式变化: 产品分-1（技术债暴露）"]),
    ),
]


def sample_random_events(
    current: CompanyState,
    triggered: set,
    base_chance: float = 0.20,
) -> List[GameEvent]:
    """Sample one random event from the eligible pool.

    Args:
        current: Current company state for condition checking.
        triggered: Set of already-triggered event types (dedup).
        base_chance: Probability of firing an event this turn (~20% → 2.4/12turns).

    Returns:
        List of 0-1 GameEvent objects.
    """
    if random.random() > base_chance:
        return []

    eligible = [
        e for e in EVENT_POOL
        if e.condition_fn(current) and e.event_type not in triggered
    ]
    if not eligible:
        return []

    chosen = random.choice(eligible)
    triggered.add(chosen.event_type)
    return [chosen.to_game_event()]


def get_event_summary() -> dict:
    """Return summary stats about the event pool (for debugging/reporting)."""
    return {
        "total": len(EVENT_POOL),
        "opportunity": sum(1 for e in EVENT_POOL if e.category == "opportunity"),
        "crisis": sum(1 for e in EVENT_POOL if e.category == "crisis"),
        "neutral": sum(1 for e in EVENT_POOL if e.category == "neutral"),
    }
