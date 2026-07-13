import uuid

from app.database.database import SessionLocal
from app.models import Component, Connection, Project


def test_project_model_can_be_created():
    db = SessionLocal()

    try:
        project = Project(
            name="Test Architecture",
            description="Test project",
        )

        db.add(project)
        db.flush()

        assert project.id is not None
        assert project.name == "Test Architecture"
        assert project.description == "Test project"
        assert project.status == "draft"
        assert project.schema_version == "1.0"
        assert project.created_at is not None
        assert project.updated_at is not None

        db.rollback()

    finally:
        db.close()


def test_component_model_can_be_created():
    db = SessionLocal()

    try:
        project = Project(
            name="Component Test",
        )

        db.add(project)
        db.flush()

        component = Component(
            project_id=project.id,
            name="React Frontend",
            component_type="frontend",
            technology="React",
            description="Frontend application",
            position_x=0,
            position_y=1,
            position_z=2,
            color="#61DAFB",
            icon="react",
            properties={}
        )

        db.add(component)
        db.flush()

        assert component.id is not None
        assert component.project_id == project.id
        assert component.name == "React Frontend"
        assert component.component_type == "frontend"
        assert component.technology == "React"
        assert component.position_x == 0
        assert component.position_y == 1
        assert component.position_z == 2
        assert component.created_at is not None
        assert component.updated_at is not None

        db.rollback()

    finally:
        db.close()


def test_connection_model_can_be_created():
    db = SessionLocal()

    try:
        project = Project(
            name="Connection Test",
        )

        db.add(project)
        db.flush()

        frontend = Component(
            project_id=project.id,
            name="Frontend",
            component_type="frontend",
            position_x=0,
            position_y=0,
            position_z=0,
            properties={}
        )

        backend = Component(
            project_id=project.id,
            name="Backend",
            component_type="backend",
            position_x=5,
            position_y=0,
            position_z=0,
            properties={}
        )

        db.add_all([frontend, backend])
        db.flush()

        connection = Connection(
            project_id=project.id,
            source_component_id=frontend.id,
            target_component_id=backend.id,
            label="HTTPS",
            protocol="HTTPS",
            properties={}
        )

        db.add(connection)
        db.flush()

        assert connection.id is not None
        assert connection.project_id == project.id
        assert connection.source_component_id == frontend.id
        assert connection.target_component_id == backend.id
        assert connection.label == "HTTPS"
        assert connection.protocol == "HTTPS"
        assert connection.connection_type == "data-flow"
        assert connection.created_at is not None
        assert connection.updated_at is not None

        db.rollback()

    finally:
        db.close()


def test_component_relationships():
    db = SessionLocal()

    try:
        project = Project(
            name="Relationship Test",
        )

        db.add(project)
        db.flush()

        frontend = Component(
            project_id=project.id,
            name="Frontend",
            component_type="frontend",
            position_x=0,
            position_y=0,
            position_z=0,
            properties={}
        )

        backend = Component(
            project_id=project.id,
            name="Backend",
            component_type="backend",
            position_x=5,
            position_y=0,
            position_z=0,
            properties={}
        )

        db.add_all([frontend, backend])
        db.flush()

        connection = Connection(
            project_id=project.id,
            source_component_id=frontend.id,
            target_component_id=backend.id,
            properties={}
        )

        db.add(connection)
        db.flush()

        db.refresh(project)
        db.refresh(frontend)
        db.refresh(backend)

        assert len(project.components) == 2
        assert len(project.connections) == 1

        assert len(frontend.outgoing_connections) == 1
        assert len(frontend.incoming_connections) == 0

        assert len(backend.incoming_connections) == 1
        assert len(backend.outgoing_connections) == 0

        db.rollback()

    finally:
        db.close()