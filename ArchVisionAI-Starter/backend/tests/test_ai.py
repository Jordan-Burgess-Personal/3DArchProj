from fastapi.testclient import TestClient

from app.main import app
from app.routes import ai
from app.schemas import (
    ArchitectureChanges,
    ArchitectureModel,
    GenerateResponse,
)


client = TestClient(app)


CURRENT_ARCHITECTURE = {
    "name": "Current Architecture",
    "description": "Architecture before AI changes.",
    "components": [
        {
            "id": "backend",
            "type": "backend",
            "name": "FastAPI Backend",
            "technology": "FastAPI",
            "description": "Application API.",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0,
            },
            "metadata": {},
        },
    ],
    "connections": [],
}


PROPOSED_ARCHITECTURE = {
    "name": "Current Architecture",
    "description": "Architecture with security and storage.",
    "components": [
        CURRENT_ARCHITECTURE["components"][0],
        {
            "id": "security-layer",
            "type": "auth",
            "name": "Security Layer",
            "technology": "OAuth2",
            "description": "Authenticates requests.",
            "position": {
                "x": 4,
                "y": 0.5,
                "z": 0,
            },
            "metadata": {},
        },
        {
            "id": "database",
            "type": "database",
            "name": "PostgreSQL Database",
            "technology": "PostgreSQL",
            "description": "Stores application data.",
            "position": {
                "x": 8,
                "y": 0.5,
                "z": 0,
            },
            "metadata": {},
        },
    ],
    "connections": [],
}


PROPOSED_ARCHITECTURE = {
    "name": "Current Architecture",
    "description": "Architecture with security and storage.",
    "components": [
        CURRENT_ARCHITECTURE["components"][0],
        {
            "id": "security-layer",
            "type": "auth",
            "name": "Security Layer",
            "technology": "OAuth2",
            "description": "Authenticates requests.",
            "position": {
                "x": 4,
                "y": 0.5,
                "z": 0,
            },
            "metadata": {},
        },
        {
            "id": "database",
            "type": "database",
            "name": "PostgreSQL Database",
            "technology": "PostgreSQL",
            "description": "Stores application data.",
            "position": {
                "x": 8,
                "y": 0.5,
                "z": 0,
            },
            "metadata": {},
        },
    ],
    "connections": [
        {
            "id": "backend-security",
            "source": "backend",
            "target": "security-layer",
            "connection_type": "dependency",
            "label": "Authenticates requests",
            "metadata": {},
        },
        {
            "id": "security-database",
            "source": "security-layer",
            "target": "database",
            "connection_type": "database_access",
            "label": "Accesses protected data",
            "metadata": {},
        },
    ],
}


def build_proposal() -> GenerateResponse:
    return GenerateResponse(
        summary=(
            "Add a security layer and database to the existing backend."
        ),
        architecture=ArchitectureModel.model_validate(
            PROPOSED_ARCHITECTURE
        ),
        changes=ArchitectureChanges(
            added_component_ids=[
                "security-layer",
                "database",
            ],
            added_connection_ids=[
                "backend-security",
                "security-database",
            ],
        ),
    )


def post_generate() -> object:
    return client.post(
        "/api/ai/generate",
        json={
            "prompt": (
                "Add a security layer and database "
                "to the backend."
            ),
            "current_model": CURRENT_ARCHITECTURE,
        },
    )


def test_generate_architecture_proposal(
    monkeypatch,
) -> None:
    def fake_generate(
        prompt: str,
        current_model: ArchitectureModel,
    ) -> GenerateResponse:
        assert "security" in prompt.lower()
        assert (
            current_model.components[0].id
            == "backend"
        )
        return build_proposal()

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        fake_generate,
    )

    response = post_generate()

    assert response.status_code == 200

    body = response.json()

    assert body["summary"].startswith(
        "Add a security layer"
    )
    assert (
        body["architecture"]["components"][0]["id"]
        == "backend"
    )
    assert len(
        body["architecture"]["components"]
    ) == 3
    assert len(
        body["architecture"]["connections"]
    ) == 2
    assert body["changes"]["added_component_ids"] == [
        "security-layer",
        "database",
    ]


def test_generate_rejects_empty_prompt() -> None:
    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": "",
            "current_model": CURRENT_ARCHITECTURE,
        },
    )

    assert response.status_code == 422


def test_generate_requires_current_model() -> None:
    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": "Add a database.",
        },
    )

    assert response.status_code == 422


def test_generate_rejects_missing_component_id(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    del invalid["architecture"]["components"][1]["id"]

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422


def test_generate_rejects_missing_component_name(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["components"][1]["name"] = " "

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422


def test_generate_rejects_invalid_position(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["components"][1]["position"]["x"] = "left"

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422


def test_generate_rejects_duplicate_component_ids(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["components"][1]["id"] = "backend"

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422
    assert (
        "duplicated"
        in str(response.json()["detail"])
    )


def test_generate_rejects_missing_connection_source(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["connections"][0]["source"] = ""

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422


def test_generate_rejects_unknown_connection_target(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["connections"][0]["target"] = "unknown"

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422
    assert (
        "unknown target"
        in str(response.json()["detail"])
    )


def test_generate_rejects_self_connection(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["connections"][0]["target"] = "backend"

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422
    assert (
        "itself"
        in str(response.json()["detail"])
    )


def test_generate_rejects_duplicate_connection_ids(
    monkeypatch,
) -> None:
    invalid = build_proposal().model_dump()
    invalid["architecture"]["connections"][1]["id"] = "backend-security"

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt, current_model: invalid,
    )

    response = post_generate()

    assert response.status_code == 422
    assert (
        "duplicated"
        in str(response.json()["detail"])
    )


def test_generate_handles_service_validation_failure(
    monkeypatch,
) -> None:
    def raise_validation_error(
        prompt: str,
        current_model: ArchitectureModel,
    ) -> GenerateResponse:
        raise ValueError(
            "The generated proposal did not "
            "match the required schema."
        )

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        raise_validation_error,
    )

    response = post_generate()

    assert response.status_code == 422
    assert response.json()["detail"] == (
        "The generated proposal did not "
        "match the required schema."
    )


def test_generate_handles_service_failure(
    monkeypatch,
) -> None:
    def raise_service_error(
        prompt: str,
        current_model: ArchitectureModel,
    ) -> GenerateResponse:
        raise RuntimeError(
            "OpenAI service unavailable."
        )

    monkeypatch.setattr(
        ai,
        "generate_architecture",
        raise_service_error,
    )

    response = post_generate()

    assert response.status_code == 502
