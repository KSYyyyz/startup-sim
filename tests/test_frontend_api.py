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
    role_memory = turn["role_memory"]
    assert role_memory
    assert {item["source"] for item in role_memory} == {"settled-turn-facts"}
    assert {"CFO", "CTO", "COO"} <= {item["role_name"] for item in role_memory}
    cfo_memory = next(item for item in role_memory if item["role_id"] == "cfo")
    assert cfo_memory["month"] == facts["month"]
    assert "cash" in cfo_memory["fact"]
    assert str(cash_change["delta"]) in cfo_memory["fact"]
    assert cfo_memory["implication"]

    office_signals = turn["office_signals"]
    assert office_signals
    assert {item["source"] for item in office_signals} >= {
        "settled-core-tension",
        "settled-business-insight",
    }
    core_signal = next(item for item in office_signals if item["source"] == "settled-core-tension")
    assert set(core_signal) == {
        "id",
        "room_id",
        "title",
        "description",
        "severity",
        "source",
        "visual_intent",
    }
    assert core_signal["title"] == state["core_tension"]["title"]
    assert core_signal["description"] == state["core_tension"]["description"]
    assert core_signal["severity"] == state["core_tension"]["severity"]
    assert core_signal["visual_intent"] == "surface-in-office"
    story_events = turn["story_events"]
    assert story_events
    assert all(
        item["source"] in {"rule-event", "competitor-fact", "business-insight"}
        for item in story_events
    )
    assert all(item["title"] and item["description"] for item in story_events)
    assert {item["tone"] for item in story_events} <= {
        "neutral",
        "good",
        "bad",
        "warning",
        "opportunity",
    }
    assert product_change["label"] == "产品"
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)


def test_submit_turn_persists_role_memory_history(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    first = client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花10万研发产品"},
    ).json()
    second = client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花5万做营销"},
    ).json()

    first_memory = first["turn"]["role_memory"]
    second_memory = second["turn"]["role_memory"]
    history = second["turn"]["memory_history"]

    assert first_memory
    assert second_memory
    assert len(history) >= len(first_memory) + len(second_memory)
    assert {item["source"] for item in history} == {"settled-turn-facts"}
    assert {item["month"] for item in history} >= {1, 2}
    cfo_history = [item for item in history if item["role_id"] == "cfo"]
    assert [item["month"] for item in cfo_history[:2]] == [2, 1]


def test_review_endpoint_returns_compact_replay_and_achievements(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]
    client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花10万研发产品"},
    )

    response = client.get(f"/api/sessions/{session_id}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ending_title"]
    assert payload["ending_summary"]
    assert payload["advice_for_next_run"]
    assert payload["review_phase"] == "阶段复盘"
    assert payload["status_copy"] == "进行中"
    assert isinstance(payload["key_moments"], list)
    assert isinstance(payload["achievements"], list)
    assert isinstance(payload["achievement_cards"], list)
    assert 2 <= len(payload["next_run_suggestions"]) <= 3
    assert all(item for item in payload["next_run_suggestions"])
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


def test_turns_return_recent_role_memory_history(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    first = client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花10万研发产品"},
    ).json()
    second = client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花5万做营销"},
    ).json()

    first_cfo = next(item for item in first["turn"]["role_memory"] if item["role_id"] == "cfo")
    second_cfo = next(item for item in second["turn"]["role_memory"] if item["role_id"] == "cfo")
    history = second["turn"]["recent_role_memory"]

    assert second["turn"]["memory_history"] == history
    assert len(history) >= len(first["turn"]["role_memory"]) + len(second["turn"]["role_memory"])
    assert {item["source"] for item in history} == {"settled-turn-facts"}
    assert (first_cfo["month"], first_cfo["fact"]) in {
        (item["month"], item["fact"]) for item in history
    }
    assert (second_cfo["month"], second_cfo["fact"]) in {
        (item["month"], item["fact"]) for item in history
    }


def test_review_endpoint_returns_read_only_review_and_achievements(client):
    from src.db import repository

    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]
    client.post(
        f"/api/sessions/{session_id}/turns",
        json={"command": "花10万研发产品"},
    )

    current = client.get(f"/api/sessions/{session_id}").json()
    repository.update_session_month(
        session_id,
        current["metrics"]["month"],
        "series_a_success",
    )
    before = client.get(f"/api/sessions/{session_id}").json()
    response = client.get(f"/api/sessions/{session_id}/review")
    after = client.get(f"/api/sessions/{session_id}").json()

    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == session_id
    assert payload["ending_status"] == before["status"]
    assert payload["review_phase"] == "终局复盘"
    assert payload["status_copy"] == "已结束"
    assert payload["final_metrics"]["month"] == before["metrics"]["month"]
    assert isinstance(payload["achievements"], list)
    assert "total_count" in payload["achievement_summary"]
    assert payload["key_moments"]
    first_moment = payload["key_moments"][0]
    assert first_moment["title"]
    assert first_moment["description"]
    assert first_moment["display_title"] == first_moment["title"]
    assert first_moment["display_description"] == first_moment["description"]
    assert first_moment["display_tone"] in {"positive", "negative", "neutral"}
    assert payload["achievement_cards"]
    first_card = payload["achievement_cards"][0]
    assert set(first_card) == {"title", "description", "rarity", "unlocked"}
    assert first_card["unlocked"] is True
    assert 2 <= len(payload["next_run_suggestions"]) <= 3
    assert "跑道" not in _body_text(payload)
    assert "Runway" not in _body_text(payload)
    assert after["metrics"] == before["metrics"]
    assert after["status"] == before["status"]


def test_empty_turn_command_returns_plain_language_error(client):
    created = client.post("/api/sessions", json={"player_name": "Tester"}).json()
    session_id = created["session_id"]

    response = client.post(f"/api/sessions/{session_id}/turns", json={"command": "  "})

    assert response.status_code == 400
    assert response.json()["message"] == "请输入本回合要执行的动作。"
