from fastapi.testclient import TestClient

from app.game.service import game_service
from app.main import app
from app.training.environment import (
    AGENT_O,
    HUMAN_X,
    get_terminal_status,
)


client = TestClient(app)


def test_evaluation_run_uses_frozen_policy_without_mutation():
    q_values_before = game_service.agent.q_table.snapshot()
    metrics_before = game_service.get_agent_metrics().copy()

    response = client.post(
        "/api/evaluation/runs",
        json={
            "games": 10,
            "opponent_type": "mixed",
            "tactical_probability": 0.7,
            "seed": 42,
        },
    )

    assert response.status_code == 200
    run = response.json()

    assert run["status"] == "completed"
    assert run["requested_games"] == 10
    assert run["completed_games"] == 10
    assert run["snapshot_id"] > 0
    assert run["tie_breaking_policy"] == (
        "lowest_action_index"
    )
    assert run["greedy_decision_rate"] == 1.0
    assert (
        run["agent_wins"]
        + run["opponent_wins"]
        + run["draws"]
        == 10
    )
    assert run["duration_seconds"] is not None
    assert run["games_per_second"] is not None
    assert run["average_moves"] > 0

    assert game_service.agent.q_table.snapshot() == (
        q_values_before
    )
    assert game_service.get_agent_metrics() == metrics_before

    episodes_response = client.get(
        f"/api/evaluation/runs/{run['id']}/episodes"
    )
    assert episodes_response.status_code == 200

    episodes = episodes_response.json()
    assert len(episodes) == 10
    assert [
        episode["game_index"]
        for episode in episodes
    ] == list(range(1, 11))

    for episode in episodes:
        assert episode["move_count"] == (
            episode["agent_moves"]
            + episode["opponent_moves"]
        )
        assert episode["move_count"] <= 9
        board = [
            int(value)
            for value in episode["final_board_key"]
        ]
        status = get_terminal_status(board)
        assert status.done is True

        if episode["result"] == "agent_win":
            assert status.winner == AGENT_O
        elif episode["result"] == "opponent_win":
            assert status.winner == HUMAN_X
        else:
            assert status.is_draw is True


def test_seeded_evaluation_is_reproducible_and_comparable():
    first_payload = {
        "games": 8,
        "opponent_type": "random",
        "seed": 17,
    }
    first_response = client.post(
        "/api/evaluation/runs",
        json=first_payload,
    )

    assert first_response.status_code == 200
    first = first_response.json()

    second_response = client.post(
        "/api/evaluation/runs",
        json={
            **first_payload,
            "snapshot_id": first["snapshot_id"],
        },
    )
    assert second_response.status_code == 200
    second = second_response.json()

    assert second["snapshot_id"] == first["snapshot_id"]

    for key in (
        "agent_wins",
        "opponent_wins",
        "draws",
        "total_moves",
        "total_decisions",
        "unique_states_visited",
        "immediate_win_opportunities",
        "immediate_win_successes",
        "immediate_block_opportunities",
        "immediate_block_successes",
    ):
        assert first[key] == second[key]

    comparison_response = client.get(
        "/api/evaluation/snapshots/"
        f"{first['snapshot_id']}/comparison"
    )
    assert comparison_response.status_code == 200

    rows = comparison_response.json()["rows"]
    random_row = next(
        row
        for row in rows
        if row["opponent_type"] == "random"
    )

    assert random_row["is_available"] is True
    assert random_row["evaluation_run_id"] == second["id"]


def test_evaluation_rejects_unknown_opponent():
    response = client.post(
        "/api/evaluation/runs",
        json={
            "games": 1,
            "opponent_type": "minimax",
            "seed": 7,
        },
    )

    assert response.status_code == 400
