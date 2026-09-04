from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class QValueModel(Base):
    __tablename__ = "q_values"

    __table_args__ = (
        UniqueConstraint(
            "state_key",
            "action",
            name="uq_state_action",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )
    state_key: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        index=True,
    )
    action: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    q_value: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    update_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )


class AgentConfigModel(Base):
    __tablename__ = "agent_config"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )
    alpha: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.20,
    )
    gamma: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.95,
    )
    epsilon: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.90,
    )
    epsilon_min: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.05,
    )
    epsilon_decay: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.995,
    )
    total_decisions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    exploration_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    exploitation_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_updates: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class ExperimentStatsModel(Base):
    __tablename__ = "experiment_stats"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        default=1,
    )
    human_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    agent_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    draws: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    episodes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )


class EpisodeModel(Base):
    __tablename__ = "episodes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    episode_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    winner: Mapped[str | None] = mapped_column(
        String(1),
        nullable=True,
    )
    is_draw: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    epsilon_after: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    total_updates_after: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )


class LearningUpdateModel(Base):
    __tablename__ = "learning_updates"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    episode_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    state_key: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        index=True,
    )
    action: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    reward: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    old_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    best_future_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    td_target: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    td_error: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    new_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    delta_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    alpha: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.20,
    )
    gamma: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.95,
    )
    terminal: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class DecisionEventModel(Base):
    __tablename__ = "decision_events"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
    )
    episode_number: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True,
    )
    decision_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    state_key: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
        index=True,
    )
    legal_actions_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    q_values_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    epsilon: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    exploration_draw: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    decision_mode: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    greedy_actions_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    selected_action: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    selected_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    best_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    second_best_q: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    action_gap: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    was_greedy_action: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    tie_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    tactical_labels_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        default="[]",
    )
    explanation: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class TrainingRunModel(Base):
    __tablename__ = "training_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )
    opponent_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="random",
        index=True,
    )
    tactical_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    requested_episodes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    completed_episodes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    agent_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    opponent_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    draws: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_agent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_opponent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    epsilon_start: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    epsilon_end: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    q_states_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    q_states_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    q_entries_start: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    q_entries_end: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    cumulative_reward: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    mean_reward: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    episodes_per_second: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    seed: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class TrainingEpisodeModel(Base):
    __tablename__ = "training_episodes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    training_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("training_runs.id"),
        nullable=False,
        index=True,
    )
    episode_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    result: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    reward: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    agent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    opponent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    epsilon_before: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    epsilon_after: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    final_board_key: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
    )
    move_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class PolicySnapshotModel(Base):
    __tablename__ = "policy_snapshots"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    source: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="live_agent",
    )
    q_values_json: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    q_table_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    q_states: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    q_entries: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    alpha: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.20,
    )
    gamma: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.95,
    )
    tie_breaking_policy: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="lowest_action_index",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )


class EvaluationRunModel(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    snapshot_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("policy_snapshots.id"),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )
    opponent_type: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    tactical_probability: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    requested_games: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    completed_games: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    agent_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    opponent_wins: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    draws: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_agent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_opponent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    total_decisions: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    unique_states_visited: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    confidence_sum: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    action_gap_sum: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    immediate_win_opportunities: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_win_successes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_block_opportunities: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_block_successes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    seed: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    tie_breaking_policy: Mapped[str] = mapped_column(
        String(40),
        nullable=False,
        default="lowest_action_index",
    )
    duration_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    games_per_second: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    error_message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class EvaluationEpisodeModel(Base):
    __tablename__ = "evaluation_episodes"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )
    evaluation_run_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("evaluation_runs.id"),
        nullable=False,
        index=True,
    )
    game_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )
    result: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        index=True,
    )
    agent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    opponent_moves: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    move_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    decision_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    mean_confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    mean_action_gap: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    immediate_win_opportunities: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_win_successes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_block_opportunities: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    immediate_block_successes: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    unique_states_visited: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    final_board_key: Mapped[str] = mapped_column(
        String(9),
        nullable=False,
    )
    duration_ms: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
        index=True,
    )
