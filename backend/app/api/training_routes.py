import random

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import (
    TrainingEpisodeModel,
    TrainingRunModel,
)
from app.game.service import game_service
from app.schemas.training import (
    TrainingEngineHealthResponse,
    TrainingEpisodeResponse,
    TrainingRunCreate,
    TrainingRunResponse,
    TrainingRunStatsResponse,
)
from app.training.agent_adapter import (
    TrainingAgentAdapter,
)
from app.training.coordinator import (
    execute_training_run,
    training_coordinator,
)
from app.training.serializers import (
    training_episode_to_dict,
    training_run_to_dict,
)


router = APIRouter(
    prefix="/api/training",
    tags=["Training Arena"],
)


@router.get(
    "/health",
    response_model=TrainingEngineHealthResponse,
)
def training_health() -> dict:
    agent_available = hasattr(
        game_service,
        "agent",
    )

    return {
        "engine_ready": (
            agent_available
            and not training_coordinator.is_busy()
        ),
        "supported_opponents": [
            "random",
            "tactical",
            "mixed",
        ],
        "active_run_id": (
            training_coordinator.active_run_id
        ),
        "agent_available": agent_available,
        "message": (
            "Training engine ready."
            if agent_available
            else "Shared RL agent is not available."
        ),
    }


@router.post(
    "/runs",
    response_model=TrainingRunResponse,
)
def create_training_run(
    payload: TrainingRunCreate,
    db: Session = Depends(get_db),
) -> dict:
    opponent_type = payload.opponent_type.strip().lower()

    if opponent_type not in {
        "random",
        "tactical",
        "mixed",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported training opponent. Use random, "
                "tactical, or mixed."
            ),
        )

    if training_coordinator.is_busy():
        raise HTTPException(
            status_code=409,
            detail="A training run is already active.",
        )

    agent = game_service.agent
    adapter = TrainingAgentAdapter(
        agent=agent,
        rng=random.Random(payload.seed),
    )

    run = TrainingRunModel(
        status="pending",
        opponent_type=opponent_type,
        tactical_probability=(
            payload.tactical_probability
            if opponent_type == "mixed"
            else None
        ),
        requested_episodes=payload.episodes,
        completed_episodes=0,
        agent_wins=0,
        opponent_wins=0,
        draws=0,
        total_agent_moves=0,
        total_opponent_moves=0,
        epsilon_start=adapter.epsilon,
        epsilon_end=adapter.epsilon,
        q_states_start=adapter.q_state_count(),
        q_states_end=adapter.q_state_count(),
        q_entries_start=adapter.q_entry_count(),
        q_entries_end=adapter.q_entry_count(),
        cumulative_reward=0.0,
        mean_reward=0.0,
        seed=payload.seed,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        execute_training_run(
            db=db,
            run_id=run.id,
            agent=agent,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Training run failed: {exc}",
        ) from exc

    db.refresh(run)
    return training_run_to_dict(run)


@router.get(
    "/runs",
    response_model=list[TrainingRunResponse],
)
def list_training_runs(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    runs = db.scalars(
        select(TrainingRunModel)
        .order_by(TrainingRunModel.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        training_run_to_dict(run)
        for run in runs
    ]


@router.get(
    "/runs/{run_id}",
    response_model=TrainingRunResponse,
)
def get_training_run(
    run_id: int,
    db: Session = Depends(get_db),
) -> dict:
    run = db.get(
        TrainingRunModel,
        run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Training run not found.",
        )

    return training_run_to_dict(run)


@router.get(
    "/runs/{run_id}/episodes",
    response_model=list[TrainingEpisodeResponse],
)
def get_training_episodes(
    run_id: int,
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    run_exists = db.scalar(
        select(TrainingRunModel.id).where(
            TrainingRunModel.id == run_id,
        )
    )

    if run_exists is None:
        raise HTTPException(
            status_code=404,
            detail="Training run not found.",
        )

    episodes = db.scalars(
        select(TrainingEpisodeModel)
        .where(
            TrainingEpisodeModel.training_run_id
            == run_id
        )
        .order_by(
            TrainingEpisodeModel.episode_index.asc()
        )
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        training_episode_to_dict(episode)
        for episode in episodes
    ]


@router.get(
    "/runs/{run_id}/stats",
    response_model=TrainingRunStatsResponse,
)
def get_training_run_stats(
    run_id: int,
    db: Session = Depends(get_db),
) -> dict:
    run = db.get(
        TrainingRunModel,
        run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Training run not found.",
        )

    completed = run.completed_episodes

    if completed > 0:
        agent_win_rate = run.agent_wins / completed
        opponent_win_rate = (
            run.opponent_wins / completed
        )
        draw_rate = run.draws / completed
    else:
        agent_win_rate = 0.0
        opponent_win_rate = 0.0
        draw_rate = 0.0

    progress = (
        completed / run.requested_episodes
        if run.requested_episodes > 0
        else 0.0
    )

    return {
        "run_id": run.id,
        "completed_episodes": completed,
        "requested_episodes": run.requested_episodes,
        "progress": float(progress),
        "agent_wins": run.agent_wins,
        "opponent_wins": run.opponent_wins,
        "draws": run.draws,
        "agent_win_rate": float(agent_win_rate),
        "opponent_win_rate": float(opponent_win_rate),
        "draw_rate": float(draw_rate),
        "cumulative_reward": run.cumulative_reward,
        "mean_reward": run.mean_reward,
        "epsilon_start": run.epsilon_start,
        "current_epsilon": (
            run.epsilon_end
            if run.epsilon_end is not None
            else run.epsilon_start
        ),
        "q_states_start": run.q_states_start,
        "current_q_states": (
            run.q_states_end
            if run.q_states_end is not None
            else run.q_states_start
        ),
        "q_entries_start": run.q_entries_start,
        "current_q_entries": (
            run.q_entries_end
            if run.q_entries_end is not None
            else run.q_entries_start
        ),
        "duration_seconds": run.duration_seconds,
        "episodes_per_second": (
            run.episodes_per_second
        ),
    }
