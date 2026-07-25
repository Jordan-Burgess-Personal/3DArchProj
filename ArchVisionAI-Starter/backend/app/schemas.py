from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ComponentType = Literal[
    "frontend",
    "mobile",
    "backend",
    "worker",
    "database",
    "cache",
    "storage",
    "auth",
    "authorization",
    "external_api",
    "message_queue",
    "load_balancer",
    "gateway",
    "service",
    "ai_service",
    "cloud",
    "container",
    "custom",
]


class Position(BaseModel):
    x: float = 0
    y: float = 0.5
    z: float = 0


class Component(BaseModel):
    id: str = Field(min_length=1)
    type: ComponentType
    name: str = Field(min_length=1)
    technology: Optional[str] = None
    description: Optional[str] = None
    position: Position = Field(default_factory=Position)


class Connection(BaseModel):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    label: Optional[str] = None


class ArchitectureModel(BaseModel):
    name: str = "Untitled Architecture"
    description: Optional[str] = None
    components: List[Component] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=5000)
    current_model: ArchitectureModel


class ArchitectureChanges(BaseModel):
    added_component_ids: List[str] = Field(default_factory=list)
    updated_component_ids: List[str] = Field(default_factory=list)
    removed_component_ids: List[str] = Field(default_factory=list)
    added_connection_ids: List[str] = Field(default_factory=list)
    removed_connection_ids: List[str] = Field(default_factory=list)


class GenerateResponse(BaseModel):
    summary: str = Field(min_length=1)
    architecture: ArchitectureModel
    changes: ArchitectureChanges


class FeedbackRequest(BaseModel):
    model: ArchitectureModel


class FeedbackResponse(BaseModel):
    """Suggestions returned by the architecture feedback endpoint."""

    suggestions: List[str] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1)
    model: ArchitectureModel


class ProjectSummary(BaseModel):
    """
    Lightweight project information used by project-management interfaces.

    This schema intentionally excludes the complete architecture model.
    Loading the complete project will be implemented by the dedicated
    project-loading story.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    schema_version: str
    component_count: int = 0
    connection_count: int = 0
    created_at: datetime
    updated_at: datetime