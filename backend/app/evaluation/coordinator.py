from __future__ import annotations

import hashlib
import json
import random
import threading
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    EvaluationEpisodeModel,
    EvaluationRunModel,
    PolicySnapshotModel,
    utc_now,
)
from app.evaluation.agent import (
    FrozenEvaluationAgent,
    TIE_BREAKING_POLICY,
)
from app.evaluation.engine import (
    EvaluationEpisodeEngine,
)
from app.training.opponents import create_opponent


class EvaluationCoordinator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_run_id: int | None = None

    @property
    def active_run_id(self) -> int | None:
        with self._lock:
            return self._active_run_id

    def is_busy(self) -> bool:
        return self.active_run_id is not None

    def begin_run(self, run_id: int) -> None:
        with self._lock:
            if self._active_run_id is not None:
                raise RuntimeError(
                    "An evaluation run is already active."
                )

            self._active_run_id = run_id

    def end_run(self, run_id: int) -> None:
        with self._lock:
            if self._active_run_id == run_id:
                self._active_run_id = None


evaluation_coordinator = EvaluationCoordinator()


def create_policy_snapshot(
    *,
    db: Session,
    agent,
) -> PolicySnapshotModel:
    q_table = getattr(agent, "q_table", None)

    if q_table is None or not hasattr(q_table, "snapshot"):
        raise AttributeError(
            "The shared agent does not expose a snapshot-capable "
            "Q-table."
        )

    q_values = q_table.snapshot()
    serialized_values = json.dumps(
        q_values,
        sort_keys=True,
        separators=(",", ":"),
    )
    table_hash = hashlib.sha256(
        serialized_values.encode("utf-8")
    ).hexdigest()
    q_entries = sum(
        1
        for values in q_values.values()
        for value in values
        if value != 0.0
    )

    snapshot = PolicySnapshotModel(
        source="live_agent",
        q_values_json=serialized_values,
        q_table_hash=table_hash,
        q_states=len(q_values),
        q_entries=q_entries,
        alpha=float(agent.alpha),
        gamma=float(agent.gamma),
        tie_breaking_policy=TIE_BREAKING_POLICY,
    )
    db.add(snapshot)
    db.flush()
    return snapshot


def execute_evaluation_run(
    *,
    db: Session,
    run_id: int,
) -> None:
    run = db.scalar(
        select(EvaluationRunModel).where(
            EvaluationRunModel.id == run_id,
        )
    )

    if run is None:
        raise ValueError(
            f"Evaluation run not found: {run_id}"
        )

    snapshot = db.get(
        PolicySnapshotModel,
        run.snapshot_id,
    )
    if snapshot is None:
        raise ValueError(
            "Evaluation policy snapshot was not found."
        )

    evaluation_coordinator.begin_run(run_id)
    started_perf = time.perf_counter()

    try:
        run.status = "running"
        run.started_at = utc_now()
        db.commit()

        rng = random.Random(run.seed)
        q_values = json.loads(snapshot.q_values_json)
        agent = FrozenEvaluationAgent(q_values)
        opponent = create_opponent(
            opponent_type=run.opponent_type,
            rng=rng,
            tactical_probability=(
                run.tactical_probability
                if run.tactical_probability is not None
                else 0.70
            ),
        )
        engine = EvaluationEpisodeEngine(
            agent=agent,
            opponent=opponent,
        )
        visited_states: set[str] = set()

        for game_index in range(
            1,
            run.requested_games + 1,
        ):
            result = engine.run_episode()
            visited_states.update(result.visited_states)

            db.add(
                EvaluationEpisodeModel(
                    evaluation_run_id=run.id,
                    game_index=game_index,
                    result=result.result,
                    agent_moves=result.agent_moves,
                    opponent_moves=result.opponent_moves,
                    move_count=result.move_count,
                    decision_count=result.decision_count,
                    mean_confidence=(
                        result.confidence_sum
                        / result.decision_count
                        if result.decision_count
                        else 0.0
                    ),
                    mean_action_gap=(
                        result.action_gap_sum
                        / result.decision_count
                        if result.decision_count
                        else 0.0
                    ),
                    immediate_win_opportunities=(
                        result.immediate_win_opportunities
                    ),
                    immediate_win_successes=(
                        result.immediate_win_successes
                    ),
                    immediate_block_opportunities=(
                        result.immediate_block_opportunities
                    ),
                    immediate_block_successes=(
                        result.immediate_block_successes
                    ),
                    unique_states_visited=len(
                        result.visited_states
                    ),
                    final_board_key=result.final_board_key,
                    duration_ms=result.duration_ms,
                )
            )

            run.completed_games += 1
            run.total_moves += result.move_count
            run.total_agent_moves += result.agent_moves
            run.total_opponent_moves += result.opponent_moves
            run.total_decisions += result.decision_count
            run.confidence_sum += result.confidence_sum
            run.action_gap_sum += result.action_gap_sum
            run.immediate_win_opportunities += (
                result.immediate_win_opportunities
            )
            run.immediate_win_successes += (
                result.immediate_win_successes
            )
            run.immediate_block_opportunities += (
                result.immediate_block_opportunities
            )
            run.immediate_block_successes += (
                result.immediate_block_successes
            )

            if result.result == "agent_win":
                run.agent_wins += 1
            elif result.result == "opponent_win":
                run.opponent_wins += 1
            else:
                run.draws += 1

        duration_seconds = (
            time.perf_counter() - started_perf
        )
        run.unique_states_visited = len(visited_states)
        run.duration_seconds = duration_seconds
        run.games_per_second = (
            run.completed_games / duration_seconds
            if duration_seconds > 0
            else 0.0
        )
        run.status = "completed"
        run.completed_at = utc_now()
        db.commit()
    except Exception as exc:
        db.rollback()
        failed_run = db.get(EvaluationRunModel, run_id)
        if failed_run is not None:
            failed_run.status = "failed"
            failed_run.error_message = str(exc)
            failed_run.completed_at = utc_now()
            db.commit()
        raise
    finally:
        evaluation_coordinator.end_run(run_id)
