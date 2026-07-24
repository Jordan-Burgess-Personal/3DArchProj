from __future__ import annotations

import json
import logging
from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from pydantic import ValidationError

from app.ai.architecture_assistant import (
    generate_architecture,
    review_architecture,
)
from app.schemas import (
    FeedbackRequest,
    FeedbackResponse,
    GenerateRequest,
    GenerateResponse,
)


logger = logging.getLogger(__name__)

router = APIRouter()


def _prepare_generated_architecture(
    result: Any,
) -> GenerateResponse:
    """
    Convert the architecture service result into a
    validated GenerateResponse.

    generate_architecture currently returns a dictionary,
    but string handling is retained for compatibility with
    earlier service implementations.
    """

    architecture_data = result

    if isinstance(result, str):
        try:
            architecture_data = json.loads(result)
        except json.JSONDecodeError as error:
            raise ValueError(
                "The AI service returned invalid JSON."
            ) from error

    if not isinstance(architecture_data, dict):
        raise ValueError(
            "The generated architecture must be a JSON object."
        )

    try:
        return GenerateResponse.model_validate(
            architecture_data,
        )
    except ValidationError as error:
        raise ValueError(
            "The generated architecture did not match "
            "the required application schema."
        ) from error


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
)
def generate(
    request: GenerateRequest,
) -> GenerateResponse:
    """
    Generate an editable software architecture from a
    natural-language prompt.
    """

    try:
        result = generate_architecture(
            request.prompt,
        )

        return _prepare_generated_architecture(
            result,
        )
    except ValueError as error:
        logger.warning(
            "AI architecture generation validation failed: %s",
            error,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error
    except Exception as error:
        logger.exception(
            "AI architecture generation failed.",
        )

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=(
                "The architecture could not be generated. "
                "Please revise the prompt and try again."
            ),
        ) from error


@router.post(
    "/feedback",
    response_model=FeedbackResponse,
    status_code=status.HTTP_200_OK,
)
def feedback(
    request: FeedbackRequest,
) -> FeedbackResponse:
    """
    Review an architecture and return improvement
    suggestions.
    """

    try:
        suggestions = review_architecture(
            request.model,
        )

        return FeedbackResponse(
            suggestions=suggestions,
        )
    except ValueError as error:
        logger.warning(
            "Architecture feedback validation failed: %s",
            error,
        )

        raise HTTPException(
            status_code=(
                status.HTTP_422_UNPROCESSABLE_ENTITY
            ),
            detail=str(error),
        ) from error
    except Exception as error:
        logger.exception(
            "Architecture feedback generation failed.",
        )

        raise HTTPException(
            status_code=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
            detail=(
                "Architecture feedback is temporarily "
                "unavailable."
            ),
        ) from error