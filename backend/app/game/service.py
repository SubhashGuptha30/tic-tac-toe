from app.database.database import (
    SessionLocal,
    create_database_tables,
)
from app.database.repositories import AgentRepository
from app.decision.observer import (
    observe_selected_action,
)
from app.game.environment import TicTacToeEnvironment
from app.rl.models import AgentDecision, LearningUpdate
from app.rl.q_agent import QLearningAgent
from app.rl.state_encoder import StateEncoder
from app.rl.transition import PendingTransition


class GameService:
    WIN_REWARD = 1.0
    LOSS_REWARD = -1.0
    DRAW_REWARD = 0.1
    STEP_REWARD = 0.0

    def __init__(self) -> None:
        create_database_tables()
        self.environment = TicTacToeEnvironment()
        self.repository = AgentRepository(
            SessionLocal
        )

        config = self.repository.load_or_create_config()

        self.agent = QLearningAgent(
            alpha=config.alpha,
            gamma=config.gamma,
            epsilon=config.epsilon,
            epsilon_min=config.epsilon_min,
            epsilon_decay=config.epsilon_decay,
        )

        self.agent.total_decisions = config.total_decisions
        self.agent.exploration_moves = config.exploration_moves
        self.agent.exploitation_moves = config.exploitation_moves
        self.agent.total_updates = config.total_updates

        saved_q_table = self.repository.load_q_table()
        self.agent.q_table.load(saved_q_table)

        stats = self.repository.load_or_create_stats()
        self.human_wins = stats.human_wins
        self.agent_wins = stats.agent_wins
        self.draws = stats.draws
        self.episodes = stats.episodes

        self._episode_recorded = False

        self.pending_transition: PendingTransition | None = None
        self.last_decision: AgentDecision | None = None
        self.last_learning_update: LearningUpdate | None = None

    def get_state(self) -> dict:
        state = self.environment.state()
        state["stats"] = self.get_stats()
        return state

    def human_move(
        self,
        action: int,
    ) -> dict:
        if self.environment.game_over:
            raise ValueError("The game is already over.")

        if self.environment.current_player != "X":
            raise ValueError("It is not the human player's turn.")

        success = self.environment.apply_move(
            action=action,
            symbol="X",
        )

        if not success:
            raise ValueError("Illegal human move.")

        learning_update = None

        if self.pending_transition is not None:
            learning_update = self._learn_after_human_response()

        self._record_episode_if_terminal()

        return {
            "game": self.get_state(),
            "learning_update": self._serialize_learning_update(
                learning_update
            ),
            "agent_metrics": self.get_agent_metrics(),
        }

    def agent_move(self) -> dict:
        if self.environment.game_over:
            raise ValueError("The game is already over.")

        if self.environment.current_player != "O":
            raise ValueError("It is not the agent's turn.")

        board_before_action = self.environment.board.copy_state()
        state = StateEncoder.encode(board_before_action)
        legal_actions = self.environment.legal_actions()

        decision = self.agent.choose_action(
            state=state,
            legal_actions=legal_actions,
        )
        tactical_labels = observe_selected_action(
            board=self._numeric_board(
                board_before_action,
            ),
            selected_action=decision.action,
        )
        decision_event = (
            self.repository.save_decision_event(
                decision=decision,
                episode_number=self.episodes + 1,
                tactical_labels=tactical_labels,
            )
        )

        success = self.environment.apply_move(
            action=decision.action,
            symbol="O",
        )

        if not success:
            raise RuntimeError("Agent selected an invalid move.")

        self.last_decision = decision
        learning_update = None

        if self.environment.game_over:
            reward = self._terminal_reward()

            learning_update = self.agent.update(
                state=state,
                action=decision.action,
                reward=reward,
                next_state=None,
                next_legal_actions=[],
                terminal=True,
            )

            self._persist_learning_update(
                learning_update
            )
            self.last_learning_update = learning_update
            self.pending_transition = None

            self._record_episode_if_terminal()
        else:
            self.pending_transition = PendingTransition(
                state=state,
                action=decision.action,
            )

        self._persist_agent_state()

        return {
            "action": decision.action,
            "decision_event_id": (
                decision_event.id
            ),
            "decision": self._serialize_decision(decision),
            "learning_update": self._serialize_learning_update(
                learning_update
            ),
            "game": self.get_state(),
            "agent_metrics": self.get_agent_metrics(),
        }

    def _learn_after_human_response(self) -> LearningUpdate:
        pending = self.pending_transition

        if pending is None:
            raise RuntimeError("No pending transition exists.")

        if self.environment.game_over:
            reward = self._terminal_reward()

            update = self.agent.update(
                state=pending.state,
                action=pending.action,
                reward=reward,
                next_state=None,
                next_legal_actions=[],
                terminal=True,
            )
        else:
            next_board = self.environment.board.copy_state()
            next_state = StateEncoder.encode(next_board)
            next_legal_actions = self.environment.legal_actions()

            update = self.agent.update(
                state=pending.state,
                action=pending.action,
                reward=self.STEP_REWARD,
                next_state=next_state,
                next_legal_actions=next_legal_actions,
                terminal=False,
            )

        self.last_learning_update = update
        self.pending_transition = None
        self._persist_learning_update(update)
        self._persist_agent_state()

        return update

    def _persist_learning_update(
        self,
        update: LearningUpdate,
    ) -> None:
        self.repository.save_q_value(
            state=update.state,
            action=update.action,
            q_value=update.new_q,
        )
        self.repository.save_learning_update(
            update=update,
            episode_number=self.episodes + 1,
        )

    def _persist_agent_state(self) -> None:
        self.repository.save_agent_state(
            alpha=self.agent.alpha,
            gamma=self.agent.gamma,
            epsilon=self.agent.epsilon,
            epsilon_min=self.agent.epsilon_min,
            epsilon_decay=self.agent.epsilon_decay,
            total_decisions=self.agent.total_decisions,
            exploration_moves=self.agent.exploration_moves,
            exploitation_moves=self.agent.exploitation_moves,
            total_updates=self.agent.total_updates,
        )

    def _terminal_reward(self) -> float:
        winner = self.environment.winner_symbol

        if winner == "O":
            return self.WIN_REWARD

        if winner == "X":
            return self.LOSS_REWARD

        return self.DRAW_REWARD

    def reset_board(self) -> dict:
        self.environment.reset()
        self.pending_transition = None
        self.last_decision = None
        self.last_learning_update = None
        self._episode_recorded = False

        return {
            "game": self.get_state(),
            "agent_metrics": self.get_agent_metrics(),
        }

    def update_parameters(
        self,
        *,
        alpha: float,
        gamma: float,
        epsilon: float,
        epsilon_min: float,
        epsilon_decay: float,
    ) -> dict:
        self.agent.update_parameters(
            alpha=alpha,
            gamma=gamma,
            epsilon=epsilon,
            epsilon_min=epsilon_min,
            epsilon_decay=epsilon_decay,
        )
        self._persist_agent_state()

        return self.get_agent_metrics()

    def reset_brain(self) -> dict:
        self.repository.reset_brain()
        self.agent.reset()

        self.human_wins = 0
        self.agent_wins = 0
        self.draws = 0
        self.episodes = 0

        self.environment.reset()
        self.pending_transition = None
        self.last_decision = None
        self.last_learning_update = None
        self._episode_recorded = False

        self._persist_agent_state()
        self.repository.save_stats(
            human_wins=0,
            agent_wins=0,
            draws=0,
            episodes=0,
        )

        return {
            "game": self.get_state(),
            "agent_metrics": self.get_agent_metrics(),
        }

    def get_stats(self) -> dict:
        return {
            "human_wins": self.human_wins,
            "agent_wins": self.agent_wins,
            "draws": self.draws,
            "episodes": self.episodes,
        }

    def get_agent_metrics(self) -> dict:
        return {
            "alpha": self.agent.alpha,
            "gamma": self.agent.gamma,
            "epsilon": self.agent.epsilon,
            "epsilon_min": self.agent.epsilon_min,
            "epsilon_decay": self.agent.epsilon_decay,
            "total_decisions": self.agent.total_decisions,
            "exploration_moves": self.agent.exploration_moves,
            "exploitation_moves": self.agent.exploitation_moves,
            "total_updates": self.agent.total_updates,
            "states_known": self.agent.q_table.state_count(),
            "learned_state_actions": self.agent.q_table.state_action_count(),
        }

    def _record_episode_if_terminal(self) -> None:
        if not self.environment.game_over:
            return

        if self._episode_recorded:
            return

        winner = self.environment.winner_symbol

        if winner == "X":
            self.human_wins += 1
        elif winner == "O":
            self.agent_wins += 1
        else:
            self.draws += 1

        self.episodes += 1
        self.agent.decay_epsilon()

        self.repository.save_stats(
            human_wins=self.human_wins,
            agent_wins=self.agent_wins,
            draws=self.draws,
            episodes=self.episodes,
        )
        self._persist_agent_state()
        self.repository.save_episode(
            episode_number=self.episodes,
            winner=winner,
            is_draw=self.environment.board.is_draw(),
            epsilon_after=self.agent.epsilon,
            total_updates_after=self.agent.total_updates,
        )

        self._episode_recorded = True

    @staticmethod
    def _serialize_decision(
        decision: AgentDecision,
    ) -> dict:
        return {
            "state": decision.state,
            "action": decision.action,
            "decision_mode": decision.decision_mode,
            "epsilon": decision.epsilon,
            "random_sample": decision.random_sample,
            "q_values": decision.q_values,
            "legal_actions": decision.legal_actions,
            "best_action": decision.best_action,
            "best_q_value": decision.best_q_value,
            "legal_q_values": decision.legal_q_values,
            "greedy_actions": decision.greedy_actions,
            "selected_q_value": (
                decision.selected_q_value
            ),
            "second_best_action": (
                decision.second_best_action
            ),
            "second_best_q_value": (
                decision.second_best_q_value
            ),
            "action_gap": decision.action_gap,
        }

    @staticmethod
    def _serialize_learning_update(
        update: LearningUpdate | None,
    ) -> dict | None:
        if update is None:
            return None

        return {
            "state": update.state,
            "action": update.action,
            "reward": update.reward,
            "old_q": update.old_q,
            "best_future_q": update.best_future_q,
            "td_target": update.td_target,
            "td_error": update.td_error,
            "new_q": update.new_q,
            "delta_q": update.delta_q,
            "alpha": update.alpha,
            "gamma": update.gamma,
            "terminal": update.terminal,
        }

    @staticmethod
    def _numeric_board(
        board: list[str],
    ) -> list[int]:
        return [
            1
            if cell == "X"
            else 2
            if cell == "O"
            else 0
            for cell in board
        ]


game_service = GameService()
