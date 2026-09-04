from datetime import datetime

from pydantic import BaseModel


class DecisionQValue(BaseModel):
    action: int
    q_value: float
    is_greedy: bool
    is_selected: bool


class DecisionEventResponse(BaseModel):
    id: int
    episode_number: int | None
    decision_number: int
    state_key: str
    legal_actions: list[int]
    q_values: list[DecisionQValue]
    epsilon: float
    exploration_draw: float
    decision_mode: str
    greedy_actions: list[int]
    selected_action: int
    selected_q: float
    best_q: float
    second_best_q: float
    action_gap: float
    was_greedy_action: bool
    tie_count: int
    tactical_labels: list[str]
    explanation: str
    created_at: datetime


class DecisionEventSummary(BaseModel):
    id: int
    episode_number: int | None
    decision_number: int
    state_key: str
    epsilon: float
    exploration_draw: float
    decision_mode: str
    selected_action: int
    selected_q: float
    best_q: float
    action_gap: float
    was_greedy_action: bool
    created_at: datetime


class DecisionStatsResponse(BaseModel):
    total_decisions: int
    exploration_decisions: int
    exploitation_decisions: int
    exploration_rate: float
    exploitation_rate: float
    greedy_selection_rate: float
    mean_action_gap: float
    mean_epsilon: float
    decisions_with_ties: int
