from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.schemas import ArchitectureModel
from app.services.backend_generator import generate_backend_files
from app.services.database_generator import generate_database_files
from app.services.docker_generator import generate_docker_files
from app.services.frontend_generator import generate_frontend_files
from app.services.readme_generator import generate_readme_file


BASE_OUTPUT = Path(
    "generated_projects",
)


def slugify(
    name: str,
) -> str:
    """Convert a project name into a safe generated-project directory name."""

    return (
        re.sub(
            r"[^a-zA-Z0-9_-]+",
            "-",
            name.strip(),
        )
        .strip("-")
        .lower()
        or "archvision-project"
    )


def _normalize_generated_files(
    files: list[str] | None,
) -> list[str]:
    """Normalize generated file paths and remove duplicate entries."""

    normalized_files: list[str] = []
    seen: set[str] = set()

    for file_path in files or []:
        normalized_path = str(
            file_path,
        ).replace(
            "\\",
            "/",
        )

        if (
            not normalized_path
            or normalized_path in seen
        ):
            continue

        seen.add(
            normalized_path,
        )
        normalized_files.append(
            normalized_path,
        )

    return normalized_files


def _collect_generated_project_files(
    architecture_files: list[str],
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
    readme_result: dict[str, Any],
) -> list[str]:
    """Return every generated project file in one ordered collection."""

    generated_files: list[str] = []

    generated_files.extend(
        architecture_files,
    )
    generated_files.extend(
        frontend_result.get(
            "generated_frontend_files",
            [],
        )
    )
    generated_files.extend(
        backend_result.get(
            "generated_backend_files",
            [],
        )
    )
    generated_files.extend(
        database_result.get(
            "generated_database_files",
            [],
        )
    )
    generated_files.extend(
        docker_result.get(
            "generated_docker_files",
            [],
        )
    )
    generated_files.extend(
        readme_result.get(
            "generated_readme_files",
            [],
        )
    )

    return _normalize_generated_files(
        generated_files,
    )


def create_project_structure(
    model: ArchitectureModel,
) -> dict[str, Any]:
    """
    Generate the complete starter project for an architecture model.

    Each specialized generator remains responsible for its own layer. This
    service coordinates those generators and combines their metadata for the
    export route and export preview.

    Backend requirements files are included automatically because the backend
    generator reports backend/requirements.txt through generated_backend_files.
    """

    project_dir = (
        BASE_OUTPUT
        / slugify(
            model.name,
        )
    )

    project_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    architecture_file = (
        project_dir
        / "architecture.json"
    )

    architecture_file.write_text(
        model.model_dump_json(
            indent=2,
        ),
        encoding="utf-8",
    )

    architecture_files = [
        str(
            architecture_file.relative_to(
                project_dir,
            )
        ).replace(
            "\\",
            "/",
        )
    ]

    frontend_result = (
        generate_frontend_files(
            project_dir,
            model,
        )
    )

    backend_result = (
        generate_backend_files(
            project_dir,
            model,
        )
    )

    database_result = (
        generate_database_files(
            project_dir,
            model,
        )
    )

    docker_result = (
        generate_docker_files(
            project_dir,
            model,
        )
    )

    readme_result = (
        generate_readme_file(
            project_dir,
            model,
            frontend_result,
            backend_result,
            database_result,
            docker_result,
        )
    )

    generated_project_files = (
        _collect_generated_project_files(
            architecture_files,
            frontend_result,
            backend_result,
            database_result,
            docker_result,
        )
    )

    return {
        "project_path": str(
            project_dir,
        ),
        "generated_architecture_files": (
            architecture_files
        ),
        "generated_project_files": (
            generated_project_files
        ),
        "generated_readme_files": (
            readme_result.get("generated_readme_files", [])
        ),
        "documented_technologies": (
            readme_result.get("documented_technologies", [])
        ),
        "generated_readme_sections": (
            readme_result.get("generated_readme_sections", [])
        ),
        "generated_project_file_count": len(
            generated_project_files,
        ),
        **frontend_result,
        **backend_result,
        **database_result,
        **docker_result,
    }