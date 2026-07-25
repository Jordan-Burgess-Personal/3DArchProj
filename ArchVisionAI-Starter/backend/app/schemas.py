from __future__ import annotations

from datetime import datetime
from math import isfinite
from typing import Any, Dict, List, Literal, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)


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


def _strip_required_text(value: str) -> str:
    cleaned = value.strip()

    if not cleaned:
        raise ValueError("Value must not be blank.")

    return cleaned


class Position(BaseModel):
    x: float
    y: float
    z: float

    @model_validator(mode="after")
    def validate_finite_coordinates(self) -> "Position":
        coordinates = {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

        invalid = [
            axis
            for axis, value in coordinates.items()
            if not isfinite(value)
        ]

        if invalid:
            raise ValueError(
                "Position coordinates must be finite numbers. "
                f"Invalid coordinates: {', '.join(invalid)}."
            )

        return self


class Component(BaseModel):
    id: str = Field(min_length=1)
    type: ComponentType
    name: str = Field(min_length=1)
    technology: Optional[str] = None
    description: Optional[str] = None
    position: Position = Field(default_factory=Position)
    color: Optional[str] = None
    icon: Optional[str] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id", "name")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return _strip_required_text(value)

    @field_validator(
        "technology",
        "description",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        return str(value).strip()


class Connection(BaseModel):
    id: str = Field(min_length=1)
    source: str = Field(min_length=1)
    target: str = Field(min_length=1)
    connection_type: str = Field(
        default="dependency",
        min_length=1,
    )
    protocol: Optional[str] = None
    direction: str = Field(
        default="unidirectional",
        min_length=1,
    )
    label: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator(
        "id",
        "source",
        "target",
        "connection_type",
        "direction",
    )
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        return _strip_required_text(value)

    @field_validator(
        "protocol",
        "label",
        mode="before",
    )
    @classmethod
    def normalize_optional_text(
        cls,
        value: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        return str(value).strip()


class ArchitectureModel(BaseModel):
    name: str = Field(
        default="Untitled Architecture",
        min_length=1,
    )
    description: Optional[str] = None
    components: List[Component] = Field(default_factory=list)
    connections: List[Connection] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        return _strip_required_text(value)

    @field_validator(
        "description",
        mode="before",
    )
    @classmethod
    def normalize_description(
        cls,
        value: Any,
    ) -> Optional[str]:
        if value is None:
            return None

        return str(value).strip()


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=5000)
    current_model: ArchitectureModel

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        return _strip_required_text(value)


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

    @field_validator("summary")
    @classmethod
    def validate_summary(cls, value: str) -> str:
        return _strip_required_text(value)


class FeedbackRequest(BaseModel):
    model: ArchitectureModel


class FeedbackResponse(BaseModel):
    """Suggestions returned by the architecture feedback endpoint."""

    suggestions: List[str] = Field(default_factory=list)


class ProjectCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    name: str = Field(min_length=1, max_length=150)
    model: ArchitectureModel


class ProjectRename(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=150)


class ProjectSummary(BaseModel):
    """
    Lightweight project information used by project-management interfaces.

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