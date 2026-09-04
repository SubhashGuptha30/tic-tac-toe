from dataclasses import dataclass


EMPTY = 0
HUMAN_X = 1
AGENT_O = 2

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


@dataclass
class TerminalStatus:
    done: bool
    winner: int | None
    is_draw: bool


def create_empty_board() -> list[int]:
    return [EMPTY] * 9


def legal_actions(
    board: list[int],
) -> list[int]:
    validate_board(board)

    return [
        index
        for index, value in enumerate(board)
        if value == EMPTY
    ]


def apply_action(
    board: list[int],
    action: int,
    player: int,
) -> None:
    validate_board(board)

    if player not in {HUMAN_X, AGENT_O}:
        raise ValueError(
            f"Invalid player value: {player}"
        )

    if action < 0 or action >= 9:
        raise ValueError(
            f"Action out of range: {action}"
        )

    if board[action] != EMPTY:
        raise ValueError(
            f"Cannot apply action {action}: cell is occupied."
        )

    board[action] = player


def get_winner(
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


def get_terminal_status(
    board: list[int],
) -> TerminalStatus:
    winner = get_winner(board)

    if winner is not None:
        return TerminalStatus(
            done=True,
            winner=winner,
            is_draw=False,
        )

    if all(value != EMPTY for value in board):
        return TerminalStatus(
            done=True,
            winner=None,
            is_draw=True,
        )

    return TerminalStatus(
        done=False,
        winner=None,
        is_draw=False,
    )


def encode_board(
    board: list[int],
) -> str:
    validate_board(board)

    return "".join(str(value) for value in board)


def validate_board(
    board: list[int],
) -> None:
    if len(board) != 9:
        raise ValueError(
            "Tic-Tac-Toe board must contain 9 cells."
        )

    if any(
        value not in {EMPTY, HUMAN_X, AGENT_O}
        for value in board
    ):
        raise ValueError(
            "Board contains an invalid cell value."
        )
