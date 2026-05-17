"""Alpha 1.5 Replay Engine: generates a narrative monthly replay of the game.

Builds a GameReplay with 12 monthly ReplayMonth entries, each with narrative title,
summary, metric changes, events, and risk level. Identifies the climax month.
"""

from __future__ import annotations

from typing import Any, Dict, List

from src.core.models import (
    CompanyState,
    GameReplay,
    ReplayMonth,
)


class ReplayEngine:
    """Stateless replay generator — takes game history, returns GameReplay."""

    _MONTH_THEMES = {
        1: "种子轮后的第一次豪赌",
        2: "初步验证",
        3: "市场反馈袭来",
        4: "调整与试错",
        5: "暗流涌动",
        6: "现金压力逼近",
        7: "中场抉择",
        8: "生死时速",
        9: "黎明前的黑暗",
        10: "决定命运的融资窗口",
        11: "终局冲刺",
        12: "结局揭晓",
    }

    @classmethod
    def generate_replay(
        cls,
        snapshots: List[Dict[str, Any]],
        actions: List[Dict[str, Any]],
        events: List[Dict[str, Any]],
        final_state: CompanyState,
        ending_status: str,
        session_id: int = 0,
    ) -> GameReplay:
        """Generate a full monthly replay timeline."""
        months = []
        prev_cash = 1_000_000
        prev_mrr = 0
        prev_users = 0
        prev_product = 20

        events_by_month: Dict[int, List[str]] = {}
        for evt in events:
            m = evt.get("month", 0)
            events_by_month.setdefault(m, []).append(evt.get("title", evt.get("event_type", "")))

        actions_by_month: Dict[int, str] = {}
        for act in actions:
            m = act.get("month", 0)
            actions_by_month[m] = act.get("raw_input", "")

        max_mrr_month = 1
        max_mrr_val = 0
        min_cash_month = 1
        min_cash_val = float("inf")

        for snap in snapshots:
            state_dict = snap.get("state_json", snap)
            if isinstance(state_dict, str):
                import json
                state_dict = json.loads(state_dict)
            month = snap.get("month", 0)

            cash = state_dict.get("cash", 0)
            mrr = state_dict.get("mrr", 0)
            users = state_dict.get("users", 0)
            product = state_dict.get("product_score", 0)
            morale = state_dict.get("team_morale", 70)
            runway = state_dict.get("runway_months", 0)
            if isinstance(runway, dict):
                runway = 0
            equity = state_dict.get("founder_equity", 100)
            valuation = state_dict.get("valuation", 5_000_000)

            title = cls._month_title(month, cash, mrr, runway, ending_status)
            summary = cls._month_summary(month, cash, mrr, product, users, ending_status)
            action_summary = actions_by_month.get(month, "")
            risk = cls._risk_level(cash, runway, morale, equity)

            changes = {
                "cash": cash - prev_cash,
                "mrr": mrr - prev_mrr,
                "users": users - prev_users,
                "product": product - prev_product,
            }
            major_events = events_by_month.get(month, [])

            months.append(ReplayMonth(
                month=month,
                title=title,
                summary=summary,
                action_summary=action_summary,
                metric_changes=changes,
                major_events=major_events,
                risk_level=risk,
            ))

            if mrr > max_mrr_val:
                max_mrr_val = mrr
                max_mrr_month = month
            if cash < min_cash_val:
                min_cash_val = cash
                min_cash_month = month

            prev_cash = cash
            prev_mrr = mrr
            prev_users = users
            prev_product = product

        # Determine climax month: the most dramatic turning point
        climax = cls._find_climax(months, max_mrr_month, min_cash_month)

        # Generate tags
        tags = cls._generate_tags(months, final_state, ending_status)

        # Opening & ending
        opening = f"你带着100万种子轮资金和一支10人团队，开始了AI客服SaaS的创业之旅。12个月，一个赛道，无数选择。"
        ending_summary = cls._ending_narrative(ending_status, final_state)

        title_text = cls._replay_title(ending_status, final_state)

        return GameReplay(
            session_id=session_id,
            title=title_text,
            opening_summary=opening,
            months=months,
            climax_month=climax,
            ending_summary=ending_summary,
            replay_tags=tags,
        )

    @classmethod
    def _month_title(cls, month: int, cash: int, mrr: int, runway, ending_status: str) -> str:
        base = cls._MONTH_THEMES.get(month, f"第{month}月")
        if month >= 12 and ending_status != "none":
            return f"{base} — 大结局"
        if cash <= 50_000 and cash > 0:
            return f"{base} — 现金告急"
        if mrr >= 300_000 and month > 6:
            return f"{base} — MRR突破30万"
        if isinstance(runway, (int, float)) and runway < 3 and runway >= 0:
            return f"{base} — 跑道告急"
        return base

    @classmethod
    def _month_summary(cls, month: int, cash: int, mrr: int, product: int,
                       users: int, ending_status: str) -> str:
        cash_w = cash // 10000
        mrr_w = mrr // 10000
        if month == 1:
            return f"初始资金100万，产品分20，团队10人。你做出了第一个关键决策。"
        if mrr >= 500_000:
            return f"MRR突破50万！现金{cash_w}万，产品分{product}，用户{users}。收入引擎已启动。"
        if mrr >= 300_000:
            return f"MRR达{mrr_w}万，现金{cash_w}万。增长势头强劲，A轮触手可及。"
        if cash <= 10_000:
            return f"现金仅剩{cash_w}万，命悬一线。"
        if product >= 80:
            return f"产品分{product}，用户{users}，MRR{mrr_w}万。产品已具备竞争力，需要商业化加速。"
        return f"现金{cash_w}万，MRR{mrr_w}万，产品分{product}，用户{users}。"

    @classmethod
    def _risk_level(cls, cash: int, runway, morale: int, equity: int) -> str:
        if cash <= 10_000:
            return "critical"
        rw = float(runway) if isinstance(runway, (int, float)) else 12.0
        if rw < 3:
            return "high"
        if rw < 6 or equity < 50:
            return "high"
        if morale < 40:
            return "high"
        if rw >= 9:
            return "low"
        return "normal"

    @classmethod
    def _find_climax(cls, months: List[ReplayMonth], max_mrr_month: int,
                     min_cash_month: int) -> int:
        """Find the most dramatic month as the climax."""
        critical_months = [m for m in months if m.risk_level in ("critical", "high")]
        if critical_months:
            return critical_months[0].month
        if max_mrr_month >= 8:
            return max_mrr_month
        return min_cash_month

    @classmethod
    def _generate_tags(cls, months: List[ReplayMonth], final_state: CompanyState,
                       ending_status: str) -> List[str]:
        tags = []
        product = final_state.product_score
        users = final_state.users
        equity = final_state.founder_equity

        if ending_status == "series_a_success":
            tags.append("A轮赢家")
            if product >= 75:
                tags.append("技术信仰")
            if users >= 1000:
                tags.append("增长神话")

        if product >= 85:
            tags.append("极致产品")

        critical_count = sum(1 for m in months if m.risk_level in ("critical", "high"))
        if critical_count >= 3:
            tags.append("惊险刺激")
        elif critical_count == 0:
            tags.append("稳健经营")

        if equity >= 95:
            tags.append("控制力MAX")

        cumulative_mrr = 0
        for m in months:
            cumulative_mrr += m.metric_changes.get("mrr", 0)
            if m.month <= 6 and cumulative_mrr >= 200_000 and m.metric_changes.get("mrr", 0) > 50_000:
                tags.append("闪电增长")
                break

        if ending_status == "bankruptcy":
            tags.append("燃烧殆尽")
        elif ending_status == "slow_death":
            tags.append("温水青蛙")

        return tags[:4] or ["未完待续"]

    @classmethod
    def _ending_narrative(cls, ending_status: str, final_state: CompanyState) -> str:
        product = final_state.product_score
        mrr = final_state.mrr
        users = final_state.users
        cash = final_state.cash

        if ending_status == "series_a_success":
            return (
                f"12个月的奋斗换来A轮入场券。产品分{product}，MRR{mrr//10000}万，"
                f"用户{users}。你证明了自己，下一站——规模化和团队建设。"
            )
        elif ending_status == "survived_but_average":
            return (
                f"公司活下来了。产品分{product}，MRR{mrr//10000}万。"
                f"你没有输，但也没有赢。也许下次可以更大胆一些。"
            )
        elif ending_status == "slow_death":
            return (
                f"公司没有戏剧性地倒下，而是一点点从市场上消失了。"
                f"最终产品分{product}，MRR{mrr//10000}万。这是一堂关于聚焦的课。"
            )
        elif ending_status == "bankruptcy":
            return (
                f"现金流断裂。产品分{product}，MRR{mrr//10000}万。"
                f"创业是一场与时间赛跑的游戏——这次，时间赢了。"
            )
        elif ending_status == "founder_removed":
            return (
                f"公司还在，但你不再掌舵。过度融资稀释了控制权。"
                f"这是一堂关于股权结构的残酷课程。"
            )
        return "游戏结束。"

    @classmethod
    def _replay_title(cls, ending_status: str, final_state: CompanyState) -> str:
        product = final_state.product_score
        mrr = final_state.mrr

        if ending_status == "series_a_success":
            if product >= 80:
                return "产品信仰者的A轮之路"
            return "12个月的逆袭"
        elif ending_status == "survived_but_average":
            if product >= 80:
                return "小而美的生存之道"
            return "活下来了，然后呢？"
        elif ending_status == "slow_death":
            return "温水中的创业旅程"
        elif ending_status == "bankruptcy":
            if product >= 70:
                return "好产品的悲歌"
            return "燃烧殆尽的12个月"
        elif ending_status == "founder_removed":
            return "失去王座的创始人"
        return f"第{final_state.month}个月的创业记录"
