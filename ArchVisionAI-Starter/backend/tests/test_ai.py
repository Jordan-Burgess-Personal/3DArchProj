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
    "name": "Existing Architecture",
    "description": "Architecture already on the canvas.",
    "components": [
        {
            "id": "backend",
            "type": "backend",
            "name": "FastAPI Backend",
            "technology": "FastAPI",
            "description": "Existing application API.",
            "position": {
                "x": 8,
                "y": 0.5,
                "z": 4,
            },
        },
    ],
    "connections": [],
}


PROPOSED_ARCHITECTURE = {
    "name": "Existing Architecture",
    "description": "Architecture already on the canvas.",
    "components": [
        CURRENT_ARCHITECTURE["components"][0],
        {
            "id": "security-layer",
            "type": "auth",
            "name": "Security Layer",
            "technology": "OAuth2",
            "description": "Authenticates requests.",
            "position": {
                "x": 0,
                "y": 0.5,
                "z": 0,
            },
        },
        {
            "id": "database",
            "type": "database",
            "name": "Application Database",
            "technology": "PostgreSQL",
            "description": "Stores application data.",
            "position": {
                "x": 4,
                "y": 0.5,
                "z": 0,
            },
        },
    ],
    "connections": [
        {
            "id": "backend-security",
            "source": "backend",
            "target": "security-layer",
            "label": "Authenticates requests",
        },
        {
            "id": "security-database",
            "source": "security-layer",
            "target": "database",
            "label": "Accesses protected data",
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

    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": (
                "Add a security layer and database "
                "to the backend."
            ),
            "current_model": CURRENT_ARCHITECTURE,
        },
    )

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


def test_generate_handles_validation_failure(
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

    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": (
                "Add a database to the backend."
            ),
            "current_model": CURRENT_ARCHITECTURE,
        },
    )

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

    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": (
                "Add a database to the backend."
            ),
            "current_model": CURRENT_ARCHITECTURE,
        },
    )

    assert response.status_code == 502
    assert response.json()["detail"] == (
        "The architecture proposal could not be generated. "
        "Please revise the prompt and try again."
    )


def test_architecture_feedback() -> None:
    response = client.post(
        "/api/ai/feedback",
        json={
            "model": CURRENT_ARCHITECTURE,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body["suggestions"],
        list,
    )
    assert len(body["suggestions"]) > 0