from app.strategy.policy_analysis import (
    analyze_policy_confidence,
    best_actions,
    preference_score,
    rank_actions,
    tactical_alignment_score,
)


def test_unique_best_action():
    values = {
        0: 0.1,
        1: 0.7,
        2: 0.2,
    }

    assert best_actions(values) == [1]


def test_tied_best_actions():
    values = {
        0: 0.5,
        1: 0.5,
        2: 0.1,
    }

    assert best_actions(values) == [
        0,
        1,
    ]


def test_action_gap():
    values = {
        0: 0.8,
        1: 0.2,
        2: -0.1,
    }

    result = analyze_policy_confidence(
        values,
    )

    assert result.best_action == 0
    assert abs(
        result.action_gap - 0.6,
    ) < 1e-9


def test_tied_action_gap_is_zero():
    values = {
        0: 0.5,
        1: 0.5,
        2: 0.1,
    }

    result = analyze_policy_confidence(
        values,
    )

    assert result.action_gap == 0.0


def test_preference_score_full():
    score = preference_score(
        preferred_actions={4},
        greedy_actions=[4],
    )

    assert score == 1.0


def test_preference_score_tied():
    score = preference_score(
        preferred_actions={4},
        greedy_actions=[0, 4],
    )

    assert score == 0.5


def test_tactical_alignment():
    score = tactical_alignment_score(
        tactical_actions={2},
        greedy_actions=[2],
    )

    assert score == 1.0


def test_rank_actions():
    ranked = rank_actions(
        {
            0: 0.1,
            1: 0.8,
            2: 0.3,
        },
    )

    assert ranked[0].action == 1
    assert ranked[0].rank == 1
    assert ranked[0].is_best is True
