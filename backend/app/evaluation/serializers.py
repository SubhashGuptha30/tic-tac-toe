from app.database.models import (
    EvaluationEpisodeModel,
    EvaluationRunModel,
    PolicySnapshotModel,
)


def policy_snapshot_to_dict(
    snapshot: PolicySnapshotModel,
) -> dict:
    return {
        "id": snapshot.id,
        "source": snapshot.source,
        "q_table_hash": snapshot.q_table_hash,
        "q_states": snapshot.q_states,
        "q_entries": snapshot.q_entries,
        "alpha": snapshot.alpha,
        "gamma": snapshot.gamma,
        "tie_breaking_policy": (
            snapshot.tie_breaking_policy
        ),
        "created_at": snapshot.created_at,
    }


def evaluation_run_to_dict(
    run: EvaluationRunModel,
) -> dict:
    games = run.completed_games
    decisions = run.total_decisions

    return {
        "id": run.id,
        "snapshot_id": run.snapshot_id,
        "status": run.status,
        "opponent_type": run.opponent_type,
        "tactical_probability": run.tactical_probability,
        "requested_games": run.requested_games,
        "completed_games": games,
        "agent_wins": run.agent_wins,
        "opponent_wins": run.opponent_wins,
        "draws": run.draws,
        "agent_win_rate": (
            run.agent_wins / games if games else 0.0
        ),
        "opponent_win_rate": (
            run.opponent_wins / games if games else 0.0
        ),
        "draw_rate": run.draws / games if games else 0.0,
        "total_moves": run.total_moves,
        "average_moves": (
            run.total_moves / games if games else 0.0
        ),
        "total_agent_moves": run.total_agent_moves,
        "total_opponent_moves": run.total_opponent_moves,
        "total_decisions": decisions,
        "greedy_decision_rate": 1.0 if decisions else 0.0,
        "unique_states_visited": (
            run.unique_states_visited
        ),
        "average_decision_confidence": (
            run.confidence_sum / decisions
            if decisions
            else 0.0
        ),
        "average_action_gap": (
            run.action_gap_sum / decisions
            if decisions
            else 0.0
        ),
        "immediate_win_opportunities": (
            run.immediate_win_opportunities
        ),
        "immediate_win_successes": (
            run.immediate_win_successes
        ),
        "immediate_win_conversion_rate": (
            run.immediate_win_successes
            / run.immediate_win_opportunities
            if run.immediate_win_opportunities
            else 0.0
        ),
        "immediate_block_opportunities": (
            run.immediate_block_opportunities
        ),
        "immediate_block_successes": (
            run.immediate_block_successes
        ),
        "immediate_block_success_rate": (
            run.immediate_block_successes
            / run.immediate_block_opportunities
            if run.immediate_block_opportunities
            else 0.0
        ),
        "seed": run.seed,
        "tie_breaking_policy": run.tie_breaking_policy,
        "duration_seconds": run.duration_seconds,
        "games_per_second": run.games_per_second,
        "error_message": run.error_message,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
    }


def evaluation_episode_to_dict(
    episode: EvaluationEpisodeModel,
) -> dict:
    return {
        "id": episode.id,
        "evaluation_run_id": episode.evaluation_run_id,
        "game_index": episode.game_index,
        "result": episode.result,
        "agent_moves": episode.agent_moves,
        "opponent_moves": episode.opponent_moves,
        "move_count": episode.move_count,
        "decision_count": episode.decision_count,
        "mean_confidence": episode.mean_confidence,
        "mean_action_gap": episode.mean_action_gap,
        "immediate_win_opportunities": (
            episode.immediate_win_opportunities
        ),
        "immediate_win_successes": (
            episode.immediate_win_successes
        ),
        "immediate_block_opportunities": (
            episode.immediate_block_opportunities
        ),
        "immediate_block_successes": (
            episode.immediate_block_successes
        ),
        "unique_states_visited": (
            episode.unique_states_visited
        ),
        "final_board_key": episode.final_board_key,
        "duration_ms": episode.duration_ms,
        "created_at": episode.created_at,
    }
