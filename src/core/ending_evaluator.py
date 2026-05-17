"""Ending evaluator: determines if the game has reached an ending condition.

Alpha 1.3: Added player path classification and narrative variants.
- classify_player_path(state) → R&D/营销/融资/均衡/保守
- describe_ending now accepts optional path for variant narratives

Five endings (unchanged conditions):
- BANKRUPTCY: cash <= 0
- FOUNDER_REMOVED: equity < 34 AND board < 45 AND runway < 4
- SERIES_A_SUCCESS: month >= 12 AND mrr >= 300k AND product >= 65 AND equity >= 50
- SURVIVED_BUT_AVERAGE: month >= 12 AND mrr >= 100k AND cash > 0
- SLOW_DEATH: month >= 12 (catch-all)
"""

from __future__ import annotations

import enum

from src.core.models import CompanyState, EndingType


class PlayerPath(str, enum.Enum):
    """Player strategy archetype based on final state."""

    RND = "rnd"  # 研发派: high product, low marketing
    MARKETING = "marketing"  # 营销派: high users, moderate product
    FUNDRAISE = "fundraise"  # 融资派: low equity, high cash
    BALANCED = "balanced"  # 均衡派: moderate everything
    CONSERVATIVE = "conservative"  # 保守派: low burn, high runway


def classify_player_path(state: CompanyState) -> PlayerPath:
    """Classify the player's strategy archetype from their final state.

    Heuristics (ordered by priority):
    - Conservative: runway > 9 months, product < 60, users < 200
    - Fundraising: equity < 50
    - R&D: product >= 70
    - Marketing: users >= 500 and MRR >= 200k
    - Balanced: everything moderate
    """
    # Conservative: extremely long runway + low growth
    if state.runway_months > 9 and state.product_score < 60 and state.users < 200:
        return PlayerPath.CONSERVATIVE

    # Fundraising-focused: diluted equity
    if state.founder_equity < 50:
        return PlayerPath.FUNDRAISE

    # R&D-focused: great product
    if state.product_score >= 70:
        return PlayerPath.RND

    # Marketing-focused: large user base with revenue
    if state.users >= 500 and state.mrr >= 200_000:
        return PlayerPath.MARKETING

    # Conservative (milder form): high runway, moderate stats
    if state.runway_months > 6:
        return PlayerPath.CONSERVATIVE

    return PlayerPath.BALANCED


# ── Narrative variants per ending × path ────────────────────────────────────────

BANKRUPTCY_NARRATIVES = {
    PlayerPath.RND: [
        "💸【烧钱过快】产品做出来了，但钱也烧光了。你投入了太多资源打磨产品，忽略了商业化的窗口期。投资人拒绝继续注资，公司现金归零。技术很好，但市场没给你足够的时间。",
        "💸【研发陷阱】你坚信好产品自己会说话，但忽略了现金流管理。产品分确实很高，可是在用户愿意付费之前，公司的钱已经烧完了。这是一个关于'做对的事'和'活下来'的残酷教训。",
    ],
    PlayerPath.MARKETING: [
        "💸【产品没人用】你花了很多钱做营销拉用户，但产品本身没有跟上。用户来了又走，LTV远低于CAC，增长的质量很差。最终资金耗尽，公司无声地关闭了服务。",
        "💸【虚假繁荣】用户数曾经冲得很高，但留存率惨不忍睹。营销的钱烧完了，用户像潮水一样退去。没有产品支撑的营销，就像是往漏水的桶里倒水。",
    ],
    PlayerPath.FUNDRAISE: [
        "💸【融资失败】你过度依赖融资来续命，但没有用融来的钱建立起真正的业务壁垒。上一轮的钱烧完了，下一轮没人愿意投。投资人用脚投票，公司清算。",
        "💸【输血依赖】融资让你活得更久，但也掩盖了商业模式的根本问题。当融资窗口关闭，你发现公司的内生增长几乎没有。现金归零的那一天，一切结束了。",
    ],
    PlayerPath.BALANCED: [
        "💸【资金耗尽】你尝试了各种方向，但始终没有找到PMF。产品不够好、用户不够多、融资不够快，三个方向都差一点。最终，时间站在了你的对手那一边。",
    ],
    PlayerPath.CONSERVATIVE: [
        "💸【慢性出血】你太省了——省到产品没有竞争力、省到市场没有存在感。虽然活了很久，但每个月都在缓慢失血。最终，你那点现金也耗尽了。",
    ],
}

FOUNDER_REMOVED_NARRATIVES = {
    PlayerPath.RND: [
        "👋【投资人逼宫】你的产品路线图非常清晰，但投资人等不及了。他们想要的不是最好的产品，而是最快的增长。董事会上，你被投票罢免。技术理想主义败给了资本逻辑。",
    ],
    PlayerPath.MARKETING: [
        "👋【竞品收购逼宫】你烧钱买量的策略让董事会忍无可忍。竞品趁机抛出了收购+换管理层的方案，投资人觉得这是止损的好机会。你被请出了自己创立的公司。",
    ],
    PlayerPath.FUNDRAISE: [
        "👋【投资人逼宫】多轮融资后你的股权已经很低了。当业绩不如预期时，投资人联合起来改组了管理层。他们找了一个'更有经验'的CEO来接管。你成了自己公司的顾问。",
        "👋【控制权丧失】融资是一把双刃剑。你拿到了钱，但也交出了控制权。当投资人觉得你不再是那个'对的人'时，他们没有犹豫。VC的冷酷你终于体会到了。",
    ],
    PlayerPath.BALANCED: [
        "👋【团队出走】公司的方向摇摆不定，核心团队成员逐渐失去信心。几个关键人物一起辞职去了竞品，董事会对你的领导能力彻底丧失信任。你被解除了CEO职务。",
    ],
    PlayerPath.CONSERVATIVE: [
        "👋【温水煮青蛙】你求稳的策略让公司一直在生存边缘徘徊。没有增长故事，投资人失去了耐心。他们需要一个能讲出增长故事的人，而你不是那个人。董事会投票，你出局了。",
    ],
}

SERIES_A_SUCCESS_NARRATIVES = {
    PlayerPath.RND: [
        "🎉【技术驱动】你从一开始就坚信产品为王，而市场证明了你是对的。优秀的产品带来了口碑传播、高留存率和自然增长。A轮投资人排队约见你，你以极其优厚的条款完成了融资。这是一个技术创业者最好的结局。",
        "🎉【产品信仰】你用12个月打磨出了一款让竞品望尘莫及的产品。用户自发推荐、媒体争相报道、投资人主动敲门。A轮融资水到渠成，你保留了足够多的控制权。产品信仰得到了回报。",
    ],
    PlayerPath.MARKETING: [
        "🎉【增长奇迹】你的增长曲线让投资人惊艳。精准的市场策略带来了指数级的用户增长，而规模效应让获客成本持续下降。A轮融资估值远超预期，你证明了营销驱动的SaaS也可以很健康。",
    ],
    PlayerPath.FUNDRAISE: [
        "🎉【寒冬独秀】在一个融资寒冬里，你用两轮融资争取到了足够的时间打磨产品和市场。当竞品因为缺钱纷纷倒下时，你成了赛道里为数不多的幸存者。A轮投资人看到的是：一个被验证的业务加上几乎没有竞争的市场。",
    ],
    PlayerPath.BALANCED: [
        "🎉【行稳致远】你没有走极端——产品够好、用户够多、现金够用。这种稳健的风格虽然不够性感，但在A轮投资人眼里恰恰是最安全的赌注。你以合理的估值完成了融资，一切都在掌控之中。",
    ],
    PlayerPath.CONSERVATIVE: [
        "🎉【厚积薄发】你小心翼翼地管理着每一分钱，同时在关键领域持续投入。虽然没有爆发式增长，但你的单位经济模型是投资人见过的最健康的。A轮融资成功，你的审慎得到了回报。",
    ],
}

SURVIVED_NARRATIVES = {
    PlayerPath.RND: [
        "😐【小而美】产品做得很不错，但商业化的步伐不够快。公司活下来了，有一批忠实用户，但离投资人的增长预期还有差距。你有一个小而美的生意——只是VC不会为此买单。",
    ],
    PlayerPath.MARKETING: [
        "😐【差点死掉】营销烧了很多钱，中间几次差点资金断裂。好在最后关头控制住了成本，产品也在逐渐改善。公司还活着，但你已经深刻体会到了'增长黑客'的另一面——增长可以很快，但也可以很贵。",
    ],
    PlayerPath.FUNDRAISE: [
        "😐【被收购边缘】融到的钱帮你活过了冬天，但春天来临时你发现自己的筹码已经不多了——股权稀释严重，估值没有明显提升。有几家公司在试探收购意向，你正在认真考虑。",
    ],
    PlayerPath.BALANCED: [
        "😐【不上不下】公司没有死、也没有起飞。你卡在了一个尴尬的位置——不够大，不够快，但也不够差。下一个12个月，你必须做出选择：找到增长引擎，或者接受一个平庸的结局。",
    ],
    PlayerPath.CONSERVATIVE: [
        "😐【省出来的存活】你太会省钱了。12个月后你还有充足的现金，但产品和用户体量都很小。公司活下来了，但在这个赢家通吃的赛道里，活着但长不大可能比死了更难受。",
    ],
}

SLOW_DEATH_NARRATIVES = {
    PlayerPath.RND: [
        "🐌【错过窗口】你一直在打磨产品，等你觉得产品'够好了'的时候，市场窗口已经关上了。竞品用更早推出的产品占领了用户心智，你的好产品没有机会被看到。时机错了，产品再好也没用。",
    ],
    PlayerPath.MARKETING: [
        "🐌【被遗忘】你曾经靠营销获得了一波声量，但热度退去后，产品留不住用户。每一次营销都能带来一波新用户，但总体趋势是下降的。慢慢地，市场上没人再提起你的名字。",
    ],
    PlayerPath.FUNDRAISE: [
        "🐌【温水煮青蛙】融资让你以为自己还有时间，但你浪费了这些时间。钱在慢慢地消耗，而真正的PMF始终没有出现。12个月后，你发现自己离最初的愿景越来越远。",
    ],
    PlayerPath.BALANCED: [
        "🐌【渐渐消失】什么都做了一点，但什么都没做好。产品、营销、融资——每个方向都差一口气。公司没有戏剧性地倒下，而是一点点地从市场上消失了。",
    ],
    PlayerPath.CONSERVATIVE: [
        "🐌【温吞水】你省下了钱，但输掉了时间。12个月后，你的现金还剩不少，但市场已经不属于你了。竞品用你不敢下的赌注赢得了用户。保守有时候才是最大的风险。",
    ],
}

PATH_FALLBACK: dict[EndingType, list[str]] = {
    EndingType.BANKRUPTCY: [
        "💸 资金耗尽！公司现金归零，破产清算。在创业这场游戏里，现金流永远是第一生命线。",
    ],
    EndingType.FOUNDER_REMOVED: [
        "👋 创始人出局！失去了股权和董事会的支持，你被请出了自己创立的公司。",
    ],
    EndingType.SERIES_A_SUCCESS: [
        "🎉 A轮融资成功！你在12个月内证明了自己，以优厚条款完成了A轮融资。恭喜！",
    ],
    EndingType.SURVIVED_BUT_AVERAGE: [
        "😐 勉强存活。公司没有死，但也没有达到高速增长预期。下一个12月，你会怎么走？",
    ],
    EndingType.SLOW_DEATH: [
        "🐌 慢性死亡。增长乏力，公司在慢慢耗尽资源。也许需要一次彻底的转型。",
    ],
}


# ── Narration table lookup ──────────────────────────────────────────────────────

NARRATIVE_TABLE: dict[EndingType, dict[PlayerPath, list[str]]] = {
    EndingType.BANKRUPTCY: BANKRUPTCY_NARRATIVES,
    EndingType.FOUNDER_REMOVED: FOUNDER_REMOVED_NARRATIVES,
    EndingType.SERIES_A_SUCCESS: SERIES_A_SUCCESS_NARRATIVES,
    EndingType.SURVIVED_BUT_AVERAGE: SURVIVED_NARRATIVES,
    EndingType.SLOW_DEATH: SLOW_DEATH_NARRATIVES,
}


def evaluate(state: CompanyState) -> EndingType | None:
    """Evaluate the current state and return an EndingType if the game is over,
    or None if the game should continue.
    """

    # Immediate endings (can happen any month)
    if state.cash <= 0:
        return EndingType.BANKRUPTCY

    if state.founder_equity < 34 and state.board_control < 45 and state.runway_months < 4:
        return EndingType.FOUNDER_REMOVED

    # Terminal month endings (only evaluated at month 12)
    if state.month >= 12:
        if state.mrr >= 300_000 and state.product_score >= 65 and state.founder_equity >= 50:
            return EndingType.SERIES_A_SUCCESS

        if state.mrr >= 100_000 and state.cash > 0:
            return EndingType.SURVIVED_BUT_AVERAGE

        return EndingType.SLOW_DEATH

    # Game continues
    return None


def describe_ending(
    ending: EndingType,
    state: CompanyState,
    path: PlayerPath | None = None,
) -> str:
    """Return a human-readable narrative for an ending.

    Alpha 1.3: If path is provided, selects a variant narrative from the
    narrative table. Otherwise falls back to a generic description.
    """
    if ending == EndingType.NONE:
        return ""

    import random

    if path is None:
        path = classify_player_path(state)

    # Look up path-specific narratives
    table = NARRATIVE_TABLE.get(ending, {})
    variants = table.get(path, [])
    if variants:
        return random.choice(variants)

    # Fallback to generic description
    fallbacks = PATH_FALLBACK.get(ending, [])
    return random.choice(fallbacks) if fallbacks else f"游戏结束：{ending.value}"


def describe_ending_with_seed(
    ending: EndingType,
    state: CompanyState,
    path: PlayerPath | None = None,
    seed: int = 0,
) -> str:
    """Deterministic variant — uses seed for reproducible narratives."""
    if ending == EndingType.NONE:
        return ""

    if path is None:
        path = classify_player_path(state)

    table = NARRATIVE_TABLE.get(ending, {})
    variants = table.get(path, [])
    if variants:
        return variants[seed % len(variants)]

    fallbacks = PATH_FALLBACK.get(ending, [])
    return fallbacks[seed % len(fallbacks)] if fallbacks else f"游戏结束：{ending.value}"
