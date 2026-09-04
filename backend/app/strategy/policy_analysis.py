from __future__ import annotations

from dataclasses import dataclass
from math import exp


@dataclass(frozen=True)
class RankedAction:
    action: int
    q_value: float
    rank: int
    is_best: bool
    action_gap_from_best: float


@dataclass(frozen=True)
class PolicyConfidence:
    best_action: int | None
    best_q: float
    second_best_q: float
    action_gap: float
    normalized_confidence: float
    tied_best_actions: list[int]


def rank_actions(
    action_values: dict[int, float],
) -> list[RankedAction]:
    if not action_values:
        return []

    sorted_items = sorted(
        action_values.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    best_q = sorted_items[0][1]

    return [
        RankedAction(
            action=action,
            q_value=q_value,
            rank=index,
            is_best=(
                abs(q_value - best_q)
                <= 1e-12
            ),
            action_gap_from_best=(
                best_q - q_value
            ),
        )
        for index, (
            action,
            q_value,
        ) in enumerate(
            sorted_items,
            start=1,
        )
    ]


def analyze_policy_confidence(
    action_values: dict[int, float],
) -> PolicyConfidence:
    if not action_values:
        return PolicyConfidence(
            best_action=None,
            best_q=0.0,
            second_best_q=0.0,
            action_gap=0.0,
            normalized_confidence=0.0,
            tied_best_actions=[],
        )

    sorted_items = sorted(
        action_values.items(),
        key=lambda item: (
            -item[1],
            item[0],
        ),
    )

    best_action = sorted_items[0][0]
    best_q = float(sorted_items[0][1])

    tied_best_actions = [
        action
        for action, q_value in sorted_items
        if abs(q_value - best_q)
        <= 1e-12
    ]

    if len(sorted_items) == 1:
        second_best_q = best_q
        action_gap = 0.0
    else:
        second_best_q = float(
            sorted_items[1][1],
        )
        action_gap = max(
            0.0,
            best_q - second_best_q,
        )

    normalized_confidence = (
        1.0 - exp(-action_gap)
    )

    return PolicyConfidence(
        best_action=best_action,
        best_q=best_q,
        second_best_q=second_best_q,
        action_gap=action_gap,
        normalized_confidence=(
            normalized_confidence
        ),
        tied_best_actions=tied_best_actions,
    )


def best_actions(
    action_values: dict[int, float],
) -> list[int]:
    if not action_values:
        return []

    best_q = max(
        action_values.values(),
    )

    return [
        action
        for action, q_value in action_values.items()
        if abs(q_value - best_q)
        <= 1e-12
    ]


def preference_score(
    preferred_actions: set[int],
    greedy_actions: list[int],
) -> float:
    if not greedy_actions:
        return 0.0

    preferred_count = sum(
        action in preferred_actions
        for action in greedy_actions
    )

    return (
        preferred_count
        / len(greedy_actions)
    )


def tactical_alignment_score(
    tactical_actions: set[int],
    greedy_actions: list[int],
) -> float:
    if not tactical_actions:
        return 0.0

    if not greedy_actions:
        return 0.0

    overlap = sum(
        action in tactical_actions
        for action in greedy_actions
    )

    return overlap / len(
        greedy_actions,
    )
