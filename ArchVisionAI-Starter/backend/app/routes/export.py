from __future__ import annotations

import shutil
from pathlib import Path

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse

from app.schemas import ArchitectureModel
from app.services.project_generator import (
    create_project_structure,
    slugify,
)


router = APIRouter(
    prefix="/export",
    tags=["export"],
)


@router.post(
    "/starter",
    status_code=status.HTTP_200_OK,
    response_class=FileResponse,
)
def export_starter(
    model: ArchitectureModel,
) -> FileResponse:
    """
    Generate a starter project, package it as a ZIP archive,
    and return the archive for browser download.
    """

    try:
        result = create_project_structure(model)

        project_path_value = result.get(
            "project_path",
        )

        if not project_path_value:
            raise OSError(
                "The project generator did not return a project path."
            )

        project_directory = Path(
            project_path_value,
        )

        if (
            not project_directory.exists()
            or not project_directory.is_dir()
        ):
            raise OSError(
                "The generated project directory could not be found."
            )

        project_slug = slugify(model.name)

        archive_base_path = (
            project_directory.parent
            / project_slug
        )

        zip_path = Path(
            shutil.make_archive(
                base_name=str(
                    archive_base_path,
                ),
                format="zip",
                root_dir=str(
                    project_directory.parent,
                ),
                base_dir=project_directory.name,
            )
        )

        if (
            not zip_path.exists()
            or not zip_path.is_file()
        ):
            raise OSError(
                "The generated ZIP archive could not be found."
            )

        return FileResponse(
            path=zip_path,
            media_type="application/zip",
            filename=f"{project_slug}.zip",
            headers={
                "Cache-Control": "no-store",
            },
        )

    except OSError as exc:
        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Unable to generate the project archive."
            ),
        ) from exc