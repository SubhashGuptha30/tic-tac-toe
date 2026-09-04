from dataclasses import dataclass


@dataclass
class PendingTransition:
    """
    Stores the agent's previous decision while waiting for
    the human opponent's response.
    """

    state: str
    action: int
