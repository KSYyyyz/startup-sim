import os
import tempfile

import pytest
from fastapi.testclient import TestClient


@pytest.fixture()
def temp_db():
    import config

    old_db_path = config.DB_PATH
    fd, tmp_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    config.DB_PATH = type(config.DB_PATH)(tmp_path)

    from src.db.connection import init_db

    init_db()
    yield tmp_path

    config.DB_PATH = old_db_path
    if os.path.exists(tmp_path):
        os.remove(tmp_path)


@pytest.fixture()
def client(temp_db):
    from src.api.app import create_app

    return TestClient(create_app())


def _body_text(payload) -> str:
    return str(payload)


def test_health_endpoint(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"ok": True, "service": "startup-sim-api"}


def test_create_session_returns_frontend_state_contract(client):
    response = client.post(
        "/api/sessions",
        json={"player_name": "Tester", "company_name": "NimbusAI"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["session_id"] > 0
    assert payload["status"] == "active"
    assert payload["metrics"]["month"] == 1
    assert payload["metrics"]["cash"] == 1_000_000
    assert payload["metrics"]["cash_coverage_months"] > 0
    assert payload["stage"]["company_name"] == "NimbusAI"
    assert payload["core_tension"]["title"]
    assert payload["insight"]["title"]
    assert payload["advice_entry"]["summary"] == "输入「建议」查看详情"
    assert "suggestions" not in payload["advice_entry"]
    assert "现金流可支撑时间" in payload["metrics"]["cash_coverage_label"]
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)


def test_submit_turn_returns_post_turn_feedback(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花10万研发产品"},
    )

    assert response.status_code == 200
    payload = response.json()
    state = payload["state"]

    assert state["metrics"]["month"] == 2
    assert state["metrics"]["cash_change"] < 0
    assert state["board"], "board feedback should be visible each turn"
    assert state["competitors"], "competitor status should be visible each turn"
    assert state["core_tension"]["title"]
    assert state["insight"]["description"]
    assert payload["turn"]["month"] == 1
    assert payload["turn"]["delta_reasons"]
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)


def test_suggestions_are_loaded_on_demand(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.get(f"/api/sessions/{session_id}/suggestions")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 3
    assert all(item["title"] for item in payload["items"])
    assert all(item["command"] for item in payload["items"])


def test_empty_turn_command_returns_plain_language_error(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.post(f"/api/sessions/{session_id}/turns", json={"command": "  "})

    assert response.status_code == 400
    assert response.json()["message"] == "请输入本回合要执行的动作。"
