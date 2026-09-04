from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_decision_endpoints_exist():
    latest_response = client.get(
        "/api/decisions/latest",
    )
    history_response = client.get(
        "/api/decisions/history?limit=5",
    )
    stats_response = client.get(
        "/api/decisions/stats",
    )

    assert latest_response.status_code == 200
    assert history_response.status_code == 200
    assert stats_response.status_code == 200


def test_agent_move_creates_decision_event():
    state_response = client.get(
        "/api/game/state",
    )
    assert state_response.status_code == 200
    state = state_response.json()

    if (
        state["game_over"]
        or state["current_player"] != "X"
    ):
        reset_response = client.post(
            "/api/game/reset",
        )
        assert reset_response.status_code == 200
        state = reset_response.json()["game"]

    human_response = client.post(
        "/api/game/human-move",
        json={
            "action": state["legal_actions"][0],
        },
    )
    assert human_response.status_code == 200

    after_human = human_response.json()["game"]
    assert after_human["game_over"] is False

    agent_response = client.post(
        "/api/game/agent-move",
    )
    assert agent_response.status_code == 200
    agent_payload = agent_response.json()

    latest_response = client.get(
        "/api/decisions/latest",
    )
    assert latest_response.status_code == 200
    latest = latest_response.json()

    assert latest is not None
    assert (
        agent_payload["decision_event_id"]
        == latest["id"]
    )
    assert (
        latest["selected_action"]
        in latest["legal_actions"]
    )

    if (
        latest["decision_mode"]
        == "exploration"
    ):
        assert (
            latest["exploration_draw"]
            < latest["epsilon"]
        )
    else:
        assert (
            latest["decision_mode"]
            == "exploitation"
        )
        assert (
            latest["exploration_draw"]
            >= latest["epsilon"]
        )
        assert (
            latest["selected_action"]
            in latest["greedy_actions"]
        )
        assert (
            latest["selected_q"]
            == latest["best_q"]
        )


def test_decision_stats_counts_add_up():
    response = client.get(
        "/api/decisions/stats",
    )
    assert response.status_code == 200

    stats = response.json()

    assert (
        stats["exploration_decisions"]
        + stats["exploitation_decisions"]
        == stats["total_decisions"]
    )
