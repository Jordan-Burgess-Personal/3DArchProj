from contextlib import asynccontextmanager
import os

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv


from app.routes import ai, projects, export
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database.dependencies import get_db
from app.database.init_db import create_database_tables


load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_database_tables()
    yield

app = FastAPI(title="ArchVision AI API", version="0.1.0", lifespan=lifespan,)

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ai.router, prefix="/api/ai", tags=["AI"])
app.include_router(projects.router, prefix="/api/projects", tags=["Projects"])
app.include_router(export.router, prefix="/api/export", tags=["Export"])

@app.get("/")
def root():
    return {"message": "ArchVision AI backend is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/database/status")
def database_status(db: Session = Depends(get_db)):

    db.execute(text("SELECT 1"))

    return {
        "status": "connected"
    }