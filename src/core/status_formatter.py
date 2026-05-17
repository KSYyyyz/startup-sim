"""Status formatter — renders CompanyState as human-readable panels.

Used by both CLI (full panel) and Feishu (compact panel).
Both versions always show ALL core metrics, even if zero.
"""

from __future__ import annotations

from src.core.models import CompanyState
from src.core.turn_engine import _identify_risks


def format_status_panel(state: CompanyState) -> str:
    """Full status panel for CLI output."""
    runway = state.runway_months
    runway_str = f"{runway:.1f}个月" if runway != float("inf") else "∞"

    lines = [
        "=" * 60,
        f"  📊 公司状态  —  第 {state.month} 个月",
        "=" * 60,
        f"  💰 现金:      {_money(state.cash):>10}     🔥 月消耗:   {_money(state.monthly_burn):>10}",
        f"  📈 MRR:       {_money(state.mrr):>10}     👥 用户:     {state.users:>10}",
        f"  🛠️  产品评分:  {state.product_score:>10}     💪 团队士气: {state.team_morale:>10}",
        f"  👨‍💻 员工数:    {state.employee_count:>10}     ⭐ 声誉:     {state.reputation:>10}",
        f"  📊 创始人股权:{state.founder_equity:>10}%    🏛️  董事会:   {state.board_control:>10}%",
        f"  📈 市场份额:  {state.market_share:>10}%    🏦 估值:     {_money(state.valuation):>10}",
        f"  ⏳ 现金流可支撑时间:  {runway_str:>10}",
        "=" * 60,
    ]

    # ── Risk summary ────────────────────────────────────────────────────
    risks = _identify_risks(state)
    if risks:
        lines.append(f"  ⚠️  当前风险: {risks[0]}")
    else:
        lines.append("  ✅ 暂无明显风险信号。")
    lines.append("=" * 60)

    return "\n".join(lines)


def format_status_panel_short(state: CompanyState) -> str:
    """Compact status for Feishu — still includes ALL core metrics."""
    risks = _identify_risks(state)
    if risks:
        # Compact: join up to 2 risks with separator
        risk_summary = "；".join(risks[:2])
    else:
        risk_summary = "暂无显著风险"

    lines = [
        f"💰 现金:{state.cash//10000}万 | 🔥 烧钱:{state.monthly_burn//10000}万/月 | ⏳ 可支撑:{state.runway_months:.1f}月",
        f"📈 MRR:{state.mrr//10000}万 | 👥 用户:{state.users} | ⭐ 声誉:{state.reputation}",
        f"🛠️ 产品:{state.product_score} | 💪 士气:{state.team_morale} | 👨‍💻 员工:{state.employee_count}人",
        f"📊 股权:创始人{state.founder_equity}% | 董事会控制:{state.board_control}% | 🏦 估值:{state.valuation//10000}万",
        f"⚠️ 风险: {risk_summary}",
    ]

    return "\n".join(lines)


def _money(v: int) -> str:
    """Format integer money to readable string."""
    if abs(v) >= 10_000:
        return f"{v/10000:.1f}万"
    return str(v)
