"""Tests for board member agents / 董事会会议 (Phase 1B)."""

import pytest
from src.core.models import ActionPlan, CompanyState, PlayerAction, ActionType
from src.agents.board import CFO, CTO, COO, InvestorDirector


def make_plan(*actions: PlayerAction) -> ActionPlan:
    """Helper to create an ActionPlan from PlayerActions."""
    return ActionPlan(raw_input="test", actions=list(actions))


# ── CFO tests ─────────────────────────────────────────────────────────────────

def test_cfo_warns_low_runway():
    """When runway < 4 months, CFO output should mention 融资 or 削减."""
    cfo = CFO()
    state = CompanyState(cash=300_000, monthly_burn=100_000)  # runway = 3.0
    plan = make_plan()
    result = cfo.speak(state, plan)
    assert "融资" in result or "削减" in result


def test_cfo_mentions_equity_on_fundraising():
    """CFO warns about equity dilution during fundraising."""
    cfo = CFO()
    state = CompanyState(cash=2_000_000, monthly_burn=100_000)  # runway = 20
    plan = make_plan(PlayerAction(type=ActionType.FUNDRAISING, budget=500_000))
    result = cfo.speak(state, plan)
    # fundraising action + healthy runway → should mention equity
    assert "股权" in result or "A轮" in result


def test_cfo_default_healthy():
    """CFO default message when everything is fine."""
    cfo = CFO()
    state = CompanyState(cash=2_000_000, monthly_burn=200_000)  # runway = 10
    plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=50_000))
    result = cfo.speak(state, plan)
    assert "正常" in result or "健康" in result or "保持" in result


# ── CTO tests ─────────────────────────────────────────────────────────────────

def test_cto_suggests_improvement():
    """When product_score < 30, CTO output should mention 研发 or 产品分."""
    cto = CTO()
    state = CompanyState(product_score=15)
    plan = make_plan()
    result = cto.speak(state, plan)
    assert "研发" in result or "产品分" in result or "产品" in result


def test_cto_strong_product():
    """When product_score > 70, CTO suggests enterprise features."""
    cto = CTO()
    state = CompanyState(product_score=85)
    plan = make_plan()
    result = cto.speak(state, plan)
    assert "企业" in result or "壁垒" in result or "专利" in result


def test_cto_team_expansion_warning():
    """CTO warns about tech debt when team action is taken."""
    cto = CTO()
    state = CompanyState(product_score=50)
    plan = make_plan(PlayerAction(type=ActionType.TEAM, budget=100_000))
    result = cto.speak(state, plan)
    assert "技术债" in result or "配比" in result


# ── COO tests ─────────────────────────────────────────────────────────────────

def test_coo_cares_morale():
    """When team_morale < 50, COO output should mention 士气 or 激励."""
    coo = COO()
    state = CompanyState(team_morale=35)
    plan = make_plan()
    result = coo.speak(state, plan)
    assert "士气" in result or "激励" in result


def test_coo_high_morale():
    """When team_morale > 80, COO says team is in good shape."""
    coo = COO()
    state = CompanyState(team_morale=90)
    plan = make_plan()
    result = coo.speak(state, plan)
    assert "状态很好" in result or "效率" in result


def test_coo_marketing_low_runway_warning():
    """COO warns against marketing when runway < 3 and marketing action present."""
    coo = COO()
    state = CompanyState(cash=400_000, monthly_burn=200_000, team_morale=60)  # runway = 2.0
    plan = make_plan(PlayerAction(type=ActionType.MARKETING, budget=100_000))
    result = coo.speak(state, plan)
    assert "不建议" in result or "优先" in result


# ── Investor Director tests (投资方董事) ───────────────────────────────────────

def test_investor_warns_equity():
    """When founder_equity < 50, investor director output should mention 控制权 or 股权."""
    investor = InvestorDirector()
    state = CompanyState(founder_equity=35)
    plan = make_plan()
    result = investor.speak(state, plan)
    assert "控制权" in result or "股权" in result


def test_investor_slow_growth():
    """When MRR is very low, investor director complains about growth."""
    investor = InvestorDirector()
    state = CompanyState(founder_equity=80, mrr=50_000)
    plan = make_plan()
    result = investor.speak(state, plan)
    assert "增长" in result or "PMF" in result


def test_investor_board_control_weak():
    """When board_control < 60, investor director suggests pausing fundraising."""
    investor = InvestorDirector()
    state = CompanyState(founder_equity=60, mrr=500_000, board_control=45)
    plan = make_plan()
    result = investor.speak(state, plan)
    assert "融资" in result or "暂缓" in result


# ── Generic tests ─────────────────────────────────────────────────────────────

def test_all_board_members_return_non_empty_string():
    """Every board member returns a non-empty string for a standard state."""
    state = CompanyState(
        cash=1_000_000,
        monthly_burn=100_000,
        product_score=50,
        team_morale=60,
        founder_equity=70,
        mrr=200_000,
        board_control=70,
    )
    plan = make_plan(PlayerAction(type=ActionType.PRODUCT, budget=100_000))

    members = [CFO(), CTO(), COO(), InvestorDirector()]
    for member in members:
        result = member.speak(state, plan)
        assert isinstance(result, str), f"{member.name} returned {type(result)}"
        assert len(result) > 0, f"{member.name} returned empty string"


def test_board_member_names_are_distinct():
    """All board members have distinct names."""
    members = [CFO(), CTO(), COO(), InvestorDirector()]
    names = [m.name for m in members]
    assert len(names) == len(set(names)), f"Duplicate names: {names}"
