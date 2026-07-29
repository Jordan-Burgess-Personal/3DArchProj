from pathlib import Path

from app.schemas import (
    ArchitectureModel,
    Component,
    Connection,
    Position,
)
from app.services.frontend_generator import (
    detect_frontend_framework,
    find_supported_frontend,
    generate_frontend_files,
    get_frontend_rest_connections,
    get_skipped_frontend_components,
    has_frontend_rest_connection,
    is_frontend_component,
    is_rest_api_connection,
)


def make_component(
    *,
    component_id: str,
    component_type: str,
    name: str,
    technology: str | None = None,
    description: str | None = None,
) -> Component:
    """Create a valid architecture component for frontend generator tests."""

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
    protocol: str | None = None,
) -> Connection:
    """Create a valid architecture connection for frontend generator tests."""

    connection_kwargs = {
        "id": connection_id,
        "source": source,
        "target": target,
        "connection_type": connection_type,
        "label": label,
        "metadata": {},
    }

    if protocol is not None:
        connection_kwargs["protocol"] = protocol

    return Connection(**connection_kwargs)


def make_architecture(
    components: list[Component],
    connections: list[Connection] | None = None,
    *,
    name: str = "Generated Test Project",
    description: str | None = (
        "Architecture used for frontend generator testing."
    ),
) -> ArchitectureModel:
    """Create an architecture containing supplied components/connections."""

    return ArchitectureModel(
        name=name,
        description=description,
        components=components,
        connections=connections or [],
    )


def read_file(path: Path) -> str:
    """Read generated text using UTF-8."""

    return path.read_text(encoding="utf-8")


def normalized_generated_files(result: dict) -> set[str]:
    """Normalize generated paths for platform-independent assertions."""

    return {
        str(path).replace("\\", "/")
        for path in result["generated_frontend_files"]
    }


def test_identifies_frontend_component() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Frontend",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_identifies_frontend_component_named_browser_client() -> None:
    component = make_component(
        component_id="client",
        component_type="frontend",
        name="Browser Client",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_identifies_frontend_component_named_web_application() -> None:
    component = make_component(
        component_id="web",
        component_type="frontend",
        name="Web Application",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_identifies_vite_frontend_component() -> None:
    component = make_component(
        component_id="web-app",
        component_type="frontend",
        name="Web Application",
        technology="Vite",
    )

    assert is_frontend_component(component) is True


def test_identifies_frontend_component_with_react() -> None:
    component = make_component(
        component_id="webapp",
        component_type="frontend",
        name="Web Application",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_identifies_user_interface_frontend() -> None:
    component = make_component(
        component_id="ui",
        component_type="frontend",
        name="User Interface",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_identifies_user_interface_frontend_with_description() -> None:
    component = make_component(
        component_id="ui-description",
        component_type="frontend",
        name="User Interface",
        technology="React",
        description="Primary browser interface.",
    )

    assert is_frontend_component(component) is True


def test_frontend_component_is_detected_with_valid_schema_type() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    assert is_frontend_component(component) is True


def test_backend_is_not_frontend_component() -> None:
    component = make_component(
        component_id="backend",
        component_type="backend",
        name="API Service",
        technology="FastAPI",
    )

    assert is_frontend_component(component) is False


def test_worker_is_not_frontend_component() -> None:
    component = make_component(
        component_id="worker",
        component_type="worker",
        name="Background Worker",
        technology="Python",
    )

    assert is_frontend_component(component) is False


def test_detects_react_from_technology() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
        technology="React",
    )

    assert detect_frontend_framework(component) == "react"


def test_detects_react_from_name() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="JavaScript",
    )

    assert detect_frontend_framework(component) == "react"


def test_detects_react_from_description() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
        technology="JavaScript",
        description="A browser interface built with React.",
    )

    assert detect_frontend_framework(component) == "react"


def test_detects_vite_as_react_framework() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
        technology="Vite",
    )

    assert detect_frontend_framework(component) == "react"


def test_detects_react_case_insensitively() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
        technology="rEaCt",
    )

    assert detect_frontend_framework(component) == "react"


def test_detects_vite_case_insensitively() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
        technology="VITE",
    )

    assert detect_frontend_framework(component) == "react"


def test_returns_none_for_unsupported_frontend_framework() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Angular Frontend",
        technology="Angular",
    )

    assert detect_frontend_framework(component) is None


def test_returns_none_for_frontend_without_framework_information() -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Web Application",
    )

    assert detect_frontend_framework(component) is None


def test_returns_none_for_backend_containing_react_word() -> None:
    component = make_component(
        component_id="backend",
        component_type="backend",
        name="React Data API",
        technology="FastAPI",
    )

    assert detect_frontend_framework(component) is None


def test_finds_first_supported_frontend() -> None:
    unsupported = make_component(
        component_id="angular",
        component_type="frontend",
        name="Angular Frontend",
        technology="Angular",
    )
    supported = make_component(
        component_id="react",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    component, framework = find_supported_frontend(
        make_architecture([unsupported, supported])
    )

    assert component is not None
    assert component.id == "react"
    assert framework == "react"


def test_returns_no_supported_frontend_when_none_exists() -> None:
    model = make_architecture([
        make_component(
            component_id="backend",
            component_type="backend",
            name="FastAPI Backend",
            technology="FastAPI",
        ),
        make_component(
            component_id="angular",
            component_type="frontend",
            name="Angular Frontend",
            technology="Angular",
        ),
    ])

    component, framework = find_supported_frontend(model)

    assert component is None
    assert framework is None


def test_reports_skipped_frontend_components() -> None:
    model = make_architecture([
        make_component(
            component_id="react",
            component_type="frontend",
            name="React Frontend",
            technology="React",
        ),
        make_component(
            component_id="angular",
            component_type="frontend",
            name="Angular Frontend",
            technology="Angular",
        ),
        make_component(
            component_id="backend",
            component_type="backend",
            name="FastAPI Backend",
            technology="FastAPI",
        ),
    ])

    assert get_skipped_frontend_components(
        model,
        generated_component_id="react",
    ) == ["Angular Frontend"]


def test_reports_additional_supported_frontend_as_skipped() -> None:
    model = make_architecture([
        make_component(
            component_id="primary",
            component_type="frontend",
            name="Primary React Frontend",
            technology="React",
        ),
        make_component(
            component_id="secondary",
            component_type="frontend",
            name="Secondary Vite Frontend",
            technology="Vite",
        ),
    ])

    assert get_skipped_frontend_components(
        model,
        generated_component_id="primary",
    ) == ["Secondary Vite Frontend"]


def test_reports_all_frontends_when_none_generated() -> None:
    model = make_architecture([
        make_component(
            component_id="angular",
            component_type="frontend",
            name="Angular Frontend",
            technology="Angular",
        ),
        make_component(
            component_id="vue",
            component_type="frontend",
            name="Vue Frontend",
            technology="Vue",
        ),
    ])

    assert get_skipped_frontend_components(model) == [
        "Angular Frontend",
        "Vue Frontend",
    ]


def test_api_call_without_protocol_is_rest_connection() -> None:
    connection = make_connection(
        connection_id="rest",
        source="frontend",
        target="backend",
    )

    assert is_rest_api_connection(connection) is True


def test_http_api_call_is_rest_connection() -> None:
    connection = make_connection(
        connection_id="http",
        source="frontend",
        target="backend",
        protocol="http",
    )

    assert is_rest_api_connection(connection) is True


def test_https_api_call_is_rest_connection() -> None:
    connection = make_connection(
        connection_id="https",
        source="frontend",
        target="backend",
        protocol="https",
    )

    assert is_rest_api_connection(connection) is True


def test_rest_protocol_api_call_is_rest_connection() -> None:
    connection = make_connection(
        connection_id="rest",
        source="frontend",
        target="backend",
        protocol="rest",
    )

    assert is_rest_api_connection(connection) is True


def test_rest_api_protocol_api_call_is_rest_connection() -> None:
    connection = make_connection(
        connection_id="rest-api",
        source="frontend",
        target="backend",
        protocol="rest-api",
    )

    assert is_rest_api_connection(connection) is True


def test_dependency_connection_is_not_rest_connection() -> None:
    connection = make_connection(
        connection_id="dependency",
        source="frontend",
        target="backend",
        connection_type="dependency",
        label="Depends On",
    )

    assert is_rest_api_connection(connection) is False


def test_non_rest_protocol_is_not_rest_connection() -> None:
    connection = make_connection(
        connection_id="grpc",
        source="frontend",
        target="backend",
        protocol="grpc",
    )

    assert is_rest_api_connection(connection) is False


def test_gets_outgoing_frontend_rest_connection() -> None:
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
        connection_id="frontend-backend",
        source="frontend",
        target="backend",
    )

    result = get_frontend_rest_connections(
        make_architecture([frontend, backend], [connection]),
        "frontend",
    )

    assert [item.id for item in result] == ["frontend-backend"]


def test_gets_incoming_frontend_rest_connection() -> None:
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
        connection_id="backend-frontend",
        source="backend",
        target="frontend",
    )

    result = get_frontend_rest_connections(
        make_architecture([frontend, backend], [connection]),
        "frontend",
    )

    assert [item.id for item in result] == ["backend-frontend"]


def test_ignores_rest_connection_not_attached_to_frontend() -> None:
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
    database = make_component(
        component_id="database",
        component_type="database",
        name="PostgreSQL Database",
        technology="PostgreSQL",
    )
    connection = make_connection(
        connection_id="backend-database",
        source="backend",
        target="database",
    )

    result = get_frontend_rest_connections(
        make_architecture(
            [frontend, backend, database],
            [connection],
        ),
        "frontend",
    )

    assert result == []


def test_ignores_non_rest_connection_attached_to_frontend() -> None:
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
        connection_id="dependency",
        source="frontend",
        target="backend",
        connection_type="dependency",
    )

    result = get_frontend_rest_connections(
        make_architecture([frontend, backend], [connection]),
        "frontend",
    )

    assert result == []


def test_has_frontend_rest_connection_returns_true() -> None:
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
        connection_id="frontend-backend",
        source="frontend",
        target="backend",
    )

    assert has_frontend_rest_connection(
        make_architecture([frontend, backend], [connection]),
        "frontend",
    ) is True


def test_has_frontend_rest_connection_returns_false() -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    assert has_frontend_rest_connection(
        make_architecture([frontend]),
        "frontend",
    ) is False


def test_generates_react_frontend_files(tmp_path: Path) -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Web Frontend",
        technology="React",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([component]),
    )

    app_file = tmp_path / "frontend" / "src" / "App.jsx"
    main_file = tmp_path / "frontend" / "src" / "main.jsx"

    assert result["frontend_framework"] == "react"
    assert result["generated_frontend_component_id"] == "frontend"
    assert normalized_generated_files(result) == {
        "frontend/src/App.jsx",
        "frontend/src/main.jsx",
    }
    assert result["generated_frontend_rest_connection_ids"] == []
    assert result["skipped_frontend_components"] == []
    assert app_file.exists()
    assert main_file.exists()


def test_generates_vite_frontend_as_react(tmp_path: Path) -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Vite Web Frontend",
        technology="Vite",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([component]),
    )

    assert result["frontend_framework"] == "react"
    assert result["generated_frontend_component_id"] == "frontend"
    assert normalized_generated_files(result) == {
        "frontend/src/App.jsx",
        "frontend/src/main.jsx",
    }


def test_generated_app_contains_project_information(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="Customer Portal",
        technology="React",
        description="Main browser application.",
    )
    backend = make_component(
        component_id="backend",
        component_type="backend",
        name="Application API",
        technology="FastAPI",
        description="Backend REST service.",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture(
            [frontend, backend],
            name="ArchVision Example",
            description="Generated architecture example.",
        ),
    )

    content = read_file(
        tmp_path / "frontend" / "src" / "App.jsx"
    )

    assert 'const projectName = "ArchVision Example"' in content
    assert 'const frontendName = "Customer Portal"' in content
    assert (
        'const projectDescription = '
        '"Generated architecture example."'
    ) in content
    assert "Generated React Starter" in content
    assert "Architecture Components" in content
    assert "Architecture Connections" in content
    assert "ArchVision AI" in content


def test_generated_app_contains_architecture_components(
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

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend]),
    )

    content = read_file(
        tmp_path / "frontend" / "src" / "App.jsx"
    )

    assert '"id": "frontend"' in content
    assert '"name": "React Frontend"' in content
    assert '"technology": "React"' in content
    assert '"id": "backend"' in content
    assert '"name": "FastAPI Backend"' in content
    assert '"technology": "FastAPI"' in content


def test_generated_app_contains_architecture_connections(
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
        connection_id="frontend-backend",
        source="frontend",
        target="backend",
        label="Frontend REST API",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend], [connection]),
    )

    content = read_file(
        tmp_path / "frontend" / "src" / "App.jsx"
    )

    assert '"source": "frontend"' in content
    assert '"target": "backend"' in content
    assert '"label": "Frontend REST API"' in content
    assert '"type": "api-call"' in content


def test_generated_app_uses_component_fallback_values(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    component_without_optional_fields = make_component(
        component_id="service",
        component_type="service",
        name="Generic Service",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture(
            [frontend, component_without_optional_fields],
        ),
    )

    content = read_file(
        tmp_path / "frontend" / "src" / "App.jsx"
    )

    assert '"technology": "Not specified"' in content
    assert '"description": "No description provided."' in content


def test_generated_main_file_contains_react_entry_point(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend]),
    )

    content = read_file(
        tmp_path / "frontend" / "src" / "main.jsx"
    )

    assert "import { StrictMode } from 'react'" in content
    assert "import { createRoot } from 'react-dom/client'" in content
    assert "import App from './App.jsx'" in content
    assert "document.getElementById('root')" in content
    assert "createRoot(rootElement).render(" in content
    assert "<App />" in content


def test_rest_connection_generates_api_service(
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

    result = generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend], [connection]),
    )

    api_file = (
        tmp_path
        / "frontend"
        / "src"
        / "services"
        / "api.js"
    )

    assert api_file.exists()
    assert "frontend/src/services/api.js" in (
        normalized_generated_files(result)
    )
    assert result["generated_frontend_rest_connection_ids"] == [
        "frontend-backend-rest"
    ]


def test_generated_api_service_contains_fetch_client(
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

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend], [connection]),
    )

    content = read_file(
        tmp_path
        / "frontend"
        / "src"
        / "services"
        / "api.js"
    )

    assert "import.meta.env.VITE_API_BASE_URL" in content
    assert "'http://localhost:8000'" in content
    assert "async function request(path, options = {})" in content
    assert "await fetch(" in content
    assert "'Content-Type': 'application/json'" in content
    assert "response.status === 204" in content
    assert "response.json()" in content
    assert "export function get(" in content
    assert "export function post(" in content
    assert "export function put(" in content
    assert "export function patch(" in content
    assert "export function remove(" in content
    assert "export { API_BASE_URL, request }" in content


def test_multiple_rest_connections_are_reported(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )
    backend_one = make_component(
        component_id="backend-one",
        component_type="backend",
        name="Primary Backend",
        technology="FastAPI",
    )
    backend_two = make_component(
        component_id="backend-two",
        component_type="backend",
        name="Secondary Backend",
        technology="Flask",
    )
    connections = [
        make_connection(
            connection_id="rest-one",
            source="frontend",
            target="backend-one",
        ),
        make_connection(
            connection_id="rest-two",
            source="frontend",
            target="backend-two",
        ),
    ]

    result = generate_frontend_files(
        tmp_path,
        make_architecture(
            [frontend, backend_one, backend_two],
            connections,
        ),
    )

    assert result["generated_frontend_rest_connection_ids"] == [
        "rest-one",
        "rest-two",
    ]
    assert normalized_generated_files(result) == {
        "frontend/src/App.jsx",
        "frontend/src/main.jsx",
        "frontend/src/services/api.js",
    }


def test_dependency_connection_does_not_generate_api_service(
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

    result = generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend], [dependency]),
    )

    assert not (
        tmp_path
        / "frontend"
        / "src"
        / "services"
        / "api.js"
    ).exists()
    assert "frontend/src/services/api.js" not in (
        normalized_generated_files(result)
    )
    assert result["generated_frontend_rest_connection_ids"] == []


def test_unrelated_rest_connection_does_not_generate_api_service(
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
    worker = make_component(
        component_id="worker",
        component_type="worker",
        name="Worker",
        technology="Python",
    )
    connection = make_connection(
        connection_id="backend-worker-rest",
        source="backend",
        target="worker",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture(
            [frontend, backend, worker],
            [connection],
        ),
    )

    assert not (
        tmp_path
        / "frontend"
        / "src"
        / "services"
        / "api.js"
    ).exists()
    assert result["generated_frontend_rest_connection_ids"] == []


def test_skips_unsupported_frontend(tmp_path: Path) -> None:
    component = make_component(
        component_id="angular",
        component_type="frontend",
        name="Angular Frontend",
        technology="Angular",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([component]),
    )

    assert result["frontend_framework"] is None
    assert result["generated_frontend_component_id"] is None
    assert result["generated_frontend_files"] == []
    assert result["generated_frontend_rest_connection_ids"] == []
    assert result["skipped_frontend_components"] == [
        "Angular Frontend"
    ]
    assert not (tmp_path / "frontend").exists()


def test_does_not_generate_frontend_for_backend(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="backend",
        component_type="backend",
        name="FastAPI Backend",
        technology="FastAPI",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([component]),
    )

    assert result["frontend_framework"] is None
    assert result["generated_frontend_component_id"] is None
    assert result["generated_frontend_files"] == []
    assert result["generated_frontend_rest_connection_ids"] == []
    assert result["skipped_frontend_components"] == []
    assert not (tmp_path / "frontend").exists()


def test_generates_only_frontend_owned_files(
    tmp_path: Path,
) -> None:
    component = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture([component]),
    )

    assert (tmp_path / "frontend" / "src" / "App.jsx").exists()
    assert (tmp_path / "frontend" / "src" / "main.jsx").exists()
    assert not (tmp_path / "frontend" / "package.json").exists()
    assert not (tmp_path / "frontend" / "index.html").exists()
    assert not (tmp_path / "frontend" / "src" / "index.css").exists()
    assert not (tmp_path / "requirements.txt").exists()
    assert not (tmp_path / "README.md").exists()
    assert not (tmp_path / "docker-compose.yml").exists()
    assert not (tmp_path / "backend").exists()
    assert not (tmp_path / "database").exists()


def test_first_supported_frontend_is_generated(
    tmp_path: Path,
) -> None:
    first = make_component(
        component_id="first",
        component_type="frontend",
        name="First React Frontend",
        technology="React",
    )
    second = make_component(
        component_id="second",
        component_type="frontend",
        name="Second Vite Frontend",
        technology="Vite",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([first, second]),
    )

    assert result["generated_frontend_component_id"] == "first"
    assert result["skipped_frontend_components"] == [
        "Second Vite Frontend"
    ]

    content = read_file(
        tmp_path / "frontend" / "src" / "App.jsx"
    )
    assert 'const frontendName = "First React Frontend"' in content


def test_unsupported_frontend_before_supported_is_reported_as_skipped(
    tmp_path: Path,
) -> None:
    unsupported = make_component(
        component_id="angular",
        component_type="frontend",
        name="Angular Frontend",
        technology="Angular",
    )
    supported = make_component(
        component_id="react",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    result = generate_frontend_files(
        tmp_path,
        make_architecture([unsupported, supported]),
    )

    assert result["generated_frontend_component_id"] == "react"
    assert result["skipped_frontend_components"] == [
        "Angular Frontend"
    ]


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

    result = generate_frontend_files(
        tmp_path,
        make_architecture([frontend, backend], connections),
    )

    generated_files = [
        str(path).replace("\\", "/")
        for path in result["generated_frontend_files"]
    ]

    assert len(generated_files) == len(set(generated_files))


def test_generation_overwrites_existing_owned_files(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    app_file = tmp_path / "frontend" / "src" / "App.jsx"
    main_file = tmp_path / "frontend" / "src" / "main.jsx"
    app_file.parent.mkdir(parents=True, exist_ok=True)
    app_file.write_text("stale app", encoding="utf-8")
    main_file.write_text("stale main", encoding="utf-8")

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend]),
    )

    assert read_file(app_file) != "stale app"
    assert read_file(main_file) != "stale main"
    assert "function App()" in read_file(app_file)
    assert "createRoot(rootElement).render(" in read_file(main_file)


def test_generation_preserves_unowned_frontend_file(
    tmp_path: Path,
) -> None:
    frontend = make_component(
        component_id="frontend",
        component_type="frontend",
        name="React Frontend",
        technology="React",
    )

    custom_file = tmp_path / "frontend" / "src" / "custom.js"
    custom_file.parent.mkdir(parents=True, exist_ok=True)
    custom_file.write_text(
        "export const custom = true",
        encoding="utf-8",
    )

    generate_frontend_files(
        tmp_path,
        make_architecture([frontend]),
    )

    assert custom_file.exists()
    assert read_file(custom_file) == "export const custom = true"