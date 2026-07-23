from __future__ import annotations

from fastapi.testclient import TestClient

from app.database.database import SessionLocal
from app.main import app
from app.models import Component, Connection, Project


client = TestClient(app)


def test_list_projects_returns_database_project_summaries():
    db = SessionLocal()

    project = Project(
        name="Project Summary Test",
        description="Project used to test the project summary endpoint.",
    )

    try:
        db.add(project)
        db.flush()

        frontend = Component(
            project_id=project.id,
            name="React Frontend",
            component_type="frontend",
            technology="React",
            description="Frontend application",
            position_x=0,
            position_y=0.6,
            position_z=0,
            color="#0d9488",
            icon="Globe",
            properties={},
        )

        backend = Component(
            project_id=project.id,
            name="FastAPI Backend",
            component_type="backend",
            technology="FastAPI",
            description="Backend API",
            position_x=3,
            position_y=0.6,
            position_z=0,
            color="#1d4ed8",
            icon="Server",
            properties={},
        )

        db.add_all(
            [
                frontend,
                backend,
            ],
        )
        db.flush()

        connection = Connection(
            project_id=project.id,
            source_component_id=frontend.id,
            target_component_id=backend.id,
            label="REST API",
            connection_type="api-call",
            protocol="HTTPS",
            properties={},
        )

        db.add(connection)
        db.commit()

        project_id = str(project.id)

        response = client.get(
            "/api/projects",
        )

        assert response.status_code == 200

        projects = response.json()

        matching_project = next(
            (
                project_record
                for project_record in projects
                if project_record["id"] == project_id
            ),
            None,
        )

        assert matching_project is not None
        assert (
            matching_project["name"]
            == "Project Summary Test"
        )
        assert (
            matching_project["description"]
            == "Project used to test the project summary endpoint."
        )
        assert matching_project["status"] == "draft"
        assert (
            matching_project["schema_version"]
            == "1.0"
        )
        assert (
            matching_project["component_count"]
            == 2
        )
        assert (
            matching_project["connection_count"]
            == 1
        )
        assert matching_project["created_at"]
        assert matching_project["updated_at"]

    finally:
        persisted_project = db.get(
            Project,
            project.id,
        )

        if persisted_project is not None:
            db.delete(persisted_project)
            db.commit()

        db.close()


def test_list_projects_returns_an_array():
    response = client.get(
        "/api/projects",
    )

    assert response.status_code == 200
    assert isinstance(
        response.json(),
        list,
    )


def test_project_summary_uses_unique_project_identifier():
    db = SessionLocal()

    first_project = Project(
        name="Duplicate Display Name",
    )

    second_project = Project(
        name="Duplicate Display Name",
    )

    try:
        db.add_all(
            [
                first_project,
                second_project,
            ],
        )
        db.commit()

        first_project_id = str(
            first_project.id,
        )

        second_project_id = str(
            second_project.id,
        )

        response = client.get(
            "/api/projects",
        )

        assert response.status_code == 200

        projects = response.json()

        matching_projects = [
            project_record
            for project_record in projects
            if project_record["name"]
            == "Duplicate Display Name"
        ]

        returned_ids = {
            project_record["id"]
            for project_record in matching_projects
        }

        assert first_project_id in returned_ids
        assert second_project_id in returned_ids
        assert (
            first_project_id
            != second_project_id
        )

    finally:
        for project in [
            first_project,
            second_project,
        ]:
            persisted_project = db.get(
                Project,
                project.id,
            )

            if persisted_project is not None:
                db.delete(
                    persisted_project,
                )

        db.commit()
        db.close()