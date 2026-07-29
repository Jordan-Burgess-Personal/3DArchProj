from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.routes import export


@pytest.fixture
def client() -> TestClient:
    """
    Create a small test application containing only the export router.

    The production application registers this router with the "/api" prefix,
    so the complete endpoint under test is "/api/export/starter".
    """

    app = FastAPI()
    app.include_router(
        export.router,
        prefix="/api",
    )

    return TestClient(app)


@pytest.fixture
def architecture_payload() -> dict:
    """Return a valid full-stack architecture request."""

    return {
        "name": "Full Stack Export",
        "description": "Generated project export test.",
        "components": [
            {
                "id": "frontend-1",
                "type": "frontend",
                "name": "React Frontend",
                "technology": "React",
                "description": "Generated web client.",
                "position": {"x": -3, "y": 0, "z": 0},
                "metadata": {},
            },
            {
                "id": "backend-1",
                "type": "backend",
                "name": "FastAPI Backend",
                "technology": "FastAPI",
                "description": "Generated API service.",
                "position": {"x": 0, "y": 0, "z": 0},
                "metadata": {},
            },
            {
                "id": "database-1",
                "type": "database",
                "name": "PostgreSQL Database",
                "technology": "PostgreSQL",
                "description": "Generated database service.",
                "position": {"x": 3, "y": 0, "z": 0},
                "metadata": {},
            },
        ],
        "connections": [
            {
                "id": "connection-1",
                "source": "frontend-1",
                "target": "backend-1",
                "connection_type": "api-call",
                "protocol": "HTTPS",
                "direction": "unidirectional",
                "label": "REST API",
                "metadata": {},
            },
            {
                "id": "connection-2",
                "source": "backend-1",
                "target": "database-1",
                "connection_type": "dependency",
                "protocol": None,
                "direction": "unidirectional",
                "label": "Database dependency",
                "metadata": {},
            },
        ],
    }


def create_generated_project(tmp_path: Path) -> Path:
    """Create a representative generated project directory."""

    project_directory = tmp_path / "generated-project"
    backend_directory = project_directory / "backend"
    frontend_directory = project_directory / "frontend"
    database_directory = project_directory / "database"

    backend_directory.mkdir(parents=True)
    frontend_directory.mkdir(parents=True)
    database_directory.mkdir(parents=True)

    (project_directory / "README.md").write_text(
        "# Generated Project\n",
        encoding="utf-8",
    )
    (project_directory / "docker-compose.yml").write_text(
        "services: {}\n",
        encoding="utf-8",
    )
    (backend_directory / "requirements.txt").write_text(
        "fastapi\nuvicorn\n",
        encoding="utf-8",
    )
    (frontend_directory / "package.json").write_text(
        '{"name": "generated-frontend"}\n',
        encoding="utf-8",
    )
    (database_directory / "init.sql").write_text(
        "SELECT 1;\n",
        encoding="utf-8",
    )

    return project_directory


def archive_names(response_content: bytes) -> set[str]:
    """Return normalized member names from a ZIP response."""

    with ZipFile(BytesIO(response_content)) as archive:
        return {
            name.replace("\\", "/")
            for name in archive.namelist()
        }


def test_export_starter_returns_zip_download(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_directory = create_generated_project(tmp_path)
    captured_model = None

    def fake_create_project_structure(model):
        nonlocal captured_model
        captured_model = model
        return {"project_path": str(project_directory)}

    monkeypatch.setattr(
        export,
        "create_project_structure",
        fake_create_project_structure,
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert "attachment" in response.headers["content-disposition"]
    assert "full-stack-export.zip" in response.headers["content-disposition"]
    assert response.headers["cache-control"] == "no-store"
    assert response.content.startswith(b"PK")

    assert captured_model is not None
    assert captured_model.name == "Full Stack Export"
    assert len(captured_model.components) == 3
    assert len(captured_model.connections) == 2


def test_export_zip_contains_generated_project_files(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_directory = create_generated_project(tmp_path)

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(project_directory)},
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 200

    names = archive_names(response.content)

    assert "generated-project/README.md" in names
    assert "generated-project/docker-compose.yml" in names
    assert "generated-project/backend/requirements.txt" in names
    assert "generated-project/frontend/package.json" in names
    assert "generated-project/database/init.sql" in names


def test_export_uses_slugified_project_name_for_filename(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_directory = create_generated_project(tmp_path)
    architecture_payload["name"] = "  My ArchVision Project!  "

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(project_directory)},
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 200
    assert "my-archvision-project.zip" in response.headers["content-disposition"]


def test_export_accepts_architecture_without_components(
    client: TestClient,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_directory = create_generated_project(tmp_path)

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(project_directory)},
    )

    response = client.post(
        "/api/export/starter",
        json={
            "name": "Empty Architecture",
            "description": "",
            "components": [],
            "connections": [],
        },
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    assert response.content.startswith(b"PK")


def test_export_rejects_invalid_architecture_payload(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/export/starter",
        json={
            "name": "Invalid Architecture",
            "components": [
                {
                    "id": "",
                    "type": "not-a-component-type",
                    "name": "",
                }
            ],
            "connections": [],
        },
    )

    assert response.status_code == 422


def test_export_returns_500_when_generator_omits_project_path(
    client: TestClient,
    architecture_payload: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {},
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to generate the project archive.",
    }


def test_export_returns_500_when_project_directory_is_missing(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    missing_directory = tmp_path / "missing-project"

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(missing_directory)},
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to generate the project archive.",
    }


def test_export_returns_500_when_project_path_is_a_file(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    file_path = tmp_path / "not-a-directory.txt"
    file_path.write_text(
        "This is not a generated project directory.",
        encoding="utf-8",
    )

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(file_path)},
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to generate the project archive.",
    }


def test_export_returns_500_when_archive_creation_fails(
    client: TestClient,
    architecture_payload: dict,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    project_directory = create_generated_project(tmp_path)

    monkeypatch.setattr(
        export,
        "create_project_structure",
        lambda model: {"project_path": str(project_directory)},
    )

    def fail_archive_creation(*args, **kwargs):
        raise OSError("Unable to create archive.")

    monkeypatch.setattr(
        export.shutil,
        "make_archive",
        fail_archive_creation,
    )

    response = client.post(
        "/api/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 500
    assert response.json() == {
        "detail": "Unable to generate the project archive.",
    }


def test_old_export_path_is_not_registered(
    client: TestClient,
    architecture_payload: dict,
) -> None:
    response = client.post(
        "/export/starter",
        json=architecture_payload,
    )

    assert response.status_code == 404