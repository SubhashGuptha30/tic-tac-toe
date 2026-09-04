from dataclasses import dataclass, field
from typing import Optional


WINNING_LINES = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


@dataclass
class Board:
    cells: list[str] = field(default_factory=lambda: [""] * 9)

    def reset(self) -> None:
        self.cells = [""] * 9

    def legal_actions(self) -> list[int]:
        return [
            index
            for index, value in enumerate(self.cells)
            if value == ""
        ]

    def is_legal_action(self, action: int) -> bool:
        return 0 <= action < 9 and self.cells[action] == ""

    def make_move(self, action: int, symbol: str) -> bool:
        if symbol not in {"X", "O"}:
            return False

        if not self.is_legal_action(action):
            return False

        self.cells[action] = symbol
        return True

    def winner(self) -> Optional[str]:
        for a, b, c in WINNING_LINES:
            if (
                self.cells[a] != ""
                and self.cells[a] == self.cells[b]
                and self.cells[b] == self.cells[c]
            ):
                return self.cells[a]

        return None

    def winning_line(self) -> Optional[list[int]]:
        for a, b, c in WINNING_LINES:
            if (
                self.cells[a] != ""
                and self.cells[a] == self.cells[b]
                and self.cells[b] == self.cells[c]
            ):
                return [a, b, c]

        return None

    def is_full(self) -> bool:
        return all(cell != "" for cell in self.cells)

    def is_draw(self) -> bool:
        return self.is_full() and self.winner() is None

    def is_terminal(self) -> bool:
        return self.winner() is not None or self.is_draw()

    def copy_state(self) -> list[str]:
        return self.cells.copy()
