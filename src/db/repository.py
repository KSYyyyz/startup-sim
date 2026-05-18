"""Repository layer: transactional DB operations for startup-sim.

All writes to game state go through this module. Every turn is wrapped in a
BEGIN IMMEDIATE transaction — if anything fails, the full turn is rolled back.

P0-2: All save_* functions accept an optional conn parameter. When called
inside a transaction(), the same conn is used for all writes.
"""

from __future__ import annotations

import sqlite3
from collections.abc import Generator
from contextlib import contextmanager

from src.core.models import CompanyState
from src.db.connection import get_connection
from src.db.connection import init_db as _init_db


def _get_conn(conn: sqlite3.Connection | None = None) -> tuple[sqlite3.Connection, bool]:
    """Return (connection, owns) — owns=True means caller must close."""
    if conn is not None:
        return conn, False
    return get_connection(), True


def _row_to_state(row) -> CompanyState:
    """Convert a sqlite3.Row to a CompanyState."""
    return CompanyState(
        month=row["current_month"] if "current_month" in row.keys() else 1,  # noqa: SIM118
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


def create_session(
    player_name: str,
    scenario_id: str = "ai_customer_service_saas",
    difficulty: str = "normal",
    seed: int = 42,
) -> int:
    """Create a new game session. Returns session ID."""
    conn, owns = _get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO game_sessions (player_name, scenario_id, difficulty, seed)
               VALUES (?, ?, ?, ?)""",
            (player_name, scenario_id, difficulty, seed),
        )
        conn.commit()
        return cur.lastrowid
    finally:
        if owns:
            conn.close()


def init_session_state(
    session_id: int, state: CompanyState, conn: sqlite3.Connection | None = None
) -> None:
    """Initialize company_state for a session."""
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            """INSERT INTO company_state (session_id, cash, monthly_burn, mrr, users,
               product_score, team_morale, founder_equity, board_control,
               market_share, reputation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                state.cash,
                state.monthly_burn,
                state.mrr,
                state.users,
                state.product_score,
                state.team_morale,
                state.founder_equity,
                state.board_control,
                state.market_share,
                state.reputation,
            ),
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()


def load_state(session_id: int) -> CompanyState:
    """Load current game state for a session, including current_month."""
    conn, owns = _get_conn()
    try:
        row = conn.execute(
            """SELECT cs.*, gs.current_month
               FROM company_state cs
               JOIN game_sessions gs ON cs.session_id = gs.id
               WHERE cs.session_id = ?""",
            (session_id,),
        ).fetchone()
        if row is None:
            raise RuntimeError(f"company_state missing for session {session_id}")
        return _row_to_state(row)
    finally:
        if owns:
            conn.close()


def save_state(
    session_id: int, state: CompanyState, conn: sqlite3.Connection | None = None
) -> None:
    """Update company_state for a session."""
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            """UPDATE company_state SET
                cash=?, monthly_burn=?, mrr=?, users=?,
                product_score=?, team_morale=?, founder_equity=?,
                board_control=?, market_share=?, reputation=?
            WHERE session_id=?""",
            (
                state.cash,
                state.monthly_burn,
                state.mrr,
                state.users,
                state.product_score,
                state.team_morale,
                state.founder_equity,
                state.board_control,
                state.market_share,
                state.reputation,
                session_id,
            ),
        )
    finally:
        if owns:
            conn.close()


def update_session_month(
    session_id: int, month: int, status: str = "active", conn: sqlite3.Connection | None = None
) -> None:
    """Update current_month and optionally status on game_sessions."""
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            """UPDATE game_sessions SET current_month=?, status=?, updated_at=datetime('now')
               WHERE id=?""",
            (month, status, session_id),
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()


def save_snapshot(
    session_id: int, month: int, state: CompanyState, conn: sqlite3.Connection | None = None
) -> int:
    """Save a snapshot of the current state. Returns snapshot ID."""
    conn, owns = _get_conn(conn)
    try:
        cur = conn.execute(
            "INSERT INTO snapshots (session_id, month, state_json) VALUES (?, ?, ?)",
            (session_id, month, state.model_dump_json()),
        )
        return cur.lastrowid
    finally:
        if owns:
            conn.close()


def snapshot_count() -> int:
    """Return the number of snapshots stored."""
    conn, owns = _get_conn()
    try:
        row = conn.execute("SELECT COUNT(*) as cnt FROM snapshots").fetchone()
        return row["cnt"]
    finally:
        if owns:
            conn.close()


def save_action(
    session_id: int,
    month: int,
    raw_input: str,
    action_plan_json: str,
    result_json: str = "{}",
    conn: sqlite3.Connection | None = None,
) -> int:
    """Log an action for a turn."""
    conn, owns = _get_conn(conn)
    try:
        cur = conn.execute(
            """INSERT INTO actions (session_id, month, raw_input, action_plan_json, result_json)
               VALUES (?, ?, ?, ?, ?)""",
            (session_id, month, raw_input, action_plan_json, result_json),
        )
        return cur.lastrowid
    finally:
        if owns:
            conn.close()


def save_event(
    session_id: int,
    month: int,
    event_type: str,
    title: str,
    severity: str = "medium",
    payload_json: str = "{}",
    conn: sqlite3.Connection | None = None,
) -> int:
    """Log a game event."""
    conn, owns = _get_conn(conn)
    try:
        cur = conn.execute(
            """INSERT INTO events (session_id, month, event_type, title, severity, payload_json)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (session_id, month, event_type, title, severity, payload_json),
        )
        return cur.lastrowid
    finally:
        if owns:
            conn.close()


def save_role_memory_history(
    session_id: int,
    memories: list[dict],
    conn: sqlite3.Connection | None = None,
) -> None:
    """Persist role memories derived from a settled turn."""
    conn, owns = _get_conn(conn)
    try:
        conn.executemany(
            """INSERT INTO role_memory_history
               (session_id, month, role_id, role_name, fact, implication, source)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            [
                (
                    session_id,
                    memory["month"],
                    memory["role_id"],
                    memory["role_name"],
                    memory["fact"],
                    memory["implication"],
                    memory.get("source", "settled-turn-facts"),
                )
                for memory in memories
            ],
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()


def list_recent_role_memory(session_id: int, limit: int = 12) -> list[dict]:
    """Return recent persisted role memories for a session, newest first."""
    conn, owns = _get_conn()
    try:
        rows = conn.execute(
            """SELECT id, session_id, month, role_id, role_name, fact, implication, source, created_at
               FROM role_memory_history
               WHERE session_id = ?
               ORDER BY month DESC, id DESC
               LIMIT ?""",
            (session_id, limit),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "month": r["month"],
                "role_id": r["role_id"],
                "role_name": r["role_name"],
                "fact": r["fact"],
                "implication": r["implication"],
                "source": r["source"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        if owns:
            conn.close()


def reset_session(session_id: int, scenario_state: CompanyState) -> None:
    """Reset a session to scenario initial state."""
    conn, owns = _get_conn()
    try:
        conn.execute("DELETE FROM company_state WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM actions WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM events WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM snapshots WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM competitors WHERE session_id = ?", (session_id,))
        conn.execute("DELETE FROM role_memory_history WHERE session_id = ?", (session_id,))
        conn.execute(
            """INSERT INTO company_state (session_id, cash, monthly_burn, mrr, users,
               product_score, team_morale, founder_equity, board_control,
               market_share, reputation)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                session_id,
                scenario_state.cash,
                scenario_state.monthly_burn,
                scenario_state.mrr,
                scenario_state.users,
                scenario_state.product_score,
                scenario_state.team_morale,
                scenario_state.founder_equity,
                scenario_state.board_control,
                scenario_state.market_share,
                scenario_state.reputation,
            ),
        )
        conn.execute(
            "UPDATE game_sessions SET current_month=1, status='active', updated_at=datetime('now') WHERE id=?",
            (session_id,),
        )
        conn.commit()
    finally:
        if owns:
            conn.close()


def get_session_status(session_id: int) -> dict | None:
    """Get session metadata."""
    conn, owns = _get_conn()
    try:
        row = conn.execute("SELECT * FROM game_sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        if owns:
            conn.close()


def find_active_session_by_player_name(player_name: str) -> int | None:
    """Find the most recent active session for a player. Returns session_id or None."""
    conn, owns = _get_conn()
    try:
        row = conn.execute(
            """SELECT id FROM game_sessions
               WHERE player_name = ? AND status = 'active'
               ORDER BY created_at DESC
               LIMIT 1""",
            (player_name,),
        ).fetchone()
        if row is None:
            return None
        return row["id"]
    finally:
        if owns:
            conn.close()


@contextmanager
def transaction() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for BEGIN IMMEDIATE transactions.

    Yields the connection so that callers can pass it to save_* functions.
    Commits on clean exit, rolls back on exception.

    Usage:
        with repository.transaction() as conn:
            repository.save_state(session_id, new_state, conn=conn)
            repository.save_snapshot(session_id, month, new_state, conn=conn)
    """
    conn = get_connection()
    try:
        conn.execute("BEGIN IMMEDIATE")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Alpha 1.4: History queries for review engine ────────────────────────────


def list_snapshots(session_id: int) -> list[dict]:
    """Return all state snapshots for a session, ordered by month."""
    conn, owns = _get_conn()
    try:
        rows = conn.execute(
            "SELECT id, session_id, month, state_json, created_at "
            "FROM snapshots WHERE session_id = ? ORDER BY month",
            (session_id,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "month": r["month"],
                "state_json": r["state_json"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        if owns:
            conn.close()


def list_actions(session_id: int) -> list[dict]:
    """Return all player actions for a session, ordered by month."""
    conn, owns = _get_conn()
    try:
        rows = conn.execute(
            "SELECT id, session_id, month, raw_input, action_plan_json, result_json, created_at "
            "FROM actions WHERE session_id = ? ORDER BY month",
            (session_id,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "month": r["month"],
                "raw_input": r["raw_input"],
                "action_plan_json": r["action_plan_json"],
                "result_json": r["result_json"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        if owns:
            conn.close()


def list_events(session_id: int) -> list[dict]:
    """Return all game events for a session, ordered by month."""
    conn, owns = _get_conn()
    try:
        rows = conn.execute(
            "SELECT id, session_id, month, event_type, title, severity, payload_json, created_at "
            "FROM events WHERE session_id = ? ORDER BY month",
            (session_id,),
        ).fetchall()
        return [
            {
                "id": r["id"],
                "session_id": r["session_id"],
                "month": r["month"],
                "event_type": r["event_type"],
                "title": r["title"],
                "severity": r["severity"],
                "payload_json": r["payload_json"],
                "created_at": r["created_at"],
            }
            for r in rows
        ]
    finally:
        if owns:
            conn.close()


# ── External sessions: map platform user IDs to game sessions ──────────────


def _ensure_schema() -> None:
    """Ensure external_sessions table exists (idempotent)."""
    _init_db()


def bind_external_session(
    source: str, external_user_id: str, session_id: int, conn: sqlite3.Connection | None = None
) -> None:
    """Bind an external user to a game session (INSERT OR REPLACE)."""
    _ensure_schema()
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            """INSERT OR REPLACE INTO external_sessions (source, external_user_id, session_id, updated_at)
               VALUES (?, ?, ?, datetime('now','localtime'))""",
            (source, external_user_id, session_id),
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()


def find_session_by_external_user(
    source: str, external_user_id: str, conn: sqlite3.Connection | None = None
) -> int | None:
    """Find the session_id bound to an external user. Returns None if not found."""
    _ensure_schema()
    conn, owns = _get_conn(conn)
    try:
        row = conn.execute(
            "SELECT session_id FROM external_sessions WHERE source = ? AND external_user_id = ?",
            (source, external_user_id),
        ).fetchone()
        return row["session_id"] if row else None
    finally:
        if owns:
            conn.close()


def get_or_create_external_session(
    source: str,
    external_user_id: str,
    player_name: str | None = None,
    conn: sqlite3.Connection | None = None,
) -> tuple[int, bool]:
    """Get existing session for external user, or create a new one.

    Returns (session_id, is_new) — is_new is True when a fresh session was created.
    """
    _ensure_schema()
    conn, owns = _get_conn(conn)
    try:
        row = conn.execute(
            "SELECT session_id FROM external_sessions WHERE source = ? AND external_user_id = ?",
            (source, external_user_id),
        ).fetchone()
        if row:
            return row["session_id"], False

        name = player_name or external_user_id
        cur = conn.execute("INSERT INTO game_sessions (player_name) VALUES (?)", (name,))
        sid = cur.lastrowid
        conn.execute(
            """INSERT INTO external_sessions (source, external_user_id, session_id)
               VALUES (?, ?, ?)""",
            (source, external_user_id, sid),
        )
        if owns:
            conn.commit()
        return sid, True
    finally:
        if owns:
            conn.close()


def update_external_session_time(
    source: str, external_user_id: str, conn: sqlite3.Connection | None = None
) -> None:
    """Touch the updated_at timestamp for an external session binding."""
    _ensure_schema()
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            "UPDATE external_sessions SET updated_at = datetime('now','localtime') "
            "WHERE source = ? AND external_user_id = ?",
            (source, external_user_id),
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()


def delete_external_session(
    source: str, external_user_id: str, conn: sqlite3.Connection | None = None
) -> None:
    """Remove an external session binding (for '重新开始')."""
    _ensure_schema()
    conn, owns = _get_conn(conn)
    try:
        conn.execute(
            "DELETE FROM external_sessions WHERE source = ? AND external_user_id = ?",
            (source, external_user_id),
        )
        if owns:
            conn.commit()
    finally:
        if owns:
            conn.close()
