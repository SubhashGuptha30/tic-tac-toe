from math import fsum

from sqlalchemy import select

from app.database.database import (
    SessionLocal,
)
from app.database.models import (
    AgentConfigModel,
    EpisodeModel,
    LearningUpdateModel,
    QValueModel,
)


class AnalyticsService:
    def __init__(
        self,
        session_factory=SessionLocal,
    ) -> None:
        self.session_factory = (
            session_factory
        )

    # ---------------------------------------------
    # OVERVIEW
    # ---------------------------------------------

    def get_overview(self) -> dict:
        with self.session_factory() as session:
            episodes = session.scalars(
                select(EpisodeModel)
                .order_by(EpisodeModel.id.asc())
            ).all()

            updates = session.scalars(
                select(LearningUpdateModel)
                .order_by(
                    LearningUpdateModel.id.asc()
                )
            ).all()

            q_rows = session.scalars(
                select(QValueModel)
            ).all()

            config = session.get(
                AgentConfigModel,
                1,
            )

            total_episodes = len(episodes)

            human_wins = sum(
                1
                for episode in episodes
                if episode.winner == "X"
            )

            agent_wins = sum(
                1
                for episode in episodes
                if episode.winner == "O"
            )

            draws = sum(
                1
                for episode in episodes
                if episode.is_draw
            )

            known_states = len({
                row.state_key
                for row in q_rows
            })

            q_values = [
                float(row.q_value)
                for row in q_rows
            ]

            td_errors = [
                float(update.td_error)
                for update in updates
            ]

            recent_td_errors = td_errors[-50:]

            exploration_moves = (
                config.exploration_moves
                if config is not None
                else 0
            )

            exploitation_moves = (
                config.exploitation_moves
                if config is not None
                else 0
            )

            total_decisions = (
                exploration_moves
                + exploitation_moves
            )

            return {
                "outcomes": {
                    "human_wins": human_wins,
                    "agent_wins": agent_wins,
                    "draws": draws,
                    "total_episodes": (
                        total_episodes
                    ),
                },
                "win_rates": {
                    "human_win_rate": (
                        self._safe_ratio(
                            human_wins,
                            total_episodes,
                        )
                    ),
                    "agent_win_rate": (
                        self._safe_ratio(
                            agent_wins,
                            total_episodes,
                        )
                    ),
                    "draw_rate": (
                        self._safe_ratio(
                            draws,
                            total_episodes,
                        )
                    ),
                },
                "known_states": known_states,
                "persisted_state_actions": (
                    len(q_rows)
                ),
                "exploration_moves": (
                    exploration_moves
                ),
                "exploitation_moves": (
                    exploitation_moves
                ),
                "exploration_rate": (
                    self._safe_ratio(
                        exploration_moves,
                        total_decisions,
                    )
                ),
                "exploitation_rate": (
                    self._safe_ratio(
                        exploitation_moves,
                        total_decisions,
                    )
                ),
                "current_epsilon": (
                    float(config.epsilon)
                    if config is not None
                    else 0.0
                ),
                "q_value_health": (
                    self._q_value_health(
                        q_values
                    )
                ),
                "td_error_health": (
                    self._td_error_health(
                        td_errors,
                        recent_td_errors,
                    )
                ),
            }

    # ---------------------------------------------
    # LEARNING CURVE
    # ---------------------------------------------

    def get_learning_curve(
        self,
        rolling_window: int = 10,
    ) -> list[dict]:
        rolling_window = max(
            1,
            rolling_window,
        )

        with self.session_factory() as session:
            episodes = session.scalars(
                select(EpisodeModel)
                .order_by(
                    EpisodeModel.episode_number.asc(),
                    EpisodeModel.id.asc(),
                )
            ).all()

        result: list[dict] = []
        cumulative_agent = 0
        cumulative_human = 0
        cumulative_draw = 0
        outcomes: list[str] = []

        for index, episode in enumerate(
            episodes,
            start=1,
        ):
            outcome = self._episode_outcome(
                episode
            )
            outcomes.append(outcome)

            if outcome == "agent":
                cumulative_agent += 1
            elif outcome == "human":
                cumulative_human += 1
            else:
                cumulative_draw += 1

            window = outcomes[
                max(
                    0,
                    len(outcomes)
                    - rolling_window,
                ) :
            ]

            result.append(
                {
                    "episode": (
                        episode.episode_number
                    ),
                    "agent_win_rate": (
                        cumulative_agent / index
                    ),
                    "human_win_rate": (
                        cumulative_human / index
                    ),
                    "draw_rate": (
                        cumulative_draw / index
                    ),
                    "rolling_agent_win_rate": (
                        window.count("agent")
                        / len(window)
                    ),
                    "rolling_human_win_rate": (
                        window.count("human")
                        / len(window)
                    ),
                    "rolling_draw_rate": (
                        window.count("draw")
                        / len(window)
                    ),
                }
            )

        return result

    # ---------------------------------------------
    # OUTCOME TIMELINE
    # ---------------------------------------------

    def get_outcome_timeline(
        self,
        limit: int = 200,
    ) -> list[dict]:
        with self.session_factory() as session:
            episodes = session.scalars(
                select(EpisodeModel)
                .order_by(
                    EpisodeModel.episode_number.desc(),
                    EpisodeModel.id.desc(),
                )
                .limit(limit)
            ).all()

        episodes = list(reversed(episodes))

        return [
            {
                "episode": (
                    episode.episode_number
                ),
                "outcome": (
                    self._episode_outcome(
                        episode
                    )
                ),
                "winner": episode.winner,
                "is_draw": episode.is_draw,
                "epsilon_after": float(
                    episode.epsilon_after
                ),
                "total_updates_after": (
                    episode.total_updates_after
                ),
                "created_at": episode.created_at,
            }
            for episode in episodes
        ]

    # ---------------------------------------------
    # TD ERROR CURVE
    # ---------------------------------------------

    def get_td_error_curve(
        self,
        limit: int = 500,
        rolling_window: int = 20,
    ) -> list[dict]:
        rolling_window = max(
            1,
            rolling_window,
        )

        with self.session_factory() as session:
            updates = session.scalars(
                select(LearningUpdateModel)
                .order_by(
                    LearningUpdateModel.id.desc()
                )
                .limit(limit)
            ).all()

        updates = list(reversed(updates))
        absolute_history: list[float] = []
        result: list[dict] = []

        for update in updates:
            absolute_error = abs(
                float(update.td_error)
            )
            absolute_history.append(
                absolute_error
            )

            window = absolute_history[
                max(
                    0,
                    len(absolute_history)
                    - rolling_window,
                ) :
            ]

            result.append(
                {
                    "update_id": update.id,
                    "episode": (
                        update.episode_number
                    ),
                    "td_error": float(
                        update.td_error
                    ),
                    "absolute_td_error": (
                        absolute_error
                    ),
                    "rolling_mean_absolute_td_error": (
                        fsum(window)
                        / len(window)
                    ),
                    "terminal": update.terminal,
                    "created_at": (
                        update.created_at
                    ),
                }
            )

        return result

    # ---------------------------------------------
    # REWARD TRAJECTORY
    # ---------------------------------------------

    def get_reward_trajectory(
        self,
        limit: int = 500,
    ) -> list[dict]:
        with self.session_factory() as session:
            updates = session.scalars(
                select(LearningUpdateModel)
                .order_by(
                    LearningUpdateModel.id.desc()
                )
                .limit(limit)
            ).all()

        updates = list(reversed(updates))
        cumulative_reward = 0.0
        result: list[dict] = []

        for update in updates:
            reward = float(update.reward)
            cumulative_reward += reward

            result.append(
                {
                    "update_id": update.id,
                    "episode": (
                        update.episode_number
                    ),
                    "reward": reward,
                    "cumulative_reward": (
                        cumulative_reward
                    ),
                    "terminal": update.terminal,
                    "created_at": (
                        update.created_at
                    ),
                }
            )

        return result

    # ---------------------------------------------
    # EPSILON CURVE
    # ---------------------------------------------

    def get_epsilon_curve(
        self,
        limit: int = 500,
    ) -> list[dict]:
        with self.session_factory() as session:
            episodes = session.scalars(
                select(EpisodeModel)
                .order_by(
                    EpisodeModel.episode_number.desc(),
                    EpisodeModel.id.desc(),
                )
                .limit(limit)
            ).all()

        episodes = list(reversed(episodes))

        return [
            {
                "episode": (
                    episode.episode_number
                ),
                "epsilon": float(
                    episode.epsilon_after
                ),
                "created_at": (
                    episode.created_at
                ),
            }
            for episode in episodes
        ]

    # ---------------------------------------------
    # RECENT LEARNING EVENTS
    # ---------------------------------------------

    def get_learning_updates(
        self,
        limit: int = 100,
    ) -> list[dict]:
        with self.session_factory() as session:
            updates = session.scalars(
                select(LearningUpdateModel)
                .order_by(
                    LearningUpdateModel.id.desc()
                )
                .limit(limit)
            ).all()

        return [
            {
                "id": update.id,
                "episode": (
                    update.episode_number
                ),
                "state": update.state_key,
                "action": update.action,
                "reward": float(
                    update.reward
                ),
                "old_q": float(
                    update.old_q
                ),
                "best_future_q": float(
                    update.best_future_q
                ),
                "td_target": float(
                    update.td_target
                ),
                "td_error": float(
                    update.td_error
                ),
                "new_q": float(
                    update.new_q
                ),
                "delta_q": float(
                    update.delta_q
                ),
                "alpha": float(
                    update.alpha
                ),
                "gamma": float(
                    update.gamma
                ),
                "terminal": update.terminal,
                "created_at": (
                    update.created_at
                ),
            }
            for update in updates
        ]

    # ---------------------------------------------
    # COMBINED DATASET
    # ---------------------------------------------

    def get_dataset(
        self,
        rolling_window: int = 10,
    ) -> dict:
        return {
            "learning_curve": (
                self.get_learning_curve(
                    rolling_window=rolling_window
                )
            ),
            "outcome_timeline": (
                self.get_outcome_timeline()
            ),
            "td_error_curve": (
                self.get_td_error_curve()
            ),
            "reward_trajectory": (
                self.get_reward_trajectory()
            ),
            "epsilon_curve": (
                self.get_epsilon_curve()
            ),
        }

    # ---------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------

    @staticmethod
    def _episode_outcome(
        episode: EpisodeModel,
    ) -> str:
        if episode.is_draw:
            return "draw"

        if episode.winner == "O":
            return "agent"

        return "human"

    @staticmethod
    def _safe_ratio(
        numerator: int,
        denominator: int,
    ) -> float:
        if denominator == 0:
            return 0.0

        return numerator / denominator

    @staticmethod
    def _q_value_health(
        values: list[float],
    ) -> dict:
        if not values:
            return {
                "total_persisted_actions": 0,
                "positive_q_values": 0,
                "negative_q_values": 0,
                "zero_q_values": 0,
                "min_q_value": 0.0,
                "max_q_value": 0.0,
                "mean_q_value": 0.0,
                "mean_absolute_q": 0.0,
            }

        return {
            "total_persisted_actions": (
                len(values)
            ),
            "positive_q_values": sum(
                value > 0.0
                for value in values
            ),
            "negative_q_values": sum(
                value < 0.0
                for value in values
            ),
            "zero_q_values": sum(
                value == 0.0
                for value in values
            ),
            "min_q_value": min(values),
            "max_q_value": max(values),
            "mean_q_value": (
                fsum(values)
                / len(values)
            ),
            "mean_absolute_q": (
                fsum(
                    abs(value)
                    for value in values
                )
                / len(values)
            ),
        }

    @staticmethod
    def _td_error_health(
        errors: list[float],
        recent_errors: list[float],
    ) -> dict:
        if not errors:
            return {
                "total_updates": 0,
                "mean_td_error": 0.0,
                "mean_absolute_td_error": 0.0,
                "min_td_error": 0.0,
                "max_td_error": 0.0,
                "recent_mean_absolute_td_error": 0.0,
            }

        mean_absolute = (
            fsum(
                abs(error)
                for error in errors
            )
            / len(errors)
        )

        recent_mean_absolute = (
            fsum(
                abs(error)
                for error in recent_errors
            )
            / len(recent_errors)
            if recent_errors
            else 0.0
        )

        return {
            "total_updates": len(errors),
            "mean_td_error": (
                fsum(errors)
                / len(errors)
            ),
            "mean_absolute_td_error": (
                mean_absolute
            ),
            "min_td_error": min(errors),
            "max_td_error": max(errors),
            "recent_mean_absolute_td_error": (
                recent_mean_absolute
            ),
        }


analytics_service = AnalyticsService()
