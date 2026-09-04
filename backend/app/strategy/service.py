from __future__ import annotations

from collections import defaultdict
from math import fsum

from sqlalchemy import (
    func,
    select,
)

from app.database.database import (
    SessionLocal,
)
from app.database.models import (
    EpisodeModel,
    LearningUpdateModel,
    QValueModel,
)
from app.strategy.board_analysis import (
    CENTER_ACTION,
    CORNER_ACTIONS,
    EDGE_ACTIONS,
    action_position_type,
    analyze_tactics,
    decode_state,
    legal_actions,
)
from app.strategy.policy_analysis import (
    analyze_policy_confidence,
    best_actions,
    preference_score,
    rank_actions,
    tactical_alignment_score,
)


class StrategyService:
    def __init__(
        self,
        session_factory=SessionLocal,
    ) -> None:
        self.session_factory = session_factory

    def _load_q_table(
        self,
    ) -> dict[str, dict[int, float]]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(QValueModel)
                .order_by(
                    QValueModel.state_key.asc(),
                    QValueModel.action.asc(),
                ),
            ).all()

        table: dict[
            str,
            dict[int, float],
        ] = defaultdict(dict)

        for row in rows:
            table[row.state_key][row.action] = float(
                row.q_value,
            )

        return dict(table)

    def inspect_state(
        self,
        state_key: str,
    ) -> dict:
        board = decode_state(state_key)
        legal = legal_actions(board)

        with self.session_factory() as session:
            rows = session.scalars(
                select(QValueModel)
                .where(
                    QValueModel.state_key
                    == state_key,
                )
                .order_by(
                    QValueModel.action.asc(),
                ),
            ).all()

        persisted_values = {
            row.action: float(row.q_value)
            for row in rows
        }

        legal_values = {
            action: persisted_values.get(
                action,
                0.0,
            )
            for action in legal
        }

        confidence = analyze_policy_confidence(
            legal_values,
        )
        ranked = rank_actions(legal_values)
        rank_lookup = {
            item.action: item
            for item in ranked
        }
        tactics = analyze_tactics(board)

        board_response = [
            {
                "index": index,
                "value": value,
                "symbol": (
                    "X"
                    if value == 1
                    else "O"
                    if value == 2
                    else None
                ),
            }
            for index, value in enumerate(board)
        ]

        action_values = []

        for action in legal:
            ranked_action = rank_lookup[action]
            action_values.append(
                {
                    "action": action,
                    "q_value": legal_values[action],
                    "rank": ranked_action.rank,
                    "is_legal": True,
                    "is_best": ranked_action.is_best,
                    "position_type": action_position_type(
                        action,
                    ),
                    "action_gap_from_best": (
                        ranked_action.action_gap_from_best
                    ),
                    "is_immediate_win": (
                        action
                        in tactics.immediate_wins
                    ),
                    "is_immediate_block": (
                        action
                        in tactics.immediate_blocks
                    ),
                    "is_fork_creation": (
                        action
                        in tactics.fork_creations
                    ),
                    "is_fork_prevention": (
                        action
                        in tactics.fork_preventions
                    ),
                },
            )

        return {
            "state_key": state_key,
            "board": board_response,
            "legal_actions": legal,
            "action_values": action_values,
            "policy_confidence": {
                "best_action": confidence.best_action,
                "best_q": confidence.best_q,
                "second_best_q": (
                    confidence.second_best_q
                ),
                "action_gap": confidence.action_gap,
                "normalized_confidence": (
                    confidence.normalized_confidence
                ),
                "tied_best_actions": (
                    confidence.tied_best_actions
                ),
            },
            "tactical_evidence": {
                "immediate_wins": (
                    tactics.immediate_wins
                ),
                "immediate_blocks": (
                    tactics.immediate_blocks
                ),
                "fork_creations": (
                    tactics.fork_creations
                ),
                "fork_preventions": (
                    tactics.fork_preventions
                ),
            },
            "q_rows_found": len(rows),
        }

    def list_states(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        with self.session_factory() as session:
            states = session.execute(
                select(
                    QValueModel.state_key,
                    func.count(
                        QValueModel.id,
                    ).label("stored_actions"),
                )
                .group_by(
                    QValueModel.state_key,
                )
                .order_by(
                    QValueModel.state_key.asc(),
                )
                .offset(offset)
                .limit(limit),
            ).all()

            update_counts = dict(
                session.execute(
                    select(
                        LearningUpdateModel.state_key,
                        func.count(
                            LearningUpdateModel.id,
                        ),
                    )
                    .group_by(
                        LearningUpdateModel.state_key,
                    ),
                ).all(),
            )

        result: list[dict] = []

        for state_key, stored_actions in states:
            board = decode_state(state_key)
            legal = legal_actions(board)
            inspection = self.inspect_state(
                state_key,
            )
            confidence = inspection[
                "policy_confidence"
            ]

            result.append(
                {
                    "state_key": state_key,
                    "stored_actions": int(
                        stored_actions,
                    ),
                    "legal_actions": len(legal),
                    "best_action": confidence[
                        "best_action"
                    ],
                    "best_q": confidence["best_q"],
                    "action_gap": confidence[
                        "action_gap"
                    ],
                    "visit_updates": int(
                        update_counts.get(
                            state_key,
                            0,
                        ),
                    ),
                },
            )

        return result

    def get_strategy_overview(
        self,
    ) -> dict:
        q_table = self._load_q_table()

        analyzed_states = 0
        states_with_legal_actions = 0
        states_with_nonzero_q = 0
        states_with_unique_best_action = 0
        action_gaps: list[float] = []
        normalized_confidences: list[
            float
        ] = []

        tactical_accumulators = {
            "immediate_win": {
                "opportunities": 0,
                "aligned": 0.0,
            },
            "immediate_block": {
                "opportunities": 0,
                "aligned": 0.0,
            },
            "fork_creation": {
                "opportunities": 0,
                "aligned": 0.0,
            },
            "fork_prevention": {
                "opportunities": 0,
                "aligned": 0.0,
            },
        }

        preference_accumulators = {
            "center": {
                "eligible": 0,
                "mass": 0.0,
            },
            "corner": {
                "eligible": 0,
                "mass": 0.0,
            },
            "edge": {
                "eligible": 0,
                "mass": 0.0,
            },
        }

        for (
            state_key,
            persisted_values,
        ) in q_table.items():
            try:
                board = decode_state(state_key)
            except ValueError:
                continue

            analyzed_states += 1
            legal = legal_actions(board)

            if not legal:
                continue

            states_with_legal_actions += 1

            legal_values = {
                action: persisted_values.get(
                    action,
                    0.0,
                )
                for action in legal
            }

            if any(
                abs(value) > 1e-12
                for value in legal_values.values()
            ):
                states_with_nonzero_q += 1

            greedy = best_actions(legal_values)
            confidence = analyze_policy_confidence(
                legal_values,
            )

            action_gaps.append(
                confidence.action_gap,
            )
            normalized_confidences.append(
                confidence.normalized_confidence,
            )

            if (
                len(confidence.tied_best_actions)
                == 1
            ):
                states_with_unique_best_action += 1

            tactics = analyze_tactics(board)

            self._accumulate_tactical(
                tactical_accumulators[
                    "immediate_win"
                ],
                tactics.immediate_wins,
                greedy,
            )
            self._accumulate_tactical(
                tactical_accumulators[
                    "immediate_block"
                ],
                tactics.immediate_blocks,
                greedy,
            )
            self._accumulate_tactical(
                tactical_accumulators[
                    "fork_creation"
                ],
                tactics.fork_creations,
                greedy,
            )
            self._accumulate_tactical(
                tactical_accumulators[
                    "fork_prevention"
                ],
                tactics.fork_preventions,
                greedy,
            )

            legal_set = set(legal)

            if CENTER_ACTION in legal_set:
                preference_accumulators["center"][
                    "eligible"
                ] += 1
                preference_accumulators["center"][
                    "mass"
                ] += preference_score(
                    {CENTER_ACTION},
                    greedy,
                )

            available_corners = (
                CORNER_ACTIONS
                & legal_set
            )
            if available_corners:
                preference_accumulators["corner"][
                    "eligible"
                ] += 1
                preference_accumulators["corner"][
                    "mass"
                ] += preference_score(
                    available_corners,
                    greedy,
                )

            available_edges = (
                EDGE_ACTIONS & legal_set
            )
            if available_edges:
                preference_accumulators["edge"][
                    "eligible"
                ] += 1
                preference_accumulators["edge"][
                    "mass"
                ] += preference_score(
                    available_edges,
                    greedy,
                )

        return {
            "analyzed_states": analyzed_states,
            "states_with_legal_actions": (
                states_with_legal_actions
            ),
            "states_with_nonzero_q": (
                states_with_nonzero_q
            ),
            "states_with_unique_best_action": (
                states_with_unique_best_action
            ),
            "mean_action_gap": self._mean(
                action_gaps,
            ),
            "mean_normalized_confidence": (
                self._mean(
                    normalized_confidences,
                )
            ),
            "immediate_win": self._strategy_metric(
                key="immediate_win",
                label="Immediate Win",
                accumulator=(
                    tactical_accumulators[
                        "immediate_win"
                    ]
                ),
                interpretation=(
                    "Greedy-policy alignment with available "
                    "one-move agent wins."
                ),
            ),
            "immediate_block": self._strategy_metric(
                key="immediate_block",
                label="Threat Blocking",
                accumulator=(
                    tactical_accumulators[
                        "immediate_block"
                    ]
                ),
                interpretation=(
                    "Greedy-policy alignment with cells where "
                    "the human could otherwise win immediately."
                ),
            ),
            "fork_creation": self._strategy_metric(
                key="fork_creation",
                label="Fork Creation",
                accumulator=(
                    tactical_accumulators[
                        "fork_creation"
                    ]
                ),
                interpretation=(
                    "Greedy-policy alignment with moves "
                    "creating at least two next-turn "
                    "winning actions."
                ),
            ),
            "fork_prevention": self._strategy_metric(
                key="fork_prevention",
                label="Fork Prevention",
                accumulator=(
                    tactical_accumulators[
                        "fork_prevention"
                    ]
                ),
                interpretation=(
                    "Greedy-policy alignment with moves "
                    "reducing detected human fork "
                    "opportunities."
                ),
            ),
            "center_preference": (
                self._preference_metric(
                    key="center_preference",
                    label="Center Preference",
                    accumulator=(
                        preference_accumulators[
                            "center"
                        ]
                    ),
                    interpretation=(
                        "Tie-aware fraction of greedy policy "
                        "mass assigned to the center when the "
                        "center is legal."
                    ),
                )
            ),
            "corner_preference": (
                self._preference_metric(
                    key="corner_preference",
                    label="Corner Preference",
                    accumulator=(
                        preference_accumulators[
                            "corner"
                        ]
                    ),
                    interpretation=(
                        "Tie-aware fraction of greedy policy "
                        "mass assigned to currently legal corners."
                    ),
                )
            ),
            "edge_preference": self._preference_metric(
                key="edge_preference",
                label="Edge Preference",
                accumulator=(
                    preference_accumulators[
                        "edge"
                    ]
                ),
                interpretation=(
                    "Tie-aware fraction of greedy policy mass "
                    "assigned to currently legal edges."
                ),
            ),
        }

    def get_strategy_evidence(
        self,
        strategy: str,
        limit: int = 100,
    ) -> list[dict]:
        q_table = self._load_q_table()

        result: list[dict] = []

        for (
            state_key,
            persisted_values,
        ) in q_table.items():
            try:
                board = decode_state(state_key)
            except ValueError:
                continue

            legal = legal_actions(board)
            if not legal:
                continue

            legal_values = {
                action: persisted_values.get(
                    action,
                    0.0,
                )
                for action in legal
            }

            greedy = best_actions(legal_values)
            confidence = analyze_policy_confidence(
                legal_values,
            )
            tactics = analyze_tactics(board)

            opportunity_actions = self._strategy_actions(
                strategy,
                tactics,
                legal,
            )

            if not opportunity_actions:
                continue

            alignment = (
                tactical_alignment_score(
                    set(opportunity_actions),
                    greedy,
                )
                if strategy
                in {
                    "immediate_win",
                    "immediate_block",
                    "fork_creation",
                    "fork_prevention",
                }
                else preference_score(
                    set(opportunity_actions),
                    greedy,
                )
            )

            result.append(
                {
                    "state_key": state_key,
                    "strategy": strategy,
                    "opportunity_actions": sorted(
                        opportunity_actions,
                    ),
                    "greedy_actions": sorted(
                        greedy,
                    ),
                    "alignment_score": alignment,
                    "best_action": (
                        confidence.best_action
                    ),
                    "best_q": confidence.best_q,
                    "action_gap": (
                        confidence.action_gap
                    ),
                },
            )

        result.sort(
            key=lambda item: (
                -item["alignment_score"],
                -item["action_gap"],
                item["state_key"],
            ),
        )

        return result[:limit]

    def inspect_decision(
        self,
        state_key: str,
    ) -> dict:
        board = decode_state(state_key)
        legal = legal_actions(board)

        with self.session_factory() as session:
            rows = session.scalars(
                select(QValueModel)
                .where(
                    QValueModel.state_key
                    == state_key,
                ),
            ).all()

        persisted_values = {
            row.action: float(row.q_value)
            for row in rows
        }
        legal_values = {
            action: persisted_values.get(
                action,
                0.0,
            )
            for action in legal
        }

        greedy = best_actions(legal_values)
        confidence = analyze_policy_confidence(
            legal_values,
        )
        tactics = analyze_tactics(board)

        immediate_win_alignment = (
            tactical_alignment_score(
                set(tactics.immediate_wins),
                greedy,
            )
        )
        immediate_block_alignment = (
            tactical_alignment_score(
                set(tactics.immediate_blocks),
                greedy,
            )
        )
        fork_creation_alignment = (
            tactical_alignment_score(
                set(tactics.fork_creations),
                greedy,
            )
        )
        fork_prevention_alignment = (
            tactical_alignment_score(
                set(tactics.fork_preventions),
                greedy,
            )
        )

        labels: list[str] = []

        if immediate_win_alignment > 0:
            labels.append(
                "immediate-win evidence",
            )
        if immediate_block_alignment > 0:
            labels.append(
                "threat-block evidence",
            )
        if fork_creation_alignment > 0:
            labels.append(
                "fork-creation evidence",
            )
        if fork_prevention_alignment > 0:
            labels.append(
                "fork-prevention evidence",
            )
        if CENTER_ACTION in greedy:
            labels.append(
                "center preference",
            )
        if any(
            action in CORNER_ACTIONS
            for action in greedy
        ):
            labels.append(
                "corner preference",
            )
        if any(
            action in EDGE_ACTIONS
            for action in greedy
        ):
            labels.append(
                "edge preference",
            )

        return {
            "state_key": state_key,
            "best_action": confidence.best_action,
            "greedy_actions": greedy,
            "best_q": confidence.best_q,
            "second_best_q": (
                confidence.second_best_q
            ),
            "action_gap": confidence.action_gap,
            "normalized_confidence": (
                confidence.normalized_confidence
            ),
            "immediate_win_alignment": (
                immediate_win_alignment
            ),
            "immediate_block_alignment": (
                immediate_block_alignment
            ),
            "fork_creation_alignment": (
                fork_creation_alignment
            ),
            "fork_prevention_alignment": (
                fork_prevention_alignment
            ),
            "tactical_labels": labels,
        }

    def list_episodes(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict]:
        with self.session_factory() as session:
            episodes = session.scalars(
                select(EpisodeModel)
                .order_by(
                    EpisodeModel.episode_number.desc(),
                    EpisodeModel.id.desc(),
                )
                .offset(offset)
                .limit(limit),
            ).all()

            counts = dict(
                session.execute(
                    select(
                        LearningUpdateModel.episode_number,
                        func.count(
                            LearningUpdateModel.id,
                        ),
                    )
                    .group_by(
                        LearningUpdateModel.episode_number,
                    ),
                ).all(),
            )

        return [
            {
                "episode_number": (
                    episode.episode_number
                ),
                "winner": episode.winner,
                "is_draw": episode.is_draw,
                "outcome": self._episode_outcome(
                    episode,
                ),
                "epsilon_after": float(
                    episode.epsilon_after,
                ),
                "total_updates_after": (
                    episode.total_updates_after
                ),
                "learning_event_count": int(
                    counts.get(
                        episode.episode_number,
                        0,
                    ),
                ),
                "created_at": episode.created_at,
            }
            for episode in episodes
        ]

    def inspect_episode(
        self,
        episode_number: int,
    ) -> dict | None:
        with self.session_factory() as session:
            episode = session.scalar(
                select(EpisodeModel)
                .where(
                    EpisodeModel.episode_number
                    == episode_number,
                )
                .order_by(
                    EpisodeModel.id.desc(),
                ),
            )

            if episode is None:
                return None

            updates = session.scalars(
                select(LearningUpdateModel)
                .where(
                    LearningUpdateModel.episode_number
                    == episode_number,
                )
                .order_by(
                    LearningUpdateModel.id.asc(),
                ),
            ).all()

        return {
            "episode_number": (
                episode.episode_number
            ),
            "winner": episode.winner,
            "is_draw": episode.is_draw,
            "outcome": self._episode_outcome(
                episode,
            ),
            "epsilon_after": float(
                episode.epsilon_after,
            ),
            "total_updates_after": (
                episode.total_updates_after
            ),
            "created_at": episode.created_at,
            "learning_events": [
                {
                    "id": update.id,
                    "state": update.state_key,
                    "action": update.action,
                    "reward": float(update.reward),
                    "old_q": float(update.old_q),
                    "best_future_q": float(
                        update.best_future_q,
                    ),
                    "td_target": float(
                        update.td_target,
                    ),
                    "td_error": float(
                        update.td_error,
                    ),
                    "new_q": float(update.new_q),
                    "delta_q": float(
                        update.delta_q,
                    ),
                    "alpha": float(update.alpha),
                    "gamma": float(update.gamma),
                    "terminal": update.terminal,
                    "created_at": update.created_at,
                }
                for update in updates
            ],
        }

    @staticmethod
    def _accumulate_tactical(
        accumulator: dict,
        opportunity_actions: list[int],
        greedy_actions: list[int],
    ) -> None:
        if not opportunity_actions:
            return

        accumulator["opportunities"] += 1
        accumulator["aligned"] += (
            tactical_alignment_score(
                set(opportunity_actions),
                greedy_actions,
            )
        )

    @staticmethod
    def _strategy_metric(
        key: str,
        label: str,
        accumulator: dict,
        interpretation: str,
    ) -> dict:
        opportunities = int(
            accumulator["opportunities"],
        )
        aligned = float(
            accumulator["aligned"],
        )
        rate = (
            aligned / opportunities
            if opportunities > 0
            else 0.0
        )

        return {
            "key": key,
            "label": label,
            "opportunities": opportunities,
            "aligned_states": aligned,
            "evidence_rate": rate,
            "interpretation": interpretation,
        }

    @staticmethod
    def _preference_metric(
        key: str,
        label: str,
        accumulator: dict,
        interpretation: str,
    ) -> dict:
        eligible = int(
            accumulator["eligible"],
        )
        mass = float(
            accumulator["mass"],
        )
        rate = (
            mass / eligible
            if eligible > 0
            else 0.0
        )

        return {
            "key": key,
            "label": label,
            "eligible_states": eligible,
            "preference_mass": mass,
            "preference_rate": rate,
            "interpretation": interpretation,
        }

    @staticmethod
    def _strategy_actions(
        strategy: str,
        tactics,
        legal: list[int],
    ) -> list[int]:
        if strategy == "immediate_win":
            return list(tactics.immediate_wins)

        if strategy == "immediate_block":
            return list(tactics.immediate_blocks)

        if strategy == "fork_creation":
            return list(tactics.fork_creations)

        if strategy == "fork_prevention":
            return list(tactics.fork_preventions)

        if strategy == "center_preference":
            return (
                [CENTER_ACTION]
                if CENTER_ACTION in legal
                else []
            )

        if strategy == "corner_preference":
            return sorted(
                CORNER_ACTIONS & set(legal),
            )

        if strategy == "edge_preference":
            return sorted(
                EDGE_ACTIONS & set(legal),
            )

        raise ValueError(
            f"Unsupported strategy: {strategy}",
        )

    @staticmethod
    def _episode_outcome(
        episode: EpisodeModel,
    ) -> str:
        if episode.is_draw:
            return "draw"

        if episode.winner == "O":
            return "agent"

        if episode.winner == "X":
            return "human"

        return "unknown"

    @staticmethod
    def _mean(
        values: list[float],
    ) -> float:
        if not values:
            return 0.0

        return fsum(values) / len(values)


strategy_service = StrategyService()
