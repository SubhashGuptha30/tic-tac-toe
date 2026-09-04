from fastapi import APIRouter, HTTPException

from app.game.service import game_service
from app.schemas.game import (
    AgentMoveResponse,
    GameStateResponse,
    HumanMoveRequest,
    HumanMoveResponse,
    ResetResponse,
)


router = APIRouter(
    prefix="/api/game",
    tags=["game"],
)


@router.get(
    "/state",
    response_model=GameStateResponse,
)
def get_game_state() -> dict:
    return game_service.get_state()


@router.post(
    "/human-move",
    response_model=HumanMoveResponse,
)
def human_move(
    request: HumanMoveRequest,
) -> dict:
    try:
        return game_service.human_move(
            action=request.action
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/agent-move",
    response_model=AgentMoveResponse,
)
def agent_move() -> dict:
    try:
        return game_service.agent_move()
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error


@router.post(
    "/reset",
    response_model=ResetResponse,
)
def reset_game() -> dict:
    return game_service.reset_board()
