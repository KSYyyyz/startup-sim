"""Repository layer: transactional DB operations for startup-sim.

All writes to game state go through this module. Every turn is wrapped in a
BEGIN IMMEDIATE transaction — if anything fails, the full turn is rolled back.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from typing import Generator, Optional

from src.db.connection import get_connection
from src.core.models import CompanyState, TurnResult


def _row_to_state(row) -> CompanyState:
    """Convert a sqlite3.Row to a CompanyState."""
    return CompanyState(
        month=row["current_month"] if "current_month" in row.keys() else 1,
        cash=row["cash"],
        monthly_burn=row["monthly_burn"],
        mrr=row["mrr"],
        users=row["users"],
        product_score=row["product_score"],
        team_morale=row["team_morale"],
        founder_equity=row["founder_equity"],
        board_control=row["board_control"],
        market_share=row["market_share"],
        reputation=row["reputation"],
    )


def create_session(player_name: str, scenario_id: str = "ai_customer_service_saas",
                   difficulty: str = "normal", seed: int = 42) -> int:
    """Create a new game session. Returns session ID."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO game_sessions (player_name, scenario_id, difficulty, seed)
               VALUES (?, ?, ?, ?)""",
            (player_name, scenario_id, difficulty, seed),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def init_session_state(session_id: int, state: CompanyState) -> None:
    """Initialize company_state for a session."""
    conn = get_connection()
    try:
        conn.execute(
            """INSERT INTO company_state (session_id, cash, monthly_burn, mrr, users,
               product_score, team_morale, founder_equity, board_control,
               market_share, reputation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, state.cash, state.monthly_burn, state.mrr, state.users,
             state.product_score, state.team_morale, state.founder_equity,
             state.board_control, state.market_share, state.reputation),
        )
        conn.commit()
    finally:
        conn.close()


def load_state(session_id: int) -> CompanyState:
    """Load current game state for a session."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM company_state WHERE session_id = ?", (session_id,)
        ).fetchone()
        if row is None:
            raise RuntimeError(f"company_state missing for session {session_id}")
        return _row_to_state(row)
    finally:
        conn.close()


def save_state(session_id: int, state: CompanyState) -> None:
    """Update company_state for a session. Must be called inside a transaction."""
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE company_state SET
                cash=?, monthly_burn=?, mrr=?, users=?,
                product_score=?, team_morale=?, founder_equity=?,
                board_control=?, market_share=?, reputation=?
            WHERE session_id=?""",
            (state.cash, state.monthly_burn, state.mrr, state.users,
             state.product_score, state.team_morale, state.founder_equity,
             state.board_control, state.market_share, state.reputation,
             session_id),
        )
    finally:
        conn.close()


def update_session_month(session_id: int, month: int, status: str = "active") -> None:
    """Update current_month and optionally status on game_sessions."""
    conn = get_connection()
    try:
        conn.execute(
            """UPDATE game_sessions SET current_month=?, status=?, updated_at=datetime('now')
               WHERE id=?""",
            (month, status, session_id),
        )
    finally:
        conn.close()


def save_snapshot(session_id: int, month: int, state: CompanyState) -> int:
    """Save a snapshot of the current state. Returns snapshot ID."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO snapshots (session_id, month, state_json) VALUES (?, ?, ?)",
            (session_id, month, state.model_dump_json()),
        )
        return cur.lastrowid
    finally:
        conn.close()


def snapshot_count() -> int:
    """Return the number of snapshots stored."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM snapshots").fetchone()
        return row["cnt"]
    finally:
        conn.close()


def save_action(session_id: int, month: int, raw_input: str,
                action_plan_json: str, result_json: str = "{}") -> int:
    """Log an action for a turn."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO actions (session_id, month, raw_input, action_plan_json, result_json)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, month, raw_input, action_plan_json, result_json),
        )
        return cur.lastrowid
    finally:
        conn.close()


def save_event(session_id: int, month: int, event_type: str, title: str,
               severity: str = "medium", payload_json: str = "{}") -> int:
    """Log a game event."""
    conn = get_connection()
    try:
        cur = conn.execute(
            """INSERT INTO events (session_id, month, event_type, title, severity, payload_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, month, event_type, title, severity, payload_json),
        )
        return cur.lastrowid
    finally:
        conn.close()


def reset_session(session_id: int, scenario_state: CompanyState) -> None:
    """Reset a session to scenario initial state."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM company_state WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM actions WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM snapshots WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM competitors WHERE session_id = ?", (session_id,))
        conn.execute(
            """INSERT INTO company_state (session_id, cash, monthly_burn, mrr, users,
               product_score, team_morale, founder_equity, board_control,
               market_share, reputation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (session_id, scenario_state.cash, scenario_state.monthly_burn,
             scenario_state.mrr, scenario_state.users,
             scenario_state.product_score, scenario_state.team_morale,
             scenario_state.founder_equity, scenario_state.board_control,
             scenario_state.market_share, scenario_state.reputation),
        )
        conn.execute(
            "UPDATE game_sessions SET current_month=1, status='active', updated_at=datetime('now') WHERE id=?",
            (session_id,),
        )
        conn.commit()
    finally:
        conn.close()


def get_session_status(session_id: int) -> Optional[dict]:
    """Get session metadata."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM game_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


@contextmanager
def transaction() -> Generator[None, None, None]:
    """Context manager for BEGIN IMMEDIATE transactions.

    Usage:
        with repository.transaction():
            repository.save_state(session_id, new_state)
            repository.save_snapshot(session_id, month, new_state)
    """
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
