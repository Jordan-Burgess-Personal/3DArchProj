from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from app.schemas import ArchitectureModel, Component, Connection, Position
from app.services import docker_generator
from app.services.docker_generator import (
    _backend_dockerfile_content,
    _backend_dockerignore_content,
    _backend_environment,
    _build_component_service_map,
    _build_service_dependencies,
    _compose_content,
    _connection_source,
    _connection_target,
    _database_service,
    _depends_on_block,
    _env_example_content,
    _frontend_dockerfile_content,
    _frontend_dockerignore_content,
    generate_docker_files,
    is_dependency_connection,
)


def component(component_id, component_type, name, technology):
    return Component(
        id=component_id,
        type=component_type,
        name=name,
        technology=technology,
        position=Position(x=0, y=0, z=0),
    )


def connection(
    connection_id,
    source,
    target,
    connection_type="dependency",
):
    return Connection(
        id=connection_id,
        source=source,
        target=target,
        connection_type=connection_type,
    )


def model(components=(), connections=()):
    return ArchitectureModel(
        name="Docker Test",
        components=list(components),
        connections=list(connections),
    )


def normalize(paths):
    return {str(path).replace("\\", "/") for path in paths}


@pytest.mark.parametrize(
    ("framework", "port", "command"),
    [
        ("fastapi", "EXPOSE 8000", "uvicorn"),
        ("flask", "EXPOSE 5000", 'python", "-m", "app.main'),
    ],
)
def test_backend_dockerfile_content(framework, port, command):
    content = _backend_dockerfile_content(framework)
    assert "FROM python:3.12-slim" in content
    assert "COPY requirements.txt" in content
    assert port in content
    assert command in content


def test_frontend_dockerfile_content():
    content = _frontend_dockerfile_content()
    assert "FROM node:22-alpine" in content
    assert "RUN npm install" in content
    assert "EXPOSE 5173" in content
    assert '--host", "0.0.0.0"' in content


def test_dockerignore_contents():
    assert "__pycache__" in _backend_dockerignore_content()
    assert ".venv" in _backend_dockerignore_content()
    assert "node_modules" in _frontend_dockerignore_content()
    assert "dist" in _frontend_dockerignore_content()


@pytest.mark.parametrize(
    ("engine", "image", "volume"),
    [
        ("postgresql", "postgres:17-alpine", "database_data"),
        ("mysql", "mysql:8.4", "database_data"),
        ("mongodb", "mongo:8", "database_data"),
    ],
)
def test_database_service(engine, image, volume):
    block, volume_name = _database_service(engine)
    assert image in block
    assert "healthcheck:" in block
    assert volume_name == volume


def test_database_service_for_sqlite_is_empty():
    assert _database_service("sqlite") == ("", "")


@pytest.mark.parametrize(
    ("engine", "expected"),
    [
        ("postgresql", "postgresql://"),
        ("mysql", "mysql+pymysql://"),
        ("mongodb", "mongodb://"),
        ("sqlite", "sqlite:///"),
        (None, None),
    ],
)
def test_backend_environment(engine, expected):
    values = _backend_environment(engine)
    if expected is None:
        assert values == []
    else:
        assert expected in values[0]


def test_connection_endpoint_helpers_support_schema_variants():
    current = SimpleNamespace(source="a", target="b")
    old = SimpleNamespace(source_id="c", target_id="d")
    database = SimpleNamespace(
        source_component_id="e", target_component_id="f"
    )
    assert _connection_source(current) == "a"
    assert _connection_target(current) == "b"
    assert _connection_source(old) == "c"
    assert _connection_target(old) == "d"
    assert _connection_source(database) == "e"
    assert _connection_target(database) == "f"


def test_dependency_connection_detection():
    assert is_dependency_connection(
        SimpleNamespace(connection_type=" Dependency ")
    )
    assert is_dependency_connection(SimpleNamespace(type="dependency"))
    assert not is_dependency_connection(
        SimpleNamespace(connection_type="api-call")
    )


def test_build_component_service_map():
    assert _build_component_service_map("front", "back", "db") == {
        "front": "frontend",
        "back": "backend",
        "db": "database",
    }
    assert _build_component_service_map(None, "back", None) == {
        "back": "backend"
    }


def test_build_service_dependencies():
    architecture = model(
        connections=[
            connection("front-back", "front", "back"),
            connection("back-db", "back", "db"),
            connection("ignored", "front", "missing"),
            connection("api", "front", "back", "api-call"),
        ]
    )
    dependencies, ids = _build_service_dependencies(
        architecture,
        {"front": "frontend", "back": "backend", "db": "database"},
    )
    assert dependencies == {
        "frontend": {"backend"},
        "backend": {"database"},
    }
    assert ids == ["front-back", "back-db"]


def test_build_service_dependencies_deduplicates_dependency_targets():
    architecture = model(
        connections=[
            connection("one", "back", "db"),
            connection("two", "back", "db"),
        ]
    )
    dependencies, ids = _build_service_dependencies(
        architecture, {"back": "backend", "db": "database"}
    )
    assert dependencies["backend"] == {"database"}
    assert ids == ["one", "two"]


def test_depends_on_block_uses_health_condition_for_container_database():
    block = _depends_on_block({"database"}, "postgresql")
    assert "database:" in block
    assert "condition: service_healthy" in block


def test_depends_on_block_uses_list_for_non_database_dependency():
    block = _depends_on_block({"backend"}, "postgresql")
    assert "- backend" in block


def test_compose_content_full_stack_postgresql():
    content = _compose_content(
        "react",
        "fastapi",
        "postgresql",
        {"frontend": {"backend"}, "backend": {"database"}},
    )
    assert "frontend:" in content
    assert "backend:" in content
    assert "database:" in content
    assert "postgres:17-alpine" in content
    assert "DATABASE_URL: postgresql://" in content
    assert "volumes:" in content
    assert "database_data:" in content


def test_compose_content_sqlite_has_no_database_service():
    content = _compose_content(None, "flask", "sqlite")
    assert "backend:" in content
    assert "DATABASE_URL: sqlite:///./database/app.db" in content
    assert "\n  database:" not in content


def test_compose_content_empty_uses_placeholder_service():
    content = _compose_content(None, None, None)

    assert content.startswith(
        "name: generated-archvision-project"
    )
    assert "services:" in content
    assert "placeholder:" in content
    assert "image: alpine:3.21" in content
    assert "No supported services were detected" in content


@pytest.mark.parametrize(
    ("frontend", "backend", "database", "expected"),
    [
        ("react", "fastapi", "postgresql", "POSTGRES_DB=app_db"),
        ("react", "flask", "mysql", "MYSQL_DATABASE=app_db"),
        (None, "fastapi", "mongodb", "MONGO_INITDB_DATABASE=app_db"),
        (None, "fastapi", "sqlite", "DATABASE_URL=sqlite:///"),
    ],
)
def test_env_example_content(frontend, backend, database, expected):
    content = _env_example_content(frontend, backend, database)
    assert expected in content
    if frontend:
        assert "VITE_API_BASE_URL=" in content
    if backend:
        assert "BACKEND_PORT=" in content


def test_generate_docker_files_full_stack(monkeypatch, tmp_path):
    frontend = component("front", "frontend", "Web", "React")
    backend = component("back", "backend", "API", "FastAPI")
    database = component("db", "database", "Data", "PostgreSQL")
    architecture = model(
        [frontend, backend, database],
        [
            connection("front-back", "front", "back"),
            connection("back-db", "back", "db"),
        ],
    )

    monkeypatch.setattr(
        docker_generator,
        "find_supported_frontend",
        lambda model: (frontend, "react"),
    )
    monkeypatch.setattr(
        docker_generator,
        "find_supported_backend",
        lambda model: (backend, "fastapi"),
    )
    monkeypatch.setattr(
        docker_generator,
        "find_supported_database",
        lambda model: (database, "postgresql"),
    )

    result = generate_docker_files(tmp_path, architecture)

    expected = {
        "frontend/Dockerfile",
        "frontend/.dockerignore",
        "backend/Dockerfile",
        "backend/.dockerignore",
        "docker-compose.yml",
        ".env.example",
    }
    assert result["docker_generated"] is True
    assert normalize(result["generated_docker_files"]) == expected
    assert result["docker_dependency_connection_ids"] == [
        "front-back", "back-db"
    ]
    assert result["docker_service_dependencies"] == {
        "frontend": ["backend"],
        "backend": ["database"],
    }
    for relative in expected:
        assert (tmp_path / relative).is_file()


def test_generate_docker_files_without_supported_services(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(
        docker_generator,
        "find_supported_frontend",
        lambda model: (None, None),
    )
    monkeypatch.setattr(
        docker_generator,
        "find_supported_backend",
        lambda model: (None, None),
    )
    monkeypatch.setattr(
        docker_generator,
        "find_supported_database",
        lambda model: (None, None),
    )

    result = generate_docker_files(tmp_path, model())

    assert result["docker_generated"] is True
    assert result["docker_frontend_framework"] is None
    assert result["docker_backend_framework"] is None
    assert result["docker_database_engine"] is None
    assert result["docker_frontend_component_id"] is None
    assert result["docker_backend_component_id"] is None
    assert result["docker_database_component_id"] is None
    assert result["docker_dependency_connection_ids"] == []
    assert result["docker_service_dependencies"] == {}
    assert normalize(result["generated_docker_files"]) == {
        "docker-compose.yml",
        ".env.example",
    }

    compose_file = tmp_path / "docker-compose.yml"
    env_file = tmp_path / ".env.example"

    assert compose_file.is_file()
    assert env_file.is_file()

    compose_content = compose_file.read_text(encoding="utf-8")
    env_content = env_file.read_text(encoding="utf-8")

    assert "placeholder:" in compose_content
    assert "image: alpine:3.21" in compose_content
    assert "No supported services were detected" in compose_content
    assert env_content == "# Generated by ArchVision AI\n"