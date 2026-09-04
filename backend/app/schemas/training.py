from datetime import datetime

from pydantic import BaseModel, Field


class TrainingRunCreate(BaseModel):
    episodes: int = Field(
        default=1000,
        ge=1,
        le=100000,
    )
    opponent_type: str = Field(
        default="random",
    )
    tactical_probability: float = Field(
        default=0.70,
        ge=0.0,
        le=1.0,
    )
    seed: int | None = None


class TrainingRunResponse(BaseModel):
    id: int
    status: str
    opponent_type: str
    tactical_probability: float | None
    requested_episodes: int
    completed_episodes: int
    agent_wins: int
    opponent_wins: int
    draws: int
    total_agent_moves: int
    total_opponent_moves: int
    epsilon_start: float
    epsilon_end: float | None
    q_states_start: int
    q_states_end: int | None
    q_entries_start: int
    q_entries_end: int | None
    cumulative_reward: float
    mean_reward: float
    duration_seconds: float | None
    episodes_per_second: float | None
    seed: int | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class TrainingEpisodeResponse(BaseModel):
    id: int
    training_run_id: int
    episode_index: int
    result: str
    reward: float
    agent_moves: int
    opponent_moves: int
    epsilon_before: float
    epsilon_after: float
    final_board_key: str
    move_count: int
    duration_ms: float
    created_at: datetime


class TrainingRunStatsResponse(BaseModel):
    run_id: int
    completed_episodes: int
    requested_episodes: int
    progress: float
    agent_wins: int
    opponent_wins: int
    draws: int
    agent_win_rate: float
    opponent_win_rate: float
    draw_rate: float
    cumulative_reward: float
    mean_reward: float
    epsilon_start: float
    current_epsilon: float
    q_states_start: int
    current_q_states: int
    q_entries_start: int
    current_q_entries: int
    duration_seconds: float | None
    episodes_per_second: float | None


class TrainingEngineHealthResponse(BaseModel):
    engine_ready: bool
    supported_opponents: list[str]
    active_run_id: int | None
    agent_available: bool
    message: str
