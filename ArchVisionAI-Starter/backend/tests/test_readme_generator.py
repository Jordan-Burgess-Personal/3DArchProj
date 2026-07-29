from __future__ import annotations

from pathlib import Path

import pytest

from app.schemas import ArchitectureModel, Component, Connection, Position
from app.services.readme_generator import (
    _all_generated_files,
    _backend_setup_section,
    _build_readme,
    _capabilities_section,
    _continuing_development_section,
    _database_setup_section,
    _docker_setup_section,
    _environment_section,
    _environment_variable_names,
    _frontend_setup_section,
    _major_file_descriptions,
    _normalize_path,
    _prerequisites_section,
    _project_structure_section,
    _project_summary,
    _quick_start_section,
    _result_files,
    _supported_technologies,
    _technology_section,
    _tree_from_paths,
    _troubleshooting_section,
    _unique,
    _unsupported_components,
    _unsupported_section,
    generate_readme_file,
)


def architecture(description="Architecture description"):
    return ArchitectureModel(
        name="README Project",
        description=description,
        components=[
            Component(
                id="frontend",
                type="frontend",
                name="Frontend",
                technology="React",
                position=Position(x=0, y=0, z=0),
            ),
            Component(
                id="backend",
                type="backend",
                name="Backend",
                technology="FastAPI",
                position=Position(x=1, y=0, z=0),
            ),
        ],
        connections=[
            Connection(
                id="rest",
                source="frontend",
                target="backend",
                connection_type="api-call",
            )
        ],
    )


def full_results():
    frontend = {
        "frontend_framework": "react",
        "generated_frontend_files": [
            "frontend/src/App.jsx",
            "frontend/src/main.jsx",
            "frontend/src/services/api.js",
        ],
        "generated_frontend_rest_connection_ids": ["rest"],
        "skipped_frontend_components": ["Angular UI"],
    }
    backend = {
        "framework": "fastapi",
        "generated_backend_files": [
            "backend/app/main.py",
            "backend/app/__init__.py",
            "backend/requirements.txt",
        ],
        "generated_backend_rest_connection_ids": ["rest"],
        "skipped_backend_components": ["Unsupported Worker"],
    }
    database = {
        "database_engine": "postgresql",
        "generated_database_files": ["database/init.sql"],
        "skipped_database_components": ["Redis Cache"],
    }
    docker = {
        "docker_generated": True,
        "generated_docker_files": [
            "frontend/Dockerfile",
            "backend/Dockerfile",
            "docker-compose.yml",
            ".env.example",
        ],
    }
    return frontend, backend, database, docker


def test_normalize_path_and_unique():
    assert _normalize_path(r" frontend\src\App.jsx ") == (
        "frontend/src/App.jsx"
    )
    assert _unique(["React", "", "React", None, "Vite"]) == [
        "React", "Vite"
    ]


def test_result_files_normalizes_and_deduplicates():
    result = {
        "files": [
            r"frontend\src\App.jsx",
            "frontend/src/App.jsx",
            "",
        ]
    }
    assert _result_files(result, "files") == ["frontend/src/App.jsx"]


def test_all_generated_files_includes_architecture_first():
    frontend, backend, database, docker = full_results()
    files = _all_generated_files(frontend, backend, database, docker)
    assert files[0] == "architecture.json"
    assert "frontend/src/App.jsx" in files
    assert "backend/requirements.txt" in files
    assert "database/init.sql" in files
    assert "docker-compose.yml" in files


def test_project_summary_uses_description_and_fallback():
    assert _project_summary(architecture()) == "Architecture description"
    assert "starter application generated" in _project_summary(
        architecture(description=None)
    )


def test_supported_technologies_full_stack():
    frontend, backend, database, docker = full_results()
    assert _supported_technologies(
        frontend, backend, database, docker
    ) == [
        "React",
        "Vite",
        "FastAPI",
        "PostgreSQL",
        "Docker",
        "Docker Compose",
    ]


def test_supported_technologies_handles_flask_mysql_without_docker():
    assert _supported_technologies(
        {},
        {"framework": "flask"},
        {"database_engine": "mysql"},
        {"docker_generated": False},
    ) == ["Flask", "MySQL"]


def test_unsupported_components_deduplicates_across_layers():
    assert _unsupported_components(
        {"skipped_frontend_components": ["Shared", "Angular"]},
        {"skipped_backend_components": ["Shared", "Worker"]},
        {"skipped_database_components": ["Redis"]},
    ) == ["Shared", "Angular", "Worker", "Redis"]


def test_technology_section_with_and_without_technologies():
    empty = _technology_section([])
    assert "No implementation-specific technology files" in empty
    section = _technology_section(["React", "FastAPI"])
    assert "| **React** |" in section
    assert "| **FastAPI** |" in section


def test_prerequisites_section_selects_required_tools():
    section = _prerequisites_section(
        ["React", "FastAPI", "Docker"]
    )
    assert "Node.js 20 LTS" in section
    assert "Python 3.11" in section
    assert "Docker Compose v2" in section


def test_prerequisites_section_without_runtime():
    assert "No additional runtime prerequisites" in (
        _prerequisites_section([])
    )


@pytest.mark.parametrize(
    ("engine", "variables"),
    [
        (
            "postgresql",
            {"DATABASE_URL", "POSTGRES_DB", "POSTGRES_USER",
             "POSTGRES_PASSWORD", "POSTGRES_PORT"},
        ),
        (
            "mysql",
            {"DATABASE_URL", "MYSQL_DATABASE", "MYSQL_USER",
             "MYSQL_PASSWORD", "MYSQL_ROOT_PASSWORD", "MYSQL_PORT"},
        ),
        (
            "mongodb",
            {"MONGODB_URL", "MONGO_INITDB_DATABASE",
             "MONGO_INITDB_ROOT_USERNAME",
             "MONGO_INITDB_ROOT_PASSWORD", "MONGO_PORT"},
        ),
        ("sqlite", {"DATABASE_URL"}),
    ],
)
def test_environment_variable_names(engine, variables):
    names = set(_environment_variable_names("react", engine, True))
    assert "VITE_API_BASE_URL" in names
    assert variables <= names


def test_environment_variable_names_without_docker():
    assert _environment_variable_names(
        "react", "postgresql", False
    ) == []


def test_environment_section():
    section = _environment_section("react", "postgresql", True)
    assert "Copy-Item .env.example .env" in section
    assert "copy .env.example .env" in section
    assert "cp .env.example .env" in section
    assert "`POSTGRES_DB`" in section


def test_environment_section_without_docker():
    assert "No `.env.example` file was generated" in (
        _environment_section("react", "postgresql", False)
    )


def test_frontend_setup_section():
    assert "npm install" in _frontend_setup_section("react")
    assert _frontend_setup_section(None) == ""


@pytest.mark.parametrize(
    ("framework", "command", "url"),
    [
        ("fastapi", "uvicorn app.main:app --reload", "localhost:8000"),
        ("flask", "python -m app.main", "localhost:5000"),
    ],
)
def test_backend_setup_section(framework, command, url):
    section = _backend_setup_section(framework)
    assert command in section
    assert url in section
    assert "backend/requirements.txt" in section


def test_backend_setup_section_unsupported():
    assert _backend_setup_section("django") == ""


@pytest.mark.parametrize(
    ("engine", "expected"),
    [
        ("postgresql", "database/init.sql"),
        ("mysql", "database/init.sql"),
        ("mongodb", "database/init.js"),
        ("sqlite", "does not require a separately running database server"),
    ],
)
def test_database_setup_section(engine, expected):
    assert expected in _database_setup_section(engine, True)


def test_docker_setup_section():
    section = _docker_setup_section(True)
    assert "docker compose up --build" in section
    assert "docker compose down -v" in section
    assert _docker_setup_section(False) == ""


def test_quick_start_docker_and_manual():
    assert "docker compose up --build" in _quick_start_section(
        "react", "fastapi", "postgresql", True
    )
    manual = _quick_start_section(
        "react", "fastapi", "postgresql", False
    )
    assert "backend virtual environment" in manual
    assert "npm install" in manual
    assert "PostgreSQL server" in manual


def test_tree_from_paths_and_project_structure():
    tree = _tree_from_paths(
        [
            "architecture.json",
            "frontend/src/App.jsx",
            "backend/app/main.py",
        ]
    )
    assert tree.startswith(".")
    assert "README.md" in tree
    assert "frontend/" in tree
    assert "App.jsx" in tree

    section = _project_structure_section(
        ["architecture.json", "frontend/src/App.jsx"]
    )
    assert "Generated Project Structure" in section
    assert "primary user interface" in section


def test_major_file_descriptions():
    descriptions = _major_file_descriptions(
        [
            "frontend/src/services/api.js",
            "backend/requirements.txt",
            "database/init.sql",
            "docker-compose.yml",
            ".env.example",
        ]
    )
    joined = "\n".join(descriptions)
    assert "REST API client" in joined
    assert "required Python packages" in joined
    assert "database initialization" in joined
    assert "coordinates generated services" in joined


def test_unsupported_section():
    assert _unsupported_section([]) == ""
    section = _unsupported_section(["Angular UI", "Redis"])
    assert "Angular UI" in section
    assert "Redis" in section


def test_troubleshooting_section_is_contextual():
    section = _troubleshooting_section("react", "fastapi", True)
    assert "Python packages cannot be imported" in section
    assert "Frontend dependencies are missing" in section
    assert "Docker services do not start" in section


def test_continuing_development_section_is_contextual():
    section = _continuing_development_section(
        "react", "fastapi", "postgresql"
    )
    assert "frontend pages" in section
    assert "application-specific routes" in section
    assert "database schema" in section


def test_capabilities_section_reports_generated_layers():
    frontend, backend, database, docker = full_results()
    section = _capabilities_section(
        architecture(), frontend, backend, database, docker
    )
    assert "2 component(s)" in section
    assert "1 connection(s)" in section
    assert "frontend starter" in section
    assert "backend service" in section
    assert "REST route scaffolding" in section
    assert "database initialization script" in section
    assert "Docker and Docker Compose" in section


def test_build_readme_full_stack():
    frontend, backend, database, docker = full_results()
    markdown, technologies, sections = _build_readme(
        architecture(), frontend, backend, database, docker
    )
    assert markdown.startswith("# README Project")
    assert "Architecture description" in markdown
    assert "## Quick Start" in markdown
    assert "## Environment Configuration" in markdown
    assert "## Architecture Components Not Implemented" in markdown
    assert technologies == [
        "React", "Vite", "FastAPI", "PostgreSQL",
        "Docker", "Docker Compose"
    ]
    assert "Project Summary" in sections
    assert "Docker Setup" in sections


def test_generate_readme_file(tmp_path: Path):
    frontend, backend, database, docker = full_results()
    result = generate_readme_file(
        tmp_path,
        architecture(),
        frontend,
        backend,
        database,
        docker,
    )
    readme = tmp_path / "README.md"
    assert readme.is_file()
    assert result["generated_readme_files"] == ["README.md"]
    assert "React" in result["documented_technologies"]
    assert "Project Summary" in result["generated_readme_sections"]
    content = readme.read_text(encoding="utf-8")
    assert "# README Project" in content
    assert "docker compose up --build" in content


def test_generate_readme_file_overwrites_existing_file(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("stale", encoding="utf-8")
    generate_readme_file(
        tmp_path, architecture(), {}, {}, {}, {"docker_generated": False}
    )
    assert readme.read_text(encoding="utf-8") != "stale"