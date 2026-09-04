from app.strategy.board_analysis import (
    AGENT,
    HUMAN,
    action_position_type,
    decode_state,
    encode_state,
    fork_actions,
    immediate_winning_actions,
    legal_actions,
)


def test_decode_state():
    board = decode_state(
        "102010000",
    )

    assert board == [
        1,
        0,
        2,
        0,
        1,
        0,
        0,
        0,
        0,
    ]


def test_encode_state():
    board = [
        1,
        0,
        2,
        0,
        1,
        0,
        0,
        0,
        0,
    ]

    assert (
        encode_state(board)
        == "102010000"
    )


def test_legal_actions():
    board = decode_state(
        "102010000",
    )

    assert legal_actions(board) == [
        1,
        3,
        5,
        6,
        7,
        8,
    ]


def test_agent_immediate_win():
    board = decode_state(
        "220110000",
    )

    wins = immediate_winning_actions(
        board,
        AGENT,
    )

    assert wins == [2]


def test_human_immediate_win():
    board = decode_state(
        "110020002",
    )

    wins = immediate_winning_actions(
        board,
        HUMAN,
    )

    assert wins == [2]


def test_action_position_types():
    assert (
        action_position_type(4)
        == "center"
    )
    assert (
        action_position_type(0)
        == "corner"
    )
    assert (
        action_position_type(1)
        == "edge"
    )


def test_agent_fork_creation():
    board = decode_state(
        "200010002",
    )

    forks = fork_actions(
        board,
        AGENT,
    )

    assert 2 in forks
    assert 6 in forks
