from app.analytics.service import (
    AnalyticsService,
)


def test_safe_ratio_with_values():
    result = AnalyticsService._safe_ratio(
        3,
        4,
    )

    assert result == 0.75


def test_safe_ratio_with_zero_denominator():
    result = AnalyticsService._safe_ratio(
        3,
        0,
    )

    assert result == 0.0


def test_q_value_health_empty():
    result = (
        AnalyticsService._q_value_health([])
    )

    assert (
        result["total_persisted_actions"]
        == 0
    )
    assert result["mean_q_value"] == 0.0
    assert result["mean_absolute_q"] == 0.0


def test_q_value_health_values():
    result = (
        AnalyticsService._q_value_health(
            [
                -0.2,
                0.0,
                0.2,
                0.4,
            ]
        )
    )

    assert (
        result["total_persisted_actions"]
        == 4
    )
    assert (
        result["positive_q_values"]
        == 2
    )
    assert (
        result["negative_q_values"]
        == 1
    )
    assert (
        result["zero_q_values"]
        == 1
    )
    assert result["min_q_value"] == -0.2
    assert result["max_q_value"] == 0.4


def test_td_error_health():
    result = (
        AnalyticsService._td_error_health(
            errors=[
                -1.0,
                0.0,
                1.0,
            ],
            recent_errors=[
                0.0,
                1.0,
            ],
        )
    )

    assert result["total_updates"] == 3
    assert (
        result["mean_td_error"]
        == 0.0
    )
    assert abs(
        result["mean_absolute_td_error"]
        - (2.0 / 3.0)
    ) < 1e-9
    assert (
        result[
            "recent_mean_absolute_td_error"
        ]
        == 0.5
    )
