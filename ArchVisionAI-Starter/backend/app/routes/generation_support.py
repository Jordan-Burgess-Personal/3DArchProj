from __future__ import annotations

from fastapi import (
    APIRouter,
    status,
)

from app.schemas import (
    GenerationSupportManifest,
)
from app.services.generation_support import (
    get_generation_support_manifest,
)


router = APIRouter(
    prefix="/generation-support",
    tags=["Generation Support"],
)


@router.get(
    "",
    response_model=GenerationSupportManifest,
    status_code=status.HTTP_200_OK,
    summary=(
        "Get project-generation support"
    ),
)
def get_generation_support(
) -> GenerationSupportManifest:
    """
    Return the components and connections currently supported by the
    backend project generators.

    The response is derived from declarations owned by the generator
    modules. The frontend should use this endpoint rather than maintaining
    a separate static list of supported generation features.
    """

    return get_generation_support_manifest()