from fastapi.testclient import TestClient

from app.main import app
from app.routes import ai


client = TestClient(app)


GENERATED_ARCHITECTURE = {
    "name": "Generated Test Architecture",
    "description": (
        "Architecture generated during API testing."
    ),
    "components": [
        {
            "id": "frontend",
            "type": "frontend",
            "name": "React Frontend",
            "technology": "React",
            "description": "User interface.",
            "position": {
                "x": -3,
                "y": 0,
                "z": 0,
            },
        },
        {
            "id": "backend",
            "type": "backend",
            "name": "FastAPI Backend",
            "technology": "FastAPI",
            "description": "Application API.",
            "position": {
                "x": 0,
                "y": 0,
                "z": 0,
            },
        },
    ],
    "connections": [
        {
            "id": "frontend-backend",
            "source": "frontend",
            "target": "backend",
            "label": "REST API",
        },
    ],
}


def test_generate_architecture(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        ai,
        "generate_architecture",
        lambda prompt: GENERATED_ARCHITECTURE,
    )

    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": (
                "Create a React frontend and "
                "FastAPI backend."
            ),
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert (
        body["name"]
        == "Generated Test Architecture"
    )

    assert len(body["components"]) == 2
    assert len(body["connections"]) == 1

    assert (
        body["connections"][0]["source"]
        == "frontend"
    )

    assert (
        body["connections"][0]["target"]
        == "backend"
    )


def test_generate_rejects_empty_prompt() -> None:
    response = client.post(
        "/api/ai/generate",
        json={
            "prompt": "",
        },
    )

    assert response.status_code == 422


def test_generate_handles_validation_failure(
    monkeypatch,
) -> None:
    def raise_validation_error(
        prompt: str,
    ) -> dict:
        raise ValueError(
            "The generated architecture did not "
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
                "Create a software architecture."
            ),
        },
    )

    assert response.status_code == 422

    assert response.json()["detail"] == (
        "The generated architecture did not "
        "match the required schema."
    )


def test_generate_handles_service_failure(
    monkeypatch,
) -> None:
    def raise_service_error(
        prompt: str,
    ) -> dict:
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
                "Create a software architecture."
            ),
        },
    )

    assert response.status_code == 502

    assert response.json()["detail"] == (
        "The architecture could not be generated. "
        "Please revise the prompt and try again."
    )


def test_architecture_feedback() -> None:
    response = client.post(
        "/api/ai/feedback",
        json={
            "model": GENERATED_ARCHITECTURE,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert isinstance(
        body["suggestions"],
        list,
    )

    assert len(body["suggestions"]) > 0