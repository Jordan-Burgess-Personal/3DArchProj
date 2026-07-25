from __future__ import annotations

from datetime import datetime
from typing import Any, List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


ComponentType = Literal[
    "frontend",
    "backend",
    "database",
    "cache",
    "storage",
    "auth",
    "external_api",
    "message_queue",
    "load_balancer",
    "service",
]


class Position(BaseModel):
    x: float = 0
    y: float = 0
    z: float = 0


class Component(BaseModel):
    id: str
    type: ComponentType
    name: str
    technology: Optional[str] = None
    description: Optional[str] = None
    position: Position = Field(default_factory=Position)
    color: Optional[str] = None
    icon: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)



class Connection(BaseModel):
    id: str
    source: str
    target: str
    connection_type: str = "data-flow"
    protocol: Optional[str] = None
    direction: str = "unidirectional"
    label: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)



class ArchitectureModel(BaseModel):
    name: str = "Untitled Architecture"
    description: Optional[str] = None

    components: List[Component] = Field(
        default_factory=list,
    )
    connections: List[Connection] = Field(
        default_factory=list,
    )



class GenerateRequest(BaseModel):
    prompt: str


class FeedbackRequest(BaseModel):
    model: ArchitectureModel


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)
    model: ArchitectureModel


class ProjectRename(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)


class ProjectSummary(BaseModel):
    """
    Lightweight project information used by project-management
    interfaces.

    This schema intentionally excludes the complete architecture model.
    """

    id: UUID
    name: str
    description: Optional[str] = None
    status: str
    schema_version: str
    component_count: int = 0
    connection_count: int = 0
    created_at: datetime
    updated_at: datetime


class ProjectDetail(ProjectSummary):
    model: ArchitectureModel