from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Any

from sqlalchemy import CheckConstraint, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.database import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.component import Component
    from app.models.project import Project


class Connection(TimestampMixin, Base):
    """A directional relationship between two architecture components."""

    __tablename__ = "connections"

    __table_args__ = (
        CheckConstraint(
            "source_component_id <> target_component_id",
            name="ck_connection_different_components",
        ),
    )

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

    source_component_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    target_component_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("components.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    label: Mapped[str | None] = mapped_column(
        String(150),
        nullable=True,
    )

    connection_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="data-flow",
    )

    protocol: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    properties: Mapped[dict[str, Any]] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    project: Mapped["Project"] = relationship(
        back_populates="connections",
    )

    source_component: Mapped["Component"] = relationship(
        back_populates="outgoing_connections",
        foreign_keys=[source_component_id],
    )

    target_component: Mapped["Component"] = relationship(
        back_populates="incoming_connections",
        foreign_keys=[target_component_id],
    )

    def __repr__(self) -> str:
        return (
            f"<Connection id={self.id} "
            f"source={self.source_component_id} "
            f"target={self.target_component_id}>"
        )