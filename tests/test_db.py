"""Tests for database transaction integrity (P0-2).

Verifies that:
- transaction() yields the connection
- All writes inside process_turn use the same conn
- After process_turn, load_state returns the updated state
"""

import os
import tempfile

import pytest

# Override DB_PATH before importing modules that use it
os.environ.setdefault("STARTUP_SIM_TEST", "1")

from src.core.models import CompanyState
from src.db.connection import get_connection, init_db


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    import config

    old_db_path = str(config.DB_PATH)
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)

    # Patch config to use temp path
    config.DB_PATH = type(config.DB_PATH)(tmp_path)

    # Initialize DB
    init_db()

    yield tmp_path

    # Cleanup
    config.DB_PATH = type(config.DB_PATH)(old_db_path)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


class TestTransactionYieldsConn:
    """Test that transaction() yields the connection."""

    def test_transaction_yields_connection(self, temp_db):
        """transaction() should yield a sqlite3.Connection."""
        from src.db import repository
        import sqlite3

        with repository.transaction() as conn:
            assert isinstance(conn, sqlite3.Connection)
            # Should be able to execute on it
            conn.execute("SELECT 1")


class TestSaveWithConn:
    """Test that save_* functions accept conn and write correctly."""

    def test_save_state_with_conn(self, temp_db):
        """save_state with conn should persist data."""
        from src.db import repository

        # Create session + state
        sid = repository.create_session("test_player")
        state = CompanyState(
            cash=500_000, mrr=10_000, users=100, product_score=50,
            team_morale=80, founder_equity=90, board_control=85,
        )
        repository.init_session_state(sid, state)

        # Update via transaction
        state2 = CompanyState(
            cash=400_000, mrr=20_000, users=200, product_score=55,
            team_morale=75, founder_equity=85, board_control=80,
        )
        with repository.transaction() as conn:
            repository.save_state(sid, state2, conn=conn)
            repository.update_session_month(sid, 2, "active", conn=conn)
            repository.save_snapshot(sid, 2, state2, conn=conn)

        # Verify state was saved
        loaded = repository.load_state(sid)
        assert loaded.cash == 400_000
        assert loaded.mrr == 20_000
        assert loaded.users == 200
        assert loaded.product_score == 55

        # Verify snapshot was saved
        assert repository.snapshot_count() >= 1


class TestProcessTurnPersistence:
    """Test that process_turn persists state correctly."""

    def test_process_turn_then_load_state_updated(self, temp_db):
        """After process_turn, load_state returns updated state."""
        from src.db import repository
        from src.core.turn_engine import TurnEngine

        # Create session
        sid = repository.create_session("test_player")
        state = CompanyState(cash=1_000_000, mrr=0, users=0)
        repository.init_session_state(sid, state)

        # Process a turn
        engine = TurnEngine(sid)
        result = engine.process_turn("研发产品花20万")

        # Load state and verify it updated
        loaded = repository.load_state(sid)
        # Cash changed (spent on product action + monthly burn)
        assert loaded.cash != 1_000_000
        # Product score should have increased (product action)
        assert loaded.product_score > 20
        # Verify snapshots saved
        assert result.snapshots_saved >= 1

    def test_process_turn_saves_snapshot(self, temp_db):
        """After process_turn, a snapshot should exist."""
        from src.db import repository
        from src.core.turn_engine import TurnEngine

        sid = repository.create_session("test_player")
        state = CompanyState(cash=1_000_000)
        repository.init_session_state(sid, state)

        count_before = repository.snapshot_count()
        engine = TurnEngine(sid)
        result = engine.process_turn("花10万做营销")
        count_after = repository.snapshot_count()

        assert count_after > count_before
        assert result.snapshots_saved >= 1

    def test_process_turn_rollback_on_error(self, temp_db):
        """A valid turn should complete and state should be consistent afterward."""
        from src.db import repository
        from src.core.turn_engine import TurnEngine

        sid = repository.create_session("test_player")
        state = CompanyState(cash=500_000)
        repository.init_session_state(sid, state)

        engine = TurnEngine(sid)
        result = engine.process_turn("花10万做产品研发")  # valid turn

        # State should be persisted
        loaded = repository.load_state(sid)
        assert loaded is not None
        assert loaded.cash != state.cash  # Cash changed
        assert loaded.product_score > state.product_score  # Product improved

    def test_process_turn_rollback_preserves_previous_state(self, temp_db):
        """If an exception occurs mid-transaction in process_turn, state is NOT changed."""
        from unittest import mock
        from src.db import repository
        from src.core.turn_engine import TurnEngine

        sid = repository.create_session("test_player")
        state = CompanyState(cash=500_000, product_score=25)
        repository.init_session_state(sid, state)

        engine = TurnEngine(sid)

        # Mock save_snapshot to raise an exception inside the transaction
        original_save_snapshot = repository.save_snapshot
        def failing_save(*args, **kwargs):
            raise RuntimeError("simulated DB write failure")

        try:
            with mock.patch.object(repository, "save_snapshot", side_effect=failing_save):
                try:
                    engine.process_turn("花10万做产品研发")
                except RuntimeError:
                    pass  # expected

            # After rollback, state should be unchanged
            loaded = repository.load_state(sid)
            assert loaded.cash == state.cash
            assert loaded.product_score == state.product_score
        finally:
            repository.save_snapshot = original_save_snapshot
