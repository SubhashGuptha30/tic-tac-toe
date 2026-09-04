from datetime import datetime

from pydantic import BaseModel


class BoardCell(BaseModel):
    index: int
    value: int
    symbol: str | None


class ActionValue(BaseModel):
    action: int
    q_value: float
    rank: int
    is_legal: bool
    is_best: bool
    position_type: str
    action_gap_from_best: float
    is_immediate_win: bool
    is_immediate_block: bool
    is_fork_creation: bool
    is_fork_prevention: bool


class PolicyConfidenceResponse(BaseModel):
    best_action: int | None
    best_q: float
    second_best_q: float
    action_gap: float
    normalized_confidence: float
    tied_best_actions: list[int]


class TacticalEvidence(BaseModel):
    immediate_wins: list[int]
    immediate_blocks: list[int]
    fork_creations: list[int]
    fork_preventions: list[int]


class StateInspection(BaseModel):
    state_key: str
    board: list[BoardCell]
    legal_actions: list[int]
    action_values: list[ActionValue]
    policy_confidence: PolicyConfidenceResponse
    tactical_evidence: TacticalEvidence
    q_rows_found: int


class StateSummary(BaseModel):
    state_key: str
    stored_actions: int
    legal_actions: int
    best_action: int | None
    best_q: float
    action_gap: float
    visit_updates: int


class StrategyMetric(BaseModel):
    key: str
    label: str
    opportunities: int
    aligned_states: float
    evidence_rate: float
    interpretation: str


class PositionPreferenceMetric(BaseModel):
    key: str
    label: str
    eligible_states: int
    preference_mass: float
    preference_rate: float
    interpretation: str


class StrategyOverview(BaseModel):
    analyzed_states: int
    states_with_legal_actions: int
    states_with_nonzero_q: int
    states_with_unique_best_action: int
    mean_action_gap: float
    mean_normalized_confidence: float
    immediate_win: StrategyMetric
    immediate_block: StrategyMetric
    fork_creation: StrategyMetric
    fork_prevention: StrategyMetric
    center_preference: PositionPreferenceMetric
    corner_preference: PositionPreferenceMetric
    edge_preference: PositionPreferenceMetric


class StrategyEvidenceItem(BaseModel):
    state_key: str
    strategy: str
    opportunity_actions: list[int]
    greedy_actions: list[int]
    alignment_score: float
    best_action: int | None
    best_q: float
    action_gap: float


class EpisodeSummary(BaseModel):
    episode_number: int
    winner: str | None
    is_draw: bool
    outcome: str
    epsilon_after: float
    total_updates_after: int
    learning_event_count: int
    created_at: datetime


class EpisodeLearningEvent(BaseModel):
    id: int
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
    created_at: datetime


class EpisodeInspection(BaseModel):
    episode_number: int
    winner: str | None
    is_draw: bool
    outcome: str
    epsilon_after: float
    total_updates_after: int
    created_at: datetime
    learning_events: list[EpisodeLearningEvent]


class DecisionInspection(BaseModel):
    state_key: str
    best_action: int | None
    greedy_actions: list[int]
    best_q: float
    second_best_q: float
    action_gap: float
    normalized_confidence: float
    immediate_win_alignment: float
    immediate_block_alignment: float
    fork_creation_alignment: float
    fork_prevention_alignment: float
    tactical_labels: list[str]
