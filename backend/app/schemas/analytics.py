from datetime import datetime

from pydantic import BaseModel


class OutcomeCounts(BaseModel):
    human_wins: int
    agent_wins: int
    draws: int
    total_episodes: int


class WinRates(BaseModel):
    human_win_rate: float
    agent_win_rate: float
    draw_rate: float


class QValueHealth(BaseModel):
    total_persisted_actions: int
    positive_q_values: int
    negative_q_values: int
    zero_q_values: int
    min_q_value: float
    max_q_value: float
    mean_q_value: float
    mean_absolute_q: float


class TDErrorHealth(BaseModel):
    total_updates: int
    mean_td_error: float
    mean_absolute_td_error: float
    min_td_error: float
    max_td_error: float
    recent_mean_absolute_td_error: float


class AnalyticsOverview(BaseModel):
    outcomes: OutcomeCounts
    win_rates: WinRates
    known_states: int
    persisted_state_actions: int
    exploration_moves: int
    exploitation_moves: int
    exploration_rate: float
    exploitation_rate: float
    current_epsilon: float
    q_value_health: QValueHealth
    td_error_health: TDErrorHealth


class LearningCurvePoint(BaseModel):
    episode: int
    agent_win_rate: float
    human_win_rate: float
    draw_rate: float
    rolling_agent_win_rate: float
    rolling_human_win_rate: float
    rolling_draw_rate: float


class OutcomeTimelinePoint(BaseModel):
    episode: int
    outcome: str
    winner: str | None
    is_draw: bool
    epsilon_after: float
    total_updates_after: int
    created_at: datetime


class TDErrorPoint(BaseModel):
    update_id: int
    episode: int
    td_error: float
    absolute_td_error: float
    rolling_mean_absolute_td_error: float
    terminal: bool
    created_at: datetime


class RewardPoint(BaseModel):
    update_id: int
    episode: int
    reward: float
    cumulative_reward: float
    terminal: bool
    created_at: datetime


class EpsilonPoint(BaseModel):
    episode: int
    epsilon: float
    created_at: datetime


class LearningUpdateDetail(BaseModel):
    id: int
    episode: int
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


class AnalyticsDataset(BaseModel):
    learning_curve: list[
        LearningCurvePoint
    ]
    outcome_timeline: list[
        OutcomeTimelinePoint
    ]
    td_error_curve: list[
        TDErrorPoint
    ]
    reward_trajectory: list[
        RewardPoint
    ]
    epsilon_curve: list[
        EpsilonPoint
    ]
