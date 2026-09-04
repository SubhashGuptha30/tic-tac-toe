from dataclasses import dataclass


@dataclass
class AgentDecision:
    state: str
    action: int
    decision_mode: str
    epsilon: float
    random_sample: float
    q_values: list[float]
    legal_actions: list[int]
    legal_q_values: dict[int, float]
    greedy_actions: list[int]
    best_action: int | None
    best_q_value: float
    selected_q_value: float
    second_best_action: int | None
    second_best_q_value: float
    action_gap: float


@dataclass
class LearningUpdate:
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
