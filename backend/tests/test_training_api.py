from fastapi.testclient import TestClient

from app.main import app
from app.training.environment import (
    AGENT_O,
    HUMAN_X,
    get_terminal_status,
)


client = TestClient(app)


def test_training_health_reports_shared_agent():
    response = client.get(
        "/api/training/health",
    )

    assert response.status_code == 200

    payload = response.json()

    assert payload["agent_available"] is True
    assert payload["supported_opponents"] == [
        "random",
        "tactical",
        "mixed",
    ]
    assert payload["engine_ready"] is True


def test_training_run_records_episode_summaries_without_decision_events():
    before_decisions = client.get(
        "/api/decisions/stats",
    ).json()["total_decisions"]

    response = client.post(
        "/api/training/runs",
        json={
            "episodes": 10,
            "opponent_type": "random",
            "seed": 42,
        },
    )

    assert response.status_code == 200

    run = response.json()

    assert run["status"] == "completed"
    assert run["requested_episodes"] == 10
    assert run["completed_episodes"] == 10
    assert (
        run["agent_wins"]
        + run["opponent_wins"]
        + run["draws"]
        == 10
    )
    assert run["epsilon_end"] <= run["epsilon_start"]
    assert run["duration_seconds"] is not None
    assert run["episodes_per_second"] is not None

    after_decisions = client.get(
        "/api/decisions/stats",
    ).json()["total_decisions"]

    assert after_decisions == before_decisions

    episodes_response = client.get(
        f"/api/training/runs/{run['id']}/episodes"
    )

    assert episodes_response.status_code == 200

    episodes = episodes_response.json()

    assert len(episodes) == 10
    assert [
        episode["episode_index"]
        for episode in episodes
    ] == list(range(1, 11))

    for episode in episodes:
        assert episode["opponent_moves"] >= episode[
            "agent_moves"
        ]
        assert (
            episode["opponent_moves"]
            - episode["agent_moves"]
            <= 1
        )
        assert episode["move_count"] == (
            episode["agent_moves"]
            + episode["opponent_moves"]
        )
        assert episode["move_count"] <= 9

        board = [
            int(value)
            for value in episode[
                "final_board_key"
            ]
        ]
        status = get_terminal_status(board)

        assert status.done is True

        if episode["result"] == "agent_win":
            assert status.winner == AGENT_O
            assert episode["reward"] == 1.0
        elif episode["result"] == "opponent_win":
            assert status.winner == HUMAN_X
            assert episode["reward"] == -1.0
        else:
            assert episode["result"] == "draw"
            assert status.is_draw is True

    stats_response = client.get(
        f"/api/training/runs/{run['id']}/stats"
    )

    assert stats_response.status_code == 200

    stats = stats_response.json()

    assert stats["run_id"] == run["id"]
    assert stats["progress"] == 1.0
    assert stats["completed_episodes"] == 10


def test_training_accepts_tactical_and_mixed_opponents():
    tactical_response = client.post(
        "/api/training/runs",
        json={
            "episodes": 5,
            "opponent_type": "tactical",
            "seed": 7,
        },
    )
    mixed_response = client.post(
        "/api/training/runs",
        json={
            "episodes": 5,
            "opponent_type": "mixed",
            "tactical_probability": 0.5,
            "seed": 7,
        },
    )

    assert tactical_response.status_code == 200
    assert mixed_response.status_code == 200

    tactical_run = tactical_response.json()
    mixed_run = mixed_response.json()

    assert tactical_run["opponent_type"] == "tactical"
    assert tactical_run["completed_episodes"] == 5
    assert (
        tactical_run["agent_wins"]
        + tactical_run["opponent_wins"]
        + tactical_run["draws"]
        == 5
    )
    assert tactical_run["tactical_probability"] is None

    assert mixed_run["opponent_type"] == "mixed"
    assert mixed_run["tactical_probability"] == 0.5
    assert mixed_run["completed_episodes"] == 5
    assert (
        mixed_run["agent_wins"]
        + mixed_run["opponent_wins"]
        + mixed_run["draws"]
        == 5
    )


def test_training_rejects_unknown_opponent():
    response = client.post(
        "/api/training/runs",
        json={
            "episodes": 1,
            "opponent_type": "minimax",
            "seed": 7,
        },
    )

    assert response.status_code == 400
