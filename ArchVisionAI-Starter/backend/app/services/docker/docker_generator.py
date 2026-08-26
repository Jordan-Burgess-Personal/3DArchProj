from __future__ import annotations

from pathlib import Path
from typing import Any

from app.schemas import ArchitectureModel
from app.services.backend.backend_generator import (
    find_supported_backend,
)
from app.services.database.database_generator import (
    find_supported_database,
)
from app.services.frontend.frontend_generator import (
    find_supported_frontend,
)


DOCKER_GENERATION_CAPABILITIES = [
    {
        "catalog_id": "container",
        "kind": "component",
        "generator": "docker",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "Dockerfiles, Docker ignore files, Docker Compose "
            "configuration, and environment examples can be generated."
        ),
        "technologies": [
            "Docker",
            "Docker Compose",
        ],
        "generated_files": [
            "frontend/Dockerfile",
            "frontend/.dockerignore",
            "backend/Dockerfile",
            "backend/.dockerignore",
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "web-frontend",
        "kind": "component",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Docker configuration can be generated for a supported "
            "React frontend."
        ),
        "technologies": [
            "Docker",
            "React",
            "Vite",
        ],
        "generated_files": [
            "frontend/Dockerfile",
            "frontend/.dockerignore",
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "api-service",
        "kind": "component",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Docker configuration can be generated for supported "
            "FastAPI and Flask backends."
        ),
        "technologies": [
            "Docker",
            "FastAPI",
            "Flask",
        ],
        "generated_files": [
            "backend/Dockerfile",
            "backend/.dockerignore",
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "relational-database",
        "kind": "component",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Docker Compose and environment configuration can be "
            "generated for PostgreSQL and MySQL. SQLite is configured "
            "without a separate database container."
        ),
        "technologies": [
            "PostgreSQL",
            "MySQL",
            "SQLite",
            "Docker Compose",
        ],
        "generated_files": [
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "document-database",
        "kind": "component",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Docker Compose and environment configuration can be "
            "generated for MongoDB."
        ),
        "technologies": [
            "MongoDB",
            "Docker Compose",
        ],
        "generated_files": [
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "database-access",
        "kind": "connection",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Database connection environment variables and container "
            "dependencies can be generated for supported databases."
        ),
        "technologies": [
            "DATABASE_URL",
            "MONGODB_URL",
            "Docker Compose",
        ],
        "generated_files": [
            "docker-compose.yml",
            ".env.example",
        ],
    },
    {
        "catalog_id": "dependency",
        "kind": "connection",
        "generator": "docker",
        "supported": True,
        "phase": "configured",
        "reason": (
            "Architecture dependency connections are converted into "
            "Docker Compose depends_on relationships."
        ),
        "technologies": [
            "Docker Compose",
            "depends_on",
        ],
        "generated_files": [
            "docker-compose.yml",
        ],
    },
]


def _backend_dockerfile_content(
    framework: str,
) -> str:
    port = (
        8000
        if framework == "fastapi"
        else 5000
    )

    if framework == "fastapi":
        command = (
            'CMD ["uvicorn", "app.main:app", '
            '"--host", "0.0.0.0", "--port", "8000"]'
        )
    else:
        command = (
            'CMD ["python", "-m", "app.main"]'
        )

    return f"""FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE {port}

{command}
"""


def _frontend_dockerfile_content() -> str:
    return """FROM node:22-alpine

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
"""


def _backend_dockerignore_content() -> str:
    return """__pycache__
*.pyc
*.pyo
*.pyd
.pytest_cache
.mypy_cache
venv
.venv
.env
.git
.gitignore
"""


def _frontend_dockerignore_content() -> str:
    return """node_modules
dist
.env
.env.local
.git
.gitignore
npm-debug.log*
"""


def _database_service(
    engine: str,
) -> tuple[str, str]:
    if engine == "postgresql":
        return (
            """  database:
    image: postgres:17-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${POSTGRES_DB:-app_db}
      POSTGRES_USER: ${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:-password}
    ports:
      - "${POSTGRES_PORT:-5432}:5432"
    volumes:
      - database_data:/var/lib/postgresql/data
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test:
        - CMD-SHELL
        - pg_isready -U ${POSTGRES_USER:-postgres} -d ${POSTGRES_DB:-app_db}
      interval: 5s
      timeout: 5s
      retries: 10
""",
            "database_data",
        )

    if engine == "mysql":
        return (
            """  database:
    image: mysql:8.4
    restart: unless-stopped
    environment:
      MYSQL_DATABASE: ${MYSQL_DATABASE:-app_db}
      MYSQL_USER: ${MYSQL_USER:-app_user}
      MYSQL_PASSWORD: ${MYSQL_PASSWORD:-password}
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD:-root_password}
    ports:
      - "${MYSQL_PORT:-3306}:3306"
    volumes:
      - database_data:/var/lib/mysql
      - ./database/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
    healthcheck:
      test:
        - CMD
        - mysqladmin
        - ping
        - -h
        - localhost
      interval: 5s
      timeout: 5s
      retries: 10
""",
            "database_data",
        )

    if engine == "mongodb":
        return (
            """  database:
    image: mongo:8
    restart: unless-stopped
    environment:
      MONGO_INITDB_DATABASE: ${MONGO_INITDB_DATABASE:-app_db}
      MONGO_INITDB_ROOT_USERNAME: ${MONGO_INITDB_ROOT_USERNAME:-root}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGO_INITDB_ROOT_PASSWORD:-password}
    ports:
      - "${MONGO_PORT:-27017}:27017"
    volumes:
      - database_data:/data/db
      - ./database/init.js:/docker-entrypoint-initdb.d/init.js:ro
    healthcheck:
      test:
        - CMD
        - mongosh
        - --eval
        - db.adminCommand("ping")
      interval: 5s
      timeout: 5s
      retries: 10
""",
            "database_data",
        )

    return "", ""


def _backend_environment(
    database_engine: str | None,
) -> list[str]:
    if database_engine == "postgresql":
        return [
            "      DATABASE_URL: postgresql://postgres:password@database:5432/app_db"
        ]

    if database_engine == "mysql":
        return [
            "      DATABASE_URL: mysql+pymysql://app_user:password@database:3306/app_db"
        ]

    if database_engine == "mongodb":
        return [
            "      MONGODB_URL: mongodb://root:password@database:27017/app_db?authSource=admin"
        ]

    if database_engine == "sqlite":
        return [
            "      DATABASE_URL: sqlite:///./database/app.db"
        ]

    return []


def _connection_source(
    connection: Any,
) -> str:
    """Return a connection source ID across supported schema variations."""

    return str(
        getattr(connection, "source_component_id", None)
        or getattr(connection, "source_id", None)
        or getattr(connection, "source", None)
        or ""
    )


def _connection_target(
    connection: Any,
) -> str:
    """Return a connection target ID across supported schema variations."""

    return str(
        getattr(connection, "target_component_id", None)
        or getattr(connection, "target_id", None)
        or getattr(connection, "target", None)
        or ""
    )


def is_dependency_connection(
    connection: Any,
) -> bool:
    """Return True when a connection represents a service dependency."""

    connection_type = str(
        getattr(connection, "connection_type", None)
        or getattr(connection, "type", None)
        or ""
    ).strip().lower()

    return connection_type == "dependency"


def _build_component_service_map(
    frontend_component_id: str | None,
    backend_component_id: str | None,
    database_component_id: str | None,
) -> dict[str, str]:
    """Map architecture component IDs to generated Compose service names."""

    service_map: dict[str, str] = {}

    if frontend_component_id:
        service_map[str(frontend_component_id)] = "frontend"

    if backend_component_id:
        service_map[str(backend_component_id)] = "backend"

    if database_component_id:
        service_map[str(database_component_id)] = "database"

    return service_map


def _build_service_dependencies(
    model: ArchitectureModel,
    service_map: dict[str, str],
) -> tuple[dict[str, set[str]], list[str]]:
    """
    Convert dependency connections into Docker Compose dependencies.

    A connection is interpreted as source depends on target. Connections
    involving components that do not generate Docker services are ignored.
    """

    dependencies: dict[str, set[str]] = {}
    connection_ids: list[str] = []

    for connection in getattr(model, "connections", []):
        if not is_dependency_connection(connection):
            continue

        source_service = service_map.get(
            _connection_source(connection),
        )
        target_service = service_map.get(
            _connection_target(connection),
        )

        if (
            source_service is None
            or target_service is None
            or source_service == target_service
        ):
            continue

        dependencies.setdefault(
            source_service,
            set(),
        ).add(target_service)

        connection_id = str(
            getattr(connection, "id", "")
        ).strip()

        if connection_id:
            connection_ids.append(connection_id)

    return dependencies, connection_ids


def _depends_on_block(
    dependencies: set[str],
    database_engine: str | None,
) -> str:
    """Return a Docker Compose depends_on block for one service."""

    if not dependencies:
        return ""

    lines = ["    depends_on:"]

    for dependency in sorted(dependencies):
        if (
            dependency == "database"
            and database_engine
            in {
                "postgresql",
                "mysql",
                "mongodb",
            }
        ):
            lines.extend(
                [
                    "      database:",
                    "        condition: service_healthy",
                ]
            )
        else:
            lines.append(f"      - {dependency}")

    return "\n".join(lines) + "\n"


def _compose_content(
    frontend_framework: str | None,
    backend_framework: str | None,
    database_engine: str | None,
    service_dependencies: dict[str, set[str]] | None = None,
) -> str:
    """Return Docker Compose configuration for generated services."""

    service_blocks: list[str] = []
    volume_names: list[str] = []
    dependencies = service_dependencies or {}

    if frontend_framework:
        frontend_depends_on = _depends_on_block(
            dependencies.get("frontend", set()),
            database_engine,
        )

        service_blocks.append(
            """  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "${FRONTEND_PORT:-5173}:5173"
    environment:
      VITE_API_BASE_URL: ${VITE_API_BASE_URL:-http://localhost:8000}
"""
            + frontend_depends_on
        )

    if backend_framework:
        backend_port = (
            8000
            if backend_framework == "fastapi"
            else 5000
        )

        environment_lines = _backend_environment(
            database_engine,
        )
        environment_block = ""

        if environment_lines:
            environment_block = (
                "    environment:\n"
                + "\n".join(environment_lines)
                + "\n"
            )

        backend_depends_on = _depends_on_block(
            dependencies.get("backend", set()),
            database_engine,
        )

        service_blocks.append(
            f"""  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "${{BACKEND_PORT:-{backend_port}}}:{backend_port}"
"""
            + environment_block
            + backend_depends_on
        )

    if database_engine:
        database_block, volume_name = _database_service(
            database_engine,
        )

        if database_block:
            service_blocks.append(database_block)

        if volume_name:
            volume_names.append(volume_name)

    compose = (
        "name: generated-archvision-project\n\n"
        "services:\n"
    )

    if service_blocks:
        compose += "\n".join(service_blocks)
    else:
        compose += (
            "  placeholder:\n"
            "    image: alpine:3.21\n"
            "    command: "
            '["sh", "-c", '
            '"echo No supported services were detected"]\n'
        )

    if volume_names:
        compose += "\nvolumes:\n"

        for volume_name in sorted(set(volume_names)):
            compose += f"  {volume_name}:\n"

    return compose



def _env_example_content(
    frontend_framework: str | None,
    backend_framework: str | None,
    database_engine: str | None,
) -> str:
    lines = [
        "# Generated by ArchVision AI",
    ]

    if frontend_framework:
        lines.extend(
            [
                "",
                "FRONTEND_PORT=5173",
                "VITE_API_BASE_URL=http://localhost:8000",
            ]
        )

    if backend_framework:
        default_port = (
            8000
            if backend_framework == "fastapi"
            else 5000
        )

        lines.extend(
            [
                "",
                f"BACKEND_PORT={default_port}",
            ]
        )

    if database_engine == "postgresql":
        lines.extend(
            [
                "",
                "POSTGRES_DB=app_db",
                "POSTGRES_USER=postgres",
                "POSTGRES_PASSWORD=password",
                "POSTGRES_PORT=5432",
            ]
        )

    elif database_engine == "mysql":
        lines.extend(
            [
                "",
                "MYSQL_DATABASE=app_db",
                "MYSQL_USER=app_user",
                "MYSQL_PASSWORD=password",
                "MYSQL_ROOT_PASSWORD=root_password",
                "MYSQL_PORT=3306",
            ]
        )

    elif database_engine == "mongodb":
        lines.extend(
            [
                "",
                "MONGO_INITDB_DATABASE=app_db",
                "MONGO_INITDB_ROOT_USERNAME=root",
                "MONGO_INITDB_ROOT_PASSWORD=password",
                "MONGO_PORT=27017",
            ]
        )

    elif database_engine == "sqlite":
        lines.extend(
            [
                "",
                "DATABASE_URL=sqlite:///./database/app.db",
            ]
        )

    return "\n".join(lines) + "\n"


def generate_docker_files(
    project_dir: Path,
    model: ArchitectureModel,
) -> dict[str, Any]:
    """
    Generate Docker configuration for supported architecture layers.

    Unsupported infrastructure components are ignored. Docker generation
    is based on supported frontend, backend, and database components.
    """

    project_path = Path(project_dir)

    (
        frontend_component,
        frontend_framework,
    ) = find_supported_frontend(
        model,
    )

    (
        backend_component,
        backend_framework,
    ) = find_supported_backend(
        model,
    )

    (
        database_component,
        database_engine,
    ) = find_supported_database(
        model,
    )

    service_map = _build_component_service_map(
        (
            str(frontend_component.id)
            if frontend_component
            else None
        ),
        (
            str(backend_component.id)
            if backend_component
            else None
        ),
        (
            str(database_component.id)
            if database_component
            else None
        ),
    )

    (
        service_dependencies,
        dependency_connection_ids,
    ) = _build_service_dependencies(
        model,
        service_map,
    )

    # Preserve the current automatic behavior for older architectures that
    # do not contain explicit Dependency connections.
    if not dependency_connection_ids:
        if frontend_framework and backend_framework:
            service_dependencies.setdefault(
                "frontend",
                set(),
            ).add("backend")

        if (
            backend_framework
            and database_engine
            in {
                "postgresql",
                "mysql",
                "mongodb",
            }
        ):
            service_dependencies.setdefault(
                "backend",
                set(),
            ).add("database")

    generated_files: list[str] = []

    if frontend_framework:
        frontend_dir = (
            project_path
            / "frontend"
        )

        frontend_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        frontend_dockerfile = (
            frontend_dir
            / "Dockerfile"
        )

        frontend_dockerignore = (
            frontend_dir
            / ".dockerignore"
        )

        frontend_dockerfile.write_text(
            _frontend_dockerfile_content(),
            encoding="utf-8",
        )

        frontend_dockerignore.write_text(
            _frontend_dockerignore_content(),
            encoding="utf-8",
        )

        generated_files.extend(
            [
                str(
                    frontend_dockerfile.relative_to(
                        project_path,
                    )
                ),
                str(
                    frontend_dockerignore.relative_to(
                        project_path,
                    )
                ),
            ]
        )

    if backend_component and backend_framework:
        backend_dir = (
            project_path
            / "backend"
        )

        backend_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        backend_dockerfile = (
            backend_dir
            / "Dockerfile"
        )

        backend_dockerignore = (
            backend_dir
            / ".dockerignore"
        )

        backend_dockerfile.write_text(
            _backend_dockerfile_content(
                backend_framework,
            ),
            encoding="utf-8",
        )

        backend_dockerignore.write_text(
            _backend_dockerignore_content(),
            encoding="utf-8",
        )

        generated_files.extend(
            [
                str(
                    backend_dockerfile.relative_to(
                        project_path,
                    )
                ),
                str(
                    backend_dockerignore.relative_to(
                        project_path,
                    )
                ),
            ]
        )

    compose_file = (
        project_path
        / "docker-compose.yml"
    )

    compose_file.write_text(
        _compose_content(
            frontend_framework,
            backend_framework,
            database_engine,
            service_dependencies,
        ),
        encoding="utf-8",
    )

    env_file = (
        project_path
        / ".env.example"
    )

    env_file.write_text(
        _env_example_content(
            frontend_framework,
            backend_framework,
            database_engine,
        ),
        encoding="utf-8",
    )

    generated_files.extend(
        [
            str(
                compose_file.relative_to(
                    project_path,
                )
            ),
            str(
                env_file.relative_to(
                    project_path,
                )
            ),
        ]
    )

    return {
        "docker_generated": True,
        "docker_frontend_framework": frontend_framework,
        "docker_backend_framework": backend_framework,
        "docker_database_engine": database_engine,
        "docker_frontend_component_id": (
            frontend_component.id
            if frontend_component
            else None
        ),
        "docker_backend_component_id": (
            backend_component.id
            if backend_component
            else None
        ),
        "docker_database_component_id": (
            database_component.id
            if database_component
            else None
        ),
        "docker_dependency_connection_ids": (
            dependency_connection_ids
        ),
        "docker_service_dependencies": {
            service: sorted(dependencies)
            for service, dependencies
            in service_dependencies.items()
        },
        "generated_docker_files": generated_files,
    }