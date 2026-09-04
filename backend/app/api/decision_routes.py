from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.database.models import DecisionEventModel
from app.decision.capture import (
    decision_event_to_dict,
    decision_summary_to_dict,
)
from app.schemas.decision import (
    DecisionEventResponse,
    DecisionEventSummary,
    DecisionStatsResponse,
)


router = APIRouter(
    prefix="/api/decisions",
    tags=["decision-microscope"],
)


@router.get(
    "/latest",
    response_model=DecisionEventResponse | None,
)
def get_latest_decision(
    db: Session = Depends(get_db),
):
    event = db.scalar(
        select(DecisionEventModel).order_by(
            DecisionEventModel.id.desc(),
        ),
    )

    if event is None:
        return None

    return decision_event_to_dict(event)


@router.get(
    "/history",
    response_model=list[DecisionEventSummary],
)
def get_decision_history(
    limit: int = Query(
        default=50,
        ge=1,
        le=500,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
    db: Session = Depends(get_db),
):
    events = db.scalars(
        select(DecisionEventModel)
        .order_by(
            DecisionEventModel.id.desc(),
        )
        .offset(offset)
        .limit(limit),
    ).all()

    return [
        decision_summary_to_dict(event)
        for event in events
    ]


@router.get(
    "/stats",
    response_model=DecisionStatsResponse,
)
def get_decision_stats(
    db: Session = Depends(get_db),
):
    total = db.scalar(
        select(
            func.count(DecisionEventModel.id),
        ),
    ) or 0

    if total == 0:
        return {
            "total_decisions": 0,
            "exploration_decisions": 0,
            "exploitation_decisions": 0,
            "exploration_rate": 0.0,
            "exploitation_rate": 0.0,
            "greedy_selection_rate": 0.0,
            "mean_action_gap": 0.0,
            "mean_epsilon": 0.0,
            "decisions_with_ties": 0,
        }

    exploration = db.scalar(
        select(
            func.count(DecisionEventModel.id),
        ).where(
            DecisionEventModel.decision_mode
            == "exploration",
        ),
    ) or 0
    exploitation = db.scalar(
        select(
            func.count(DecisionEventModel.id),
        ).where(
            DecisionEventModel.decision_mode
            == "exploitation",
        ),
    ) or 0
    greedy_count = db.scalar(
        select(
            func.count(DecisionEventModel.id),
        ).where(
            DecisionEventModel.was_greedy_action.is_(
                True,
            ),
        ),
    ) or 0
    decisions_with_ties = db.scalar(
        select(
            func.count(DecisionEventModel.id),
        ).where(
            DecisionEventModel.tie_count > 1,
        ),
    ) or 0
    mean_gap = db.scalar(
        select(
            func.avg(
                DecisionEventModel.action_gap,
            ),
        ),
    ) or 0.0
    mean_epsilon = db.scalar(
        select(
            func.avg(
                DecisionEventModel.epsilon,
            ),
        ),
    ) or 0.0

    return {
        "total_decisions": int(total),
        "exploration_decisions": int(
            exploration,
        ),
        "exploitation_decisions": int(
            exploitation,
        ),
        "exploration_rate": float(
            exploration / total,
        ),
        "exploitation_rate": float(
            exploitation / total,
        ),
        "greedy_selection_rate": float(
            greedy_count / total,
        ),
        "mean_action_gap": float(mean_gap),
        "mean_epsilon": float(mean_epsilon),
        "decisions_with_ties": int(
            decisions_with_ties,
        ),
    }


@router.get(
    "/{decision_id}",
    response_model=DecisionEventResponse,
)
def get_decision(
    decision_id: int,
    db: Session = Depends(get_db),
):
    event = db.get(
        DecisionEventModel,
        decision_id,
    )

    if event is None:
        raise HTTPException(
            status_code=404,
            detail="Decision event not found.",
        )

    return decision_event_to_dict(event)
