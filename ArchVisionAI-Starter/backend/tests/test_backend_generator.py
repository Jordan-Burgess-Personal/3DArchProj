from pathlib import Path

from app.schemas import (
    ArchitectureModel,
    Component,
    Connection,
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
    """Create a valid architecture component for generator tests."""

    return Component(
        id=component_id,
        type=component_type,
        name=name,
        technology=technology,
        description=description,
        position=Position(x=0, y=0, z=0),
        metadata={},
    )


def make_connection(
    *,
    connection_id: str,
    source: str,
    target: str,
    connection_type: str = "api-call",
    label: str = "REST API",
) -> Connection:
    """Create a valid architecture connection for generator tests."""

    return Connection(
        id=connection_id,
        source=source,
        target=target,
        connection_type=connection_type,
        label=label,
        metadata={},
    )


def make_architecture(
    components: list[Component],
    connections: list[Connection] | None = None,
) -> ArchitectureModel:
    """Create an architecture containing supplied components/connections."""

    return ArchitectureModel(
        name="Generated Test Project",
        description="Architecture used for backend generator testing.",
        components=components,
        connections=connections or [],
    )


def read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalized_generated_files(result: dict) -> set[str]:
    return {
        str(path).replace("\\", "/")
        for path in result["generated_backend_files"]
    }


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


def test_worker_is_treated_as_backend_component() -> None:
    component = make_component(
        component_id="worker",
        component_type="worker",
        name="Background Worker",
        technology="Python",
    )
    assert is_backend_component(component) is True


def test_detects_fastapi_from_technology() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Python FastAPI",
    )
    assert detect_backend_framework(component) == "fastapi"


def test_detects_fastapi_from_name() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI Service",
        technology="Python",
    )
    assert detect_backend_framework(component) == "fastapi"


def test_detects_fastapi_case_insensitively() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="FASTAPI",
    )
    assert detect_backend_framework(component) == "fastapi"


def test_detects_flask_from_technology() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Flask",
    )
    assert detect_backend_framework(component) == "flask"


def test_detects_flask_from_description() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="Python",
        description="Backend application using the Flask framework.",
    )
    assert detect_backend_framework(component) == "flask"


def test_detects_flask_case_insensitively() -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Application API",
        technology="fLaSk",
    )
    assert detect_backend_framework(component) == "flask"


def test_returns_none_for_unsupported_backend() -> None:
    component = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )
    assert detect_backend_framework(component) is None


def test_returns_none_for_backend_without_framework_information() -> None:
    component = make_component(
        component_id="generic-api",
        component_type="backend",
        name="Application Service",
    )
    assert detect_backend_framework(component) is None


def test_returns_none_for_frontend_using_flask_word() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Flask Documentation Frontend",
        technology="React",
    )
    assert detect_backend_framework(component) is None


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
    component, framework = find_supported_backend(
        make_architecture([unsupported, supported])
    )
    assert component is not None
    assert component.id == "fastapi-api"
    assert framework == "fastapi"


def test_returns_no_supported_backend_when_none_exists() -> None:
    model = make_architecture([
        make_component(
            component_id="frontend",
            component_type="frontend",
            name="React Frontend",
            technology="React",
        ),
        make_component(
            component_id="spring-api",
            component_type="backend",
            name="Spring Boot API",
            technology="Spring Boot",
        ),
    ])
    component, framework = find_supported_backend(model)
    assert component is None
    assert framework is None


def test_reports_skipped_backend_components() -> None:
    model = make_architecture([
        make_component(
            component_id="api",
            component_type="backend",
            name="FastAPI API",
            technology="FastAPI",
        ),
        make_component(
            component_id="spring-api",
            component_type="backend",
            name="Spring Boot API",
            technology="Spring Boot",
        ),
        make_component(
            component_id="frontend",
            component_type="frontend",
            name="React Frontend",
            technology="React",
        ),
    ])
    assert get_skipped_backend_components(
        model,
        generated_component_id="api",
    ) == ["Spring Boot API"]


def test_reports_additional_supported_backend_as_skipped() -> None:
    model = make_architecture([
        make_component(
            component_id="fastapi-api",
            component_type="backend",
            name="Primary FastAPI API",
            technology="FastAPI",
        ),
        make_component(
            component_id="flask-api",
            component_type="backend",
            name="Secondary Flask API",
            technology="Flask",
        ),
    ])
    assert get_skipped_backend_components(
        model,
        generated_component_id="fastapi-api",
    ) == ["Secondary Flask API"]


def test_generates_fastapi_backend_files(tmp_path: Path) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI Application API",
        technology="FastAPI",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    init_file = tmp_path / "backend" / "app" / "__init__.py"
    main_file = tmp_path / "backend" / "app" / "main.py"
    requirements_file = tmp_path / "backend" / "requirements.txt"

    assert result["framework"] == "fastapi"
    assert result["generated_component_id"] == "api"
    assert normalized_generated_files(result) == {
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/requirements.txt",
    }
    assert result["skipped_backend_components"] == []
    assert init_file.exists()
    assert main_file.exists()
    assert requirements_file.exists()

    main_content = read_file(main_file)
    assert "from fastapi import FastAPI" in main_content
    assert "app = FastAPI(" in main_content
    assert '@app.get("/")' in main_content
    assert '@app.get("/api/health")' in main_content
    assert '@app.get("/api/example")' in main_content


def test_fastapi_requirements_are_generated(tmp_path: Path) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI API",
        technology="FastAPI",
    )
    generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    requirements = read_file(
        tmp_path / "backend" / "requirements.txt"
    ).lower()
    assert "fastapi" in requirements
    assert "uvicorn" in requirements
    assert "flask" not in requirements


def test_generates_flask_backend_files(tmp_path: Path) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Flask Application API",
        technology="Flask",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    init_file = tmp_path / "backend" / "app" / "__init__.py"
    main_file = tmp_path / "backend" / "app" / "main.py"
    requirements_file = tmp_path / "backend" / "requirements.txt"

    assert result["framework"] == "flask"
    assert result["generated_component_id"] == "api"
    assert normalized_generated_files(result) == {
        "backend/app/__init__.py",
        "backend/app/main.py",
        "backend/requirements.txt",
    }
    assert result["skipped_backend_components"] == []
    assert init_file.exists()
    assert main_file.exists()
    assert requirements_file.exists()

    main_content = read_file(main_file)
    assert "from flask import Flask, jsonify" in main_content
    assert "def create_app() -> Flask:" in main_content
    assert '@app.get("/")' in main_content
    assert '@app.get("/api/health")' in main_content
    assert '@app.get("/api/example")' in main_content
    assert 'if __name__ == "__main__":' in main_content


def test_flask_requirements_are_generated(tmp_path: Path) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="Flask API",
        technology="Flask",
    )
    generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    requirements = read_file(
        tmp_path / "backend" / "requirements.txt"
    ).lower()
    assert "flask" in requirements
    assert "fastapi" not in requirements


def test_skips_unsupported_backend(tmp_path: Path) -> None:
    component = make_component(
        component_id="spring-api",
        component_type="backend",
        name="Spring Boot API",
        technology="Spring Boot",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    assert result["framework"] is None
    assert result["generated_component_id"] is None
    assert result["generated_backend_files"] == []
    assert result["skipped_backend_components"] == ["Spring Boot API"]
    assert not (tmp_path / "backend").exists()


def test_does_not_generate_backend_for_frontend(tmp_path: Path) -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Web Frontend",
        technology="React",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    assert result["framework"] is None
    assert result["generated_component_id"] is None
    assert result["generated_backend_files"] == []
    assert result["skipped_backend_components"] == []
    assert not (tmp_path / "backend").exists()


def test_generates_only_backend_owned_files(tmp_path: Path) -> None:
    component = make_component(
        component_id="api",
        component_type="backend",
        name="FastAPI API",
        technology="FastAPI",
    )
    generate_backend_files(
        tmp_path,
        make_architecture([component]),
    )
    assert (tmp_path / "backend" / "app" / "__init__.py").exists()
    assert (tmp_path / "backend" / "app" / "main.py").exists()
    assert (tmp_path / "backend" / "requirements.txt").exists()
    assert not (tmp_path / "requirements.txt").exists()
    assert not (tmp_path / "README.md").exists()
    assert not (tmp_path / "docker-compose.yml").exists()
    assert not (tmp_path / "frontend").exists()
    assert not (tmp_path / "database").exists()


def test_fastapi_rest_connection_generates_route_files(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    backend = make_component(
        component_id="backend",
        component_type="backend",
        name="FastAPI Backend",
        technology="FastAPI",
    )
    connection = make_connection(
        connection_id="frontend-backend-rest",
        source="frontend",
        target="backend",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([frontend, backend], [connection]),
    )

    routes_init = tmp_path / "backend" / "app" / "routes" / "__init__.py"
    generated_route = tmp_path / "backend" / "app" / "routes" / "generated.py"
    main_file = tmp_path / "backend" / "app" / "main.py"

    assert routes_init.exists()
    assert generated_route.exists()
    generated_files = normalized_generated_files(result)
    assert "backend/app/routes/__init__.py" in generated_files
    assert "backend/app/routes/generated.py" in generated_files
    assert "APIRouter" in read_file(generated_route)
    assert "include_router" in read_file(main_file)

    if "generated_rest_connection_ids" in result:
        assert result["generated_rest_connection_ids"] == [
            "frontend-backend-rest"
        ]


def test_flask_rest_connection_generates_route_files(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    backend = make_component(
        component_id="backend",
        component_type="backend",
        name="Flask Backend",
        technology="Flask",
    )
    connection = make_connection(
        connection_id="frontend-backend-rest",
        source="frontend",
        target="backend",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([frontend, backend], [connection]),
    )

    routes_init = tmp_path / "backend" / "app" / "routes" / "__init__.py"
    generated_route = tmp_path / "backend" / "app" / "routes" / "generated.py"
    main_file = tmp_path / "backend" / "app" / "main.py"

    assert routes_init.exists()
    assert generated_route.exists()
    generated_files = normalized_generated_files(result)
    assert "backend/app/routes/__init__.py" in generated_files
    assert "backend/app/routes/generated.py" in generated_files
    assert "Blueprint" in read_file(generated_route)
    assert "register_blueprint" in read_file(main_file)

    if "generated_rest_connection_ids" in result:
        assert result["generated_rest_connection_ids"] == [
            "frontend-backend-rest"
        ]


def test_dependency_connection_does_not_generate_rest_routes(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    backend = make_component(
        component_id="backend",
        component_type="backend",
        name="FastAPI Backend",
        technology="FastAPI",
    )
    dependency = make_connection(
        connection_id="frontend-backend-dependency",
        source="frontend",
        target="backend",
        connection_type="dependency",
        label="Depends On",
    )
    result = generate_backend_files(
        tmp_path,
        make_architecture([frontend, backend], [dependency]),
    )

    assert not (
        tmp_path / "backend" / "app" / "routes" / "generated.py"
    ).exists()
    assert "backend/app/routes/generated.py" not in normalized_generated_files(
        result
    )
    if "generated_rest_connection_ids" in result:
        assert result["generated_rest_connection_ids"] == []


def test_generated_file_paths_do_not_contain_duplicates(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    backend = make_component(
        component_id="backend",
        component_type="backend",
        name="FastAPI Backend",
        technology="FastAPI",
    )
    connections = [
        make_connection(
            connection_id="rest-one",
            source="frontend",
            target="backend",
        ),
        make_connection(
            connection_id="rest-two",
            source="frontend",
            target="backend",
        ),
    ]
    result = generate_backend_files(
        tmp_path,
        make_architecture([frontend, backend], connections),
    )
    generated_files = [
        str(path).replace("\\", "/")
        for path in result["generated_backend_files"]
    ]
    assert len(generated_files) == len(set(generated_files))