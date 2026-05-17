"""Alpha 1.6 Tutorial Engine: onboarding guide + threshold-based hints.

Provides a first-turn tutorial (4 steps explaining the game) and contextual
hints triggered by crossing key thresholds (low runway, equity dilution, etc.).
Lightweight — no forced actions, no numerical changes.
"""

from __future__ import annotations

from collections.abc import Callable

from src.core.models import CompanyState, TutorialHint, TutorialStep


class TutorialEngine:
    """Stateless tutorial guide. All methods are pure functions of state."""

    _FIRST_TURN_STEPS: list[dict] = [
        {
            "step_id": "welcome",
            "title": "欢迎来到创业模拟器",
            "description": (
                "你是AI客服SaaS的创始人，手握100万种子轮资金。"
                "你有12个月时间带领公司走向A轮融资。"
                "每个回合你可以做一个或多个决策，输入自然语言即可。"
            ),
            "example_input": "",
        },
        {
            "step_id": "how_to_input",
            "title": "如何输入决策",
            "description": (
                "用自然语言描述你的决策，系统会自动解析。"
                '示例格式："花20万研发产品"、"融资500万出让10%股权"。'
                "支持多个决策同时输入，用逗号或顿号分隔。"
            ),
            "example_input": "花20万研发产品，花10万做营销推广",
        },
        {
            "step_id": "action_types",
            "title": "五种决策类型",
            "description": (
                "🛠️ 研发(product)：投入研发提升产品分\n"
                "📢 营销(marketing)：获取用户和MRR增长\n"
                "💰 融资(fundraising)：出让股权换取现金\n"
                "👥 团队(team)：招聘或团建提升士气\n"
                "📊 战略(strategy)：提升市场份额和声誉"
            ),
            "example_input": "花20万研发产品，融资500万出让10%股权",
        },
        {
            "step_id": "metrics_101",
            "title": "关键指标说明",
            "description": (
                "💰 现金：公司的命脉，耗尽则破产\n"
                "🔥 月消耗：每月固定支出（烧钱速度）\n"
                "📈 MRR：月度经常性收入，A轮关键门槛(≥30万)\n"
                "👥 用户：付费客户数，影响MRR\n"
                "🛠️ 产品分：产品竞争力(0-100)，影响用户留存\n"
                "📊 创始人股权：你对公司的控制权\n"
                "⏳ 现金流可支撑时间：现金/月消耗，剩余生存月数"
            ),
            "example_input": "",
        },
    ]

    # (trigger_name, check_fn, title, message_fn, example_inputs)
    _THRESHOLD_DEFS: list[tuple[str, Callable, str, Callable, list[str]]] = [
        (
            "runway_below_3",
            lambda s: 0 < s.runway_months < 3 and s.cash > 0,
            "⚠️ 现金流风险",
            lambda s: (
                f"现金仅{s.cash//10000}万，现金流可支撑不足3个月。"
                "公司面临现金流断裂风险——你有两个选择：\n"
                "1) 立即融资（出让股权换现金）\n"
                "2) 大幅削减开支（降低研发和营销预算）\n"
                "什么都不做的话，可能在1-2个月内破产。"
            ),
            ["融资300万出让8%股权", "花1万研发产品保持最低运转"],
        ),
        (
            "equity_dilution",
            lambda s: s.founder_equity < 70,
            "⚠️ 股权稀释提醒",
            lambda s: (
                f"创始人股权已降至{s.founder_equity}%。"
                "每次融资都在稀释你的控制权——当股权低于50%时，你会在董事会上失去绝对话语权。"
                "后续融资考虑债转股或可转债，保护控制权。"
            ),
            ["花10万做营销提升MRR以支撑估值", "花15万研发产品提升竞争力"],
        ),
        (
            "marketing_low_product",
            lambda s: s.product_score < 35 and s.users > 0,
            "⚠️ 营销泡沫风险",
            lambda s: (
                f"产品分仅{s.product_score}，但已经开始获客。"
                "低产品分意味着用户留存率很差——花大钱拉来的用户会很快流失。"
                "建议先提升产品分到40以上，再大规模做营销。"
            ),
            ["花15万研发产品提升产品分", "花5万研发产品，花5万做基础营销"],
        ),
        (
            "high_product_low_mrr",
            lambda s: s.product_score >= 60 and s.mrr < 50_000 and s.month >= 4,
            "💡 产品已成熟，该做商业化了",
            lambda s: (
                f"产品分{s.product_score}已经不错了，但MRR仅{s.mrr//10000}万。"
                "好的产品需要好的商业化——现在应该加大营销投入，把产品优势转化为收入。"
            ),
            ["花20万做营销推广获取客户", "花10万做营销，花10万继续研发"],
        ),
        (
            "low_morale",
            lambda s: s.team_morale < 45,
            "⚠️ 团队士气危机",
            lambda s: (
                f"团队士气降至{s.team_morale}，核心成员可能离职。"
                "低士气影响研发效率、客户服务质量和公司整体执行力。"
                "考虑安排团建活动或分配期权来提振士气。"
            ),
            ["花5万组织团建提升团队士气", "花10万招聘新员工扩充团队"],
        ),
        (
            "board_pressure",
            lambda s: s.founder_equity < 60 and s.board_control < 60,
            "⚠️ 董事会控制权风险",
            lambda s: (
                f"创始人股权{s.founder_equity}%、董事会控制权{s.board_control}%。"
                "你已经失去了对公司的绝对控制权。投资方可能在董事会上推动换CEO。"
            ),
            ["花15万研发产品证明执行力", "花20万做营销快速提升MRR和估值"],
        ),
    ]

    @classmethod
    def get_first_turn_tutorial(cls) -> list[TutorialStep]:
        """Return the onboarding tutorial steps shown on month 1."""
        return [
            TutorialStep(
                step_id=s["step_id"],
                title=s["title"],
                description=s["description"],
                example_input=s["example_input"],
                trigger_condition="first_turn",
                shown_once=True,
            )
            for s in cls._FIRST_TURN_STEPS
        ]

    @classmethod
    def check_hints(
        cls, state: CompanyState, shown_triggers: set | None = None
    ) -> list[TutorialHint]:
        """Check all threshold conditions and return triggered hints.

        Args:
            state: Current company state.
            shown_triggers: Set of trigger IDs already shown (to avoid repeats).

        Returns:
            List of TutorialHint for newly triggered thresholds.
        """
        already = shown_triggers or set()
        hints: list[TutorialHint] = []

        for trigger_name, check_fn, title, msg_fn, examples in cls._THRESHOLD_DEFS:
            if trigger_name in already:
                continue
            try:
                if check_fn(state):
                    hints.append(
                        TutorialHint(
                            title=title,
                            message=msg_fn(state),
                            example_inputs=list(examples),
                        )
                    )
                    already.add(trigger_name)
            except Exception:
                pass

        return hints
