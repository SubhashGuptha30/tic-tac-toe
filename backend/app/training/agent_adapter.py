import math
import random

from typing import Any

from app.rl.models import LearningUpdate


class TrainingAgentAdapter:
    def __init__(
        self,
        agent: Any,
        rng: random.Random,
    ) -> None:
        self.agent = agent
        self.rng = rng
        self.dirty_state_actions: set[
            tuple[str, int]
        ] = set()
        self.dirty_update_counts: dict[
            tuple[str, int],
            int,
        ] = {}

    @property
    def epsilon(self) -> float:
        return float(self.agent.epsilon)

    def choose_action(
        self,
        state_key: str,
        legal_actions: list[int],
    ) -> int:
        if not legal_actions:
            raise ValueError(
                "Training agent cannot choose from an empty "
                "legal action set."
            )

        q_values = {
            action: self.get_q_value(state_key, action)
            for action in legal_actions
        }
        exploration_draw = self.rng.random()
        is_exploration = exploration_draw < self.epsilon

        if is_exploration:
            action = self.rng.choice(legal_actions)
            if hasattr(self.agent, "exploration_moves"):
                self.agent.exploration_moves += 1
        else:
            best_q = max(q_values.values())
            greedy_actions = [
                action
                for action, value in q_values.items()
                if math.isclose(
                    value,
                    best_q,
                    rel_tol=1e-9,
                    abs_tol=1e-12,
                )
            ]
            action = self.rng.choice(greedy_actions)
            if hasattr(self.agent, "exploitation_moves"):
                self.agent.exploitation_moves += 1

        if hasattr(self.agent, "total_decisions"):
            self.agent.total_decisions += 1

        return action

    def get_q_value(
        self,
        state_key: str,
        action: int,
    ) -> float:
        if hasattr(self.agent, "get_q_value"):
            return float(
                self.agent.get_q_value(state_key, action)
            )

        if hasattr(self.agent, "get_q"):
            return float(
                self.agent.get_q(state_key, action)
            )

        q_table = getattr(self.agent, "q_table", None)

        if q_table is None:
            raise AttributeError(
                "Agent exposes neither get_q_value(), "
                "get_q(), nor q_table."
            )

        if hasattr(q_table, "get_value"):
            return float(
                q_table.get_value(
                    state_key,
                    action,
                )
            )

        return float(
            q_table.get(
                (state_key, action),
                0.0,
            )
        )

    def update(
        self,
        state_key: str,
        action: int,
        reward: float,
        next_state_key: str,
        next_legal_actions: list[int],
        done: bool,
    ) -> LearningUpdate | None:
        update: LearningUpdate | None = None

        if hasattr(self.agent, "update"):
            update = self.agent.update(
                state=state_key,
                action=action,
                reward=reward,
                next_state=None if done else next_state_key,
                next_legal_actions=next_legal_actions,
                terminal=done,
            )
        elif hasattr(self.agent, "update_q_value"):
            self.agent.update_q_value(
                state_key,
                action,
                reward,
                next_state_key,
                next_legal_actions,
                done,
            )
        elif hasattr(self.agent, "learn"):
            self.agent.learn(
                state_key,
                action,
                reward,
                next_state_key,
                next_legal_actions,
                done,
            )
        else:
            self._manual_q_update(
                state_key=state_key,
                action=action,
                reward=reward,
                next_state_key=next_state_key,
                next_legal_actions=next_legal_actions,
                done=done,
            )

        key = (state_key, action)
        self.dirty_state_actions.add(key)
        self.dirty_update_counts[key] = (
            self.dirty_update_counts.get(key, 0)
            + 1
        )
        return update

    def q_entry_count(self) -> int:
        q_table = getattr(self.agent, "q_table", None)

        if q_table is None:
            return 0

        if hasattr(q_table, "state_action_count"):
            return int(q_table.state_action_count())

        try:
            return len(q_table)
        except TypeError:
            return 0

    def q_state_count(self) -> int:
        q_table = getattr(self.agent, "q_table", None)

        if q_table is None:
            return 0

        if hasattr(q_table, "state_count"):
            return int(q_table.state_count())

        states: set[str] = set()

        try:
            for key in q_table.keys():
                if isinstance(key, tuple) and len(key) >= 1:
                    states.add(str(key[0]))
                elif isinstance(key, str):
                    states.add(key)
        except (AttributeError, TypeError):
            return 0

        return len(states)

    def decay_epsilon(self) -> None:
        if hasattr(self.agent, "decay_epsilon"):
            self.agent.decay_epsilon()
            return

        if hasattr(self.agent, "update_epsilon"):
            self.agent.update_epsilon()
            return

        if not hasattr(self.agent, "epsilon"):
            return

        decay = None

        for name in ("epsilon_decay", "decay_rate"):
            if hasattr(self.agent, name):
                decay = float(getattr(self.agent, name))
                break

        if decay is None:
            return

        minimum = 0.0

        for name in ("epsilon_min", "min_epsilon"):
            if hasattr(self.agent, name):
                minimum = float(getattr(self.agent, name))
                break

        self.agent.epsilon = max(
            minimum,
            float(self.agent.epsilon) * decay,
        )

    def clear_dirty_state_actions(self) -> None:
        self.dirty_state_actions.clear()
        self.dirty_update_counts.clear()

    def _manual_q_update(
        self,
        *,
        state_key: str,
        action: int,
        reward: float,
        next_state_key: str,
        next_legal_actions: list[int],
        done: bool,
    ) -> None:
        q_table = getattr(self.agent, "q_table", None)

        if q_table is None:
            raise AttributeError(
                "Cannot perform Q-learning update. Agent "
                "exposes no compatible learning method and no q_table."
            )

        alpha = self._get_learning_rate()
        gamma = self._get_discount_factor()
        old_q = self.get_q_value(state_key, action)

        if done or not next_legal_actions:
            max_next_q = 0.0
        else:
            max_next_q = max(
                self.get_q_value(
                    next_state_key,
                    next_action,
                )
                for next_action in next_legal_actions
            )

        target = reward + gamma * max_next_q
        new_q = old_q + alpha * (target - old_q)

        if hasattr(q_table, "set_value"):
            q_table.set_value(
                state_key,
                action,
                new_q,
            )
        else:
            q_table[(state_key, action)] = float(new_q)

        if hasattr(self.agent, "total_updates"):
            self.agent.total_updates += 1

    def _get_learning_rate(self) -> float:
        for name in ("alpha", "learning_rate", "lr"):
            if hasattr(self.agent, name):
                return float(getattr(self.agent, name))

        raise AttributeError(
            "Could not find agent learning rate. "
            "Expected alpha, learning_rate, or lr."
        )

    def _get_discount_factor(self) -> float:
        for name in ("gamma", "discount_factor", "discount"):
            if hasattr(self.agent, name):
                return float(getattr(self.agent, name))

        raise AttributeError(
            "Could not find agent discount factor. "
            "Expected gamma, discount_factor, or discount."
        )
