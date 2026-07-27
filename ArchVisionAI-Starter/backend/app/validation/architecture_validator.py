from __future__ import annotations

from app.schemas import ArchitectureModel


class ArchitectureValidationError(ValueError):
    """Raised when a complete architecture fails relationship validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors

        super().__init__(
            "The generated architecture failed validation."
        )


def validate_architecture(
    architecture: ArchitectureModel,
) -> list[str]:
    """
    Validate architecture-wide rules that individual Pydantic fields
    cannot evaluate by themselves.
    """

    errors: list[str] = []

    component_ids = [
        component.id
        for component in architecture.components
    ]
    connection_ids = [
        connection.id
        for connection in architecture.connections
    ]

    duplicate_component_ids = sorted(
        {
            component_id
            for component_id in component_ids
            if component_ids.count(component_id) > 1
        }
    )

    for component_id in duplicate_component_ids:
        errors.append(
            f"Component ID {component_id!r} is duplicated."
        )

    duplicate_connection_ids = sorted(
        {
            connection_id
            for connection_id in connection_ids
            if connection_ids.count(connection_id) > 1
        }
    )

    for connection_id in duplicate_connection_ids:
        errors.append(
            f"Connection ID {connection_id!r} is duplicated."
        )

    known_component_ids = set(component_ids)

    for index, connection in enumerate(
        architecture.connections,
    ):
        connection_label = (
            connection.id
            or f"connection at index {index}"
        )

        if connection.source == connection.target:
            errors.append(
                f"Connection {connection_label!r} cannot connect "
                "a component to itself."
            )

        if connection.source not in known_component_ids:
            errors.append(
                f"Connection {connection_label!r} references "
                f"unknown source component {connection.source!r}."
            )

        if connection.target not in known_component_ids:
            errors.append(
                f"Connection {connection_label!r} references "
                f"unknown target component {connection.target!r}."
            )

    return errors


def validate_architecture_or_raise(
    architecture: ArchitectureModel,
) -> None:
    """Raise one structured error when the architecture is invalid."""

    errors = validate_architecture(architecture)

    if errors:
        raise ArchitectureValidationError(errors)
