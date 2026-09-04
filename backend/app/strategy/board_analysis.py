from __future__ import annotations

from dataclasses import dataclass


EMPTY = 0
HUMAN = 1
AGENT = 2

BOARD_SIZE = 9

CENTER_ACTION = 4

CORNER_ACTIONS = {
    0,
    2,
    6,
    8,
}

EDGE_ACTIONS = {
    1,
    3,
    5,
    7,
}

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)


@dataclass(frozen=True)
class TacticalAnalysis:
    legal_actions: list[int]
    immediate_wins: list[int]
    immediate_blocks: list[int]
    fork_creations: list[int]
    fork_preventions: list[int]


def decode_state(
    state_key: str,
) -> list[int]:
    if len(state_key) != BOARD_SIZE:
        raise ValueError(
            "State key must contain exactly 9 cells.",
        )

    if any(
        cell not in {"0", "1", "2"}
        for cell in state_key
    ):
        raise ValueError(
            "State key may contain only 0, 1, and 2.",
        )

    return [
        int(cell)
        for cell in state_key
    ]


def encode_state(
    board: list[int],
) -> str:
    validate_board(board)

    return "".join(
        str(cell)
        for cell in board
    )


def validate_board(
    board: list[int],
) -> None:
    if len(board) != BOARD_SIZE:
        raise ValueError(
            "Board must contain exactly 9 cells.",
        )

    if any(
        cell not in {
            EMPTY,
            HUMAN,
            AGENT,
        }
        for cell in board
    ):
        raise ValueError(
            "Board cells must be 0, 1, or 2.",
        )


def legal_actions(
    board: list[int],
) -> list[int]:
    validate_board(board)

    return [
        index
        for index, cell in enumerate(board)
        if cell == EMPTY
    ]


def winner(
    board: list[int],
) -> int | None:
    validate_board(board)

    for a, b, c in WINNING_LINES:
        if (
            board[a] != EMPTY
            and board[a] == board[b]
            and board[b] == board[c]
        ):
            return board[a]

    return None


def is_winning_action(
    board: list[int],
    action: int,
    player: int,
) -> bool:
    if action not in legal_actions(board):
        return False

    next_board = board.copy()
    next_board[action] = player

    return winner(next_board) == player


def immediate_winning_actions(
    board: list[int],
    player: int,
) -> list[int]:
    return [
        action
        for action in legal_actions(board)
        if is_winning_action(
            board,
            action,
            player,
        )
    ]


def count_immediate_wins(
    board: list[int],
    player: int,
) -> int:
    return len(
        immediate_winning_actions(
            board,
            player,
        ),
    )


def is_fork_action(
    board: list[int],
    action: int,
    player: int,
) -> bool:
    if action not in legal_actions(board):
        return False

    next_board = board.copy()
    next_board[action] = player

    if winner(next_board) is not None:
        return False

    future_wins = immediate_winning_actions(
        next_board,
        player,
    )

    return len(future_wins) >= 2


def fork_actions(
    board: list[int],
    player: int,
) -> list[int]:
    return [
        action
        for action in legal_actions(board)
        if is_fork_action(
            board,
            action,
            player,
        )
    ]


def fork_prevention_actions(
    board: list[int],
    defender: int,
    attacker: int,
) -> list[int]:
    current_threats = set(
        fork_actions(
            board,
            attacker,
        ),
    )

    if not current_threats:
        return []

    prevention_actions: list[int] = []

    for action in legal_actions(board):
        next_board = board.copy()
        next_board[action] = defender

        if winner(next_board) == defender:
            continue

        remaining_threats = set(
            fork_actions(
                next_board,
                attacker,
            ),
        )

        if len(remaining_threats) < len(
            current_threats,
        ):
            prevention_actions.append(action)

    return prevention_actions


def action_position_type(
    action: int,
) -> str:
    if action == CENTER_ACTION:
        return "center"

    if action in CORNER_ACTIONS:
        return "corner"

    if action in EDGE_ACTIONS:
        return "edge"

    raise ValueError(
        f"Invalid action index: {action}",
    )


def analyze_tactics(
    board: list[int],
) -> TacticalAnalysis:
    return TacticalAnalysis(
        legal_actions=legal_actions(board),
        immediate_wins=immediate_winning_actions(
            board,
            AGENT,
        ),
        immediate_blocks=immediate_winning_actions(
            board,
            HUMAN,
        ),
        fork_creations=fork_actions(
            board,
            AGENT,
        ),
        fork_preventions=fork_prevention_actions(
            board,
            defender=AGENT,
            attacker=HUMAN,
        ),
    )
