"""Alpha 1.6 Suggestion Engine: generates 3 actionable suggestions per turn.

Each suggestion includes a title, description, example_input (parseable by
parse_multi), risk level, and reason. Generated suggestions are contextual
to the player's current state — conservative, aggressive, and warning paths.
"""

from __future__ import annotations

from src.core.models import ActionSuggestion, CompanyState, SuggestionResult


class SuggestionEngine:
    """Stateless suggestion generator — 3 suggestions per state: 稳健/激进/风险提示."""

    @classmethod
    def generate(cls, state: CompanyState, turn_number: int = 1) -> SuggestionResult:
        """Generate 3 action suggestions tailored to current state.

        Always returns exactly 3 suggestions: conservative, aggressive, warning.
        """
        suggestions: list[ActionSuggestion] = []
        warning = ""
        recommended = ""

        runway = state.runway_months
        cash_w = state.cash // 10000
        burn_w = state.monthly_burn // 10000
        product = state.product_score
        mrr_w = state.mrr // 10000
        users = state.users
        equity = state.founder_equity

        # ── Conservative: 稳健路线 ──
        conservative = cls._conservative(
            state, runway, cash_w, burn_w, product, mrr_w, users, equity, turn_number
        )
        suggestions.append(conservative)

        # ── Aggressive: 激进路线 ──
        aggressive = cls._aggressive(
            state, runway, cash_w, burn_w, product, mrr_w, users, equity, turn_number
        )
        suggestions.append(aggressive)

        # ── Warning: 风险提示 ──
        warn_suggestion, warn_text = cls._warning(state, runway, cash_w, product, mrr_w, equity)
        suggestions.append(warn_suggestion)
        warning = warn_text

        # ── Recommended focus ──
        recommended = cls._recommend_focus(state, runway, product, mrr_w, equity)

        return SuggestionResult(
            suggestions=suggestions,
            warning=warning,
            recommended_focus=recommended,
        )

    # ── Conservative ─────────────────────────────────────────────────────────

    @classmethod
    def _conservative(cls, state, runway, cash_w, burn_w, product, mrr_w, users, equity, turn):
        """Generate a conservative (稳健) suggestion."""
        # Cash crisis: cut spending hard
        if runway < 4 and cash_w > 0:
            if product < 50:
                return ActionSuggestion(
                    title="稳健：控支保命",
                    description=f"现金{cash_w}万、可支撑{runway:.1f}月。大幅削减开支，最小研发维持产品，暂停营销。",
                    example_input="花2万研发产品维持最低运转",
                    risk_level="conservative",
                    reason="现金流优先——先活下来，再谈增长。",
                )
            else:
                return ActionSuggestion(
                    title="稳健：控支过渡",
                    description=f"现金{cash_w}万、可支撑{runway:.1f}月。暂停大额支出，用现有产品维持客户，等待融资窗口。",
                    example_input="花2万做基础运维",
                    risk_level="conservative",
                    reason="现金流优先——产品已成熟，先守住存量客户。",
                )

        # High product but low MRR: start small marketing
        if product >= 55 and mrr_w < 10:
            return ActionSuggestion(
                title="稳健：轻量获客",
                description=f"产品分{product}，MRR仅{mrr_w}万。少量营销投入测试市场反应，降低风险。",
                example_input="花10万做精准营销推广",
                risk_level="conservative",
                reason="产品基础好，小步快跑验证商业化路径。",
            )

        # Normal: moderate R&D + light marketing
        budget = min(cash_w // 4, 15) if cash_w > 0 else 2
        return ActionSuggestion(
            title="稳健：均衡发展",
            description="保持研发和营销的平衡。适度投入产品+轻量获客，控制烧钱速度。",
            example_input=f"花{budget}万研发产品，花{budget}万做营销",
            risk_level="conservative",
            reason="均衡策略适合当前状态，避免在单一方向过度投资。",
        )

    # ── Aggressive ───────────────────────────────────────────────────────────

    @classmethod
    def _aggressive(cls, state, runway, cash_w, burn_w, product, mrr_w, users, equity, turn):
        """Generate an aggressive (激进) suggestion."""
        # Low product, decent cash: go hard on R&D
        if product < 50 and cash_w >= 30:
            budget = min(cash_w // 3, 30)
            return ActionSuggestion(
                title="激进：全力研发",
                description=f"产品分仅{product}，现金{cash_w}万。集中资源猛攻产品，3个月内产品分推到60+。",
                example_input=f"花{budget}万研发产品提升竞争力",
                risk_level="aggressive",
                reason="产品是根本——没有好产品，营销和融资都是空中楼阁。",
            )

        # Good product, low MRR: aggressive marketing + fundraising
        if product >= 50 and mrr_w < 15 and cash_w >= 20:
            return ActionSuggestion(
                title="激进：增长冲刺",
                description=f"产品分{product}已可商用。加大营销投入+启动融资，为规模化储备弹药。",
                example_input="花20万做大规模营销，融资500万出让10%股权",
                risk_level="aggressive",
                reason="产品已有竞争力，抢占市场的窗口期有限。",
            )

        # Low cash: aggressive fundraising
        if runway < 5 and equity >= 70:
            return ActionSuggestion(
                title="激进：融资续命",
                description=f"可支撑仅{runway:.1f}月。果断融资换取现金和时间，出让少量股权换生存权。",
                example_input="融资400万出让10%股权",
                risk_level="aggressive",
                reason="生死存亡之际，股权稀释的代价远小于破产。",
            )

        # Default aggressive
        return ActionSuggestion(
            title="激进：加速扩张",
            description="同时推进研发和营销，快速扩大用户规模和MRR，缩短A轮时间。",
            example_input="花20万研发产品，花20万做营销推广",
            risk_level="aggressive",
            reason="加速策略适合想冲击A轮的玩家，但需注意现金流。",
        )

    # ── Warning ──────────────────────────────────────────────────────────────

    @classmethod
    def _warning(cls, state, runway, cash_w, product, mrr_w, equity):
        """Generate a risk warning + suggestion."""
        risks = []

        if runway <= 3 and cash_w > 0:
            risks.append(f"可支撑仅{runway:.1f}月——本回合必须行动，否则下月可能破产。")
        elif runway <= 5 and cash_w > 0:
            risks.append(f"可支撑{runway:.1f}月，建议尽快启动融资准备。")

        if product < 30:
            risks.append(f"产品分{product}太低，用户留存极差，花营销钱基本白花。")

        if product >= 60 and mrr_w < 5 and state.month >= 5:
            risks.append(f"产品分{product}但MRR仅{mrr_w}万——你可能被困在'技术孤岛'里。")

        if equity < 50:
            risks.append(f"股权{equity}%——下次融资可能失去公司控制权。")

        if not risks:
            risks.append("当前无明显风险信号。保持节奏，关注竞品动态即可。")

        # Build a specific warning suggestion
        if runway <= 3:
            if equity >= 80:
                example = "融资300万出让8%股权"
            else:
                example = "花2万研发产品压缩消耗"
        elif product < 30 and cash_w > 10:
            example = "花15万研发产品快速提升产品分"
        elif product >= 60 and mrr_w < 5:
            example = "花20万做营销推广，花10万研发产品"
        else:
            example = "花5万研发产品，花5万做营销"

        suggestion = ActionSuggestion(
            title="风险：当前最需要注意的点",
            description="；".join(risks),
            example_input=example,
            risk_level="warning",
            reason="正视风险是创业者的基本素养。",
        )

        return suggestion, risks[0] if risks else ""

    # ── Recommended focus ────────────────────────────────────────────────────

    @classmethod
    def _recommend_focus(cls, state, runway, product, mrr_w, equity) -> str:
        """Determine the single most important focus area."""
        if runway <= 3:
            return "现金流：融资或大幅削减开支是当前唯一优先级。"
        if product < 40:
            return "产品：产品是一切的基础，先把产品分提升到40以上。"
        if product >= 55 and mrr_w < 10:
            return "商业化：产品已成熟，需要加大营销投入把产品优势转化为收入。"
        if equity < 50:
            return "控制权：股权稀释严重，后续融资优先考虑债权。"
        if mrr_w >= 20:
            return "增长：MRR势头良好，考虑A轮融资为规模化扩张储备弹药。"
        return "均衡：当前各维度较为平衡，稳步推进研发和营销。"
