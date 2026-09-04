from datetime import datetime, timezone

from fastapi import FastAPI
from fastapi.middleware.cors import (
    CORSMiddleware,
)

from app.config import settings
from app.database.database import (
    create_database_tables,
)
from app.database.migrations import (
    run_database_migrations,
)


# -------------------------------------------------
# DATABASE STARTUP
# -------------------------------------------------

create_database_tables()
run_database_migrations()


# -------------------------------------------------
# ROUTES
#
# Imported only after database initialization.
# -------------------------------------------------

from app.api.agent_routes import (
    router as agent_router,
)
from app.api.analytics_routes import (
    router as analytics_router,
)
from app.api.decision_routes import (
    router as decision_router,
)
from app.api.evaluation_routes import (
    router as evaluation_router,
)
from app.api.strategy_routes import (
    router as strategy_router,
)
from app.api.training_routes import (
    router as training_router,
)
from app.api.game_routes import router as game_router


# -------------------------------------------------
# FASTAPI APPLICATION
# -------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Persistent human-trained Q-learning "
        "Tic-Tac-Toe research laboratory "
        "with scientific learning analytics."
    ),
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.frontend_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(game_router)
app.include_router(agent_router)
app.include_router(analytics_router)
app.include_router(strategy_router)
app.include_router(decision_router)
app.include_router(training_router)
app.include_router(evaluation_router)


@app.get("/")
def root():
    return {
        "project": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "analytics": "enabled",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "rl-backend",
        "version": settings.app_version,
        "analytics": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
