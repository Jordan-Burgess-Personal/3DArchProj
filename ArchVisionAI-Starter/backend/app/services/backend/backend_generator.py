from __future__ import annotations

from pathlib import Path
from typing import Any

from app.schemas import ArchitectureModel, Component


SUPPORTED_BACKEND_FRAMEWORKS = {
    "fastapi": "fastapi",
    "flask": "flask",
}

BACKEND_COMPONENT_TYPES = {
    "backend",
    "worker",
    "ai-service",
    "gateway",
    "auth",
    "authorization",
}


BACKEND_REQUIREMENTS = {
    "fastapi": (
        "fastapi",
        "uvicorn[standard]",
    ),
    "flask": (
        "Flask",
    ),
}


BACKEND_GENERATION_CAPABILITIES = [
    {
        "catalog_id": "api-service",
        "kind": "component",
        "generator": "backend",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "FastAPI and Flask backend starter files can be generated."
        ),
        "technologies": [
            "FastAPI",
            "Flask",
        ],
        "generated_files": [
            "backend/app/__init__.py",
            "backend/app/main.py",
            "backend/requirements.txt",
        ],
    },
    {
        "catalog_id": "rest-api",
        "kind": "connection",
        "generator": "backend",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "Starter REST route files are generated for supported "
            "backend API connections."
        ),
        "technologies": [
            "FastAPI",
            "Flask",
            "HTTP",
            "HTTPS",
            "REST",
        ],
        "generated_files": [
            "backend/app/routes/__init__.py",
            "backend/app/routes/generated.py",
        ],
    },
]


def _component_search_text(
    component: Component,
) -> str:
    """
    Combine the fields that may identify a backend framework.

    Framework detection checks the component type, name, technology,
    and description. This allows components such as "FastAPI Service"
    or components with technology set to "Python FastAPI" to work.
    """

    values = [
        component.type,
        component.name,
        component.technology,
        component.description,
    ]

    return " ".join(
        str(value)
        for value in values
        if value is not None
    ).lower()


def is_backend_component(
    component: Component,
) -> bool:
    """
    Return True when the component represents a backend responsibility.

    Components outside this set remain in the architecture but do not
    participate in backend source generation.
    """

    component_type = str(
        component.type or ""
    ).strip().lower()

    return (
        component_type
        in BACKEND_COMPONENT_TYPES
    )


def detect_backend_framework(
    component: Component,
) -> str | None:
    """
    Detect the supported backend framework selected for a component.

    Only FastAPI and Flask are supported. Unsupported backend
    technologies return None and are skipped.
    """

    if not is_backend_component(component):
        return None

    searchable_text = (
        _component_search_text(
            component,
        )
    )

    for keyword, framework in (
        SUPPORTED_BACKEND_FRAMEWORKS.items()
    ):
        if keyword in searchable_text:
            return framework

    return None


def _connection_source(connection: Any) -> str:
    """Return a connection source ID across supported schema variations."""

    return str(
        getattr(connection, "source_component_id", None)
        or getattr(connection, "source_id", None)
        or getattr(connection, "source", None)
        or ""
    )


def _connection_target(connection: Any) -> str:
    """Return a connection target ID across supported schema variations."""

    return str(
        getattr(connection, "target_component_id", None)
        or getattr(connection, "target_id", None)
        or getattr(connection, "target", None)
        or ""
    )


def is_rest_api_connection(connection: Any) -> bool:
    """Return True when a connection represents a REST-style API call."""

    connection_type = str(
        getattr(connection, "connection_type", None)
        or getattr(connection, "type", None)
        or ""
    ).strip().lower()

    protocol = str(
        getattr(connection, "protocol", None)
        or ""
    ).strip().lower()

    return (
        connection_type == "api-call"
        and protocol in {
            "",
            "http",
            "https",
            "rest",
            "rest-api",
            "rest api",
        }
    )


def get_backend_rest_connections(
    model: ArchitectureModel,
    backend_component_id: str,
) -> list[Any]:
    """Return REST connections attached to the generated backend."""

    return [
        connection
        for connection in getattr(
            model,
            "connections",
            [],
        )
        if (
            is_rest_api_connection(connection)
            and backend_component_id
            in {
                _connection_source(connection),
                _connection_target(connection),
            }
        )
    ]


def _fastapi_main_content(
    project_name: str,
    component: Component,
    include_generated_routes: bool = False,
) -> str:
    """Return the generated FastAPI starter application."""

    title = (
        component.name.strip()
        if component.name.strip()
        else project_name
    )

    route_import = ""
    route_registration = ""

    if include_generated_routes:
        route_import = (
            "from app.routes.generated import "
            "router as generated_router\n"
        )
        route_registration = (
            "\napp.include_router(generated_router)\n"
        )

    return f'''from fastapi import FastAPI
{route_import}

app = FastAPI(
    title={title!r},
    description=(
        "Starter FastAPI backend generated by ArchVision AI."
    ),
)
{route_registration}

@app.get("/")
def root() -> dict[str, str]:
    """Return a basic message showing that the backend is running."""

    return {{
        "message": "Generated FastAPI backend is running.",
        "service": {title!r},
    }}


@app.get("/api/health")
def health() -> dict[str, str]:
    """Return the current health of the generated backend."""

    return {{
        "status": "healthy",
        "service": {title!r},
    }}


@app.get("/api/example")
def example_endpoint() -> dict[str, str]:
    """Placeholder endpoint for future application logic."""

    return {{
        "message": "Replace this endpoint with application logic."
    }}
'''

def _flask_main_content(
    project_name: str,
    component: Component,
    include_generated_routes: bool = False,
) -> str:
    """Return the generated Flask starter application."""

    title = (
        component.name.strip()
        if component.name.strip()
        else project_name
    )

    route_import = ""
    route_registration = ""

    if include_generated_routes:
        route_import = (
            "from app.routes.generated import "
            "generated_blueprint\n"
        )
        route_registration = (
            "\n    app.register_blueprint("
            "generated_blueprint"
            ")\n"
        )

    return f'''from flask import Flask, jsonify
{route_import}

def create_app() -> Flask:
    """Create and configure the generated Flask application."""

    app = Flask(__name__)
{route_registration}
    @app.get("/")
    def root():
        """Return a basic message showing that the backend is running."""

        return jsonify(
            message="Generated Flask backend is running.",
            service={title!r},
        )

    @app.get("/api/health")
    def health():
        """Return the current health of the generated backend."""

        return jsonify(
            status="healthy",
            service={title!r},
        )

    @app.get("/api/example")
    def example_endpoint():
        """Placeholder endpoint for future application logic."""

        return jsonify(
            message=(
                "Replace this endpoint with application logic."
            )
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )
'''

def _main_file_content(
    framework: str,
    project_name: str,
    component: Component,
    include_generated_routes: bool = False,
) -> str:
    """Return the main application file for a supported framework."""

    if framework == "fastapi":
        return _fastapi_main_content(
            project_name,
            component,
            include_generated_routes,
        )

    if framework == "flask":
        return _flask_main_content(
            project_name,
            component,
            include_generated_routes,
        )

    raise ValueError(
        f"Unsupported backend framework: {framework}"
    )


def _fastapi_generated_routes_content() -> str:
    """Return starter FastAPI routes for generated REST support."""

    return '''from fastapi import APIRouter


router = APIRouter(
    prefix="/api/generated",
    tags=["generated"],
)


@router.get("/health")
def generated_health() -> dict[str, str]:
    """Return the health of the generated REST route."""

    return {
        "status": "healthy",
        "message": "Generated REST route is available.",
    }
'''


def _flask_generated_routes_content() -> str:
    """Return starter Flask routes for generated REST support."""

    return '''from flask import Blueprint, jsonify


generated_blueprint = Blueprint(
    "generated",
    __name__,
    url_prefix="/api/generated",
)


@generated_blueprint.get("/health")
def generated_health():
    """Return the health of the generated REST route."""

    return jsonify(
        status="healthy",
        message="Generated REST route is available.",
    )
'''


def _generated_routes_content(
    framework: str,
) -> str:
    """Return framework-specific generated REST route content."""

    if framework == "fastapi":
        return _fastapi_generated_routes_content()

    if framework == "flask":
        return _flask_generated_routes_content()

    raise ValueError(
        f"Unsupported backend framework: {framework}"
    )



def get_backend_requirements(
    framework: str,
) -> tuple[str, ...]:
    """
    Return the starter dependencies required by a supported backend.

    The generated requirements intentionally contain only packages used by
    the generated starter source. Unsupported framework names are rejected
    instead of silently producing an incomplete dependency file.
    """

    try:
        return BACKEND_REQUIREMENTS[framework]
    except KeyError as error:
        raise ValueError(
            f"Unsupported backend framework: {framework}"
        ) from error


def _requirements_content(
    framework: str,
) -> str:
    """
    Return newline-delimited requirements.txt content for the framework.
    """

    requirements = get_backend_requirements(
        framework,
    )

    return (
        "\n".join(requirements)
        + "\n"
    )


def find_supported_backend(
    model: ArchitectureModel,
) -> tuple[Component | None, str | None]:
    """
    Find the first backend component using FastAPI or Flask.

    One backend starter project is created. Additional backend
    components remain part of the architecture but do not overwrite
    the generated backend application.
    """

    for component in model.components:
        framework = (
            detect_backend_framework(
                component,
            )
        )

        if framework:
            return component, framework

    return None, None


def get_skipped_backend_components(
    model: ArchitectureModel,
    generated_component_id: str | None = None,
) -> list[str]:
    """
    Return backend components that did not generate source files.

    Unsupported backend technologies are reported as skipped. Supported
    components appearing after the selected backend are also skipped
    because only one starter backend is generated.
    """

    skipped: list[str] = []

    for component in model.components:
        if not is_backend_component(
            component,
        ):
            continue

        if (
            generated_component_id is not None
            and component.id
            == generated_component_id
        ):
            continue

        skipped.append(
            component.name,
        )

    return skipped


def generate_backend_files(
    project_dir: Path,
    model: ArchitectureModel,
) -> dict[str, Any]:
    """
    Generate backend starter source files for the architecture.

    This function always generates:

    - backend/app/__init__.py
    - backend/app/main.py
    - backend/requirements.txt

    When the selected backend participates in a REST API connection, it
    also generates:

    - backend/app/routes/__init__.py
    - backend/app/routes/generated.py

    It intentionally does not generate frontend files, README
    documentation, Docker configuration, or database files.
    """

    component, framework = (
        find_supported_backend(
            model,
        )
    )

    if (
        component is None
        or framework is None
    ):
        return {
            "framework": None,
            "generated_component_id": None,
            "generated_backend_files": [],
            "generated_backend_requirements": [],
            "generated_backend_rest_connection_ids": [],
            "skipped_backend_components": (
                get_skipped_backend_components(
                    model,
                )
            ),
        }

    backend_dir = (
        Path(project_dir)
        / "backend"
    )

    backend_app_dir = (
        backend_dir
        / "app"
    )

    backend_app_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    init_file = (
        backend_app_dir
        / "__init__.py"
    )

    main_file = (
        backend_app_dir
        / "main.py"
    )

    requirements_file = (
        backend_dir
        / "requirements.txt"
    )

    rest_connections = get_backend_rest_connections(
        model,
        str(component.id),
    )
    include_generated_routes = bool(
        rest_connections,
    )

    init_file.write_text(
        (
            '"""Generated backend application package."""\n'
        ),
        encoding="utf-8",
    )

    main_file.write_text(
        _main_file_content(
            framework,
            model.name,
            component,
            include_generated_routes,
        ),
        encoding="utf-8",
    )

    requirements = get_backend_requirements(
        framework,
    )

    requirements_file.write_text(
        _requirements_content(
            framework,
        ),
        encoding="utf-8",
    )

    generated_files = [
        str(
            init_file.relative_to(
                project_dir,
            )
        ).replace("\\", "/"),
        str(
            main_file.relative_to(
                project_dir,
            )
        ).replace("\\", "/"),
        str(
            requirements_file.relative_to(
                project_dir,
            )
        ).replace("\\", "/"),
    ]

    if include_generated_routes:
        routes_dir = (
            backend_app_dir
            / "routes"
        )

        routes_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        routes_init_file = (
            routes_dir
            / "__init__.py"
        )
        generated_routes_file = (
            routes_dir
            / "generated.py"
        )

        routes_init_file.write_text(
            '"""Generated backend route package."""\n',
            encoding="utf-8",
        )
        generated_routes_file.write_text(
            _generated_routes_content(
                framework,
            ),
            encoding="utf-8",
        )

        generated_files.extend(
            [
                str(
                    routes_init_file.relative_to(
                        project_dir,
                    )
                ).replace("\\", "/"),
                str(
                    generated_routes_file.relative_to(
                        project_dir,
                    )
                ).replace("\\", "/"),
            ]
        )

    return {
        "framework": framework,
        "generated_component_id": (
            component.id
        ),
        "generated_backend_files": (
            generated_files
        ),
        "generated_backend_requirements": (
            list(requirements)
        ),
        "generated_backend_rest_connection_ids": [
            str(
                getattr(
                    connection,
                    "id",
                    "",
                )
            )
            for connection in rest_connections
        ],
        "skipped_backend_components": (
            get_skipped_backend_components(
                model,
                generated_component_id=component.id,
            )
        ),
    }