from fastapi import (
    APIRouter,
    Query,
)

from app.analytics.service import (
    analytics_service,
)
from app.schemas.analytics import (
    AnalyticsDataset,
    AnalyticsOverview,
    EpsilonPoint,
    LearningCurvePoint,
    LearningUpdateDetail,
    OutcomeTimelinePoint,
    RewardPoint,
    TDErrorPoint,
)


router = APIRouter(
    prefix="/api/analytics",
    tags=["analytics"],
)


@router.get(
    "/overview",
    response_model=AnalyticsOverview,
)
def get_analytics_overview():
    return analytics_service.get_overview()


@router.get(
    "/learning-curve",
    response_model=list[
        LearningCurvePoint
    ],
)
def get_learning_curve(
    rolling_window: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    return analytics_service.get_learning_curve(
        rolling_window=rolling_window
    )


@router.get(
    "/outcomes",
    response_model=list[
        OutcomeTimelinePoint
    ],
)
def get_outcome_timeline(
    limit: int = Query(
        default=200,
        ge=1,
        le=5000,
    ),
):
    return (
        analytics_service
        .get_outcome_timeline(
            limit=limit
        )
    )


@router.get(
    "/td-errors",
    response_model=list[
        TDErrorPoint
    ],
)
def get_td_error_curve(
    limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
    rolling_window: int = Query(
        default=20,
        ge=1,
        le=500,
    ),
):
    return (
        analytics_service
        .get_td_error_curve(
            limit=limit,
            rolling_window=rolling_window,
        )
    )


@router.get(
    "/rewards",
    response_model=list[
        RewardPoint
    ],
)
def get_reward_trajectory(
    limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
):
    return (
        analytics_service
        .get_reward_trajectory(
            limit=limit
        )
    )


@router.get(
    "/epsilon",
    response_model=list[
        EpsilonPoint
    ],
)
def get_epsilon_curve(
    limit: int = Query(
        default=500,
        ge=1,
        le=5000,
    ),
):
    return (
        analytics_service
        .get_epsilon_curve(
            limit=limit
        )
    )


@router.get(
    "/learning-updates",
    response_model=list[
        LearningUpdateDetail
    ],
)
def get_learning_updates(
    limit: int = Query(
        default=100,
        ge=1,
        le=5000,
    ),
):
    return (
        analytics_service
        .get_learning_updates(
            limit=limit
        )
    )


@router.get(
    "/dataset",
    response_model=AnalyticsDataset,
)
def get_analytics_dataset(
    rolling_window: int = Query(
        default=10,
        ge=1,
        le=100,
    ),
):
    return analytics_service.get_dataset(
        rolling_window=rolling_window
    )
