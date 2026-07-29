from __future__ import annotations

import json
import re
from copy import deepcopy

from openai import OpenAI
from pydantic import ValidationError

from app.config import settings
from app.schemas import (
    ArchitectureChanges,
    ArchitectureModel,
    Component,
    Connection,
    GenerateResponse,
    Position,
)


GRID_SPACING = 4.0
GRID_Y = 0.5
GRID_COLUMNS = 4

SYSTEM_PROMPT = """
You modify an existing software architecture according to the user's request.

Return one strict JSON object with this structure:

{
  "summary": "Short human-readable explanation of the proposed changes",
  "architecture": {
    "name": "Architecture name",
    "description": "Architecture description",
    "components": [
      {
        "id": "unique-id",
        "type": "frontend | mobile | backend | worker | database | document-database | cache | object-storage | auth | authorization | external-api | message-queue | load-balancer | gateway | service | ai-service | cloud | container | custom",
        "name": "Display name",
        "technology": "Technology or empty string",
        "description": "Purpose of the component",
        "position": {"x": 0, "y": 0.5, "z": 0}
      }
    ],
    "connections": [
      {
        "id": "unique-id",
        "source": "source-component-id",
        "target": "target-component-id",
        "label": "Relationship description"
      }
    ]
  }
}

Rules:

1. Return JSON only.
2. Treat the supplied current architecture as the source of truth.
3. Preserve every existing component unless the user explicitly requests removal.
4. Preserve every existing connection unless the user explicitly requests removal
   or replacement.
5. Reuse existing component IDs when referring to current components.
6. Do not create a duplicate backend, frontend, database, authentication service,
   or other component when an appropriate existing component already exists.
7. Do not rename existing components unless the user explicitly requests it.
8. Do not move existing components unless the user explicitly requests movement.
9. New components must have unique, descriptive IDs.
10. New connections must reference valid component IDs.
11. Never connect a component to itself.
12. Interpret phrases such as "the backend", "the database", "security layer",
    or "authentication" by matching existing names, types, technologies, and
    descriptions.
13. If the user asks to add a database and security layer to an existing backend,
    reuse the backend and create backend -> security -> database connections.
14. Return the complete proposed architecture, including unchanged existing
    components and connections.
15. The result is a proposal only. The frontend will require user approval before
    applying it.
""".strip()


def _create_openai_client() -> OpenAI | None:
    if not settings.openai_api_key:
        return None

    return OpenAI(api_key=settings.openai_api_key)


def _validate_architecture_data(data: dict) -> ArchitectureModel:
    try:
        return ArchitectureModel.model_validate(data)
    except ValidationError as error:
        raise ValueError(
            "The generated architecture did not match the required schema."
        ) from error


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    return normalized.strip("-") or "component"


def _unique_id(base: str, used_ids: set[str]) -> str:
    candidate = _slug(base)
    suffix = 2

    while candidate in used_ids:
        candidate = f"{_slug(base)}-{suffix}"
        suffix += 1

    used_ids.add(candidate)
    return candidate


def _position_key(position: Position) -> tuple[float, float]:
    return (
        round(float(position.x), 3),
        round(float(position.z), 3),
    )


def _next_grid_position(
    occupied: set[tuple[float, float]],
) -> Position:
    slot = 0

    while True:
        column = slot % GRID_COLUMNS
        row = slot // GRID_COLUMNS
        x = float(column * GRID_SPACING)
        z = float(row * GRID_SPACING)

        if (x, z) not in occupied:
            occupied.add((x, z))
            return Position(x=x, y=GRID_Y, z=z)

        slot += 1


def _contains_removal_request(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(
        phrase in lowered
        for phrase in (
            "remove ",
            "delete ",
            "drop ",
            "get rid of ",
        )
    )


def _contains_move_request(prompt: str) -> bool:
    lowered = prompt.lower()
    return any(
        phrase in lowered
        for phrase in (
            "move ",
            "reposition ",
            "relocate ",
            "place ",
            "arrange ",
        )
    )


def _component_signature(component: Component) -> dict:
    return component.model_dump()


def _connection_signature(connection: Connection) -> dict:
    return connection.model_dump()


def _calculate_changes(
    current_model: ArchitectureModel,
    proposed_model: ArchitectureModel,
) -> ArchitectureChanges:
    current_components = {
        component.id: component
        for component in current_model.components
    }
    proposed_components = {
        component.id: component
        for component in proposed_model.components
    }

    current_connections = {
        connection.id: connection
        for connection in current_model.connections
    }
    proposed_connections = {
        connection.id: connection
        for connection in proposed_model.connections
    }

    added_component_ids = sorted(
        proposed_components.keys() - current_components.keys()
    )
    removed_component_ids = sorted(
        current_components.keys() - proposed_components.keys()
    )
    updated_component_ids = sorted(
        component_id
        for component_id in (
            current_components.keys() & proposed_components.keys()
        )
        if _component_signature(current_components[component_id])
        != _component_signature(proposed_components[component_id])
    )

    added_connection_ids = sorted(
        proposed_connections.keys() - current_connections.keys()
    )
    removed_connection_ids = sorted(
        current_connections.keys() - proposed_connections.keys()
    )

    return ArchitectureChanges(
        added_component_ids=added_component_ids,
        updated_component_ids=updated_component_ids,
        removed_component_ids=removed_component_ids,
        added_connection_ids=added_connection_ids,
        removed_connection_ids=removed_connection_ids,
    )


def _sanitize_proposal(
    prompt: str,
    current_model: ArchitectureModel,
    proposed_model: ArchitectureModel,
) -> ArchitectureModel:
    """
    Protect existing work and assign deterministic positions to new components.

    Existing positions always win unless the user explicitly requested movement.
    Existing components/connections omitted by the model are restored unless the
    prompt explicitly requested deletion.
    """

    allow_removal = _contains_removal_request(prompt)
    allow_movement = _contains_move_request(prompt)

    current_components = {
        component.id: component
        for component in current_model.components
    }
    proposed_components = {
        component.id: component
        for component in proposed_model.components
    }

    if not allow_removal:
        for component_id, component in current_components.items():
            proposed_components.setdefault(
                component_id,
                component.model_copy(deep=True),
            )

    occupied = {
        _position_key(component.position)
        for component in current_model.components
    }

    sanitized_components: list[Component] = []

    for component in proposed_components.values():
        existing = current_components.get(component.id)

        if existing:
            next_component = component.model_copy(deep=True)

            if not allow_movement:
                next_component.position = existing.position.model_copy(
                    deep=True
                )

            sanitized_components.append(next_component)
            continue

        next_component = component.model_copy(deep=True)
        next_component.position = _next_grid_position(occupied)
        sanitized_components.append(next_component)

    valid_component_ids = {
        component.id
        for component in sanitized_components
    }

    current_connections = {
        connection.id: connection
        for connection in current_model.connections
    }
    proposed_connections = {
        connection.id: connection
        for connection in proposed_model.connections
        if connection.source in valid_component_ids
        and connection.target in valid_component_ids
        and connection.source != connection.target
    }

    if not allow_removal:
        for connection_id, connection in current_connections.items():
            if (
                connection.source in valid_component_ids
                and connection.target in valid_component_ids
            ):
                proposed_connections.setdefault(
                    connection_id,
                    connection.model_copy(deep=True),
                )

    return ArchitectureModel(
        name=proposed_model.name or current_model.name,
        description=(
            proposed_model.description
            if proposed_model.description is not None
            else current_model.description
        ),
        components=sanitized_components,
        connections=list(proposed_connections.values()),
    )


def _find_component(
    model: ArchitectureModel,
    *,
    types: set[str],
    keywords: tuple[str, ...],
) -> Component | None:
    for component in model.components:
        haystack = " ".join(
            [
                component.name or "",
                component.type or "",
                component.technology or "",
                component.description or "",
            ]
        ).lower()

        if component.type in types:
            return component

        if any(keyword in haystack for keyword in keywords):
            return component

    return None


def _demo_proposal(
    prompt: str,
    current_model: ArchitectureModel,
) -> GenerateResponse:
    """
    Produce a useful local proposal when no OpenAI key is configured.

    The fallback intentionally supports the most important SCRUM-53 flows:
    adding a frontend, backend, security layer, database, and connections to
    existing components.
    """

    proposed = current_model.model_copy(deep=True)
    used_component_ids = {
        component.id
        for component in proposed.components
    }
    used_connection_ids = {
        connection.id
        for connection in proposed.connections
    }

    lowered = prompt.lower()

    backend = _find_component(
        proposed,
        types={"backend", "service", "gateway"},
        keywords=("backend", "api server", "application server"),
    )
    frontend = _find_component(
        proposed,
        types={"frontend", "mobile"},
        keywords=("frontend", "user interface", "client"),
    )
    security = _find_component(
        proposed,
        types={"auth", "authorization"},
        keywords=("security", "authentication", "authorization", "oauth"),
    )
    database = _find_component(
        proposed,
        types={"database"},
        keywords=("database", "postgres", "mongodb", "storage"),
    )

    added_names: list[str] = []

    if (
        any(word in lowered for word in ("frontend", "user interface", "client"))
        and frontend is None
    ):
        frontend = Component(
            id=_unique_id("frontend", used_component_ids),
            type="frontend",
            name="User Interface",
            technology="React",
            description="Presents the application to users.",
        )
        proposed.components.append(frontend)
        added_names.append(frontend.name)

    if (
        any(word in lowered for word in ("backend", "api", "server"))
        and backend is None
    ):
        backend = Component(
            id=_unique_id("backend", used_component_ids),
            type="backend",
            name="Application Server",
            technology="FastAPI",
            description="Handles business logic and API requests.",
        )
        proposed.components.append(backend)
        added_names.append(backend.name)

    if (
        any(
            word in lowered
            for word in (
                "security",
                "authentication",
                "authorization",
                "auth",
                "oauth",
            )
        )
        and security is None
    ):
        security = Component(
            id=_unique_id("security-layer", used_component_ids),
            type="auth",
            name="Security Layer",
            technology="OAuth2",
            description="Handles authentication and authorization.",
        )
        proposed.components.append(security)
        added_names.append(security.name)

    if (
        any(
            word in lowered
            for word in (
                "database",
                "postgres",
                "mongodb",
                "data layer",
                "storage",
            )
        )
        and database is None
    ):
        database = Component(
            id=_unique_id("database", used_component_ids),
            type="database",
            name="Application Database",
            technology=(
                "MongoDB"
                if "mongo" in lowered
                else "PostgreSQL"
            ),
            description="Stores persistent application data.",
        )
        proposed.components.append(database)
        added_names.append(database.name)

    def add_connection(
        source: Component | None,
        target: Component | None,
        label: str,
        base_id: str,
    ) -> None:
        if not source or not target or source.id == target.id:
            return

        duplicate = any(
            connection.source == source.id
            and connection.target == target.id
            for connection in proposed.connections
        )

        if duplicate:
            return

        proposed.connections.append(
            Connection(
                id=_unique_id(base_id, used_connection_ids),
                source=source.id,
                target=target.id,
                label=label,
            )
        )

    if security and backend:
        add_connection(
            backend,
            security,
            "Backend authenticates and authorizes requests",
            "backend-security",
        )

    if security and database:
        add_connection(
            security,
            database,
            "Security layer accesses protected data",
            "security-database",
        )
    elif backend and database:
        add_connection(
            backend,
            database,
            "Backend reads and writes application data",
            "backend-database",
        )

    if frontend and backend:
        add_connection(
            frontend,
            backend,
            "User interface communicates with backend",
            "frontend-backend",
        )

    sanitized = _sanitize_proposal(
        prompt,
        current_model,
        proposed,
    )
    changes = _calculate_changes(
        current_model,
        sanitized,
    )

    summary = (
        "Proposed adding "
        + ", ".join(added_names)
        + " and the related connections."
        if added_names
        else "Proposed updates to the existing architecture."
    )

    return GenerateResponse(
        summary=summary,
        architecture=sanitized,
        changes=changes,
    )


def generate_architecture(
    prompt: str,
    current_model: ArchitectureModel,
) -> GenerateResponse:
    """
    Generate a proposed modification to the current architecture.

    The returned proposal does not alter the user's canvas. The frontend must
    explicitly approve it before calling the store's apply action.
    """

    cleaned_prompt = prompt.strip()

    if not cleaned_prompt:
        raise ValueError("An architecture prompt is required.")

    client = _create_openai_client()

    if client is None:
        return _demo_proposal(
            cleaned_prompt,
            current_model,
        )

    user_payload = {
        "request": cleaned_prompt,
        "current_architecture": current_model.model_dump(),
    }

    response = client.chat.completions.create(
        model=settings.openai_model or "gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps(user_payload),
            },
        ],
        response_format={"type": "json_object"},
    )

    response_content = response.choices[0].message.content

    if not response_content:
        raise RuntimeError(
            "The OpenAI API returned an empty architecture response."
        )

    try:
        result_data = json.loads(response_content)
    except json.JSONDecodeError as error:
        raise ValueError(
            "The OpenAI API returned invalid JSON."
        ) from error

    if not isinstance(result_data, dict):
        raise ValueError(
            "The generated proposal must be a JSON object."
        )

    architecture_data = result_data.get("architecture")

    if not isinstance(architecture_data, dict):
        raise ValueError(
            "The generated proposal did not contain an architecture object."
        )

    proposed_model = _validate_architecture_data(
        architecture_data
    )
    sanitized_model = _sanitize_proposal(
        cleaned_prompt,
        current_model,
        proposed_model,
    )
    changes = _calculate_changes(
        current_model,
        sanitized_model,
    )

    summary = str(
        result_data.get("summary")
        or "Proposed architecture changes are ready for review."
    ).strip()

    return GenerateResponse(
        summary=summary,
        architecture=sanitized_model,
        changes=changes,
    )


def review_architecture(
    model: ArchitectureModel,
) -> list[str]:
    """Provide initial rule-based feedback for an architecture model."""

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

    if "database" in component_types and not (
        {"auth", "authorization"} & component_types
    ):
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