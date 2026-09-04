from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from app.strategy.policy_analysis import (
    analyze_policy_confidence,
)


TIE_BREAKING_POLICY = "lowest_action_index"


@dataclass(frozen=True)
class EvaluationDecision:
    state_key: str
    action: int
    legal_q_values: dict[int, float]
    best_q: float
    second_best_q: float
    action_gap: float
    normalized_confidence: float
    tied_best_actions: list[int]


class FrozenEvaluationAgent:
    """Read-only greedy policy created from a persisted Q-table copy."""

    def __init__(
        self,
        q_values: Mapping[str, Sequence[float]],
    ) -> None:
        self._q_values = {
            state_key: tuple(
                float(value)
                for value in values
            )
            for state_key, values in q_values.items()
            if len(values) == 9
        }

    def choose_action(
        self,
        state_key: str,
        legal_actions: list[int],
    ) -> EvaluationDecision:
        if not legal_actions:
            raise ValueError(
                "Evaluation agent cannot choose from an empty "
                "legal action set."
            )

        state_values = self._q_values.get(
            state_key,
            (0.0,) * 9,
        )
        legal_q_values = {
            action: float(state_values[action])
            for action in legal_actions
        }
        confidence = analyze_policy_confidence(
            legal_q_values,
        )

        if confidence.best_action is None:
            raise RuntimeError(
                "Evaluation policy could not identify a "
                "legal action."
            )

        # The policy is fully deterministic, including Q-value ties.
        action = min(confidence.tied_best_actions)

        return EvaluationDecision(
            state_key=state_key,
            action=action,
            legal_q_values=legal_q_values,
            best_q=confidence.best_q,
            second_best_q=confidence.second_best_q,
            action_gap=confidence.action_gap,
            normalized_confidence=(
                confidence.normalized_confidence
            ),
            tied_best_actions=(
                confidence.tied_best_actions.copy()
            ),
        )
