import json

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.models import DecisionEventModel
from app.rl.models import AgentDecision


def build_decision_explanation(
    *,
    decision_mode: str,
    epsilon: float,
    exploration_draw: float,
    selected_action: int,
    selected_q: float,
    best_q: float,
    action_gap: float,
    greedy_actions: list[int],
) -> str:
    if decision_mode == "exploration":
        if selected_action in greedy_actions:
            return (
                "The exploration gate activated because "
                f"the random draw {exploration_draw:.4f} "
                f"was below epsilon {epsilon:.4f}. "
                f"Action {selected_action} was sampled from "
                "the legal action set. It also happened to "
                "belong to the current greedy action set."
            )

        return (
            "The exploration gate activated because "
            f"the random draw {exploration_draw:.4f} "
            f"was below epsilon {epsilon:.4f}. "
            f"Action {selected_action} was sampled from "
            "the legal action set even though it was not "
            "a current greedy action."
        )

    if len(greedy_actions) > 1:
        return (
            "The agent exploited its learned policy because "
            f"the random draw {exploration_draw:.4f} "
            f"was not below epsilon {epsilon:.4f}. "
            f"Actions {greedy_actions} were tied at the "
            f"highest Q-value {best_q:.4f}. "
            f"Action {selected_action} was selected from "
            "that greedy tie set."
        )

    return (
        "The agent exploited its learned policy because "
        f"the random draw {exploration_draw:.4f} "
        f"was not below epsilon {epsilon:.4f}. "
        f"Action {selected_action} had the highest stored "
        f"Q-value {selected_q:.4f}, with an action gap "
        f"of {action_gap:.4f} over the next distinct "
        "Q-value."
    )


def get_next_decision_number(
    db: Session,
) -> int:
    current_max = db.scalar(
        select(
            func.max(
                DecisionEventModel.decision_number,
            ),
        ),
    )

    if current_max is None:
        return 1

    return int(current_max) + 1


def decision_q_value_rows(
    decision: AgentDecision,
) -> list[dict]:
    return [
        {
            "action": action,
            "q_value": float(
                decision.legal_q_values[action],
            ),
            "is_greedy": (
                action
                in decision.greedy_actions
            ),
            "is_selected": (
                action == decision.action
            ),
        }
        for action in decision.legal_actions
    ]


def make_decision_event_model(
    *,
    decision: AgentDecision,
    episode_number: int | None,
    decision_number: int,
    tactical_labels: list[str],
) -> DecisionEventModel:
    explanation = build_decision_explanation(
        decision_mode=decision.decision_mode,
        epsilon=decision.epsilon,
        exploration_draw=decision.random_sample,
        selected_action=decision.action,
        selected_q=decision.selected_q_value,
        best_q=decision.best_q_value,
        action_gap=decision.action_gap,
        greedy_actions=decision.greedy_actions,
    )

    return DecisionEventModel(
        episode_number=episode_number,
        decision_number=decision_number,
        state_key=decision.state,
        legal_actions_json=json.dumps(
            decision.legal_actions,
        ),
        q_values_json=json.dumps(
            decision_q_value_rows(decision),
        ),
        epsilon=float(decision.epsilon),
        exploration_draw=float(
            decision.random_sample,
        ),
        decision_mode=decision.decision_mode,
        greedy_actions_json=json.dumps(
            decision.greedy_actions,
        ),
        selected_action=decision.action,
        selected_q=float(
            decision.selected_q_value,
        ),
        best_q=float(decision.best_q_value),
        second_best_q=float(
            decision.second_best_q_value,
        ),
        action_gap=float(decision.action_gap),
        was_greedy_action=(
            decision.action
            in decision.greedy_actions
        ),
        tie_count=len(decision.greedy_actions),
        tactical_labels_json=json.dumps(
            tactical_labels,
        ),
        explanation=explanation,
    )


def decision_event_to_dict(
    event: DecisionEventModel,
) -> dict:
    return {
        "id": event.id,
        "episode_number": event.episode_number,
        "decision_number": event.decision_number,
        "state_key": event.state_key,
        "legal_actions": json.loads(
            event.legal_actions_json,
        ),
        "q_values": json.loads(
            event.q_values_json,
        ),
        "epsilon": event.epsilon,
        "exploration_draw": (
            event.exploration_draw
        ),
        "decision_mode": event.decision_mode,
        "greedy_actions": json.loads(
            event.greedy_actions_json,
        ),
        "selected_action": (
            event.selected_action
        ),
        "selected_q": event.selected_q,
        "best_q": event.best_q,
        "second_best_q": (
            event.second_best_q
        ),
        "action_gap": event.action_gap,
        "was_greedy_action": (
            event.was_greedy_action
        ),
        "tie_count": event.tie_count,
        "tactical_labels": json.loads(
            event.tactical_labels_json,
        ),
        "explanation": event.explanation,
        "created_at": event.created_at,
    }


def decision_summary_to_dict(
    event: DecisionEventModel,
) -> dict:
    return {
        "id": event.id,
        "episode_number": event.episode_number,
        "decision_number": event.decision_number,
        "state_key": event.state_key,
        "epsilon": event.epsilon,
        "exploration_draw": (
            event.exploration_draw
        ),
        "decision_mode": event.decision_mode,
        "selected_action": (
            event.selected_action
        ),
        "selected_q": event.selected_q,
        "best_q": event.best_q,
        "action_gap": event.action_gap,
        "was_greedy_action": (
            event.was_greedy_action
        ),
        "created_at": event.created_at,
    }
