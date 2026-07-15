from contextlib import asynccontextmanager
from app.config import settings

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import ai, projects, export
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.database.init_db import create_database_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
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

app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": f"{settings.app_name} is running",
        "environment": settings.app_environment,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/database/status")
def database_status(
    db: Session = Depends(get_db),
) -> dict[str, str]:
    db.execute(text("SELECT 1"))

    return {"status": "connected"}