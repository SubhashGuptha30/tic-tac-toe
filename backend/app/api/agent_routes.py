from fastapi import APIRouter, HTTPException

from app.game.service import game_service
from app.schemas.game import (
    AgentMetrics,
    AgentParameterUpdate,
    ResetResponse,
)


router = APIRouter(
    prefix="/api/agent",
    tags=["agent"],
)


@router.get(
    "/metrics",
    response_model=AgentMetrics,
)
def get_agent_metrics():
    return game_service.get_agent_metrics()


@router.put(
    "/parameters",
    response_model=AgentMetrics,
)
def update_agent_parameters(
    request: AgentParameterUpdate,
):
    try:
        return game_service.update_parameters(
            alpha=request.alpha,
            gamma=request.gamma,
            epsilon=request.epsilon,
            epsilon_min=request.epsilon_min,
            epsilon_decay=request.epsilon_decay,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.delete(
    "/brain",
    response_model=ResetResponse,
)
def reset_agent_brain():
    return game_service.reset_brain()
