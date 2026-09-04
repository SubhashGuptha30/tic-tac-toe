from typing import Sequence


class StateEncoder:
    """
    Converts a Tic-Tac-Toe board into a stable hashable state string.

    Encoding:
        empty -> 0
        X     -> 1
        O     -> 2
    """

    SYMBOL_MAP = {
        "": "0",
        "X": "1",
        "O": "2",
    }

    @classmethod
    def encode(
        cls,
        board: Sequence[str],
    ) -> str:
        if len(board) != 9:
            raise ValueError(
                "A Tic-Tac-Toe board must contain 9 cells."
            )

        try:
            return "".join(
                cls.SYMBOL_MAP[cell]
                for cell in board
            )
        except KeyError as error:
            raise ValueError(
                f"Unknown board symbol: {error.args[0]}"
            ) from error
