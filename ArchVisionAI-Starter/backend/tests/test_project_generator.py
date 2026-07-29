from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.schemas import ArchitectureModel, Component, Position
from app.services import project_generator
from app.services.project_generator import (
    _collect_generated_project_files,
    _normalize_generated_files,
    create_project_structure,
    slugify,
)


def model(name="Example Project"):
    return ArchitectureModel(
        name=name,
        description="Generated project",
        components=[
            Component(
                id="frontend",
                type="frontend",
                name="Web",
                technology="React",
                position=Position(x=0, y=0, z=0),
            )
        ],
        connections=[],
    )


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("Example Project", "example-project"),
        ("  Example Project  ", "example-project"),
        ("Project_Name", "project_name"),
        ("Project--Name", "project--name"),
        ("Hello! World?", "hello-world"),
        ("***", "archvision-project"),
    ],
)
def test_slugify(name, expected):
    assert slugify(name) == expected


def test_normalize_generated_files_deduplicates_and_preserves_order():
    assert _normalize_generated_files(
        [
            "architecture.json",
            r"frontend\src\App.jsx",
            "architecture.json",
            "",
            None,
            "README.md",
        ]
    ) == [
        "architecture.json",
        "frontend/src/App.jsx",
        "README.md",
    ]


def test_collect_generated_project_files():
    result = _collect_generated_project_files(
        ["architecture.json"],
        {"generated_frontend_files": ["frontend/src/App.jsx"]},
        {
            "generated_backend_files": [
                "backend/app/main.py",
                "backend/requirements.txt",
            ]
        },
        {"generated_database_files": ["database/init.sql"]},
        {
            "generated_docker_files": [
                "docker-compose.yml",
                "architecture.json",
            ]
        },
        {"generated_readme_files": ["README.md"]},
    )
    assert result == [
        "architecture.json",
        "frontend/src/App.jsx",
        "backend/app/main.py",
        "backend/requirements.txt",
        "database/init.sql",
        "docker-compose.yml",
        "README.md",
    ]


def test_create_project_structure_coordinates_generators(
    monkeypatch, tmp_path
):
    architecture = model("Coordinated Project")
    monkeypatch.setattr(project_generator, "BASE_OUTPUT", tmp_path)

    calls = []

    def frontend(project_dir, supplied_model):
        calls.append(("frontend", project_dir, supplied_model))
        (project_dir / "frontend").mkdir(exist_ok=True)
        (project_dir / "frontend" / "App.jsx").write_text(
            "app", encoding="utf-8"
        )
        return {
            "frontend_framework": "react",
            "generated_frontend_files": ["frontend/App.jsx"],
            "skipped_frontend_components": [],
        }

    def backend(project_dir, supplied_model):
        calls.append(("backend", project_dir, supplied_model))
        return {
            "framework": "fastapi",
            "generated_backend_files": [
                "backend/app/main.py",
                "backend/requirements.txt",
            ],
            "skipped_backend_components": [],
        }

    def database(project_dir, supplied_model):
        calls.append(("database", project_dir, supplied_model))
        return {
            "database_engine": "postgresql",
            "generated_database_files": ["database/init.sql"],
            "skipped_database_components": [],
        }

    def docker(project_dir, supplied_model):
        calls.append(("docker", project_dir, supplied_model))
        return {
            "docker_generated": True,
            "generated_docker_files": [
                "docker-compose.yml",
                ".env.example",
            ],
        }

    def readme(
        project_dir,
        supplied_model,
        frontend_result,
        backend_result,
        database_result,
        docker_result,
    ):
        calls.append(("readme", project_dir, supplied_model))
        (project_dir / "README.md").write_text("readme", encoding="utf-8")
        return {
            "generated_readme_files": ["README.md"],
            "documented_technologies": [
                "React", "Vite", "FastAPI", "PostgreSQL", "Docker"
            ],
            "generated_readme_sections": [
                "Project Summary", "Quick Start"
            ],
        }

    monkeypatch.setattr(project_generator, "generate_frontend_files", frontend)
    monkeypatch.setattr(project_generator, "generate_backend_files", backend)
    monkeypatch.setattr(project_generator, "generate_database_files", database)
    monkeypatch.setattr(project_generator, "generate_docker_files", docker)
    monkeypatch.setattr(project_generator, "generate_readme_file", readme)

    result = create_project_structure(architecture)
    project_path = tmp_path / "coordinated-project"

    assert result["project_path"] == str(project_path)
    assert [entry[0] for entry in calls] == [
        "frontend", "backend", "database", "docker", "readme"
    ]
    assert all(entry[1] == project_path for entry in calls)
    assert all(entry[2] is architecture for entry in calls)

    architecture_json = json.loads(
        (project_path / "architecture.json").read_text(encoding="utf-8")
    )
    assert architecture_json["name"] == "Coordinated Project"
    assert architecture_json["components"][0]["id"] == "frontend"

    assert result["generated_project_files"] == [
        "architecture.json",
        "frontend/App.jsx",
        "backend/app/main.py",
        "backend/requirements.txt",
        "database/init.sql",
        "docker-compose.yml",
        ".env.example",
        "README.md",
    ]
    assert result["generated_project_file_count"] == 8
    assert result["generated_readme_files"] == ["README.md"]
    assert result["frontend_framework"] == "react"
    assert result["framework"] == "fastapi"
    assert result["database_engine"] == "postgresql"
    assert result["docker_generated"] is True


def test_create_project_structure_reuses_slug_directory(
    monkeypatch, tmp_path
):
    architecture = model("Same Project")
    monkeypatch.setattr(project_generator, "BASE_OUTPUT", tmp_path)

    empty_frontend = {
        "generated_frontend_files": [],
        "skipped_frontend_components": [],
    }
    empty_backend = {
        "generated_backend_files": [],
        "skipped_backend_components": [],
    }
    empty_database = {
        "generated_database_files": [],
        "skipped_database_components": [],
    }
    empty_docker = {
        "generated_docker_files": [],
        "docker_generated": False,
    }
    readme = {
        "generated_readme_files": ["README.md"],
        "documented_technologies": [],
        "generated_readme_sections": ["Project Summary"],
    }

    monkeypatch.setattr(
        project_generator, "generate_frontend_files",
        lambda *args: empty_frontend
    )
    monkeypatch.setattr(
        project_generator, "generate_backend_files",
        lambda *args: empty_backend
    )
    monkeypatch.setattr(
        project_generator, "generate_database_files",
        lambda *args: empty_database
    )
    monkeypatch.setattr(
        project_generator, "generate_docker_files",
        lambda *args: empty_docker
    )
    monkeypatch.setattr(
        project_generator, "generate_readme_file",
        lambda *args: readme
    )

    first = create_project_structure(architecture)
    second = create_project_structure(architecture)
    assert first["project_path"] == second["project_path"]
    assert (tmp_path / "same-project" / "architecture.json").is_file()