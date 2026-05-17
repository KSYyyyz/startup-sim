"""Alpha 1.6 State Explainer: translates raw numbers into human-readable descriptions.

Takes a CompanyState and returns natural-language explanations of what each
metric means in context — runway estimates, product maturity, conversion issues,
equity/control status.
"""

from __future__ import annotations

from src.core.models import CompanyState


class StateExplainer:
    """Stateless translator — CompanyState → human-readable insights."""

    @classmethod
    def explain_cash(cls, state: CompanyState) -> str:
        """Explain cash and runway situation."""
        cash_w = state.cash // 10000
        burn_w = state.monthly_burn // 10000
        runway = state.runway_months

        if state.cash <= 0:
            return "💰 现金已耗尽，公司无法继续运营。"

        if runway < 2:
            return (
                f"💰 现金{cash_w}万，每月烧{burn_w}万——跑道仅{runway:.1f}个月。"
                f"公司处于极度危险状态，必须立即融资或大幅削减开支。"
            )
        elif runway < 4:
            return (
                f"💰 现金{cash_w}万，每月烧{burn_w}万——跑道{runway:.1f}个月。"
                f"现金流紧张，建议尽快启动融资准备或控制支出。"
            )
        elif runway < 7:
            return (
                f"💰 现金{cash_w}万，每月烧{burn_w}万——跑道{runway:.1f}个月。"
                f"现金流偏紧但尚可维持，注意控制烧钱速度。"
            )
        elif runway >= 12:
            return (
                f"💰 现金{cash_w}万，每月烧{burn_w}万——跑道{runway:.1f}个月。"
                f"现金储备充裕，可以考虑加大投入加速增长。"
            )
        return (
            f"💰 现金{cash_w}万，每月烧{burn_w}万——跑道{runway:.1f}个月。"
            f"现金流健康，有足够的缓冲空间。"
        )

    @classmethod
    def explain_product(cls, state: CompanyState) -> str:
        """Explain product score in human terms."""
        p = state.product_score

        if p < 15:
            return f"🛠️ 产品分{p}——原型阶段。功能简陋，用户几乎无法正常使用。"
        elif p < 30:
            return f"🛠️ 产品分{p}——MVP阶段。基本功能可用，但体验粗糙，用户留存率很低。"
        elif p < 45:
            return f"🛠️ 产品分{p}——早期产品。有一定可用性，但竞品可以轻松超越。"
        elif p < 60:
            return f"🛠️ 产品分{p}——可用产品。核心功能完善，用户开始觉得好用。"
        elif p < 75:
            return f"🛠️ 产品分{p}——成熟产品。用户留存良好，口碑开始传播。"
        elif p < 90:
            return f"🛠️ 产品分{p}——优秀产品。竞品难以追赶，用户自发推荐。"
        else:
            return f"🛠️ 产品分{p}——顶尖产品。行业标杆，定义了品类标准。"

    @classmethod
    def explain_users_mrr(cls, state: CompanyState) -> str:
        """Explain user count and MRR relationship."""
        users = state.users
        mrr_w = state.mrr // 10000
        product = state.product_score

        if users == 0 and mrr_w == 0:
            return "👥 暂无付费客户。需要先做出产品，然后通过营销获取第一批用户。"

        if users > 100 and mrr_w < 3:
            return (
                f"👥 {users}个用户，MRR仅{mrr_w}万——转化率严重偏低。"
                f"用户多但收入少，可能是定价过低或免费用户占比太高。"
            )

        if product >= 60 and users < 20 and state.month >= 5:
            return (
                f"👥 仅{users}个用户但产品分{product}——产品好却没人用。"
                f"严重缺乏获客能力，需要加大营销投入让市场知道你的产品。"
            )

        if mrr_w >= 30:
            return (
                f"👥 {users}个用户，MRR{mrr_w}万——收入引擎已启动。"
                f"MRR超过30万已经达到A轮门槛之一，继续保持增长势头。"
            )

        return f"👥 {users}个用户，MRR{mrr_w}万——月经常性收入。MRR是A轮融资的关键指标。"

    @classmethod
    def explain_equity(cls, state: CompanyState) -> str:
        """Explain equity and control status."""
        equity = state.founder_equity
        board = state.board_control

        if equity >= 95:
            return (
                f"📊 创始人股权{equity}%，董事会控制{board}%。"
                f"你对公司拥有绝对控制权——这是最好的状态，但融资需要出让部分股权。"
            )
        elif equity >= 70:
            return (
                f"📊 创始人股权{equity}%，董事会控制{board}%。"
                f"控制权健康，你有充分的话语权推动决策。"
            )
        elif equity >= 50:
            return (
                f"📊 创始人股权{equity}%，董事会控制{board}%。"
                f"股权已大幅稀释，但仍保持相对控股。下一轮融资需谨慎计算稀释比例。"
            )
        elif equity >= 34:
            return (
                f"⚠️ 创始人股权仅{equity}%，董事会控制{board}%。"
                f"你仍有重大事项否决权（34%是一票否决线），但日常控制权已大幅削弱。"
            )
        else:
            return (
                f"⚠️ 创始人股权仅{equity}%，董事会控制{board}%。"
                f"你已经失去了对公司重大决策的否决权。投资方可以联合投票更换CEO。"
            )

    @classmethod
    def explain_morale(cls, state: CompanyState) -> str:
        """Explain team morale."""
        morale = state.team_morale

        if morale < 30:
            return f"💪 团队士气{morale}——濒临崩溃。核心员工正在流失，团队濒临解体。"
        elif morale < 50:
            return f"💪 团队士气{morale}——低落。员工消极怠工，招聘困难，执行力下降。"
        elif morale < 70:
            return f"💪 团队士气{morale}——正常。团队运转平稳，但缺少激情。"
        elif morale < 85:
            return f"💪 团队士气{morale}——良好。员工积极投入，效率和创新能力强。"
        else:
            return f"💪 团队士气{morale}——高涨。团队凝聚力极强，战斗力爆表。"

    @classmethod
    def explain_full(cls, state: CompanyState) -> dict[str, str]:
        """Return a complete set of human-readable explanations for all metrics."""
        return {
            "cash": cls.explain_cash(state),
            "product": cls.explain_product(state),
            "users_mrr": cls.explain_users_mrr(state),
            "equity": cls.explain_equity(state),
            "morale": cls.explain_morale(state),
        }
