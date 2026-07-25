from pathlib import Path

from app.schemas import (
    ArchitectureModel,
    Component,
    Position,
)
from app.services.backend_generator import (
    detect_backend_framework,
    find_supported_backend,
    generate_backend_files,
    get_skipped_backend_components,
    is_backend_component,
)


def make_component(
    *,
    component_id: str,
    component_type: str,
    name: str,
    technology: str | None = None,
    description: str | None = None,
) -> Component:
    """Create a valid component for backend generator tests."""

    return Component(
        id=component_id,
        type=component_type,
        name=name,
        technology=technology,
        description=description,
        position=Position(
            x=0,
            y=0,
            z=0,
        ),
        metadata={},
    )


def make_architecture(
    components: list[Component],
) -> ArchitectureModel:
    """Create a basic architecture containing the supplied components."""

    return ArchitectureModel(
        name="Generated Test Project",
        description=(
            "Architecture used for backend generator testing."
        ),
        components=components,
        connections=[],
    )


def test_identifies_backend_component() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="API Service",
        technology="FastAPI",
    )

    assert is_backend_component(component) is True


def test_frontend_is_not_backend_component() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Frontend",
        technology="React",
    )

    assert is_backend_component(component) is False


def test_detects_fastapi_from_technology() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Python FastAPI",
    )

    assert (
        detect_backend_framework(component)
        == "fastapi"
    )


def test_detects_fastapi_from_name() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI Service",
        technology="Python",
    )

    assert (
        detect_backend_framework(component)
        == "fastapi"
    )


def test_detects_flask_from_technology() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Flask",
    )

    assert (
        detect_backend_framework(component)
        == "flask"
    )


def test_detects_flask_from_description() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Python",
        description=(
            "Backend application using the Flask framework."
        ),
    )

    assert (
        detect_backend_framework(component)
        == "flask"
    )


def test_returns_none_for_unsupported_backend() -> None:
    component = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )

    assert (
        detect_backend_framework(component)
        is None
    )


def test_returns_none_for_frontend_using_flask_word() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Flask Documentation Frontend",
        technology="React",
    )

    assert (
        detect_backend_framework(component)
        is None
    )


def test_finds_first_supported_backend() -> None:
    unsupported = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )

    supported = make_component(
        component_id="fastapi-api",
        component_type="backend",
        name="FastAPI API",
        technology="FastAPI",
    )

    model = make_architecture(
        [
            unsupported,
            supported,
        ]
    )

    component, framework = (
        find_supported_backend(model)
    )

    assert component is not None
    assert component.id == "fastapi-api"
    assert framework == "fastapi"


def test_reports_skipped_backend_components() -> None:
    fastapi_component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI API",
        technology="FastAPI",
    )

    unsupported_component = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )

    frontend_component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    model = make_architecture(
        [
            fastapi_component,
            unsupported_component,
            frontend_component,
        ]
    )

    skipped = get_skipped_backend_components(
        model,
        generated_component_id="api",
    )

    assert skipped == [
        "Spring Boot API",
    ]


def test_generates_fastapi_backend_files(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI Application API",
        technology="FastAPI",
    )

    model = make_architecture(
        [component]
    )

    result = generate_backend_files(
        tmp_path,
        model,
    )

    init_file = (
        tmp_path
        / "backend"
        / "app"
        / "__init__.py"
    )

    main_file = (
        tmp_path
        / "backend"
        / "app"
        / "main.py"
    )

    assert result["framework"] == "fastapi"
    assert (
        result["generated_component_id"]
        == "api"
    )

    assert result[
        "generated_backend_files"
    ] == [
        "backend/app/__init__.py",
        "backend/app/main.py",
    ]

    assert result[
        "skipped_backend_components"
    ] == []

    assert init_file.exists()
    assert main_file.exists()

    main_content = main_file.read_text(
        encoding="utf-8",
    )

    assert (
        "from fastapi import FastAPI"
        in main_content
    )

    assert (
        "app = FastAPI("
        in main_content
    )

    assert (
        '@app.get("/")'
        in main_content
    )

    assert (
        '@app.get("/api/health")'
        in main_content
    )

    assert (
        '@app.get("/api/example")'
        in main_content
    )


def test_generates_flask_backend_files(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Flask Application API",
        technology="Flask",
    )

    model = make_architecture(
        [component]
    )

    result = generate_backend_files(
        tmp_path,
        model,
    )

    main_file = (
        tmp_path
        / "backend"
        / "app"
        / "main.py"
    )

    assert result["framework"] == "flask"
    assert main_file.exists()

    main_content = main_file.read_text(
        encoding="utf-8",
    )

    assert (
        "from flask import Flask, jsonify"
        in main_content
    )

    assert (
        "def create_app() -> Flask:"
        in main_content
    )

    assert (
        '@app.get("/")'
        in main_content
    )

    assert (
        '@app.get("/api/health")'
        in main_content
    )

    assert (
        '@app.get("/api/example")'
        in main_content
    )

    assert (
        'if __name__ == "__main__":'
        in main_content
    )


def test_skips_unsupported_backend(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )

    model = make_architecture(
        [component]
    )

    result = generate_backend_files(
        tmp_path,
        model,
    )

    assert result["framework"] is None

    assert (
        result["generated_component_id"]
        is None
    )

    assert result[
        "generated_backend_files"
    ] == []

    assert result[
        "skipped_backend_components"
    ] == [
        "Spring Boot API",
    ]

    assert not (
        tmp_path
        / "backend"
        / "app"
        / "main.py"
    ).exists()


def test_does_not_generate_backend_for_frontend(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Web Frontend",
        technology="React",
    )

    model = make_architecture(
        [component]
    )

    result = generate_backend_files(
        tmp_path,
        model,
    )

    assert result["framework"] is None

    assert result[
        "generated_backend_files"
    ] == []

    assert result[
        "skipped_backend_components"
    ] == []

    assert not (
        tmp_path
        / "backend"
    ).exists()


def test_generates_only_backend_source_files(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI API",
        technology="FastAPI",
    )

    model = make_architecture(
        [component]
    )

    generate_backend_files(
        tmp_path,
        model,
    )

    assert (
        tmp_path
        / "backend"
        / "app"
        / "__init__.py"
    ).exists()

    assert (
        tmp_path
        / "backend"
        / "app"
        / "main.py"
    ).exists()

    assert not (
        tmp_path
        / "requirements.txt"
    ).exists()

    assert not (
        tmp_path
        / "backend"
        / "requirements.txt"
    ).exists()

    assert not (
        tmp_path
        / "README.md"
    ).exists()

    assert not (
        tmp_path
        / "docker-compose.yml"
    ).exists()

    assert not (
        tmp_path
        / "frontend"
    ).exists()

    assert not (
        tmp_path
        / "database"
    ).exists()