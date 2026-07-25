from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.config import settings
from app.database.dependencies import get_db
from app.database.init_db import create_database_tables
from app.routes import ai, export, generation_support, projects


@asynccontextmanager
async def lifespan(
    app: FastAPI,
):
    """
    Initialize application resources before accepting requests.
    """

    create_database_tables()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    ai.router,
    prefix="/api/ai",
    tags=["AI"],
)

app.include_router(
    projects.router,
    prefix="/api/projects",
    tags=["Projects"],
)

app.include_router(
    export.router,
    prefix="/api",
)

app.include_router(
    generation_support.router,
    prefix="/api",
)


@app.get("/")
def root() -> dict[str, str]:
    """
    Return basic API information.
    """

    return {
        "message": (
            f"{settings.app_name} is running"
        ),
        "environment": (
            settings.app_environment
        ),
    }


@app.get("/health")
def health() -> dict[str, str]:
    """
    Return the general API health status.
    """

    return {
        "status": "healthy",
    }


@app.get("/api/database/status")
def database_status(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    """
    Verify that the configured database connection is available.
    """

    db.execute(
        text("SELECT 1"),
    )

    return {
        "status": "connected",
    }