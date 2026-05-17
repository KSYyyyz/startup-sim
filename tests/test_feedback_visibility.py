"""Tests that TurnResult always has feedback fields populated after Alpha 1.8."""

from src.core.difficulty import get_difficulty
from src.core.models import CompanyState
from src.core.turn_engine import TurnEngine


def test_board_feedback_always_present():
    """TurnResult.board_feedback is not empty."""
    state = CompanyState(
        month=1,
        cash=1_000_000,
        monthly_burn=180_000,
        product_score=20,
        team_morale=70,
        founder_equity=100,
        board_control=100,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
    )
    result = TurnEngine.process_turn_raw(
        state, "花5万研发产品", difficulty=get_difficulty("normal")
    )
    assert result.board_feedback, "Board feedback should always be present"
    assert isinstance(result.board_feedback, dict)
    assert len(result.board_feedback) > 0


def test_competitor_moves_always_present():
    """TurnResult.competitor_moves list exists."""
    state = CompanyState(
        month=1,
        cash=1_000_000,
        monthly_burn=180_000,
        product_score=20,
        team_morale=70,
        founder_equity=100,
        board_control=100,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
    )
    result = TurnEngine.process_turn_raw(
        state, "花5万研发产品", difficulty=get_difficulty("normal")
    )
    assert isinstance(result.competitor_moves, list)
    assert len(result.competitor_moves) > 0


def test_customer_response_always_present():
    """TurnResult.customer_response dict exists."""
    state = CompanyState(
        month=1,
        cash=1_000_000,
        monthly_burn=180_000,
        product_score=20,
        team_morale=70,
        founder_equity=100,
        board_control=100,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
    )
    result = TurnEngine.process_turn_raw(
        state, "花5万研发产品", difficulty=get_difficulty("normal")
    )
    assert isinstance(result.customer_response, dict)
    assert len(result.customer_response) > 0


def test_events_list_always_exists():
    """TurnResult.events is a list."""
    state = CompanyState(
        month=1,
        cash=1_000_000,
        monthly_burn=180_000,
        product_score=20,
        team_morale=70,
        founder_equity=100,
        board_control=100,
        reputation=50,
        employee_count=10,
        price=5000,
        valuation=5_000_000,
    )
    result = TurnEngine.process_turn_raw(
        state, "花5万研发产品", difficulty=get_difficulty("normal")
    )
    assert isinstance(result.events, list)
