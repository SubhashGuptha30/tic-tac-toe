from fastapi.testclient import (
    TestClient,
)

from app.main import app


client = TestClient(app)


def test_analytics_overview():
    response = client.get(
        "/api/analytics/overview"
    )

    assert response.status_code == 200

    data = response.json()

    assert "outcomes" in data
    assert "win_rates" in data
    assert "q_value_health" in data
    assert "td_error_health" in data


def test_learning_curve():
    response = client.get(
        "/api/analytics/learning-curve"
        "?rolling_window=10"
    )

    assert response.status_code == 200

    assert isinstance(
        response.json(),
        list,
    )


def test_invalid_rolling_window():
    response = client.get(
        "/api/analytics/learning-curve"
        "?rolling_window=0"
    )

    assert response.status_code == 422


def test_analytics_dataset():
    response = client.get(
        "/api/analytics/dataset"
    )

    assert response.status_code == 200

    data = response.json()

    assert "learning_curve" in data
    assert "outcome_timeline" in data
    assert "td_error_curve" in data
    assert "reward_trajectory" in data
    assert "epsilon_curve" in data
