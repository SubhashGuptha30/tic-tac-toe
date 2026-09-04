from datetime import datetime

from pydantic import BaseModel, Field


class EvaluationRunCreate(BaseModel):
    games: int = Field(
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
    snapshot_id: int | None = Field(
        default=None,
        ge=1,
    )


class PolicySnapshotResponse(BaseModel):
    id: int
    source: str
    q_table_hash: str
    q_states: int
    q_entries: int
    alpha: float
    gamma: float
    tie_breaking_policy: str
    created_at: datetime


class EvaluationRunResponse(BaseModel):
    id: int
    snapshot_id: int
    status: str
    opponent_type: str
    tactical_probability: float | None
    requested_games: int
    completed_games: int
    agent_wins: int
    opponent_wins: int
    draws: int
    agent_win_rate: float
    opponent_win_rate: float
    draw_rate: float
    total_moves: int
    average_moves: float
    total_agent_moves: int
    total_opponent_moves: int
    total_decisions: int
    greedy_decision_rate: float
    unique_states_visited: int
    average_decision_confidence: float
    average_action_gap: float
    immediate_win_opportunities: int
    immediate_win_successes: int
    immediate_win_conversion_rate: float
    immediate_block_opportunities: int
    immediate_block_successes: int
    immediate_block_success_rate: float
    seed: int | None
    tie_breaking_policy: str
    duration_seconds: float | None
    games_per_second: float | None
    error_message: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


class EvaluationEpisodeResponse(BaseModel):
    id: int
    evaluation_run_id: int
    game_index: int
    result: str
    agent_moves: int
    opponent_moves: int
    move_count: int
    decision_count: int
    mean_confidence: float
    mean_action_gap: float
    immediate_win_opportunities: int
    immediate_win_successes: int
    immediate_block_opportunities: int
    immediate_block_successes: int
    unique_states_visited: int
    final_board_key: str
    duration_ms: float
    created_at: datetime


class EvaluationComparisonRow(BaseModel):
    opponent_type: str
    evaluation_run_id: int | None
    games: int
    agent_win_rate: float
    draw_rate: float
    opponent_win_rate: float
    average_moves: float
    average_decision_confidence: float
    is_available: bool


class EvaluationComparisonResponse(BaseModel):
    snapshot: PolicySnapshotResponse
    rows: list[EvaluationComparisonRow]


class EvaluationEngineHealthResponse(BaseModel):
    engine_ready: bool
    active_run_id: int | None
    supported_opponents: list[str]
    tie_breaking_policy: str
    message: str
