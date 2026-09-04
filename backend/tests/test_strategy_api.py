from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(app)


def test_strategy_overview():
    response = client.get(
        "/api/strategy/overview",
    )

    assert response.status_code == 200

    data = response.json()

    assert "immediate_win" in data
    assert "immediate_block" in data
    assert "fork_creation" in data
    assert "fork_prevention" in data
    assert "center_preference" in data
    assert "corner_preference" in data
    assert "edge_preference" in data


def test_state_list():
    response = client.get(
        "/api/strategy/q-table/states?limit=10",
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list,
    )


def test_valid_state_inspection():
    response = client.get(
        "/api/strategy/q-table/state/102010000",
    )

    assert response.status_code == 200

    data = response.json()

    assert (
        data["state_key"]
        == "102010000"
    )
    assert len(data["board"]) == 9
    assert "policy_confidence" in data
    assert "tactical_evidence" in data


def test_invalid_state_length():
    response = client.get(
        "/api/strategy/q-table/state/123",
    )

    assert response.status_code == 400


def test_invalid_state_character():
    response = client.get(
        "/api/strategy/q-table/state/1000A0000",
    )

    assert response.status_code == 400


def test_invalid_strategy():
    response = client.get(
        "/api/strategy/evidence?strategy=magic_strategy",
    )

    assert response.status_code == 400


def test_episode_list():
    response = client.get(
        "/api/strategy/episodes?limit=10",
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list,
    )


def test_decision_inspection():
    response = client.get(
        "/api/strategy/decision/220110000",
    )

    assert response.status_code == 200

    data = response.json()

    assert "greedy_actions" in data
    assert "action_gap" in data
    assert (
        "normalized_confidence"
        in data
    )
