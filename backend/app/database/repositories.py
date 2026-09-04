from sqlalchemy import delete, select

from app.decision.capture import (
    get_next_decision_number,
    make_decision_event_model,
)
from app.database.models import (
    AgentConfigModel,
    DecisionEventModel,
    EpisodeModel,
    ExperimentStatsModel,
    LearningUpdateModel,
    QValueModel,
)
from app.rl.models import (
    AgentDecision,
    LearningUpdate,
)


class AgentRepository:
    def __init__(
        self,
        session_factory,
    ) -> None:
        self.session_factory = session_factory

    def load_q_table(
        self,
    ) -> dict[str, list[float]]:
        with self.session_factory() as session:
            rows = session.scalars(
                select(QValueModel)
            ).all()

            table: dict[str, list[float]] = {}

            for row in rows:
                if row.state_key not in table:
                    table[row.state_key] = [0.0] * 9

                table[row.state_key][
                    row.action
                ] = row.q_value

            return table

    def save_q_value(
        self,
        state: str,
        action: int,
        q_value: float,
    ) -> None:
        with self.session_factory() as session:
            row = session.scalar(
                select(QValueModel).where(
                    QValueModel.state_key == state,
                    QValueModel.action == action,
                )
            )

            if row is None:
                row = QValueModel(
                    state_key=state,
                    action=action,
                    q_value=q_value,
                    update_count=1,
                )
                session.add(row)
            else:
                row.q_value = q_value
                row.update_count += 1

            session.commit()

    def load_or_create_config(
        self,
    ) -> AgentConfigModel:
        with self.session_factory() as session:
            config = session.get(
                AgentConfigModel,
                1,
            )

            if config is None:
                config = AgentConfigModel(id=1)
                session.add(config)
                session.commit()
                session.refresh(config)

            session.expunge(config)
            return config

    def save_agent_state(
        self,
        *,
        alpha: float,
        gamma: float,
        epsilon: float,
        epsilon_min: float,
        epsilon_decay: float,
        total_decisions: int,
        exploration_moves: int,
        exploitation_moves: int,
        total_updates: int,
    ) -> None:
        with self.session_factory() as session:
            config = session.get(
                AgentConfigModel,
                1,
            )

            if config is None:
                config = AgentConfigModel(id=1)
                session.add(config)

            config.alpha = alpha
            config.gamma = gamma
            config.epsilon = epsilon
            config.epsilon_min = epsilon_min
            config.epsilon_decay = epsilon_decay
            config.total_decisions = total_decisions
            config.exploration_moves = exploration_moves
            config.exploitation_moves = exploitation_moves
            config.total_updates = total_updates

            session.commit()

    def load_or_create_stats(
        self,
    ) -> ExperimentStatsModel:
        with self.session_factory() as session:
            stats = session.get(
                ExperimentStatsModel,
                1,
            )

            if stats is None:
                stats = ExperimentStatsModel(id=1)
                session.add(stats)
                session.commit()
                session.refresh(stats)

            session.expunge(stats)
            return stats

    def save_stats(
        self,
        *,
        human_wins: int,
        agent_wins: int,
        draws: int,
        episodes: int,
    ) -> None:
        with self.session_factory() as session:
            stats = session.get(
                ExperimentStatsModel,
                1,
            )

            if stats is None:
                stats = ExperimentStatsModel(id=1)
                session.add(stats)

            stats.human_wins = human_wins
            stats.agent_wins = agent_wins
            stats.draws = draws
            stats.episodes = episodes

            session.commit()

    def save_learning_update(
        self,
        update: LearningUpdate,
        episode_number: int,
    ) -> None:
        with self.session_factory() as session:
            row = LearningUpdateModel(
                episode_number=episode_number,
                state_key=update.state,
                action=update.action,
                reward=update.reward,
                old_q=update.old_q,
                best_future_q=update.best_future_q,
                td_target=update.td_target,
                td_error=update.td_error,
                new_q=update.new_q,
                delta_q=update.delta_q,
                alpha=update.alpha,
                gamma=update.gamma,
                terminal=update.terminal,
            )

            session.add(row)
            session.commit()

    def save_decision_event(
        self,
        *,
        decision: AgentDecision,
        episode_number: int | None,
        tactical_labels: list[str],
    ) -> DecisionEventModel:
        with self.session_factory() as session:
            decision_number = get_next_decision_number(
                session,
            )
            row = make_decision_event_model(
                decision=decision,
                episode_number=episode_number,
                decision_number=decision_number,
                tactical_labels=tactical_labels,
            )

            session.add(row)
            session.commit()
            session.refresh(row)
            session.expunge(row)

            return row

    def save_episode(
        self,
        *,
        episode_number: int,
        winner: str | None,
        is_draw: bool,
        epsilon_after: float,
        total_updates_after: int,
    ) -> None:
        with self.session_factory() as session:
            row = EpisodeModel(
                episode_number=episode_number,
                winner=winner,
                is_draw=is_draw,
                epsilon_after=epsilon_after,
                total_updates_after=total_updates_after,
            )

            session.add(row)
            session.commit()

    def reset_brain(self) -> None:
        with self.session_factory() as session:
            session.execute(delete(QValueModel))
            session.execute(delete(DecisionEventModel))
            session.execute(delete(LearningUpdateModel))
            session.execute(delete(EpisodeModel))
            session.execute(delete(AgentConfigModel))
            session.execute(delete(ExperimentStatsModel))
            session.commit()
