from app.database.models import (
    TrainingEpisodeModel,
    TrainingRunModel,
)


def training_run_to_dict(
    run: TrainingRunModel,
) -> dict:
    return {
        "id": run.id,
        "status": run.status,
        "opponent_type": run.opponent_type,
        "tactical_probability": run.tactical_probability,
        "requested_episodes": run.requested_episodes,
        "completed_episodes": run.completed_episodes,
        "agent_wins": run.agent_wins,
        "opponent_wins": run.opponent_wins,
        "draws": run.draws,
        "total_agent_moves": run.total_agent_moves,
        "total_opponent_moves": run.total_opponent_moves,
        "epsilon_start": run.epsilon_start,
        "epsilon_end": run.epsilon_end,
        "q_states_start": run.q_states_start,
        "q_states_end": run.q_states_end,
        "q_entries_start": run.q_entries_start,
        "q_entries_end": run.q_entries_end,
        "cumulative_reward": run.cumulative_reward,
        "mean_reward": run.mean_reward,
        "duration_seconds": run.duration_seconds,
        "episodes_per_second": run.episodes_per_second,
        "seed": run.seed,
        "error_message": run.error_message,
        "created_at": run.created_at,
        "started_at": run.started_at,
        "completed_at": run.completed_at,
    }


def training_episode_to_dict(
    episode: TrainingEpisodeModel,
) -> dict:
    return {
        "id": episode.id,
        "training_run_id": episode.training_run_id,
        "episode_index": episode.episode_index,
        "result": episode.result,
        "reward": episode.reward,
        "agent_moves": episode.agent_moves,
        "opponent_moves": episode.opponent_moves,
        "epsilon_before": episode.epsilon_before,
        "epsilon_after": episode.epsilon_after,
        "final_board_key": episode.final_board_key,
        "move_count": episode.move_count,
        "duration_ms": episode.duration_ms,
        "created_at": episode.created_at,
    }
