import random
import time

from dataclasses import dataclass

from app.training.agent_adapter import (
    TrainingAgentAdapter,
)
from app.training.environment import (
    AGENT_O,
    HUMAN_X,
    apply_action,
    create_empty_board,
    encode_board,
    get_terminal_status,
    legal_actions,
)
from app.training.opponents import TrainingOpponent
from app.training.rewards import TrainingRewards


@dataclass
class EpisodeResult:
    result: str
    reward: float
    agent_moves: int
    opponent_moves: int
    epsilon_before: float
    epsilon_after: float
    final_board_key: str
    move_count: int
    duration_ms: float


class TrainingEpisodeEngine:
    def __init__(
        self,
        *,
        agent: TrainingAgentAdapter,
        opponent: TrainingOpponent,
        rewards: TrainingRewards,
        rng: random.Random,
    ) -> None:
        self.agent = agent
        self.opponent = opponent
        self.rewards = rewards
        self.rng = rng

    def run_episode(self) -> EpisodeResult:
        started = time.perf_counter()
        board = create_empty_board()
        epsilon_before = self.agent.epsilon
        agent_moves = 0
        opponent_moves = 0
        final_reward = 0.0

        opening_action = self.opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        apply_action(
            board,
            opening_action,
            HUMAN_X,
        )
        opponent_moves += 1

        while True:
            transition = self._play_agent_transition(
                board
            )
            agent_moves += 1
            opponent_moves = sum(
                1
                for value in board
                if value == HUMAN_X
            )

            if transition is not None:
                result, final_reward = transition
                break

        self.agent.decay_epsilon()
        duration_ms = (
            time.perf_counter() - started
        ) * 1000.0

        episode_result = EpisodeResult(
            result=result,
            reward=float(final_reward),
            agent_moves=agent_moves,
            opponent_moves=opponent_moves,
            epsilon_before=float(epsilon_before),
            epsilon_after=float(self.agent.epsilon),
            final_board_key=encode_board(board),
            move_count=agent_moves + opponent_moves,
            duration_ms=float(duration_ms),
        )

        validate_episode_result(episode_result)
        return episode_result

    def _play_agent_transition(
        self,
        board: list[int],
    ) -> tuple[str, float] | None:
        state_key = encode_board(board)
        actions = legal_actions(board)

        if not actions:
            return ("draw", self.rewards.draw)

        action = self.agent.choose_action(
            state_key,
            actions,
        )
        apply_action(board, action, AGENT_O)

        after_agent_status = get_terminal_status(
            board
        )

        if after_agent_status.done:
            if after_agent_status.winner == AGENT_O:
                reward = self.rewards.win
                self.agent.update(
                    state_key=state_key,
                    action=action,
                    reward=reward,
                    next_state_key=encode_board(board),
                    next_legal_actions=[],
                    done=True,
                )
                return ("agent_win", reward)

            if after_agent_status.is_draw:
                reward = self.rewards.draw
                self.agent.update(
                    state_key=state_key,
                    action=action,
                    reward=reward,
                    next_state_key=encode_board(board),
                    next_legal_actions=[],
                    done=True,
                )
                return ("draw", reward)

        opponent_actions = legal_actions(board)

        if not opponent_actions:
            reward = self.rewards.draw
            self.agent.update(
                state_key=state_key,
                action=action,
                reward=reward,
                next_state_key=encode_board(board),
                next_legal_actions=[],
                done=True,
            )
            return ("draw", reward)

        opponent_action = self.opponent.choose_action(
            board=board,
            legal_actions=opponent_actions,
        )
        apply_action(board, opponent_action, HUMAN_X)

        status = get_terminal_status(board)
        next_state_key = encode_board(board)

        if status.done:
            if status.winner == HUMAN_X:
                reward = self.rewards.loss
                self.agent.update(
                    state_key=state_key,
                    action=action,
                    reward=reward,
                    next_state_key=next_state_key,
                    next_legal_actions=[],
                    done=True,
                )
                return ("opponent_win", reward)

            if status.is_draw:
                reward = self.rewards.draw
                self.agent.update(
                    state_key=state_key,
                    action=action,
                    reward=reward,
                    next_state_key=next_state_key,
                    next_legal_actions=[],
                    done=True,
                )
                return ("draw", reward)

        self.agent.update(
            state_key=state_key,
            action=action,
            reward=self.rewards.step,
            next_state_key=next_state_key,
            next_legal_actions=legal_actions(board),
            done=False,
        )

        return None


def validate_episode_result(
    result: EpisodeResult,
) -> None:
    if result.result not in {
        "agent_win",
        "opponent_win",
        "draw",
    }:
        raise ValueError(
            f"Invalid episode result: {result.result}"
        )

    if len(result.final_board_key) != 9:
        raise ValueError(
            "Final board key must contain 9 cells."
        )

    if (
        result.agent_moves < 0
        or result.opponent_moves < 0
    ):
        raise ValueError(
            "Move counts cannot be negative."
        )

    if (
        result.move_count
        != result.agent_moves + result.opponent_moves
    ):
        raise ValueError(
            "Episode move-count invariant failed."
        )

    if result.move_count > 9:
        raise ValueError(
            "Tic-Tac-Toe episode cannot exceed 9 moves."
        )

    if result.opponent_moves < result.agent_moves:
        raise ValueError(
            "Opponent X must have at least as many moves "
            "as agent O."
        )

    if result.opponent_moves - result.agent_moves > 1:
        raise ValueError("Move-count parity failed.")

    board = [
        int(character)
        for character in result.final_board_key
    ]
    status = get_terminal_status(board)

    if not status.done:
        raise ValueError(
            "Training episode ended on a non-terminal board."
        )

    if (
        result.result == "agent_win"
        and status.winner != AGENT_O
    ):
        raise ValueError(
            "Agent win result does not match final board."
        )

    if (
        result.result == "opponent_win"
        and status.winner != HUMAN_X
    ):
        raise ValueError(
            "Opponent win result does not match final board."
        )

    if result.result == "draw" and not status.is_draw:
        raise ValueError(
            "Draw result does not match final board."
        )
