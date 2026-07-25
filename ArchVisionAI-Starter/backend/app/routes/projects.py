from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, distinct, func, select
from sqlalchemy.orm import Session, selectinload

from app.database.dependencies import get_db
from app.models import Component, Connection, Project
from app.schemas import (
    ArchitectureModel,
    ProjectCreate,
    ProjectDetail,
    ProjectRename,
    ProjectSummary,
)


router = APIRouter()

DatabaseSession = Annotated[
    Session,
    Depends(get_db),
]


def get_project_or_404(
    project_id: UUID,
    db: Session,
) -> Project:
    statement = (
        select(Project)
        .where(Project.id == project_id)
        .options(
            selectinload(Project.components),
            selectinload(Project.connections),
        )
    )

    project = db.scalar(statement)

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )

    return project


def serialize_project(project: Project) -> dict:
    components = [
        {
            "id": str(component.id),
            "type": component.component_type,
            "name": component.name,
            "technology": component.technology,
            "description": component.description,
            "position": {
                "x": component.position_x,
                "y": component.position_y,
                "z": component.position_z,
            },
            "color": component.color,
            "icon": component.icon,
            "metadata": dict(component.properties or {}),
        }
        for component in project.components
    ]

    connections = []

    for connection in project.connections:
        properties = dict(connection.properties or {})
        direction = properties.pop(
            "direction",
            "unidirectional",
        )

        connections.append(
            {
                "id": str(connection.id),
                "source": str(connection.source_component_id),
                "target": str(connection.target_component_id),
                "connection_type": connection.connection_type,
                "protocol": connection.protocol,
                "direction": direction,
                "label": connection.label,
                "metadata": properties,
            }
        )

    return {
        "id": project.id,
        "name": project.name,
        "description": project.description,
        "status": project.status,
        "schema_version": project.schema_version,
        "component_count": len(project.components),
        "connection_count": len(project.connections),
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "model": {
            "name": project.name,
            "description": project.description,
            "components": components,
            "connections": connections,
        },
    }


def save_architecture_records(
    db: Session,
    project: Project,
    model: ArchitectureModel,
) -> None:
    component_ids: dict[str, UUID] = {}

    for component in model.components:
        if component.id in component_ids:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Duplicate component ID: {component.id}",
            )

        record = Component(
            project_id=project.id,
            name=component.name,
            component_type=component.type,
            technology=component.technology,
            description=component.description,
            position_x=component.position.x,
            position_y=component.position.y,
            position_z=component.position.z,
            color=component.color,
            icon=component.icon,
            properties=dict(component.metadata),
        )

        db.add(record)
        db.flush()

        component_ids[component.id] = record.id

    for connection in model.connections:
        source_id = component_ids.get(connection.source)
        target_id = component_ids.get(connection.target)

        if source_id is None or target_id is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    "Each connection must reference components "
                    "that belong to the project."
                ),
            )

        if source_id == target_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="A component cannot be connected to itself.",
            )

        properties = dict(connection.metadata)
        properties["direction"] = connection.direction

        record = Connection(
            project_id=project.id,
            source_component_id=source_id,
            target_component_id=target_id,
            label=connection.label,
            connection_type=connection.connection_type,
            protocol=connection.protocol,
            properties=properties,
        )

        db.add(record)


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


@router.post(
    "",
    response_model=ProjectDetail,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    project = Project(
        name=project_data.name,
        description=project_data.model.description,
    )

    try:
        db.add(project)
        db.flush()

        save_architecture_records(
            db,
            project,
            project_data.model,
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.expire_all()

    saved_project = get_project_or_404(project.id, db)
    return serialize_project(saved_project)


@router.get(
    "/{project_id}",
    response_model=ProjectDetail,
)
def load_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)
    return serialize_project(project)


@router.put(
    "/{project_id}",
    response_model=ProjectDetail,
)
def save_project(
    project_id: UUID,
    project_data: ProjectCreate,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    try:
        db.execute(
            delete(Connection).where(
                Connection.project_id == project.id
            )
        )

        db.execute(
            delete(Component).where(
                Component.project_id == project.id
            )
        )

        project.name = project_data.name
        project.description = project_data.model.description

        db.flush()

        save_architecture_records(
            db,
            project,
            project_data.model,
        )

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.expire_all()

    saved_project = get_project_or_404(project.id, db)
    return serialize_project(saved_project)


@router.patch(
    "/{project_id}",
    response_model=ProjectSummary,
)
def rename_project(
    project_id: UUID,
    rename_data: ProjectRename,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    project.name = rename_data.name

    try:
        db.commit()
        db.refresh(project)
    except Exception:
        db.rollback()
        raise

    project = get_project_or_404(project_id, db)

    return ProjectSummary(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        schema_version=project.schema_version,
        component_count=len(project.components),
        connection_count=len(project.connections),
        created_at=project.created_at,
        updated_at=project.updated_at,
    )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_project(
    project_id: UUID,
    db: Session = Depends(get_db),
):
    project = get_project_or_404(project_id, db)

    try:
        db.delete(project)
        db.commit()
    except Exception:
        db.rollback()
        raise

    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )