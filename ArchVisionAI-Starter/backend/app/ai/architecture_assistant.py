from __future__ import annotations

import json
from copy import deepcopy

from openai import OpenAI
from pydantic import ValidationError

from app.config import settings
from app.schemas import ArchitectureModel


DEMO_MODEL = {
    "name": "AI Generated Architecture",
    "description": (
        "Starter architecture generated from plain-English input."
    ),
    "components": [
        {
            "id": "frontend",
            "type": "frontend",
            "name": "React Frontend",
            "technology": "React + Tailwind",
            "description": "Browser-based user interface.",
            "position": {
                "x": -3,
                "y": 0,
                "z": 0,
            },
        },
        {
            "id": "api",
            "type": "backend",
            "name": "FastAPI Backend",
            "technology": "Python FastAPI",
            "description": "Application API and business-logic layer.",
            "position": {
                "x": 0,
                "y": 0,
                "z": 0,
            },
        },
        {
            "id": "db",
            "type": "database",
            "name": "Project Database",
            "technology": "PostgreSQL",
            "description": "Persistent storage for projects and architecture data.",
            "position": {
                "x": 3,
                "y": 0,
                "z": 0,
            },
        },
        {
            "id": "ai",
            "type": "external_api",
            "name": "OpenAI API",
            "technology": "OpenAI",
            "description": "Architecture generation and review service.",
            "position": {
                "x": 0,
                "y": 0,
                "z": -2,
            },
        },
    ],
    "connections": [
        {
            "id": "c1",
            "source": "frontend",
            "target": "api",
            "label": "HTTP requests",
        },
        {
            "id": "c2",
            "source": "api",
            "target": "db",
            "label": "Reads and writes projects",
        },
        {
            "id": "c3",
            "source": "api",
            "target": "ai",
            "label": "AI generation and feedback",
        },
    ],
}


SYSTEM_PROMPT = """
Convert the user's software architecture description into one strict JSON
object matching this structure:

{
  "name": "Architecture name",
  "description": "Architecture summary",
  "components": [
    {
      "id": "unique-component-id",
      "type": "frontend | backend | database | cache | auth | queue |
               storage | external_api | gateway | service",
      "name": "Human-readable component name",
      "technology": "Selected technology or platform",
      "description": "Short description of the component",
      "position": {
        "x": 0,
        "y": 0,
        "z": 0
      }
    }
  ],
  "connections": [
    {
      "id": "unique-connection-id",
      "source": "source-component-id",
      "target": "target-component-id",
      "label": "Description of the relationship"
    }
  ]
}

Requirements:

1. Return JSON only.
2. Do not include Markdown or code fences.
3. Every component ID must be unique.
4. Every connection ID must be unique.
5. Every connection source and target must reference an existing component ID.
6. Source and target must not be the same.
7. Use simple numeric coordinates.
8. Produce an architecture suitable for visualization in a 3D workspace.
""".strip()


def _create_openai_client() -> OpenAI | None:
    """
    Create an OpenAI client only when an API key is configured.

    Returning None allows local development to use the demonstration
    architecture without requiring an OpenAI API key.
    """

    if not settings.openai_api_key:
        return None

    return OpenAI(api_key=settings.openai_api_key)


def _validate_architecture_data(data: dict) -> dict:
    """
    Validate generated architecture data against ArchitectureModel.

    Returning model_dump() guarantees the caller receives a normal
    JSON-compatible dictionary using the application's expected schema.
    """

    try:
        architecture = ArchitectureModel.model_validate(data)
    except ValidationError as error:
        raise ValueError(
            "The generated architecture did not match the required schema."
        ) from error

    return architecture.model_dump()


def generate_architecture(prompt: str) -> dict:
    """
    Generate an architecture from a plain-English prompt.

    When OPENAI_API_KEY is unavailable, a copy of DEMO_MODEL is returned
    so the application remains usable during local development.
    """

    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("An architecture prompt is required.")

    client = _create_openai_client()

    if client is None:
        return deepcopy(DEMO_MODEL)

    response = client.chat.completions.create(
        model=settings.openai_model or "gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": cleaned_prompt,
            },
        ],
        response_format={
            "type": "json_object",
        },
    )

    response_content = response.choices[0].message.content

    if not response_content:
        raise RuntimeError(
            "The OpenAI API returned an empty architecture response."
        )

    try:
        architecture_data = json.loads(response_content)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The OpenAI API returned invalid JSON."
        ) from error

    if not isinstance(architecture_data, dict):
        raise ValueError(
            "The generated architecture must be a JSON object."
        )

    return _validate_architecture_data(architecture_data)


def review_architecture(
    model: ArchitectureModel,
) -> list[str]:
    """
    Provide initial rule-based feedback for an architecture model.

    This function currently uses local validation rules so architecture
    review remains available without an OpenAI API key.
    """

    suggestions: list[str] = []

    component_types = {
        component.type.lower()
        for component in model.components
    }

    component_ids = {
        component.id
        for component in model.components
    }

    if "frontend" in component_types and "backend" not in component_types:
        suggestions.append(
            "Add a backend or API layer so the frontend does not communicate "
            "directly with storage or sensitive external services."
        )

    if "database" in component_types and "auth" not in component_types:
        suggestions.append(
            "Consider adding authentication and authorization before allowing "
            "project data to be saved, modified, or shared."
        )

    if "backend" in component_types and "database" not in component_types:
        suggestions.append(
            "Add persistent storage if users need saved architecture models, "
            "history, or generated project records."
        )

    if len(model.components) > 1 and not model.connections:
        suggestions.append(
            "Add connections to describe how the architecture components "
            "communicate with one another."
        )

    for connection in model.connections:
        if connection.source not in component_ids:
            suggestions.append(
                f"Connection {connection.id!r} references an unknown source "
                f"component {connection.source!r}."
            )

        if connection.target not in component_ids:
            suggestions.append(
                f"Connection {connection.id!r} references an unknown target "
                f"component {connection.target!r}."
            )

        if connection.source == connection.target:
            suggestions.append(
                f"Connection {connection.id!r} connects a component to itself."
            )

    if not suggestions:
        suggestions.append(
            "The architecture looks reasonable for an MVP. Consider adding "
            "logging, validation, monitoring, security controls, and deployment "
            "configuration as the design evolves."
        )

    return suggestions