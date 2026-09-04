import random
import threading
import time

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.models import (
    AgentConfigModel,
    QValueModel,
    TrainingEpisodeModel,
    TrainingRunModel,
    utc_now,
)
from app.training.agent_adapter import (
    TrainingAgentAdapter,
)
from app.training.engine import TrainingEpisodeEngine
from app.training.opponents import create_opponent
from app.training.rewards import (
    DEFAULT_TRAINING_REWARDS,
)


class TrainingCoordinator:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_run_id: int | None = None

    @property
    def active_run_id(self) -> int | None:
        with self._lock:
            return self._active_run_id

    def is_busy(self) -> bool:
        return self.active_run_id is not None

    def begin_run(
        self,
        run_id: int,
    ) -> None:
        with self._lock:
            if self._active_run_id is not None:
                raise RuntimeError(
                    "A training run is already active."
                )

            self._active_run_id = run_id

    def end_run(
        self,
        run_id: int,
    ) -> None:
        with self._lock:
            if self._active_run_id == run_id:
                self._active_run_id = None


training_coordinator = TrainingCoordinator()


def execute_training_run(
    *,
    db: Session,
    run_id: int,
    agent,
) -> None:
    run = db.scalar(
        select(TrainingRunModel).where(
            TrainingRunModel.id == run_id,
        )
    )

    if run is None:
        raise ValueError(
            f"Training run not found: {run_id}"
        )

    training_coordinator.begin_run(run_id)
    started_perf = time.perf_counter()

    try:
        run.status = "running"
        run.started_at = utc_now()
        db.commit()

        rng = random.Random(run.seed)
        adapter = TrainingAgentAdapter(
            agent=agent,
            rng=rng,
        )
        opponent = create_opponent(
            opponent_type=run.opponent_type,
            rng=rng,
            tactical_probability=(
                run.tactical_probability
                if run.tactical_probability is not None
                else 0.70
            ),
        )
        engine = TrainingEpisodeEngine(
            agent=adapter,
            opponent=opponent,
            rewards=DEFAULT_TRAINING_REWARDS,
            rng=rng,
        )

        for episode_index in range(
            1,
            run.requested_episodes + 1,
        ):
            episode_result = engine.run_episode()

            db.add(
                TrainingEpisodeModel(
                    training_run_id=run.id,
                    episode_index=episode_index,
                    result=episode_result.result,
                    reward=episode_result.reward,
                    agent_moves=episode_result.agent_moves,
                    opponent_moves=(
                        episode_result.opponent_moves
                    ),
                    epsilon_before=(
                        episode_result.epsilon_before
                    ),
                    epsilon_after=(
                        episode_result.epsilon_after
                    ),
                    final_board_key=(
                        episode_result.final_board_key
                    ),
                    move_count=episode_result.move_count,
                    duration_ms=episode_result.duration_ms,
                )
            )

            run.completed_episodes += 1
            run.total_agent_moves += (
                episode_result.agent_moves
            )
            run.total_opponent_moves += (
                episode_result.opponent_moves
            )
            run.cumulative_reward += episode_result.reward

            if episode_result.result == "agent_win":
                run.agent_wins += 1
            elif episode_result.result == "opponent_win":
                run.opponent_wins += 1
            elif episode_result.result == "draw":
                run.draws += 1

            run.mean_reward = (
                run.cumulative_reward
                / run.completed_episodes
            )
            run.epsilon_end = adapter.epsilon
            run.q_states_end = adapter.q_state_count()
            run.q_entries_end = adapter.q_entry_count()

            elapsed = time.perf_counter() - started_perf
            run.duration_seconds = elapsed

            if elapsed > 0:
                run.episodes_per_second = (
                    run.completed_episodes / elapsed
                )

            if (
                episode_index % 25 == 0
                or episode_index
                == run.requested_episodes
            ):
                _persist_dirty_q_values(db, adapter)
                _persist_agent_state(db, agent)
                db.commit()

        _persist_dirty_q_values(db, adapter)
        _persist_agent_state(db, agent)

        run.status = "completed"
        run.completed_at = utc_now()
        final_elapsed = time.perf_counter() - started_perf
        run.duration_seconds = final_elapsed

        if final_elapsed > 0:
            run.episodes_per_second = (
                run.completed_episodes / final_elapsed
            )

        run.epsilon_end = adapter.epsilon
        run.q_states_end = adapter.q_state_count()
        run.q_entries_end = adapter.q_entry_count()
        db.commit()

    except Exception as exc:
        db.rollback()
        failed_run = db.scalar(
            select(TrainingRunModel).where(
                TrainingRunModel.id == run_id,
            )
        )

        if failed_run is not None:
            failed_run.status = "failed"
            failed_run.error_message = str(exc)
            failed_run.completed_at = utc_now()
            db.commit()

        raise

    finally:
        training_coordinator.end_run(run_id)


def _persist_dirty_q_values(
    db: Session,
    adapter: TrainingAgentAdapter,
) -> None:
    for state_key, action in sorted(
        adapter.dirty_state_actions
    ):
        row = db.scalar(
            select(QValueModel).where(
                QValueModel.state_key == state_key,
                QValueModel.action == action,
            )
        )
        q_value = adapter.get_q_value(
            state_key,
            action,
        )
        update_count = adapter.dirty_update_counts.get(
            (state_key, action),
            1,
        )

        if row is None:
            row = QValueModel(
                state_key=state_key,
                action=action,
                q_value=q_value,
                update_count=update_count,
            )
            db.add(row)
        else:
            row.q_value = q_value
            row.update_count += update_count

    adapter.clear_dirty_state_actions()


def _persist_agent_state(
    db: Session,
    agent,
) -> None:
    config = db.get(
        AgentConfigModel,
        1,
    )

    if config is None:
        config = AgentConfigModel(id=1)
        db.add(config)

    config.alpha = agent.alpha
    config.gamma = agent.gamma
    config.epsilon = agent.epsilon
    config.epsilon_min = agent.epsilon_min
    config.epsilon_decay = agent.epsilon_decay
    config.total_decisions = agent.total_decisions
    config.exploration_moves = agent.exploration_moves
    config.exploitation_moves = agent.exploitation_moves
    config.total_updates = agent.total_updates
