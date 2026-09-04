import random

from app.training.environment import (
    AGENT_O,
    EMPTY,
    HUMAN_X,
    legal_actions,
)
from app.training.opponents import (
    MixedOpponent,
    RandomOpponent,
    TacticalOpponent,
    create_opponent,
)


def test_random_opponent_distribution_is_reasonably_uniform():
    rng = random.Random(123)
    opponent = RandomOpponent(rng=rng)
    board = [EMPTY] * 9
    counts = {
        action: 0
        for action in range(9)
    }

    for _ in range(9000):
        action = opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        counts[action] += 1

    assert all(
        count > 850
        for count in counts.values()
    )
    assert all(
        count < 1150
        for count in counts.values()
    )


def test_tactical_opponent_wins_when_possible():
    opponent = TacticalOpponent()
    board = [
        HUMAN_X,
        HUMAN_X,
        EMPTY,
        AGENT_O,
        AGENT_O,
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
    ]

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 2
    )


def test_tactical_opponent_blocks_agent_immediate_win():
    opponent = TacticalOpponent()
    board = [
        AGENT_O,
        AGENT_O,
        EMPTY,
        EMPTY,
        HUMAN_X,
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
    ]

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 2
    )


def test_tactical_opponent_prefers_center():
    opponent = TacticalOpponent()
    board = [EMPTY] * 9

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 4
    )


def test_tactical_opponent_prefers_opposite_corner():
    opponent = TacticalOpponent()
    board = [
        AGENT_O,
        EMPTY,
        EMPTY,
        EMPTY,
        HUMAN_X,
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
    ]

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 8
    )


def test_tactical_opponent_prefers_empty_corner_before_edge():
    opponent = TacticalOpponent()
    board = [
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
        HUMAN_X,
        EMPTY,
        EMPTY,
        EMPTY,
        EMPTY,
    ]

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 0
    )


def test_tactical_opponent_prefers_edge_when_only_edges_remain():
    opponent = TacticalOpponent()
    board = [
        HUMAN_X,
        EMPTY,
        AGENT_O,
        EMPTY,
        HUMAN_X,
        EMPTY,
        AGENT_O,
        EMPTY,
        HUMAN_X,
    ]

    assert (
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        == 1
    )


def test_mixed_opponent_uses_configured_tactical_probability():
    opponent = MixedOpponent(
        rng=random.Random(7),
        tactical_probability=0.70,
    )
    board = [EMPTY] * 9

    for _ in range(1000):
        opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )

    tactical_rate = (
        opponent.tactical_choices
        / (
            opponent.tactical_choices
            + opponent.random_choices
        )
    )

    assert 0.64 <= tactical_rate <= 0.76


def test_opponent_factory_supports_all_5e2_opponents():
    rng = random.Random(1)

    assert create_opponent(
        "random",
        rng,
    ).name == "random"
    assert create_opponent(
        "tactical",
        rng,
    ).name == "tactical"
    assert create_opponent(
        "mixed",
        rng,
        tactical_probability=0.5,
    ).name == "mixed"
