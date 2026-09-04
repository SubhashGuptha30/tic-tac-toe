import random


class RandomAgent:
    """
    Temporary Phase 2 agent.

    This is not the final RL agent.
    """

    def choose_action(self, legal_actions: list[int]) -> int:
        if not legal_actions:
            raise ValueError("No legal actions are available.")

        return random.choice(legal_actions)
