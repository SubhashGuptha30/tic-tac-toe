import random

from abc import ABC, abstractmethod

from app.training.environment import (
    AGENT_O,
    HUMAN_X,
    apply_action,
    get_terminal_status,
)


CORNER_ACTIONS = (0, 2, 6, 8)
EDGE_ACTIONS = (1, 3, 5, 7)
OPPOSITE_CORNERS = {
    0: 8,
    2: 6,
    6: 2,
    8: 0,
}


class TrainingOpponent(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def choose_action(
        self,
        board: list[int],
        legal_actions: list[int],
    ) -> int:
        raise NotImplementedError


class RandomOpponent(TrainingOpponent):
    def __init__(
        self,
        rng: random.Random,
    ) -> None:
        self.rng = rng

    @property
    def name(self) -> str:
        return "random"

    def choose_action(
        self,
        board: list[int],
        legal_actions: list[int],
    ) -> int:
        if not legal_actions:
            raise ValueError(
                "RandomOpponent cannot choose from an empty "
                "legal action set."
            )

        return self.rng.choice(legal_actions)


class TacticalOpponent(TrainingOpponent):
    @property
    def name(self) -> str:
        return "tactical"

    def choose_action(
        self,
        board: list[int],
        legal_actions: list[int],
    ) -> int:
        if not legal_actions:
            raise ValueError(
                "TacticalOpponent cannot choose from an empty "
                "legal action set."
            )

        immediate_win = find_immediate_winning_action(
            board=board,
            legal_actions=legal_actions,
            player=HUMAN_X,
        )

        if immediate_win is not None:
            return immediate_win

        immediate_block = find_immediate_winning_action(
            board=board,
            legal_actions=legal_actions,
            player=AGENT_O,
        )

        if immediate_block is not None:
            return immediate_block

        if 4 in legal_actions:
            return 4

        opposite_corner = find_opposite_corner(
            board=board,
            legal_actions=legal_actions,
        )

        if opposite_corner is not None:
            return opposite_corner

        for action in CORNER_ACTIONS:
            if action in legal_actions:
                return action

        for action in EDGE_ACTIONS:
            if action in legal_actions:
                return action

        return legal_actions[0]


class MixedOpponent(TrainingOpponent):
    def __init__(
        self,
        rng: random.Random,
        tactical_probability: float = 0.70,
    ) -> None:
        if not 0.0 <= tactical_probability <= 1.0:
            raise ValueError(
                "tactical_probability must be between 0 and 1."
            )

        self.rng = rng
        self.tactical_probability = tactical_probability
        self.tactical = TacticalOpponent()
        self.random_opponent = RandomOpponent(rng=rng)
        self.tactical_choices = 0
        self.random_choices = 0

    @property
    def name(self) -> str:
        return "mixed"

    def choose_action(
        self,
        board: list[int],
        legal_actions: list[int],
    ) -> int:
        if self.rng.random() < self.tactical_probability:
            self.tactical_choices += 1
            return self.tactical.choose_action(
                board=board,
                legal_actions=legal_actions,
            )

        self.random_choices += 1
        return self.random_opponent.choose_action(
            board=board,
            legal_actions=legal_actions,
        )


def create_opponent(
    opponent_type: str,
    rng: random.Random,
    tactical_probability: float = 0.70,
) -> TrainingOpponent:
    normalized = opponent_type.strip().lower()

    if normalized == "random":
        return RandomOpponent(rng=rng)

    if normalized == "tactical":
        return TacticalOpponent()

    if normalized == "mixed":
        return MixedOpponent(
            rng=rng,
            tactical_probability=tactical_probability,
        )

    raise ValueError(
        f"Unsupported opponent type: {opponent_type}"
    )


def find_immediate_winning_action(
    *,
    board: list[int],
    legal_actions: list[int],
    player: int,
) -> int | None:
    for action in legal_actions:
        candidate = board.copy()
        apply_action(
            candidate,
            action,
            player,
        )

        status = get_terminal_status(candidate)

        if status.winner == player:
            return action

    return None


def find_opposite_corner(
    *,
    board: list[int],
    legal_actions: list[int],
) -> int | None:
    for agent_corner, opposite_corner in (
        OPPOSITE_CORNERS.items()
    ):
        if (
            board[agent_corner] == AGENT_O
            and opposite_corner in legal_actions
        ):
            return opposite_corner

    return None
