from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import distinct, func, select
from sqlalchemy.orm import Session

from app.database.dependencies import get_db
from app.models import Component, Connection, Project
from app.schemas import ProjectSummary


router = APIRouter()

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


@router.get(
    "",
    response_model=list[ProjectSummary],
    summary="List project summaries",
)
def list_projects(
    db: DatabaseSession,
) -> list[ProjectSummary]:
    """
    Return lightweight summary information for all saved projects.

    The project-management interface only needs summary information
    when displaying the project list. The complete component and
    connection data will be retrieved by the dedicated project-loading
    endpoint in a later Jira story.

    Projects are ordered with the most recently updated project first.
    """

    statement = (
        select(
            Project.id,
            Project.name,
            Project.description,
            Project.status,
            Project.schema_version,
            Project.created_at,
            Project.updated_at,
            func.count(
                distinct(Component.id),
            ).label("component_count"),
            func.count(
                distinct(Connection.id),
            ).label("connection_count"),
        )
        .outerjoin(
            Component,
            Component.project_id == Project.id,
        )
        .outerjoin(
            Connection,
            Connection.project_id == Project.id,
        )
        .group_by(
            Project.id,
            Project.name,
            Project.description,
            Project.status,
            Project.schema_version,
            Project.created_at,
            Project.updated_at,
        )
        .order_by(
            Project.updated_at.desc(),
            Project.name.asc(),
        )
    )

    rows = db.execute(statement).all()

    return [
        ProjectSummary(
            id=row.id,
            name=row.name,
            description=row.description,
            status=row.status,
            schema_version=row.schema_version,
            component_count=row.component_count,
            connection_count=row.connection_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]