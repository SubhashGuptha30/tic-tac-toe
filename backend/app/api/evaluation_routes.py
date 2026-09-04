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
    EvaluationEpisodeModel,
    EvaluationRunModel,
    PolicySnapshotModel,
)
from app.evaluation.agent import TIE_BREAKING_POLICY
from app.evaluation.coordinator import (
    create_policy_snapshot,
    evaluation_coordinator,
    execute_evaluation_run,
)
from app.evaluation.serializers import (
    evaluation_episode_to_dict,
    evaluation_run_to_dict,
    policy_snapshot_to_dict,
)
from app.game.service import game_service
from app.schemas.evaluation import (
    EvaluationComparisonResponse,
    EvaluationEngineHealthResponse,
    EvaluationEpisodeResponse,
    EvaluationRunCreate,
    EvaluationRunResponse,
    PolicySnapshotResponse,
)


router = APIRouter(
    prefix="/api/evaluation",
    tags=["Evaluation Lab"],
)

SUPPORTED_OPPONENTS = (
    "random",
    "tactical",
    "mixed",
)


@router.get(
    "/health",
    response_model=EvaluationEngineHealthResponse,
)
def evaluation_health() -> dict:
    return {
        "engine_ready": not evaluation_coordinator.is_busy(),
        "active_run_id": evaluation_coordinator.active_run_id,
        "supported_opponents": list(SUPPORTED_OPPONENTS),
        "tie_breaking_policy": TIE_BREAKING_POLICY,
        "message": (
            "Evaluation engine ready. Policy snapshots run "
            "with epsilon fixed at zero and learning disabled."
            if not evaluation_coordinator.is_busy()
            else "An evaluation run is active."
        ),
    }


@router.post(
    "/runs",
    response_model=EvaluationRunResponse,
)
def create_evaluation_run(
    payload: EvaluationRunCreate,
    db: Session = Depends(get_db),
) -> dict:
    opponent_type = payload.opponent_type.strip().lower()

    if opponent_type not in SUPPORTED_OPPONENTS:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported evaluation opponent. Use random, "
                "tactical, or mixed."
            ),
        )

    if evaluation_coordinator.is_busy():
        raise HTTPException(
            status_code=409,
            detail="An evaluation run is already active.",
        )

    if payload.snapshot_id is None:
        snapshot = create_policy_snapshot(
            db=db,
            agent=game_service.agent,
        )
    else:
        snapshot = db.get(
            PolicySnapshotModel,
            payload.snapshot_id,
        )
        if snapshot is None:
            raise HTTPException(
                status_code=404,
                detail="Requested policy snapshot was not found.",
            )
    run = EvaluationRunModel(
        snapshot_id=snapshot.id,
        status="pending",
        opponent_type=opponent_type,
        tactical_probability=(
            payload.tactical_probability
            if opponent_type == "mixed"
            else None
        ),
        requested_games=payload.games,
        seed=payload.seed,
        tie_breaking_policy=TIE_BREAKING_POLICY,
    )
    db.add(run)
    db.commit()
    db.refresh(run)

    try:
        execute_evaluation_run(
            db=db,
            run_id=run.id,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Evaluation run failed: {exc}",
        ) from exc

    db.refresh(run)
    return evaluation_run_to_dict(run)


@router.get(
    "/runs",
    response_model=list[EvaluationRunResponse],
)
def list_evaluation_runs(
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
        select(EvaluationRunModel)
        .order_by(EvaluationRunModel.id.desc())
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        evaluation_run_to_dict(run)
        for run in runs
    ]


@router.get(
    "/runs/{run_id}",
    response_model=EvaluationRunResponse,
)
def get_evaluation_run(
    run_id: int,
    db: Session = Depends(get_db),
) -> dict:
    run = db.get(EvaluationRunModel, run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    return evaluation_run_to_dict(run)


@router.get(
    "/runs/{run_id}/episodes",
    response_model=list[EvaluationEpisodeResponse],
)
def get_evaluation_episodes(
    run_id: int,
    limit: int = Query(
        default=1000,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    run = db.get(EvaluationRunModel, run_id)
    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Evaluation run not found.",
        )

    episodes = db.scalars(
        select(EvaluationEpisodeModel)
        .where(
            EvaluationEpisodeModel.evaluation_run_id
            == run_id
        )
        .order_by(EvaluationEpisodeModel.game_index.asc())
        .offset(offset)
        .limit(limit)
    ).all()

    return [
        evaluation_episode_to_dict(episode)
        for episode in episodes
    ]


@router.get(
    "/snapshots",
    response_model=list[PolicySnapshotResponse],
)
def list_policy_snapshots(
    limit: int = Query(
        default=50,
        ge=1,
        le=200,
    ),
    db: Session = Depends(get_db),
) -> list[dict]:
    snapshots = db.scalars(
        select(PolicySnapshotModel)
        .order_by(PolicySnapshotModel.id.desc())
        .limit(limit)
    ).all()

    return [
        policy_snapshot_to_dict(snapshot)
        for snapshot in snapshots
    ]


@router.get(
    "/snapshots/{snapshot_id}/comparison",
    response_model=EvaluationComparisonResponse,
)
def get_snapshot_comparison(
    snapshot_id: int,
    db: Session = Depends(get_db),
) -> dict:
    snapshot = db.get(PolicySnapshotModel, snapshot_id)
    if snapshot is None:
        raise HTTPException(
            status_code=404,
            detail="Policy snapshot not found.",
        )

    snapshot_runs = db.scalars(
        select(EvaluationRunModel)
        .where(
            EvaluationRunModel.snapshot_id == snapshot_id,
            EvaluationRunModel.status == "completed",
        )
        .order_by(EvaluationRunModel.id.desc())
    ).all()
    latest_by_opponent: dict[str, EvaluationRunModel] = {}
    for run in snapshot_runs:
        latest_by_opponent.setdefault(
            run.opponent_type,
            run,
        )

    rows: list[dict] = []
    for opponent_type in SUPPORTED_OPPONENTS:
        run = latest_by_opponent.get(opponent_type)
        if run is None:
            rows.append(
                {
                    "opponent_type": opponent_type,
                    "evaluation_run_id": None,
                    "games": 0,
                    "agent_win_rate": 0.0,
                    "draw_rate": 0.0,
                    "opponent_win_rate": 0.0,
                    "average_moves": 0.0,
                    "average_decision_confidence": 0.0,
                    "is_available": False,
                }
            )
            continue

        report = evaluation_run_to_dict(run)
        rows.append(
            {
                "opponent_type": opponent_type,
                "evaluation_run_id": run.id,
                "games": run.completed_games,
                "agent_win_rate": report["agent_win_rate"],
                "draw_rate": report["draw_rate"],
                "opponent_win_rate": report[
                    "opponent_win_rate"
                ],
                "average_moves": report["average_moves"],
                "average_decision_confidence": report[
                    "average_decision_confidence"
                ],
                "is_available": True,
            }
        )

    return {
        "snapshot": policy_snapshot_to_dict(snapshot),
        "rows": rows,
    }
