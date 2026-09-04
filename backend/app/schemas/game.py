from typing import Optional

from pydantic import BaseModel, Field


class HumanMoveRequest(BaseModel):
    action: int = Field(ge=0, le=8)


class GameStats(BaseModel):
    human_wins: int
    agent_wins: int
    draws: int
    episodes: int


class GameStateResponse(BaseModel):
    board: list[str]
    current_player: str
    game_over: bool
    winner: Optional[str]
    winning_line: Optional[list[int]]
    is_draw: bool
    legal_actions: list[int]
    stats: GameStats


class AgentMetrics(BaseModel):
    alpha: float
    gamma: float
    epsilon: float
    epsilon_min: float
    epsilon_decay: float
    total_decisions: int
    exploration_moves: int
    exploitation_moves: int
    total_updates: int
    states_known: int
    learned_state_actions: int


class DecisionData(BaseModel):
    state: str
    action: int
    decision_mode: str
    epsilon: float
    random_sample: float
    q_values: list[float]
    legal_actions: list[int]
    legal_q_values: dict[int, float]
    greedy_actions: list[int]
    best_action: Optional[int]
    best_q_value: float
    selected_q_value: float
    second_best_action: Optional[int]
    second_best_q_value: float
    action_gap: float


class LearningUpdateData(BaseModel):
    state: str
    action: int
    reward: float
    old_q: float
    best_future_q: float
    td_target: float
    td_error: float
    new_q: float
    delta_q: float
    alpha: float
    gamma: float
    terminal: bool


class HumanMoveResponse(BaseModel):
    game: GameStateResponse
    learning_update: Optional[LearningUpdateData]
    agent_metrics: AgentMetrics


class AgentMoveResponse(BaseModel):
    action: int
    decision_event_id: int
    decision: DecisionData
    learning_update: Optional[LearningUpdateData]
    game: GameStateResponse
    agent_metrics: AgentMetrics


class ResetResponse(BaseModel):
    game: GameStateResponse
    agent_metrics: AgentMetrics


class AgentParameterUpdate(BaseModel):
    alpha: float = Field(
        ge=0.0,
        le=1.0,
    )
    gamma: float = Field(
        ge=0.0,
        le=1.0,
    )
    epsilon: float = Field(
        ge=0.0,
        le=1.0,
    )
    epsilon_min: float = Field(
        ge=0.0,
        le=1.0,
    )
    epsilon_decay: float = Field(
        ge=0.0,
        le=1.0,
    )
