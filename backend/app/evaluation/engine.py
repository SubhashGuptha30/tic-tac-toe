from __future__ import annotations

import time

from dataclasses import dataclass

from app.evaluation.agent import (
    FrozenEvaluationAgent,
)
from app.strategy.board_analysis import analyze_tactics
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


@dataclass(frozen=True)
class EvaluationEpisodeResult:
    result: str
    agent_moves: int
    opponent_moves: int
    move_count: int
    decision_count: int
    confidence_sum: float
    action_gap_sum: float
    immediate_win_opportunities: int
    immediate_win_successes: int
    immediate_block_opportunities: int
    immediate_block_successes: int
    visited_states: set[str]
    final_board_key: str
    duration_ms: float


class EvaluationEpisodeEngine:
    def __init__(
        self,
        *,
        agent: FrozenEvaluationAgent,
        opponent: TrainingOpponent,
    ) -> None:
        self.agent = agent
        self.opponent = opponent

    def run_episode(self) -> EvaluationEpisodeResult:
        started = time.perf_counter()
        board = create_empty_board()
        agent_moves = 0
        opponent_moves = 0
        confidence_sum = 0.0
        action_gap_sum = 0.0
        immediate_win_opportunities = 0
        immediate_win_successes = 0
        immediate_block_opportunities = 0
        immediate_block_successes = 0
        visited_states: set[str] = set()

        opening_action = self.opponent.choose_action(
            board=board,
            legal_actions=legal_actions(board),
        )
        apply_action(board, opening_action, HUMAN_X)
        opponent_moves += 1

        while True:
            state_key = encode_board(board)
            actions = legal_actions(board)
            visited_states.add(state_key)

            decision = self.agent.choose_action(
                state_key,
                actions,
            )
            tactics = analyze_tactics(board)

            if tactics.immediate_wins:
                immediate_win_opportunities += 1
                if decision.action in tactics.immediate_wins:
                    immediate_win_successes += 1

            if tactics.immediate_blocks:
                immediate_block_opportunities += 1
                if decision.action in tactics.immediate_blocks:
                    immediate_block_successes += 1

            confidence_sum += decision.normalized_confidence
            action_gap_sum += decision.action_gap

            apply_action(board, decision.action, AGENT_O)
            agent_moves += 1

            after_agent_status = get_terminal_status(board)
            if after_agent_status.done:
                result = (
                    "agent_win"
                    if after_agent_status.winner == AGENT_O
                    else "draw"
                )
                break

            opponent_action = self.opponent.choose_action(
                board=board,
                legal_actions=legal_actions(board),
            )
            apply_action(board, opponent_action, HUMAN_X)
            opponent_moves += 1

            after_opponent_status = get_terminal_status(board)
            if after_opponent_status.done:
                result = (
                    "opponent_win"
                    if after_opponent_status.winner == HUMAN_X
                    else "draw"
                )
                break

        duration_ms = (
            time.perf_counter() - started
        ) * 1000.0
        return EvaluationEpisodeResult(
            result=result,
            agent_moves=agent_moves,
            opponent_moves=opponent_moves,
            move_count=agent_moves + opponent_moves,
            decision_count=agent_moves,
            confidence_sum=confidence_sum,
            action_gap_sum=action_gap_sum,
            immediate_win_opportunities=(
                immediate_win_opportunities
            ),
            immediate_win_successes=(
                immediate_win_successes
            ),
            immediate_block_opportunities=(
                immediate_block_opportunities
            ),
            immediate_block_successes=(
                immediate_block_successes
            ),
            visited_states=visited_states,
            final_board_key=encode_board(board),
            duration_ms=duration_ms,
        )
