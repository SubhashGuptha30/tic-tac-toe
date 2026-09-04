from dataclasses import dataclass


@dataclass(frozen=True)
class TrainingRewards:
    win: float = 1.0
    loss: float = -1.0
    draw: float = 0.1
    step: float = 0.0


DEFAULT_TRAINING_REWARDS = TrainingRewards()
