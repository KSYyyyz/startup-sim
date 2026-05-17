"""Alpha 1.4 Review Engine: post-game analysis, scoring, and founder profiling.

Generates a GameReview that explains why the player succeeded or failed,
identifies key turning points, scores strategy across 5 dimensions,
and profiles the founder archetype.
"""

from __future__ import annotations

from typing import Any

from src.core.models import (
    CompanyState,
    FounderProfile,
    GameReview,
    KeyMoment,
    StrategyScore,
)


class ReviewEngine:
    """Stateless review generator — takes game history, returns GameReview."""

    # ── Founder profile classification ───────────────────────────────────────

    @staticmethod
    def _classify_founder(
        initial_state: CompanyState,
        snapshots: list[dict[str, Any]],
        final_state: CompanyState,
        ending_status: str,
    ) -> FounderProfile:
        """Classify the player's founder archetype from full-game patterns."""
        total_actions = len(snapshots)
        if total_actions == 0:
            return FounderProfile(
                profile_type="chaotic_survivor",
                profile_title="混乱求生者",
                description="你的决策缺乏清晰方向，公司在混乱中勉强前行。",
            )

        # Estimate spending patterns from snapshots (cash delta between months)
        total_spend = 0.0

        prev_state = initial_state
        for snap in snapshots:
            state_dict = snap.get("state_json", snap)
            if isinstance(state_dict, str):
                import json

                state_dict = json.loads(state_dict)
            cash_delta = prev_state.cash - state_dict.get("cash", prev_state.cash)
            if cash_delta > 0:
                total_spend += cash_delta
            # Roughly attribute spending: snapshots alternate or we estimate
            prev_state = CompanyState(
                **{k: v for k, v in state_dict.items() if k in CompanyState.model_fields}
            )

        # Classify based on final state indicators
        product = final_state.product_score
        users = final_state.users
        mrr = final_state.mrr
        equity = final_state.founder_equity
        runway = final_state.runway_months
        valuation = final_state.valuation

        # tech_visionary: high product, Series A or survived
        if product >= 70 and ending_status in (
            "series_a_success",
            "survived_but_average",
        ):
            return FounderProfile(
                profile_type="tech_visionary",
                profile_title="技术极客",
                description="你相信产品为王，用技术实力说话。产品分高但商业化步伐可能偏慢——你是一个有信仰的建造者。",
            )

        # capital_player: heavy fundraising, low equity
        if equity < 80 and valuation > 20_000_000:
            return FounderProfile(
                profile_type="capital_player",
                profile_title="资本玩家",
                description="你深谙资本游戏——用股权换弹药，用规模换估值。每一轮融资都是精心计算的杠杆，但股权稀释是必须付出的代价。",
            )

        # growth_hacker: large user base, marketing-heavy
        if users >= 500 and mrr >= 200_000:
            return FounderProfile(
                profile_type="growth_hacker",
                profile_title="增长黑客",
                description="你对增长有敏锐的嗅觉，善于用营销和规模效应撬动市场。用户数和MRR是成绩单，但也需要注意产品根基。",
            )

        # conservative_operator: long runway, low spend
        if runway > 9 and product < 60 and users < 200:
            return FounderProfile(
                profile_type="conservative_operator",
                profile_title="保守派操盘手",
                description="你把现金流安全放在第一位，精打细算过日子。公司不容易死，但增长也相对缓慢——你是一个稳健的守成者。",
            )

        # balanced_leader: A轮成功 or moderate everything
        if ending_status == "series_a_success" or (50 <= product <= 85 and 200 <= users <= 800):
            return FounderProfile(
                profile_type="balanced_leader",
                profile_title="均衡型CEO",
                description="你在研发、营销、融资之间找到了平衡点。不极端、不偏废，用全面的能力带公司走向成功。",
            )

        # chaotic_survivor: no clear pattern, often slow_death or bankruptcy
        return FounderProfile(
            profile_type="chaotic_survivor",
            profile_title="混乱求生者",
            description="你的决策风格跳跃很大，时而激进时而保守。公司经历了不少波折——也许下次需要更清晰的战略主线。",
        )

    # ── Strategy scoring ─────────────────────────────────────────────────────

    @staticmethod
    def _score_strategy(
        initial_state: CompanyState,
        snapshots: list[dict[str, Any]],
        final_state: CompanyState,
        ending_status: str,
    ) -> StrategyScore:
        """Score the player's strategy across 5 dimensions (0-100)."""
        product = final_state.product_score
        users = final_state.users
        mrr = final_state.mrr
        equity = final_state.founder_equity
        runway = final_state.runway_months
        cash = final_state.cash

        # Product score: directly from final product_score
        product_score = min(100, max(0, product))

        # Growth score: based on MRR + users combination
        growth_raw = (mrr / 5000) + (users / 10)  # ~0-100 scale
        growth_score = min(100, max(0, int(growth_raw)))

        # Finance score: cash management + fundraising efficiency
        if equity >= 90:
            finance_score = min(100, max(0, int(cash / 10000 + runway * 5)))
        else:
            # Fundraised — value depends on whether it paid off
            finance_score = min(100, max(0, int(mrr / 5000 + runway * 3)))

        # Control score: equity retention
        control_score = min(100, equity)

        # Risk score: runway health
        if runway >= 12:
            risk_score = 100
        elif runway >= 6:
            risk_score = 80
        elif runway >= 3:
            risk_score = 50
        elif runway >= 1:
            risk_score = 30
        else:
            risk_score = 10

        # Overall: weighted average, bonus for Series A
        weights = {
            "product": 0.25,
            "growth": 0.25,
            "finance": 0.2,
            "control": 0.15,
            "risk": 0.15,
        }
        overall = int(
            product_score * weights["product"]
            + growth_score * weights["growth"]
            + finance_score * weights["finance"]
            + control_score * weights["control"]
            + risk_score * weights["risk"]
        )
        if ending_status == "series_a_success":
            overall = min(100, overall + 10)
        elif ending_status in ("bankruptcy", "founder_removed"):
            overall = max(0, overall - 15)

        return StrategyScore(
            product_score=product_score,
            growth_score=growth_score,
            finance_score=finance_score,
            control_score=control_score,
            risk_score=risk_score,
            overall_score=min(100, max(0, overall)),
        )

    # ── Key moments identification ───────────────────────────────────────────

    @staticmethod
    def _identify_key_moments(
        initial_state: CompanyState,
        snapshots: list[dict[str, Any]],
        event_logs: list[dict[str, Any]],
        final_state: CompanyState,
        ending_status: str,
    ) -> list[KeyMoment]:
        """Scan game history for pivotal turning points."""
        moments: list[KeyMoment] = []
        prev_cash = initial_state.cash
        prev_product = initial_state.product_score
        prev_mrr = initial_state.mrr
        prev_equity = initial_state.founder_equity

        for snap in snapshots:
            state_dict = snap.get("state_json", snap)
            if isinstance(state_dict, str):
                import json

                state_dict = json.loads(state_dict)
            month = snap.get("month", 0)
            cash = state_dict.get("cash", 0)
            product = state_dict.get("product_score", 0)
            mrr = state_dict.get("mrr", 0)
            equity = state_dict.get("founder_equity", 100)
            runway = state_dict.get("runway_months", 0)
            if isinstance(runway, (int, float)):
                rw = float(runway)
            else:
                burn = state_dict.get("monthly_burn", 120000)
                rw = cash / burn if burn > 0 else float("inf")

            # Cash danger
            if cash <= 100_000 and prev_cash > 100_000:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="现金告急",
                        description=f"现金跌破10万，跑道仅剩{int(rw)}个月。生存成为第一优先级。",
                        impact_type="negative",
                        related_metrics={"cash": cash, "runway_months": int(rw)},
                    )
                )
            elif cash <= 10_000 and prev_cash > 10_000:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="现金濒危",
                        description="现金不足1万，公司命悬一线。",
                        impact_type="negative",
                        related_metrics={"cash": cash},
                    )
                )

            # Product breakthrough
            if product >= 70 and prev_product < 70:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="产品突破",
                        description="产品分突破70分，跻身市场领先水平。用户留存和转化率显著提升。",
                        impact_type="positive",
                        related_metrics={"product_score": product},
                    )
                )

            # MRR milestones
            for threshold, label in [
                (300_000, "30万"),
                (500_000, "50万"),
                (1_000_000, "100万"),
            ]:
                if mrr >= threshold and prev_mrr < threshold:
                    moments.append(
                        KeyMoment(
                            month=month,
                            title=f"MRR突破{label}",
                            description=f"月度经常性收入突破{label}元，公司进入新的增长阶段。",
                            impact_type="positive",
                            related_metrics={"mrr": mrr},
                        )
                    )
                    break  # only the first breakthrough counts

            # Equity dilution
            if equity < 80 and prev_equity >= 80:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="股权稀释",
                        description="创始人股权跌破80%，控制权开始松动。每次融资都是一把双刃剑。",
                        impact_type="neutral",
                        related_metrics={"founder_equity": equity},
                    )
                )
            elif equity < 50 and prev_equity >= 50:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="控制权危机",
                        description="股权跌破50%，已经失去了对公司的绝对控制。",
                        impact_type="negative",
                        related_metrics={"founder_equity": equity},
                    )
                )

            # Runway warning
            if rw < 3 and rw >= 0:
                moments.append(
                    KeyMoment(
                        month=month,
                        title="跑道不足3个月",
                        description=f"按当前烧钱速度，现金只够撑{int(rw)}个月。必须立刻融资或大幅削减开支。",
                        impact_type="negative",
                        related_metrics={"runway_months": int(rw)},
                    )
                )

            prev_cash = cash
            prev_product = product
            prev_mrr = mrr
            prev_equity = equity

        # Events as moments
        for evt in event_logs:
            severity = evt.get("severity", "medium")
            impact = (
                "positive"
                if severity == "low"
                else ("negative" if severity == "high" else "neutral")
            )
            moments.append(
                KeyMoment(
                    month=evt.get("month", 0),
                    title=evt.get("title", evt.get("event_type", "事件")),
                    description=evt.get("payload_json", "{}"),
                    impact_type=impact,
                    related_metrics={},
                )
            )

        # Ending as a moment
        if ending_status == "series_a_success":
            moments.append(
                KeyMoment(
                    month=final_state.month,
                    title="A轮融资成功",
                    description="公司完成了A轮融资，估值和收入都达到了投资人预期。这是创业路上的第一个里程碑。",
                    impact_type="positive",
                    related_metrics={
                        "mrr": final_state.mrr,
                        "valuation": final_state.valuation,
                    },
                )
            )

        # Sort by month, deduplicate, cap at 8
        moments.sort(key=lambda m: m.month)
        seen = set()
        unique = []
        for m in moments:
            key = (m.month, m.title)
            if key not in seen:
                seen.add(key)
                unique.append(m)
        return unique[:8]

    # ── Ending explanation ───────────────────────────────────────────────────

    @staticmethod
    def _explain_ending(
        ending_status: str,
        final_state: CompanyState,
        founder_profile: FounderProfile,
    ) -> tuple:
        """Return (title, summary, advice) for the ending."""
        profile_type = founder_profile.profile_type

        if ending_status == "series_a_success":
            titles = {
                "tech_visionary": "产品信仰",
                "growth_hacker": "增长为王",
                "capital_player": "资本杠杆",
                "balanced_leader": "技术驱动",
                "conservative_operator": "稳健制胜",
                "chaotic_survivor": "逆袭成功",
            }
            summaries = {
                "tech_visionary": "你用12个月打磨出了一款让竞品望尘莫及的产品。用户自发推荐、媒体争相报道、投资人主动敲门。产品信仰得到了回报。",
                "growth_hacker": "你以惊人的速度获取用户、占领市场。虽然产品不是最强的，但规模和品牌效应让你在A轮拿到了不错的估值。",
                "capital_player": "你精准地运用资本杠杆——在正确的时间融资，用股权换资源，把公司推到了A轮的门口。这是一场漂亮的资本游戏。",
                "balanced_leader": "你没有极端偏科，在研发、营销、融资之间保持了出色的平衡。全面的能力让公司在12个月后脱颖而出。",
                "conservative_operator": "你以稳扎稳打的方式走到了A轮——不冒进、不浪费、不乱稀释。这种风格也许不够性感，但足够可靠。",
                "chaotic_survivor": "经历了混乱和波折，但你最终挺过来了。A轮成功是对坚持最好的回报。下次也许可以更有章法。",
            }
            title = titles.get(profile_type, "A轮成功")
            summary = summaries.get(profile_type, "公司在第12个月成功完成了A轮融资。")
            advice = (
                "你已经找到了可复制的增长模式。A轮之后，关注团队规模化、市场扩张和产品矩阵的建立。"
            )

        elif ending_status == "survived_but_average":
            titles = {
                "tech_visionary": "小而美",
                "growth_hacker": "增长不足",
                "capital_player": "估值未兑现",
                "balanced_leader": "勉强及格",
                "conservative_operator": "现金流守成",
                "chaotic_survivor": "惊险存活",
            }
            if profile_type == "tech_visionary":
                summary = "产品做得很不错，但商业化的步伐不够快。公司活下来了，有一批忠实用户，但离投资人的增长预期还有差距。你有一个小而美的生意——只是VC不会为此买单。"
            elif profile_type == "conservative_operator":
                summary = "你小心翼翼地管理着现金流，公司确实活到了第12个月。但过于保守的策略让增长几乎停滞——活下来了，但没有飞起来。"
            else:
                summary = (
                    "公司活到了第12个月，但各项指标都未达到A轮门槛。你没有死，但也没有真正成功。"
                )
            title = titles.get(profile_type, "勉强存活")
            advice = "生存是第一课，你已经过关了。下一步需要把产品优势和商业化能力结合起来，找到增长飞轮的启动点。"

        elif ending_status == "slow_death":
            titles = {
                "tech_visionary": "技术孤岛",
                "growth_hacker": "营销泡沫",
                "capital_player": "错失融资窗口",
                "balanced_leader": "渐渐消失",
                "conservative_operator": "现金消耗过慢但增长停滞",
                "chaotic_survivor": "方向迷失",
            }
            if profile_type == "growth_hacker":
                summary = "你花了很多钱做营销，用户数确实涨了，但没有产品根基的支撑，留存率持续下滑。营销泡沫破裂时，用户走得比来得还快。"
            elif profile_type == "tech_visionary":
                summary = "你做出了不错的产品，但完全忽视了商业化和市场推广。好产品被埋没在噪音中，公司无声无息地走向终点。"
            else:
                summary = "公司没有戏剧性地倒下，而是一点点地从市场上消失了。每一个月的增长都差一口气，最终耗尽了时间和资源。"
            title = titles.get(profile_type, "慢性死亡")
            advice = "慢性死亡往往源于战略上的犹豫不决。下次尝试更聚焦的策略——要么全力打磨产品，要么全力做增长，中间状态最危险。"

        elif ending_status == "bankruptcy":
            if profile_type == "growth_hacker":
                title = "烧钱自焚"
                summary = "高增长的代价是高消耗。当营销投入无法快速转化为收入时，现金流断裂只是时间问题。你烧完了最后一分钱。"
            elif profile_type == "tech_visionary":
                title = "研发生不逢时"
                summary = "你在产品研发上投入了全部资源，但产品尚未成熟、收入尚未建立，现金已经耗尽。好的产品需要好的时机。"
            else:
                title = "现金断裂"
                summary = (
                    "公司现金流断裂，无法继续运营。创业路上最致命的不是竞争对手，而是钱花完了。"
                )
            advice = "现金流是创业公司的命脉。下次运营时，始终保持至少6个月的跑道，在现金低于危险线前果断融资或削减成本。"

        elif ending_status == "founder_removed":
            title = "出局"
            summary = "过度融资导致股权大幅稀释，你在董事会上失去了控制权。投资方联合投票更换了CEO——公司还在，但不再属于你。"
            advice = "融资是一把双刃剑。下次出让股权前，仔细计算每一轮稀释对控制权的影响。保留至少34%的股权才能拥有重大事项否决权。"

        else:
            title = "游戏结束"
            summary = "游戏结束。"
            advice = "总结这次经验，下次重新出发。"

        return title, summary, advice

    # ── Main entry point ────────────────────────────────────────────────────

    @classmethod
    def generate_review(
        cls,
        initial_state: CompanyState,
        snapshots: list[dict[str, Any]],
        action_logs: list[dict[str, Any]],
        event_logs: list[dict[str, Any]],
        final_state: CompanyState,
        ending_status: str,
        session_id: int = 0,
    ) -> GameReview:
        """Generate a complete post-game review.

        Args:
            initial_state: Company state at game start (month=1).
            snapshots: List of monthly state snapshots (each with 'month', 'state_json').
            action_logs: List of player actions per turn (each with 'month', 'raw_input', 'action_plan_json').
            event_logs: List of triggered events (each with 'month', 'event_type', 'title', 'severity').
            final_state: Company state at game end.
            ending_status: EndingType value string (e.g. 'series_a_success').
            session_id: Game session ID.

        Returns:
            GameReview with full analysis.
        """
        founder_profile = cls._classify_founder(
            initial_state, snapshots, final_state, ending_status
        )
        strategy_scores = cls._score_strategy(initial_state, snapshots, final_state, ending_status)
        key_moments = cls._identify_key_moments(
            initial_state, snapshots, event_logs, final_state, ending_status
        )
        ending_title, ending_summary, advice = cls._explain_ending(
            ending_status, final_state, founder_profile
        )

        final_metrics = {
            "month": final_state.month,
            "cash": final_state.cash,
            "monthly_burn": final_state.monthly_burn,
            "mrr": final_state.mrr,
            "users": final_state.users,
            "product_score": final_state.product_score,
            "team_morale": final_state.team_morale,
            "founder_equity": final_state.founder_equity,
            "board_control": final_state.board_control,
            "market_share": final_state.market_share,
            "reputation": final_state.reputation,
            "valuation": final_state.valuation,
            "runway_months": final_state.runway_months,
        }

        return GameReview(
            session_id=session_id,
            ending_status=ending_status,
            ending_title=ending_title,
            ending_summary=ending_summary,
            founder_profile=founder_profile,
            strategy_scores=strategy_scores,
            key_moments=key_moments,
            final_metrics=final_metrics,
            advice_for_next_run=advice,
        )
