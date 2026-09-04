import math
import random

from app.rl.models import (
    AgentDecision,
    LearningUpdate,
)
from app.rl.q_table import QTable


class QLearningAgent:
    def __init__(
        self,
        alpha: float = 0.20,
        gamma: float = 0.95,
        epsilon: float = 0.90,
        epsilon_min: float = 0.05,
        epsilon_decay: float = 0.995,
    ) -> None:
        self.default_alpha = 0.20
        self.default_gamma = 0.95
        self.default_epsilon = 0.90
        self.default_epsilon_min = 0.05
        self.default_epsilon_decay = 0.995

        self.alpha = alpha
        self.gamma = gamma

        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

        self.q_table = QTable()

        self.total_decisions = 0
        self.exploration_moves = 0
        self.exploitation_moves = 0
        self.total_updates = 0

    def choose_action(
        self,
        state: str,
        legal_actions: list[int],
    ) -> AgentDecision:
        if not legal_actions:
            raise ValueError(
                "No legal actions are available."
            )

        q_values = self.q_table.get_values(state)
        random_sample = random.random()

        legal_q_values = {
            action: q_values[action]
            for action in legal_actions
        }
        max_legal_q = max(legal_q_values.values())

        best_actions = [
            action
            for action, value in legal_q_values.items()
            if math.isclose(
                value,
                max_legal_q,
                rel_tol=1e-9,
                abs_tol=1e-12,
            )
        ]
        best_action = random.choice(best_actions)

        sorted_legal_values = sorted(
            legal_q_values.items(),
            key=lambda item: (
                -item[1],
                item[0],
            ),
        )
        distinct_q_values = sorted(
            {
                float(value)
                for value in legal_q_values.values()
            },
            reverse=True,
        )
        second_best_q_value = (
            distinct_q_values[1]
            if len(distinct_q_values) >= 2
            else max_legal_q
        )
        second_best_action = next(
            (
                action
                for action, value in sorted_legal_values
                if not math.isclose(
                    value,
                    max_legal_q,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                )
            ),
            None,
        )
        action_gap = max(
            0.0,
            max_legal_q - second_best_q_value,
        )

        if random_sample < self.epsilon:
            action = random.choice(legal_actions)
            decision_mode = "exploration"
            self.exploration_moves += 1
        else:
            action = best_action
            decision_mode = "exploitation"
            self.exploitation_moves += 1

        self.total_decisions += 1

        return AgentDecision(
            state=state,
            action=action,
            decision_mode=decision_mode,
            epsilon=self.epsilon,
            random_sample=random_sample,
            q_values=q_values,
            legal_actions=legal_actions.copy(),
            legal_q_values={
                action: float(value)
                for action, value in legal_q_values.items()
            },
            greedy_actions=best_actions.copy(),
            best_action=best_action,
            best_q_value=max_legal_q,
            selected_q_value=float(
                legal_q_values[action],
            ),
            second_best_action=second_best_action,
            second_best_q_value=float(
                second_best_q_value,
            ),
            action_gap=float(action_gap),
        )

    def update(
        self,
        state: str,
        action: int,
        reward: float,
        next_state: str | None,
        next_legal_actions: list[int],
        terminal: bool,
    ) -> LearningUpdate:
        old_q = self.q_table.get_value(
            state=state,
            action=action,
        )

        if terminal or next_state is None:
            best_future_q = 0.0
        else:
            best_future_q = self.q_table.best_legal_value(
                state=next_state,
                legal_actions=next_legal_actions,
            )

        td_target = reward + self.gamma * best_future_q
        td_error = td_target - old_q
        new_q = old_q + self.alpha * td_error

        self.q_table.set_value(
            state=state,
            action=action,
            value=new_q,
        )

        self.total_updates += 1

        return LearningUpdate(
            state=state,
            action=action,
            reward=reward,
            old_q=old_q,
            best_future_q=best_future_q,
            td_target=td_target,
            td_error=td_error,
            new_q=new_q,
            delta_q=new_q - old_q,
            alpha=self.alpha,
            gamma=self.gamma,
            terminal=terminal,
        )

    def decay_epsilon(self) -> None:
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay,
        )

    def update_parameters(
        self,
        *,
        alpha: float,
        gamma: float,
        epsilon: float,
        epsilon_min: float,
        epsilon_decay: float,
    ) -> None:
        if not 0.0 <= alpha <= 1.0:
            raise ValueError("Alpha must be between 0 and 1.")

        if not 0.0 <= gamma <= 1.0:
            raise ValueError("Gamma must be between 0 and 1.")

        if not 0.0 <= epsilon <= 1.0:
            raise ValueError("Epsilon must be between 0 and 1.")

        if not 0.0 <= epsilon_min <= 1.0:
            raise ValueError(
                "Epsilon minimum must be between 0 and 1."
            )

        if not 0.0 <= epsilon_decay <= 1.0:
            raise ValueError(
                "Epsilon decay must be between 0 and 1."
            )

        if epsilon < epsilon_min:
            raise ValueError(
                "Epsilon cannot be lower than epsilon minimum."
            )

        self.alpha = alpha
        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay

    def reset(self) -> None:
        self.q_table.clear()

        self.alpha = self.default_alpha
        self.gamma = self.default_gamma
        self.epsilon = self.default_epsilon
        self.epsilon_min = self.default_epsilon_min
        self.epsilon_decay = self.default_epsilon_decay

        self.total_decisions = 0
        self.exploration_moves = 0
        self.exploitation_moves = 0
        self.total_updates = 0
