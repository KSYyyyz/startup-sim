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
    turn = payload["turn"]
    assert turn["month"] == 1
    assert turn["delta_reasons"]
    facts = turn["turn_facts"]
    assert set(facts) == {
        "month",
        "command",
        "changes",
        "replay_basis",
        "next_pressure",
        "authority",
    }
    assert facts["month"] == turn["month"]
    assert facts["command"] == "花10万研发产品"
    assert facts["authority"] == "backend-turn-engine"
    assert facts["replay_basis"] == turn["delta_reasons"]
    assert facts["next_pressure"] == state["core_tension"]["next_focus"]
    cash_change = next(item for item in facts["changes"] if item["metric"] == "cash")
    product_change = next(item for item in facts["changes"] if item["metric"] == "product_score")
    assert cash_change["delta"] == state["metrics"]["cash_change"]
    assert cash_change["label"] == "现金"
    assert cash_change["tone"] == "bad"
    assert product_change["delta"] == state["metrics"]["product_change"]
    assert product_change["label"] == "产品"
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)


def test_command_preview_explains_free_text_without_advancing_turn(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/command-preview",
        json={"command": "花10万研发产品，花5万做营销"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert payload["summary"] == "系统将这条 CEO 指令理解为 2 个可执行动作。"
    assert [action["type"] for action in payload["actions"]] == ["product", "marketing"]
    assert [action["label"] for action in payload["actions"]] == ["产品研发", "市场营销"]
    assert payload["actions"][0]["budget"] == 100_000
    assert payload["actions"][0]["budget_label"] == "10万"
    assert payload["actions"][0]["tradeoffs"] == ["产品 +", "现金 -"]
    assert payload["actions"][1]["budget"] == 50_000
    assert payload["status"] == "ready"
    assert "数值结算仍由 TurnEngine 执行" in payload["guardrail"]

    after = client.get(f"/api/sessions/{session_id}").json()
    assert after["metrics"]["month"] == 1
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)


def test_command_preview_handles_unclear_input(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.post(
        f"/api/sessions/{session_id}/command-preview",
        json={"command": "让公司变得更厉害"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "needs_clarification"
    assert payload["actions"] == []
    assert "没有识别到可执行动作" in payload["summary"]


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
