from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_export_generates_fastapi_backend():
    payload = {
        "name": "FastAPI Project",
        "description": "Generated backend",
        "components": [
            {
                "id": "backend-1",
                "type": "backend",
                "name": "API Service",
                "technology": "FastAPI",
                "description": "",
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "metadata": {},
            }
        ],
        "connections": [],
    }

    response = client.post(
        "/export/starter",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["framework"] == "fastapi"

    assert body["generated_backend_files"] == [
        "backend/app/__init__.py",
        "backend/app/main.py",
    ]

    assert body["generated_component_id"] == "backend-1"

    assert body["skipped_backend_components"] == []


def test_export_generates_flask_backend():
    payload = {
        "name": "Flask Project",
        "description": "Generated backend",
        "components": [
            {
                "id": "backend-1",
                "type": "backend",
                "name": "API Service",
                "technology": "Flask",
                "description": "",
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "metadata": {},
            }
        ],
        "connections": [],
    }

    response = client.post(
        "/export/starter",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["framework"] == "flask"

    assert body["generated_backend_files"] == [
        "backend/app/__init__.py",
        "backend/app/main.py",
    ]


def test_export_skips_unsupported_backend():
    payload = {
        "name": "Unsupported Project",
        "description": "",
        "components": [
            {
                "id": "backend-1",
                "type": "backend",
                "name": "API Service",
                "technology": "Spring Boot",
                "description": "",
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "metadata": {},
            }
        ],
        "connections": [],
    }

    response = client.post(
        "/export/starter",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["framework"] is None
    assert body["generated_backend_files"] == []
    assert body["generated_component_id"] is None

    assert body["skipped_backend_components"] == [
        "API Service",
    ]


def test_export_ignores_frontend_components():
    payload = {
        "name": "Frontend Project",
        "description": "",
        "components": [
            {
                "id": "frontend-1",
                "type": "frontend",
                "name": "Web Frontend",
                "technology": "React",
                "description": "",
                "position": {
                    "x": 0,
                    "y": 0,
                    "z": 0,
                },
                "metadata": {},
            }
        ],
        "connections": [],
    }

    response = client.post(
        "/export/starter",
        json=payload,
    )

    assert response.status_code == 201

    body = response.json()

    assert body["framework"] is None
    assert body["generated_backend_files"] == []
    assert body["skipped_backend_components"] == []