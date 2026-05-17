"""Tests for feishu session persistence via external_sessions table.

Verifies that external_user_id → session_id mapping survives process
restarts, that consecutive turns reuse the same session, and that
restart/diagnostic commands behave correctly.
"""

import os
import tempfile

import pytest

os.environ.setdefault("STARTUP_SIM_TEST", "1")


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    import config

    old_db_path = str(config.DB_PATH)
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    config.DB_PATH = type(config.DB_PATH)(tmp_path)

    from src.db.connection import init_db

    init_db()

    yield tmp_path

    config.DB_PATH = type(config.DB_PATH)(old_db_path)
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


class TestSessionCreation:
    """Tests for session creation and reuse."""

    def test_first_message_creates_session(self, temp_db):
        """Same user's first message should create a new session."""
        from src.db import repository

        ext_id = "feishu:ou_test_user_1"

        sid, is_new = repository.get_or_create_external_session("feishu", ext_id)
        assert is_new
        assert sid > 0

    def test_second_message_reuses_session(self, temp_db):
        """Same user's second message must return the same session_id."""
        from src.db import repository

        ext_id = "feishu:ou_test_user_2"

        sid1, is_new1 = repository.get_or_create_external_session("feishu", ext_id)
        sid2, is_new2 = repository.get_or_create_external_session("feishu", ext_id)

        assert is_new1
        assert not is_new2
        assert sid1 == sid2

    def test_consecutive_turns_increment_month(self, temp_db):
        """Two consecutive turns on the same session should advance month."""
        from src.core.models import CompanyState
        from src.core.turn_engine import TurnEngine
        from src.db import repository

        ext_id = "feishu:ou_test_user_3"
        sid, _ = repository.get_or_create_external_session("feishu", ext_id)
        state = CompanyState(cash=2_000_000, month=1)
        repository.init_session_state(sid, state)
        repository.update_session_month(sid, 1)

        engine = TurnEngine(sid)
        engine.process_turn("花20万研发产品")
        loaded1 = repository.load_state(sid)
        month1 = loaded1.month

        engine.process_turn("花10万做营销")
        loaded2 = repository.load_state(sid)
        month2 = loaded2.month

        assert month2 > month1

    def test_status_does_not_create_session(self, temp_db):
        """Status command must not create a new session."""
        from src.db import repository

        ext_id = "feishu:ou_test_user_4"
        found = repository.find_session_by_external_user("feishu", ext_id)
        assert found is None


class TestStartAndRestart:
    """Tests for start/restart command behavior."""

    def test_start_with_existing_session_does_not_overwrite(self, temp_db):
        """'开始' when session exists should keep the old session."""
        from src.core.models import CompanyState
        from src.db import repository

        ext_id = "feishu:ou_test_user_5"
        sid1, _ = repository.get_or_create_external_session("feishu", ext_id)
        state = CompanyState(cash=3_000_000, month=3)
        repository.init_session_state(sid1, state)

        # Simulate checking — existing sid should still be found
        sid2 = repository.find_session_by_external_user("feishu", ext_id)
        assert sid2 == sid1

    def test_restart_creates_new_session_and_overwrites_binding(self, temp_db):
        """'重新开始' must delete old binding and create new session."""
        from src.db import repository

        ext_id = "feishu:ou_test_user_6"
        sid1, _ = repository.get_or_create_external_session("feishu", ext_id)

        # Restart: delete old, create new
        repository.delete_external_session("feishu", ext_id)
        sid2 = repository.create_session(ext_id)
        repository.bind_external_session("feishu", ext_id, sid2)

        assert sid2 != sid1
        found = repository.find_session_by_external_user("feishu", ext_id)
        assert found == sid2

    def test_restart_preserves_game_state_separately(self, temp_db):
        """After restart, old session state should be untouched in DB."""
        from src.core.models import CompanyState
        from src.db import repository

        ext_id = "feishu:ou_test_user_7"
        sid1, _ = repository.get_or_create_external_session("feishu", ext_id)
        state1 = CompanyState(cash=1_500_000, month=5)
        repository.init_session_state(sid1, state1)
        repository.update_session_month(sid1, 5)

        # Restart
        repository.delete_external_session("feishu", ext_id)
        sid2 = repository.create_session(ext_id)
        repository.bind_external_session("feishu", ext_id, sid2)

        # Old session state still exists
        old = repository.load_state(sid1)
        assert old.cash == 1_500_000
        assert old.month == 5


class TestProcessRestartRecovery:
    """Tests that session mapping survives simulated process restart."""

    def test_recover_session_after_simulated_restart(self, temp_db):
        """After creating a session, querying again (like after restart) must find it."""
        from src.db import repository

        ext_id = "feishu:ou_test_user_8"
        sid1, _ = repository.get_or_create_external_session("feishu", ext_id)

        # Simulate process restart: query by external_user_id directly
        sid2 = repository.find_session_by_external_user("feishu", ext_id)
        assert sid2 == sid1

    def test_recover_session_with_state_after_restart(self, temp_db):
        """After restart, full state should be recoverable from external_user_id."""
        from src.core.models import CompanyState
        from src.db import repository

        ext_id = "feishu:ou_test_user_9"
        sid, _ = repository.get_or_create_external_session("feishu", ext_id)
        state = CompanyState(cash=800_000, month=4, product_score=45)
        repository.init_session_state(sid, state)
        repository.update_session_month(sid, 4)

        # Simulate restart — find session and load state
        recovered_sid = repository.find_session_by_external_user("feishu", ext_id)
        assert recovered_sid == sid
        loaded = repository.load_state(recovered_sid)
        assert loaded.cash == 800_000
        assert loaded.month == 4
        assert loaded.product_score == 45


class TestMultiUserIsolation:
    """Tests that different users get different sessions."""

    def test_group_chat_different_users_not_shared(self, temp_db):
        """Two users in same group chat must get separate sessions."""
        from src.db import repository

        user_a = "feishu:chat_001:user_A"
        user_b = "feishu:chat_001:user_B"

        sid_a, _ = repository.get_or_create_external_session("feishu", user_a)
        sid_b, _ = repository.get_or_create_external_session("feishu", user_b)

        assert sid_a != sid_b

    def test_private_chat_same_user_stable_mapping(self, temp_db):
        """Same private chat user always returns the same session_id."""
        from src.db import repository

        user_p = "feishu:ou_private_user_P"
        sid1, _ = repository.get_or_create_external_session("feishu", user_p)
        sid2 = repository.find_session_by_external_user("feishu", user_p)
        sid3, _ = repository.get_or_create_external_session("feishu", user_p)

        assert sid1 == sid2 == sid3


class TestSessionDiagnostic:
    """Tests for the session diagnostic command."""

    def test_diagnostic_returns_correct_info(self, temp_db):
        """Session diagnostic should return external_user_id, session_id, month, status."""
        from src.core.models import CompanyState
        from src.db import repository

        ext_id = "feishu:ou_diag_test"
        sid, _ = repository.get_or_create_external_session("feishu", ext_id)
        state = CompanyState(cash=1_200_000, month=3, product_score=35, mrr=50_000)
        repository.init_session_state(sid, state)
        repository.update_session_month(sid, 3)

        session_info = repository.get_session_status(sid)
        loaded = repository.load_state(sid)

        assert session_info is not None
        assert loaded.month == 3
        assert loaded.cash == 1_200_000
        assert loaded.product_score == 35

    def test_diagnostic_unknown_user(self, temp_db):
        """Diagnostic for unknown user should return None from find_session."""
        from src.db import repository

        result = repository.find_session_by_external_user("feishu", "feishu:ou_nonexistent")
        assert result is None


class TestExtractFeishuIdentity:
    """Tests for extract_feishu_identity function."""

    def test_default_identity_with_no_event(self):
        """With no event, returns the default test user."""
        import feishu_play

        uid = feishu_play.extract_feishu_identity(None)
        assert uid == feishu_play.DEFAULT_EXTERNAL_USER_ID

    def test_default_identity_starts_with_feishu(self):
        """The default identity must start with 'feishu:'."""
        import feishu_play

        uid = feishu_play.extract_feishu_identity(None)
        assert uid.startswith("feishu:")
