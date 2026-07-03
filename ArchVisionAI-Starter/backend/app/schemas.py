from pydantic import BaseModel, Field
from typing import List, Optional, Literal

ComponentType = Literal[
    "frontend", "backend", "database", "cache", "storage", "auth",
    "external_api", "message_queue", "load_balancer", "service"
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

class Connection(BaseModel):
    id: str
    source: str
    target: str
    label: Optional[str] = None

class ArchitectureModel(BaseModel):
    name: str = "Untitled Architecture"
    description: Optional[str] = None
    components: List[Component] = []
    connections: List[Connection] = []

class GenerateRequest(BaseModel):
    prompt: str

class FeedbackRequest(BaseModel):
    model: ArchitectureModel

class ProjectCreate(BaseModel):
    name: str
    model: ArchitectureModel
