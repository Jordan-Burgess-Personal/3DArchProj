from __future__ import annotations

from collections.abc import Iterable

from app.schemas import GenerationCapability, GenerationCapabilityDeclaration, GenerationSupportManifest
from app.services.backend_generator import BACKEND_GENERATION_CAPABILITIES
from app.services.database_generator import DATABASE_GENERATION_CAPABILITIES
from app.services.docker_generator import DOCKER_GENERATION_CAPABILITIES
from app.services.frontend_generator import FRONTEND_GENERATION_CAPABILITIES
from app.services.readme_generator import README_GENERATION_CAPABILITIES


GENERATION_CAPABILITY_GROUPS = (
    FRONTEND_GENERATION_CAPABILITIES,
    BACKEND_GENERATION_CAPABILITIES,
    DATABASE_GENERATION_CAPABILITIES,
    DOCKER_GENERATION_CAPABILITIES,
    README_GENERATION_CAPABILITIES,
)


def _support_label(
    supported: bool,
    phase: str,
) -> str:
    """
    Return the user-facing label for a support capability.
    """

    if supported and phase == "experimental":
        return "Experimental Support"

    if supported and phase == "configured":
        return "Configuration Supported"

    if supported and phase == "represented":
        return "Representation Supported"

    if supported:
        return "Generation Supported"

    if phase == "represented":
        return "Represented Only"

    if phase == "unknown":
        return "Support Unknown"

    return "Modeling Only"


def _unique_sorted(
    values: Iterable[str],
) -> list[str]:
    """
    Return normalized, unique values in predictable order.
    """

    return sorted(
        {
            str(value).strip()
            for value in values
            if str(value).strip()
        },
        key=str.lower,
    )


def _merge_declarations(
    declarations: list[
        GenerationCapabilityDeclaration
    ],
) -> GenerationCapability:
    """
    Merge declarations that target the same catalog item.

    Multiple generators may contribute to one catalog item. For example,
    a database component can generate an initialization file while the
    Docker generator contributes container configuration.

    An item is considered supported when at least one declaration reports
    actual support.
    """

    if not declarations:
        raise ValueError(
            "At least one capability declaration is required.",
        )

    supported_declarations = [
        declaration
        for declaration in declarations
        if declaration.supported
    ]

    supported = bool(supported_declarations)

    preferred_declarations = (
        supported_declarations
        if supported_declarations
        else declarations
    )

    phase_priority = {
        "implemented": 6,
        "configured": 5,
        "represented": 4,
        "experimental": 3,
        "modeling-only": 2,
        "unknown": 1,
    }

    primary_declaration = max(
        preferred_declarations,
        key=lambda declaration: phase_priority.get(
            declaration.phase,
            0,
        ),
    )

    reasons = _unique_sorted(
        declaration.reason
        for declaration in declarations
    )

    reason = " ".join(reasons)

    generators = _unique_sorted(
        declaration.generator
        for declaration in declarations
    )

    technologies = _unique_sorted(
        technology
        for declaration in declarations
        for technology in declaration.technologies
    )

    generated_files = _unique_sorted(
        generated_file
        for declaration in declarations
        for generated_file in declaration.generated_files
    )

    return GenerationCapability(
        supported=supported,
        phase=primary_declaration.phase,
        label=_support_label(
            supported,
            primary_declaration.phase,
        ),
        reason=reason,
        generators=generators,
        technologies=technologies,
        generated_files=generated_files,
    )


def _validated_declarations(
) -> list[GenerationCapabilityDeclaration]:
    """
    Validate all declarations exported by generator modules.
    """

    validated: list[
        GenerationCapabilityDeclaration
    ] = []

    for capability_group in (
        GENERATION_CAPABILITY_GROUPS
    ):
        for declaration in capability_group:
            validated.append(
                GenerationCapabilityDeclaration.model_validate(
                    declaration,
                )
            )

    return validated


def get_generation_support_manifest(
) -> GenerationSupportManifest:
    """
    Build the complete project-generation support manifest.

    The frontend calls the related API endpoint instead of maintaining a
    separate static support configuration.

    Backend capability declarations include backend/requirements.txt, and the
    README generator contributes README.md. Both generated files are surfaced
    automatically through the manifest without additional coordinator logic.
    """

    grouped_components: dict[
        str,
        list[GenerationCapabilityDeclaration],
    ] = {}

    grouped_connections: dict[
        str,
        list[GenerationCapabilityDeclaration],
    ] = {}

    for declaration in (
        _validated_declarations()
    ):
        target = (
            grouped_components
            if declaration.kind == "component"
            else grouped_connections
        )

        target.setdefault(
            declaration.catalog_id,
            [],
        ).append(declaration)

    components = {
        catalog_id: _merge_declarations(
            declarations,
        )
        for catalog_id, declarations
        in sorted(
            grouped_components.items(),
        )
    }

    connections = {
        catalog_id: _merge_declarations(
            declarations,
        )
        for catalog_id, declarations
        in sorted(
            grouped_connections.items(),
        )
    }

    return GenerationSupportManifest(
        schema_version="1.0",
        components=components,
        connections=connections,
    )