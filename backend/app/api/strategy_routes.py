from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from app.schemas.strategy import (
    DecisionInspection,
    EpisodeInspection,
    EpisodeSummary,
    StateInspection,
    StateSummary,
    StrategyEvidenceItem,
    StrategyOverview,
)
from app.strategy.service import (
    strategy_service,
)


router = APIRouter(
    prefix="/api/strategy",
    tags=["strategy"],
)


ALLOWED_STRATEGIES = {
    "immediate_win",
    "immediate_block",
    "fork_creation",
    "fork_prevention",
    "center_preference",
    "corner_preference",
    "edge_preference",
}


@router.get(
    "/overview",
    response_model=StrategyOverview,
)
def get_strategy_overview():
    return strategy_service.get_strategy_overview()


@router.get(
    "/evidence",
    response_model=list[
        StrategyEvidenceItem
    ],
)
def get_strategy_evidence(
    strategy: str = Query(...),
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
):
    if strategy not in ALLOWED_STRATEGIES:
        raise HTTPException(
            status_code=400,
            detail={
                "message": (
                    "Unsupported strategy."
                ),
                "allowed": sorted(
                    ALLOWED_STRATEGIES,
                ),
            },
        )

    return strategy_service.get_strategy_evidence(
        strategy=strategy,
        limit=limit,
    )


@router.get(
    "/q-table/states",
    response_model=list[StateSummary],
)
def list_q_table_states(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    return strategy_service.list_states(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/q-table/state/{state_key}",
    response_model=StateInspection,
)
def inspect_q_table_state(
    state_key: str,
):
    try:
        return strategy_service.inspect_state(
            state_key,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get(
    "/decision/{state_key}",
    response_model=DecisionInspection,
)
def inspect_decision(
    state_key: str,
):
    try:
        return strategy_service.inspect_decision(
            state_key,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.get(
    "/episodes",
    response_model=list[
        EpisodeSummary
    ],
)
def list_episodes(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
    offset: int = Query(
        default=0,
        ge=0,
    ),
):
    return strategy_service.list_episodes(
        limit=limit,
        offset=offset,
    )


@router.get(
    "/episodes/{episode_number}",
    response_model=EpisodeInspection,
)
def inspect_episode(
    episode_number: int,
):
    episode = strategy_service.inspect_episode(
        episode_number,
    )

    if episode is None:
        raise HTTPException(
            status_code=404,
            detail="Episode not found.",
        )

    return episode
