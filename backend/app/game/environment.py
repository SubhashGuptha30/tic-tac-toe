from dataclasses import dataclass, field
from typing import Optional

from app.game.board import Board


@dataclass
class TicTacToeEnvironment:
    board: Board = field(default_factory=Board)
    current_player: str = "X"
    game_over: bool = False
    winner_symbol: Optional[str] = None

    def reset(self) -> None:
        self.board.reset()
        self.current_player = "X"
        self.game_over = False
        self.winner_symbol = None

    def apply_move(self, action: int, symbol: str) -> bool:
        if self.game_over:
            return False

        if symbol != self.current_player:
            return False

        move_applied = self.board.make_move(
            action=action,
            symbol=symbol,
        )

        if not move_applied:
            return False

        self._update_terminal_state()

        if not self.game_over:
            self.current_player = "O" if symbol == "X" else "X"

        return True

    def _update_terminal_state(self) -> None:
        winner = self.board.winner()

        if winner is not None:
            self.game_over = True
            self.winner_symbol = winner
            return

        if self.board.is_draw():
            self.game_over = True
            self.winner_symbol = None

    def legal_actions(self) -> list[int]:
        return self.board.legal_actions()

    def state(self) -> dict:
        return {
            "board": self.board.copy_state(),
            "current_player": self.current_player,
            "game_over": self.game_over,
            "winner": self.winner_symbol,
            "winning_line": self.board.winning_line(),
            "is_draw": self.board.is_draw(),
            "legal_actions": self.legal_actions(),
        }
