from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.connection import Connection
    from app.models.project import Project


class Component(TimestampMixin, Base):
    """A node displayed in the architecture workspace."""

    __tablename__ = "components"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    component_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    technology: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    position_x: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    position_y: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    position_z: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
    )

    color: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
    )

    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    properties: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    project: Mapped["Project"] = relationship(
        back_populates="components",
    )

    outgoing_connections: Mapped[list["Connection"]] = relationship(
        back_populates="source_component",
        foreign_keys="Connection.source_component_id",
        passive_deletes=True,
    )

    incoming_connections: Mapped[list["Connection"]] = relationship(
        back_populates="target_component",
        foreign_keys="Connection.target_component_id",
        passive_deletes=True,
    )

    def __repr__(self) -> str:
        return (
            f"<Component id={self.id} "
            f"name={self.name!r} type={self.component_type!r}>"
        )