from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models import Component, Connection, Project


@pytest.fixture
def db() -> Session:
    """
    Provide an isolated database session for each model test.

    Tests use flush rather than commit whenever possible. Rolling the session
    back at the end prevents test records from remaining in the configured
    test database.
    """

    session = SessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def create_project(
    db: Session,
    *,
    name: str = "Model Test Project",
) -> Project:
    """Create and flush a project used by model tests."""

    project = Project(
        name=name,
        description="Architecture model test project.",
    )

    db.add(project)
    db.flush()

    return project


def create_component(
    db: Session,
    project: Project,
    *,
    name: str,
    component_type: str,
    position_x: float = 0.0,
    position_y: float = 0.0,
    position_z: float = 0.0,
) -> Component:
    """Create and flush a component associated with a project."""

    component = Component(
        project_id=project.id,
        name=name,
        component_type=component_type,
        position_x=position_x,
        position_y=position_y,
        position_z=position_z,
        properties={},
    )

    db.add(component)
    db.flush()

    return component


def test_project_model_can_be_created(
    db: Session,
) -> None:
    project = Project(
        name="Architecture Project",
        description="A saved architecture.",
    )

    db.add(project)
    db.flush()

    assert isinstance(project.id, UUID)
    assert project.name == "Architecture Project"
    assert project.description == "A saved architecture."
    assert project.status == "draft"
    assert project.schema_version == "1.0"
    assert isinstance(project.created_at, datetime)
    assert isinstance(project.updated_at, datetime)


def test_project_defaults_are_applied(
    db: Session,
) -> None:
    project = Project(
        name="Default Project",
    )

    db.add(project)
    db.flush()

    assert project.description is None
    assert project.status == "draft"
    assert project.schema_version == "1.0"
    assert project.components == []
    assert project.connections == []


def test_project_repr_contains_id_and_name(
    db: Session,
) -> None:
    project = create_project(
        db,
        name="Representation Project",
    )

    representation = repr(project)

    assert str(project.id) in representation
    assert "Representation Project" in representation
    assert representation.startswith("<Project")


def test_component_model_can_be_created(
    db: Session,
) -> None:
    project = create_project(db)

    component = Component(
        project_id=project.id,
        name="React Frontend",
        component_type="frontend",
        technology="React",
        description="Browser-based user interface.",
        position_x=-3.5,
        position_y=1.25,
        position_z=0.5,
        color="#61dafb",
        icon="react",
        properties={
            "framework": "Vite",
            "language": "JavaScript",
        },
    )

    db.add(component)
    db.flush()

    assert isinstance(component.id, UUID)
    assert component.project_id == project.id
    assert component.name == "React Frontend"
    assert component.component_type == "frontend"
    assert component.technology == "React"
    assert component.description == "Browser-based user interface."
    assert component.position_x == pytest.approx(-3.5)
    assert component.position_y == pytest.approx(1.25)
    assert component.position_z == pytest.approx(0.5)
    assert component.color == "#61dafb"
    assert component.icon == "react"
    assert component.properties == {
        "framework": "Vite",
        "language": "JavaScript",
    }
    assert component.project is project
    assert isinstance(component.created_at, datetime)
    assert isinstance(component.updated_at, datetime)


def test_component_defaults_are_applied(
    db: Session,
) -> None:
    project = create_project(db)

    component = Component(
        project_id=project.id,
        name="Backend",
        component_type="backend",
    )

    db.add(component)
    db.flush()

    assert component.technology is None
    assert component.description is None
    assert component.position_x == pytest.approx(0.0)
    assert component.position_y == pytest.approx(0.0)
    assert component.position_z == pytest.approx(0.0)
    assert component.color is None
    assert component.icon is None
    assert component.properties == {}


def test_component_is_added_to_project_relationship(
    db: Session,
) -> None:
    project = create_project(db)

    component = create_component(
        db,
        project,
        name="API Service",
        component_type="backend",
    )

    assert component in project.components
    assert component.project is project


def test_component_repr_contains_identifying_information(
    db: Session,
) -> None:
    project = create_project(db)

    component = create_component(
        db,
        project,
        name="PostgreSQL Database",
        component_type="database",
    )

    representation = repr(component)

    assert str(component.id) in representation
    assert "PostgreSQL Database" in representation
    assert "database" in representation
    assert representation.startswith("<Component")


def test_connection_model_can_be_created(
    db: Session,
) -> None:
    project = create_project(db)

    frontend = create_component(
        db,
        project,
        name="Frontend",
        component_type="frontend",
        position_x=-3.0,
    )
    backend = create_component(
        db,
        project,
        name="Backend",
        component_type="backend",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=frontend.id,
        target_component_id=backend.id,
        label="REST API",
        connection_type="api-call",
        protocol="HTTPS",
        properties={
            "authenticated": True,
        },
    )

    db.add(connection)
    db.flush()

    assert isinstance(connection.id, UUID)
    assert connection.project_id == project.id
    assert connection.source_component_id == frontend.id
    assert connection.target_component_id == backend.id
    assert connection.label == "REST API"
    assert connection.connection_type == "api-call"
    assert connection.protocol == "HTTPS"
    assert connection.properties == {
        "authenticated": True,
    }
    assert connection.project is project
    assert connection.source_component is frontend
    assert connection.target_component is backend
    assert isinstance(connection.created_at, datetime)
    assert isinstance(connection.updated_at, datetime)


def test_connection_defaults_are_applied(
    db: Session,
) -> None:
    project = create_project(db)

    source = create_component(
        db,
        project,
        name="API Service",
        component_type="backend",
    )
    target = create_component(
        db,
        project,
        name="Database",
        component_type="database",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=source.id,
        target_component_id=target.id,
    )

    db.add(connection)
    db.flush()

    assert connection.label is None
    assert connection.connection_type == "dependency"
    assert connection.protocol is None
    assert connection.properties == {}


def test_connection_relationships_are_populated(
    db: Session,
) -> None:
    project = create_project(db)

    source = create_component(
        db,
        project,
        name="Frontend",
        component_type="frontend",
    )
    target = create_component(
        db,
        project,
        name="Backend",
        component_type="backend",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=source.id,
        target_component_id=target.id,
        label="API request",
    )

    db.add(connection)
    db.flush()

    assert connection in project.connections
    assert connection in source.outgoing_connections
    assert connection in target.incoming_connections
    assert connection.source_component is source
    assert connection.target_component is target


def test_connection_repr_contains_source_and_target_ids(
    db: Session,
) -> None:
    project = create_project(db)

    source = create_component(
        db,
        project,
        name="Worker",
        component_type="worker",
    )
    target = create_component(
        db,
        project,
        name="Queue",
        component_type="message-queue",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=source.id,
        target_component_id=target.id,
    )

    db.add(connection)
    db.flush()

    representation = repr(connection)

    assert str(connection.id) in representation
    assert str(source.id) in representation
    assert str(target.id) in representation
    assert representation.startswith("<Connection")


def test_connection_cannot_target_its_source_component(
    db: Session,
) -> None:
    project = create_project(db)

    component = create_component(
        db,
        project,
        name="Single Component",
        component_type="service",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=component.id,
        target_component_id=component.id,
    )

    db.add(connection)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_component_requires_project(
    db: Session,
) -> None:
    component = Component(
        project_id=None,
        name="Orphan Component",
        component_type="service",
    )

    db.add(component)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_connection_requires_source_and_target(
    db: Session,
) -> None:
    project = create_project(db)

    connection = Connection(
        project_id=project.id,
        source_component_id=None,
        target_component_id=None,
    )

    db.add(connection)

    with pytest.raises(IntegrityError):
        db.flush()

    db.rollback()


def test_project_delete_cascades_to_components_and_connections(
    db: Session,
) -> None:
    project = create_project(db)

    source = create_component(
        db,
        project,
        name="Frontend",
        component_type="frontend",
    )
    target = create_component(
        db,
        project,
        name="Backend",
        component_type="backend",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=source.id,
        target_component_id=target.id,
    )

    db.add(connection)
    db.flush()

    project_id = project.id
    source_id = source.id
    target_id = target.id
    connection_id = connection.id

    db.delete(project)
    db.flush()
    db.expire_all()

    assert db.get(Project, project_id) is None
    assert db.get(Component, source_id) is None
    assert db.get(Component, target_id) is None
    assert db.get(Connection, connection_id) is None


def test_deleting_component_removes_connected_connections(
    db: Session,
) -> None:
    project = create_project(db)

    source = create_component(
        db,
        project,
        name="Source",
        component_type="service",
    )
    target = create_component(
        db,
        project,
        name="Target",
        component_type="service",
    )

    connection = Connection(
        project_id=project.id,
        source_component_id=source.id,
        target_component_id=target.id,
    )

    db.add(connection)
    db.flush()

    connection_id = connection.id

    db.delete(source)
    db.flush()
    db.expire_all()

    assert db.get(Connection, connection_id) is None
    assert db.get(Component, target.id) is not None


def test_timestamp_values_are_utc_aware(
    db: Session,
) -> None:
    project = create_project(db)

    assert project.created_at.tzinfo is not None
    assert project.updated_at.tzinfo is not None

    created_offset = project.created_at.utcoffset()
    updated_offset = project.updated_at.utcoffset()

    assert created_offset == timezone.utc.utcoffset(project.created_at)
    assert updated_offset == timezone.utc.utcoffset(project.updated_at)