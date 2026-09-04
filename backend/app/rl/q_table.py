from collections import defaultdict


class QTable:
    def __init__(self) -> None:
        self._table: dict[
            str,
            list[float],
        ] = defaultdict(
            lambda: [0.0] * 9
        )

    def get_values(
        self,
        state: str,
    ) -> list[float]:
        return self._table[state].copy()

    def get_value(
        self,
        state: str,
        action: int,
    ) -> float:
        return self._table[state][action]

    def set_value(
        self,
        state: str,
        action: int,
        value: float,
    ) -> None:
        self._table[state][action] = float(value)

    def best_legal_value(
        self,
        state: str,
        legal_actions: list[int],
    ) -> float:
        if not legal_actions:
            return 0.0

        values = self._table[state]

        return max(
            values[action]
            for action in legal_actions
        )

    def load(
        self,
        data: dict[str, list[float]],
    ) -> None:
        self._table.clear()

        for state, values in data.items():
            if len(values) != 9:
                continue

            self._table[state] = [
                float(value)
                for value in values
            ]

    def snapshot(self) -> dict[str, list[float]]:
        """Return an independent, serializable copy of learned values."""
        return {
            state: values.copy()
            for state, values in self._table.items()
        }

    def state_count(self) -> int:
        return len(self._table)

    def state_action_count(self) -> int:
        return sum(
            1
            for values in self._table.values()
            for value in values
            if value != 0.0
        )

    def clear(self) -> None:
        self._table.clear()
