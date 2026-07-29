from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.schemas import (
    ArchitectureChanges,
    ArchitectureModel,
    Component,
    Connection,
    FeedbackRequest,
    FeedbackResponse,
    GenerateRequest,
    GenerateResponse,
    GenerationCapability,
    GenerationCapabilityDeclaration,
    GenerationSupportManifest,
    Position,
    ProjectCreate,
    ProjectDetail,
    ProjectRename,
    ProjectSummary,
)


def component(**overrides):
    data = {
        "id": "frontend-1",
        "type": "frontend",
        "name": "Web Frontend",
        "technology": "React",
        "description": "Browser client",
        "position": {"x": 0, "y": 1, "z": 2},
    }
    data.update(overrides)
    return Component(**data)


def connection(**overrides):
    data = {
        "id": "connection-1",
        "source": "frontend-1",
        "target": "backend-1",
    }
    data.update(overrides)
    return Connection(**data)


def architecture(**overrides):
    data = {
        "name": "Example Project",
        "description": "Example architecture",
        "components": [component()],
        "connections": [],
    }
    data.update(overrides)
    return ArchitectureModel(**data)


@pytest.mark.parametrize("axis", ["x", "y", "z"])
@pytest.mark.parametrize(
    "value",
    [float("inf"), float("-inf"), float("nan")],
)
def test_position_rejects_non_finite_coordinates(axis, value):
    values = {"x": 0.0, "y": 0.0, "z": 0.0}
    values[axis] = value

    with pytest.raises(ValidationError, match="finite"):
        Position(**values)


def test_position_accepts_finite_coordinates():
    position = Position(x=-1.5, y=0, z=4.25)

    assert position.model_dump() == {
        "x": -1.5,
        "y": 0.0,
        "z": 4.25,
    }


@pytest.mark.parametrize("field", ["id", "name"])
def test_component_strips_required_text(field):
    instance = component(**{field: "  value  "})

    assert getattr(instance, field) == "value"


@pytest.mark.parametrize("field", ["id", "name"])
def test_component_rejects_blank_required_text(field):
    with pytest.raises(ValidationError, match="must not be blank"):
        component(**{field: "   "})


def test_component_normalizes_optional_text_and_metadata():
    instance = component(
        technology="  React  ",
        description="  Browser UI  ",
        metadata={"owner": "team"},
    )

    assert instance.technology == "React"
    assert instance.description == "Browser UI"
    assert instance.metadata == {"owner": "team"}


def test_component_converts_optional_text_values_to_strings():
    instance = component(
        technology=123,
        description=True,
    )

    assert instance.technology == "123"
    assert instance.description == "True"


def test_component_preserves_none_optional_text():
    instance = component(
        technology=None,
        description=None,
    )

    assert instance.technology is None
    assert instance.description is None


def test_component_defaults_metadata_to_independent_dict():
    first = component(id="one")
    second = component(id="two")

    first.metadata["key"] = "value"

    assert second.metadata == {}


@pytest.mark.parametrize(
    "component_type",
    [
        "frontend",
        "mobile",
        "backend",
        "worker",
        "ai-service",
        "database",
        "document-database",
        "cache",
        "object-storage",
        "auth",
        "authorization",
        "external-api",
        "message-queue",
        "load-balancer",
        "gateway",
        "service",
        "cloud",
        "container",
        "custom",
    ],
)
def test_component_accepts_supported_component_types(component_type):
    assert component(type=component_type).type == component_type


def test_component_rejects_unknown_component_type():
    with pytest.raises(ValidationError):
        component(type="unsupported")


@pytest.mark.parametrize(
    "field",
    ["id", "source", "target", "connection_type", "direction"],
)
def test_connection_strips_required_text(field):
    instance = connection(**{field: "  value  "})

    assert getattr(instance, field) == "value"


@pytest.mark.parametrize(
    "field",
    ["id", "source", "target", "connection_type", "direction"],
)
def test_connection_rejects_blank_required_text(field):
    with pytest.raises(ValidationError, match="must not be blank"):
        connection(**{field: "   "})


def test_connection_uses_expected_defaults():
    instance = connection()

    assert instance.connection_type == "dependency"
    assert instance.direction == "unidirectional"
    assert instance.protocol is None
    assert instance.label is None
    assert instance.metadata == {}


def test_connection_normalizes_optional_text():
    instance = connection(
        protocol="  HTTPS  ",
        label="  API request  ",
    )

    assert instance.protocol == "HTTPS"
    assert instance.label == "API request"


def test_connection_converts_optional_text_values_to_strings():
    instance = connection(protocol=443, label=False)

    assert instance.protocol == "443"
    assert instance.label == "False"


def test_connection_metadata_is_independent():
    first = connection(id="one")
    second = connection(id="two")

    first.metadata["key"] = "value"

    assert second.metadata == {}


def test_architecture_defaults():
    instance = ArchitectureModel()

    assert instance.name == "Untitled Architecture"
    assert instance.description is None
    assert instance.components == []
    assert instance.connections == []


def test_architecture_strips_name_and_description():
    instance = ArchitectureModel(
        name="  My Architecture  ",
        description="  Description  ",
    )

    assert instance.name == "My Architecture"
    assert instance.description == "Description"


def test_architecture_rejects_blank_name():
    with pytest.raises(ValidationError, match="must not be blank"):
        ArchitectureModel(name="   ")


def test_architecture_converts_description_to_string():
    instance = ArchitectureModel(description=123)

    assert instance.description == "123"


def test_architecture_collection_defaults_are_independent():
    first = ArchitectureModel()
    second = ArchitectureModel()

    first.components.append(component())

    assert second.components == []


def test_generate_request_strips_prompt():
    request = GenerateRequest(
        prompt="  Add a database  ",
        current_model=architecture(),
    )

    assert request.prompt == "Add a database"


def test_generate_request_rejects_blank_prompt():
    with pytest.raises(ValidationError, match="must not be blank"):
        GenerateRequest(
            prompt="   ",
            current_model=architecture(),
        )


def test_generate_request_rejects_prompt_over_5000_characters():
    with pytest.raises(ValidationError):
        GenerateRequest(
            prompt="x" * 5001,
            current_model=architecture(),
        )


def test_architecture_changes_defaults_are_empty_and_independent():
    first = ArchitectureChanges()
    second = ArchitectureChanges()

    first.added_component_ids.append("frontend-1")

    assert first.added_component_ids == ["frontend-1"]
    assert second.added_component_ids == []
    assert second.updated_component_ids == []
    assert second.removed_component_ids == []
    assert second.added_connection_ids == []
    assert second.removed_connection_ids == []


def test_generate_response_strips_summary():
    response = GenerateResponse(
        summary="  Added a backend  ",
        architecture=architecture(),
        changes=ArchitectureChanges(
            added_component_ids=["backend-1"],
        ),
    )

    assert response.summary == "Added a backend"
    assert response.changes.added_component_ids == ["backend-1"]


def test_generate_response_rejects_blank_summary():
    with pytest.raises(ValidationError, match="must not be blank"):
        GenerateResponse(
            summary="   ",
            architecture=architecture(),
            changes=ArchitectureChanges(),
        )


def test_feedback_request_wraps_architecture():
    model = architecture()
    request = FeedbackRequest(model=model)

    assert request.model is model


def test_feedback_response_defaults_and_values():
    empty = FeedbackResponse()
    populated = FeedbackResponse(
        suggestions=["Add caching", "Add authentication"],
    )

    assert empty.suggestions == []
    assert populated.suggestions == [
        "Add caching",
        "Add authentication",
    ]


def test_feedback_response_default_list_is_independent():
    first = FeedbackResponse()
    second = FeedbackResponse()

    first.suggestions.append("Suggestion")

    assert second.suggestions == []


def test_project_create_strips_name():
    request = ProjectCreate(
        name="  Project Name  ",
        model=architecture(),
    )

    assert request.name == "Project Name"


def test_project_create_rejects_blank_or_too_long_name():
    with pytest.raises(ValidationError):
        ProjectCreate(name="   ", model=architecture())

    with pytest.raises(ValidationError):
        ProjectCreate(name="x" * 151, model=architecture())


def test_project_rename_strips_name():
    request = ProjectRename(name="  Renamed Project  ")

    assert request.name == "Renamed Project"


def test_project_rename_rejects_blank_or_too_long_name():
    with pytest.raises(ValidationError):
        ProjectRename(name="   ")

    with pytest.raises(ValidationError):
        ProjectRename(name="x" * 151)


def test_project_summary_defaults_and_round_trip():
    project_id = uuid4()
    now = datetime.now(timezone.utc)

    summary = ProjectSummary(
        id=project_id,
        name="Project",
        status="active",
        schema_version="1.0",
        created_at=now,
        updated_at=now,
    )

    assert summary.id == project_id
    assert summary.description is None
    assert summary.component_count == 0
    assert summary.connection_count == 0

    rebuilt = ProjectSummary.model_validate(
        summary.model_dump(),
    )
    assert rebuilt == summary


def test_project_detail_extends_project_summary():
    project_id = uuid4()
    now = datetime.now(timezone.utc)
    model = architecture()

    detail = ProjectDetail(
        id=project_id,
        name="Project",
        description="Description",
        status="active",
        schema_version="1.0",
        component_count=1,
        connection_count=0,
        created_at=now,
        updated_at=now,
        model=model,
    )

    assert detail.model is model
    assert detail.component_count == 1
    assert isinstance(detail, ProjectSummary)


@pytest.mark.parametrize("field", ["catalog_id", "generator", "reason"])
def test_generation_capability_declaration_strips_required_text(field):
    data = {
        "catalog_id": "frontend",
        "kind": "component",
        "generator": "frontend",
        "supported": True,
        "phase": "implemented",
        "reason": "React generation is supported.",
    }
    data[field] = "  value  "

    declaration = GenerationCapabilityDeclaration(**data)

    assert getattr(declaration, field) == "value"


@pytest.mark.parametrize("field", ["catalog_id", "generator", "reason"])
def test_generation_capability_declaration_rejects_blank_text(field):
    data = {
        "catalog_id": "frontend",
        "kind": "component",
        "generator": "frontend",
        "supported": True,
        "phase": "implemented",
        "reason": "Supported.",
    }
    data[field] = "   "

    with pytest.raises(ValidationError, match="must not be blank"):
        GenerationCapabilityDeclaration(**data)


@pytest.mark.parametrize("kind", ["component", "connection"])
def test_generation_capability_declaration_accepts_kinds(kind):
    declaration = GenerationCapabilityDeclaration(
        catalog_id="item",
        kind=kind,
        generator="test",
        supported=True,
        phase="implemented",
        reason="Supported.",
    )

    assert declaration.kind == kind


@pytest.mark.parametrize(
    "phase",
    [
        "implemented",
        "configured",
        "represented",
        "experimental",
        "modeling-only",
        "unknown",
    ],
)
def test_generation_capability_declaration_accepts_phases(phase):
    declaration = GenerationCapabilityDeclaration(
        catalog_id="frontend",
        kind="component",
        generator="frontend",
        supported=True,
        phase=phase,
        reason="Supported.",
    )

    assert declaration.phase == phase


def test_generation_capability_declaration_rejects_invalid_literals():
    base = {
        "catalog_id": "frontend",
        "generator": "frontend",
        "supported": True,
        "reason": "Supported.",
    }

    with pytest.raises(ValidationError):
        GenerationCapabilityDeclaration(
            **base,
            kind="invalid",
            phase="implemented",
        )

    with pytest.raises(ValidationError):
        GenerationCapabilityDeclaration(
            **base,
            kind="component",
            phase="invalid",
        )


def test_generation_capability_declaration_cleans_lists():
    declaration = GenerationCapabilityDeclaration(
        catalog_id="frontend",
        kind="component",
        generator="frontend",
        supported=True,
        phase="implemented",
        reason="Supported.",
        technologies=[" React ", "", "   ", "Vite"],
        generated_files=[
            " frontend/src/App.jsx ",
            "",
            "frontend/package.json",
        ],
    )

    assert declaration.technologies == ["React", "Vite"]
    assert declaration.generated_files == [
        "frontend/src/App.jsx",
        "frontend/package.json",
    ]


def test_generation_capability_declaration_list_defaults_are_independent():
    first = GenerationCapabilityDeclaration(
        catalog_id="one",
        kind="component",
        generator="test",
        supported=True,
        phase="implemented",
        reason="Supported.",
    )
    second = GenerationCapabilityDeclaration(
        catalog_id="two",
        kind="component",
        generator="test",
        supported=True,
        phase="implemented",
        reason="Supported.",
    )

    first.technologies.append("React")

    assert second.technologies == []


def test_generation_capability_requires_label():
    with pytest.raises(ValidationError):
        GenerationCapability(
            supported=True,
            phase="implemented",
            reason="Supported.",
        )


def test_generation_capability_and_manifest_round_trip():
    capability = GenerationCapability(
        supported=True,
        phase="implemented",
        label="API Service",
        reason="FastAPI is supported.",
        technologies=["FastAPI"],
        generators=["backend"],
        generated_files=["backend/app/main.py"],
    )

    manifest = GenerationSupportManifest(
        schema_version="1.0",
        components={"api-service": capability},
        connections={},
    )

    dumped = manifest.model_dump()
    rebuilt = GenerationSupportManifest.model_validate(dumped)

    assert rebuilt == manifest
    assert rebuilt.components["api-service"].label == "API Service"
    assert rebuilt.components["api-service"].generators == ["backend"]


def test_generation_capability_rejects_invalid_phase():
    with pytest.raises(ValidationError):
        GenerationCapability(
            supported=False,
            phase="invalid",
            label="Unsupported",
            reason="Not supported.",
        )


def test_generation_support_manifest_defaults_are_independent():
    first = GenerationSupportManifest()
    second = GenerationSupportManifest()

    first.components["frontend"] = GenerationCapability(
        supported=True,
        phase="implemented",
        label="Frontend",
        reason="Supported.",
    )

    assert first.schema_version == "1.0"
    assert second.schema_version == "1.0"
    assert second.components == {}
    assert second.connections == {}


def test_generation_support_manifest_rejects_blank_schema_version():
    with pytest.raises(ValidationError):
        GenerationSupportManifest(schema_version="")