from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from app.schemas import ArchitectureModel


README_GENERATION_CAPABILITIES = [
    {
        "catalog_id": "project-documentation",
        "kind": "component",
        "generator": "readme",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "A dynamic README.md can be generated for supported project "
            "technologies and generated starter files."
        ),
        "technologies": [
            "Markdown",
            "React",
            "Vite",
            "FastAPI",
            "Flask",
            "PostgreSQL",
            "MySQL",
            "MongoDB",
            "SQLite",
            "Docker",
            "Docker Compose",
        ],
        "generated_files": [
            "README.md",
        ],
    },
]


TECHNOLOGY_DISPLAY_NAMES = {
    "react": "React",
    "vite": "Vite",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "docker": "Docker",
    "docker-compose": "Docker Compose",
}


TECHNOLOGY_ROLES = {
    "React": (
        "Builds the generated browser-based user interface using reusable "
        "client-side components."
    ),
    "Vite": (
        "Provides the frontend development server and build tooling for the "
        "generated React application."
    ),
    "FastAPI": (
        "Provides the generated Python API service, health endpoint, and "
        "starter REST routes."
    ),
    "Flask": (
        "Provides the generated Python web service, health endpoint, and "
        "starter REST routes."
    ),
    "PostgreSQL": (
        "Provides relational data storage and runs the generated SQL "
        "initialization script."
    ),
    "MySQL": (
        "Provides relational data storage and runs the generated SQL "
        "initialization script."
    ),
    "MongoDB": (
        "Provides document-oriented data storage and runs the generated "
        "JavaScript initialization script."
    ),
    "SQLite": (
        "Provides file-based relational storage without requiring a separate "
        "database server."
    ),
    "Docker": (
        "Packages supported frontend and backend services into reproducible "
        "containers."
    ),
    "Docker Compose": (
        "Coordinates generated application services, environment settings, "
        "service dependencies, ports, and database startup."
    ),
}


ENVIRONMENT_VARIABLES = {
    "VITE_API_BASE_URL": {
        "purpose": (
            "Base URL used by the generated React frontend when calling the "
            "backend API."
        ),
        "example": "http://localhost:8000",
    },
    "DATABASE_URL": {
        "purpose": (
            "Connection string used by the generated backend to locate a "
            "relational or SQLite database."
        ),
        "example": "postgresql://postgres:password@database:5432/app_db",
    },
    "MONGODB_URL": {
        "purpose": (
            "MongoDB connection string used by the generated backend."
        ),
        "example": (
            "mongodb://root:password@database:27017/"
            "app_db?authSource=admin"
        ),
    },
    "POSTGRES_DB": {
        "purpose": "Name of the PostgreSQL database created at startup.",
        "example": "app_db",
    },
    "POSTGRES_USER": {
        "purpose": "PostgreSQL application user created at startup.",
        "example": "postgres",
    },
    "POSTGRES_PASSWORD": {
        "purpose": "Password assigned to the PostgreSQL application user.",
        "example": "change_me",
    },
    "POSTGRES_PORT": {
        "purpose": "Host port mapped to the PostgreSQL container.",
        "example": "5432",
    },
    "MYSQL_DATABASE": {
        "purpose": "Name of the MySQL database created at startup.",
        "example": "app_db",
    },
    "MYSQL_USER": {
        "purpose": "MySQL application user created at startup.",
        "example": "app_user",
    },
    "MYSQL_PASSWORD": {
        "purpose": "Password assigned to the MySQL application user.",
        "example": "change_me",
    },
    "MYSQL_ROOT_PASSWORD": {
        "purpose": "Administrative password for the MySQL root account.",
        "example": "change_root_password",
    },
    "MYSQL_PORT": {
        "purpose": "Host port mapped to the MySQL container.",
        "example": "3306",
    },
    "MONGO_INITDB_DATABASE": {
        "purpose": "Name of the MongoDB database initialized at startup.",
        "example": "app_db",
    },
    "MONGO_INITDB_ROOT_USERNAME": {
        "purpose": "Administrative MongoDB username created at startup.",
        "example": "root",
    },
    "MONGO_INITDB_ROOT_PASSWORD": {
        "purpose": "Administrative MongoDB password created at startup.",
        "example": "change_me",
    },
    "MONGO_PORT": {
        "purpose": "Host port mapped to the MongoDB container.",
        "example": "27017",
    },
}


def _normalize_path(value: object) -> str:
    """Return a normalized project-relative path."""

    return str(value or "").strip().replace("\\", "/")


def _unique(values: Iterable[object]) -> list[str]:
    """Return non-empty values once while preserving their original order."""

    result: list[str] = []
    seen: set[str] = set()

    for value in values:
        normalized = str(value or "").strip()

        if not normalized or normalized in seen:
            continue

        seen.add(normalized)
        result.append(normalized)

    return result


def _result_files(result: dict[str, Any], key: str) -> list[str]:
    """Return normalized generated file paths from one generator result."""

    return _unique(
        _normalize_path(item)
        for item in result.get(key, [])
    )


def _all_generated_files(
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
) -> list[str]:
    """Return all files generated before README generation."""

    files: list[str] = ["architecture.json"]

    files.extend(
        _result_files(
            frontend_result,
            "generated_frontend_files",
        )
    )
    files.extend(
        _result_files(
            backend_result,
            "generated_backend_files",
        )
    )
    files.extend(
        _result_files(
            database_result,
            "generated_database_files",
        )
    )
    files.extend(
        _result_files(
            docker_result,
            "generated_docker_files",
        )
    )

    return _unique(files)


def _project_summary(model: ArchitectureModel) -> str:
    """Return the architecture summary used near the top of the README."""

    description = str(
        getattr(model, "description", None) or ""
    ).strip()

    if description:
        return description

    return (
        "A starter application generated by ArchVision AI from the selected "
        "software architecture."
    )


def _supported_technologies(
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
) -> list[str]:
    """Return only technologies that produced supported project output."""

    technologies: list[str] = []

    frontend_framework = str(
        frontend_result.get("frontend_framework") or ""
    ).strip().lower()

    if frontend_framework == "react":
        technologies.extend(["React", "Vite"])

    backend_framework = str(
        backend_result.get("framework") or ""
    ).strip().lower()

    if backend_framework:
        technologies.append(
            TECHNOLOGY_DISPLAY_NAMES.get(
                backend_framework,
                backend_framework.title(),
            )
        )

    database_engine = str(
        database_result.get("database_engine") or ""
    ).strip().lower()

    if database_engine:
        technologies.append(
            TECHNOLOGY_DISPLAY_NAMES.get(
                database_engine,
                database_engine.title(),
            )
        )

    if docker_result.get("docker_generated"):
        technologies.extend(["Docker", "Docker Compose"])

    return _unique(technologies)


def _unsupported_components(
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
) -> list[str]:
    """Return architecture components that did not generate implementation."""

    return _unique(
        [
            *frontend_result.get(
                "skipped_frontend_components",
                [],
            ),
            *backend_result.get(
                "skipped_backend_components",
                [],
            ),
            *database_result.get(
                "skipped_database_components",
                [],
            ),
        ]
    )


def _technology_section(technologies: list[str]) -> str:
    """Build the supported technology and role section."""

    if not technologies:
        return (
            "## Supported Technologies\n\n"
            "No implementation-specific technology files were generated. "
            "The architecture remains available in `architecture.json`.\n"
        )

    lines = [
        "## Supported Technologies",
        "",
        "| Technology | Role in this project |",
        "|---|---|",
    ]

    for technology in technologies:
        role = TECHNOLOGY_ROLES.get(
            technology,
            "Included as a supported generated project technology.",
        )
        lines.append(
            f"| **{technology}** | {role} |"
        )

    return "\n".join(lines) + "\n"


def _prerequisites_section(technologies: list[str]) -> str:
    """Build installation checks and recommended version guidance."""

    lines = [
        "## Prerequisites",
        "",
        "Install only the tools required by the generated layers.",
        "",
    ]

    if "React" in technologies:
        lines.extend(
            [
                "### Frontend prerequisites",
                "",
                "- Node.js 20 LTS or later",
                "- npm 10 or later",
                "",
                "Verify the installations:",
                "",
                "```bash",
                "node --version",
                "npm --version",
                "```",
                "",
            ]
        )

    if "FastAPI" in technologies or "Flask" in technologies:
        lines.extend(
            [
                "### Backend prerequisites",
                "",
                "- Python 3.11 or later",
                "- pip included with the selected Python installation",
                "",
                "Verify the installations:",
                "",
                "```bash",
                "python --version",
                "pip --version",
                "```",
                "",
            ]
        )

    if "Docker" in technologies:
        lines.extend(
            [
                "### Container prerequisites",
                "",
                "- A current Docker Desktop or Docker Engine release",
                "- Docker Compose v2",
                "",
                "Verify the installations:",
                "",
                "```bash",
                "docker --version",
                "docker compose version",
                "```",
                "",
            ]
        )

    if len(lines) == 4:
        lines.append(
            "No additional runtime prerequisites were generated."
        )

    return "\n".join(lines).rstrip() + "\n"


def _environment_variable_names(
    frontend_framework: str | None,
    database_engine: str | None,
    docker_generated: bool,
) -> list[str]:
    """Return environment variables relevant to the generated project."""

    if not docker_generated:
        return []

    variables: list[str] = []

    if frontend_framework:
        variables.append("VITE_API_BASE_URL")

    if database_engine == "postgresql":
        variables.extend(
            [
                "DATABASE_URL",
                "POSTGRES_DB",
                "POSTGRES_USER",
                "POSTGRES_PASSWORD",
                "POSTGRES_PORT",
            ]
        )
    elif database_engine == "mysql":
        variables.extend(
            [
                "DATABASE_URL",
                "MYSQL_DATABASE",
                "MYSQL_USER",
                "MYSQL_PASSWORD",
                "MYSQL_ROOT_PASSWORD",
                "MYSQL_PORT",
            ]
        )
    elif database_engine == "mongodb":
        variables.extend(
            [
                "MONGODB_URL",
                "MONGO_INITDB_DATABASE",
                "MONGO_INITDB_ROOT_USERNAME",
                "MONGO_INITDB_ROOT_PASSWORD",
                "MONGO_PORT",
            ]
        )
    elif database_engine == "sqlite":
        variables.append("DATABASE_URL")

    return _unique(variables)


def _environment_section(
    frontend_framework: str | None,
    database_engine: str | None,
    docker_generated: bool,
) -> str:
    """Build .env creation and environment-variable documentation."""

    variable_names = _environment_variable_names(
        frontend_framework,
        database_engine,
        docker_generated,
    )

    if not docker_generated:
        return (
            "## Environment Configuration\n\n"
            "No `.env.example` file was generated for this project. Add "
            "environment variables as application-specific configuration is "
            "introduced.\n"
        )

    lines = [
        "## Environment Configuration",
        "",
        "Create a working `.env` file before launching the Docker-based project.",
        "",
        "### Windows PowerShell",
        "",
        "```powershell",
        "Copy-Item .env.example .env",
        "```",
        "",
        "### Windows Command Prompt",
        "",
        "```bat",
        "copy .env.example .env",
        "```",
        "",
        "### Linux",
        "",
        "```bash",
        "cp .env.example .env",
        "```",
        "",
        "Review the copied values and replace example credentials before using "
        "the project outside local development.",
    ]

    if variable_names:
        lines.extend(
            [
                "",
                "### Environment variables",
                "",
                "| Variable | Purpose | Example value |",
                "|---|---|---|",
            ]
        )

        for variable_name in variable_names:
            details = ENVIRONMENT_VARIABLES[variable_name]
            lines.append(
                f"| `{variable_name}` | {details['purpose']} | "
                f"`{details['example']}` |"
            )

    return "\n".join(lines) + "\n"


def _frontend_setup_section(
    frontend_framework: str | None,
) -> str:
    """Build local frontend setup instructions."""

    if frontend_framework != "react":
        return ""

    return """## Frontend Setup

The generated frontend uses React with Vite.

### Install frontend dependencies

```bash
cd frontend
npm install
```

### Start the frontend development server

```bash
npm run dev
```

The Vite development server normally runs at `http://localhost:5173`.

To stop the local frontend server, press `Ctrl+C` in its terminal.
"""


def _backend_setup_section(
    backend_framework: str | None,
) -> str:
    """Build Windows and Linux backend setup instructions."""

    if backend_framework not in {"fastapi", "flask"}:
        return ""

    launch_command = (
        "uvicorn app.main:app --reload"
        if backend_framework == "fastapi"
        else "python -m app.main"
    )

    default_url = (
        "http://localhost:8000"
        if backend_framework == "fastapi"
        else "http://localhost:5000"
    )

    framework_name = TECHNOLOGY_DISPLAY_NAMES[
        backend_framework
    ]

    return f"""## Backend Setup

The generated backend uses {framework_name}. Its Python dependencies are listed
in `backend/requirements.txt`.

### Windows PowerShell

```powershell
cd backend
python -m venv venv
venv\\Scripts\\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
{launch_command}
```

### Windows Command Prompt

```bat
cd backend
python -m venv venv
venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
{launch_command}
```

### Linux

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
{launch_command}
```

The backend normally runs at `{default_url}`.

To stop the local backend server, press `Ctrl+C` in its terminal.
"""


def _database_setup_section(
    database_engine: str | None,
    docker_generated: bool,
) -> str:
    """Build database-specific initialization guidance."""

    if not database_engine:
        return ""

    display_name = TECHNOLOGY_DISPLAY_NAMES.get(
        database_engine,
        database_engine.title(),
    )

    lines = [
        "## Database Setup",
        "",
        f"The generated project includes **{display_name}** support.",
        "",
    ]

    if database_engine in {"postgresql", "mysql"}:
        lines.extend(
            [
                "`database/init.sql` creates a starter health table and inserts "
                "an initial record.",
                "",
            ]
        )
    elif database_engine == "mongodb":
        lines.extend(
            [
                "`database/init.js` creates a starter collection and inserts "
                "an initial health document.",
                "",
            ]
        )
    elif database_engine == "sqlite":
        lines.extend(
            [
                "`database/init.sql` contains the starter schema. SQLite does "
                "not require a separately running database server.",
                "",
            ]
        )

    if docker_generated and database_engine != "sqlite":
        lines.append(
            "Docker Compose starts the database service and automatically runs "
            "the initialization file during the first database-volume setup."
        )
    elif database_engine != "sqlite":
        lines.append(
            "When running without Docker, install the selected database server "
            "and apply the generated initialization file manually."
        )

    if database_engine == "sqlite":
        lines.extend(
            [
                "",
                "Create or initialize the SQLite database with a local SQLite "
                "tool when application data-access code is added.",
            ]
        )

    return "\n".join(lines) + "\n"


def _docker_setup_section(
    docker_generated: bool,
) -> str:
    """Build Docker launch and shutdown instructions."""

    if not docker_generated:
        return ""

    return """## Docker Setup

Docker Compose is the fastest way to launch all generated services together.

### Build and start

```bash
docker compose up --build
```

### Build and start in the background

```bash
docker compose up --build -d
```

### View running services

```bash
docker compose ps
```

### View service logs

```bash
docker compose logs -f
```

### Stop the project

```bash
docker compose down
```

### Stop the project and remove generated database volumes

```bash
docker compose down -v
```

Using `docker compose down -v` deletes persisted database data stored in the
Compose volume.
"""


def _quick_start_section(
    frontend_framework: str | None,
    backend_framework: str | None,
    database_engine: str | None,
    docker_generated: bool,
) -> str:
    """Build a concise first-run sequence."""

    if docker_generated:
        return """## Quick Start

1. Open a terminal in the generated project root.
2. Create `.env` from `.env.example`.
3. Review and update the example environment values.
4. Run `docker compose up --build`.
5. Open the frontend or backend URL shown in the service logs.
6. Run `docker compose down` when finished.
"""

    steps = [
        "1. Open a terminal in the generated project root.",
    ]
    step_number = 2

    if backend_framework:
        steps.append(
            f"{step_number}. Create the backend virtual environment and "
            "install `backend/requirements.txt`."
        )
        step_number += 1

    if frontend_framework:
        steps.append(
            f"{step_number}. Run `npm install` inside `frontend/`."
        )
        step_number += 1

    if database_engine and database_engine != "sqlite":
        steps.append(
            f"{step_number}. Start the local "
            f"{TECHNOLOGY_DISPLAY_NAMES[database_engine]} server and apply "
            "the generated initialization file."
        )
        step_number += 1

    if backend_framework:
        steps.append(
            f"{step_number}. Start the backend in its own terminal."
        )
        step_number += 1

    if frontend_framework:
        steps.append(
            f"{step_number}. Start the frontend in a second terminal."
        )

    return "## Quick Start\n\n" + "\n".join(steps) + "\n"


def _tree_from_paths(paths: list[str]) -> str:
    """Create a compact directory tree from generated file paths."""

    tree: dict[str, Any] = {}

    for raw_path in _unique(["README.md", *paths]):
        parts = [
            part
            for part in _normalize_path(raw_path).split("/")
            if part
        ]

        current = tree

        for part in parts:
            current = current.setdefault(part, {})

    lines: list[str] = ["."]

    def visit(
        node: dict[str, Any],
        prefix: str,
    ) -> None:
        items = sorted(
            node.items(),
            key=lambda item: (
                not bool(item[1]),
                item[0].lower(),
            ),
        )

        for index, (name, children) in enumerate(items):
            last = index == len(items) - 1
            connector = "└── " if last else "├── "
            suffix = "/" if children else ""
            lines.append(
                f"{prefix}{connector}{name}{suffix}"
            )

            if children:
                visit(
                    children,
                    prefix + ("    " if last else "│   "),
                )

    visit(tree, "")

    return "\n".join(lines)


def _major_file_descriptions(paths: list[str]) -> list[str]:
    """Describe important generated files and directories that exist."""

    normalized = set(paths)
    descriptions: list[str] = [
        "- `README.md` explains how to configure, launch, and extend the "
        "generated project.",
        "- `architecture.json` preserves the architecture model used during "
        "generation.",
    ]

    if any(path.startswith("frontend/") for path in normalized):
        descriptions.append(
            "- `frontend/` contains the generated React client application."
        )

    if "frontend/src/App.jsx" in normalized:
        descriptions.append(
            "- `frontend/src/App.jsx` contains the generated primary user "
            "interface."
        )

    if "frontend/src/services/api.js" in normalized:
        descriptions.append(
            "- `frontend/src/services/api.js` contains the reusable REST API "
            "client."
        )

    if any(path.startswith("backend/") for path in normalized):
        descriptions.append(
            "- `backend/` contains the generated Python service."
        )

    if "backend/app/main.py" in normalized:
        descriptions.append(
            "- `backend/app/main.py` is the backend application entry point."
        )

    if "backend/requirements.txt" in normalized:
        descriptions.append(
            "- `backend/requirements.txt` lists required Python packages."
        )

    if any(path.startswith("database/") for path in normalized):
        descriptions.append(
            "- `database/` contains the generated database initialization "
            "script."
        )

    if "docker-compose.yml" in normalized:
        descriptions.append(
            "- `docker-compose.yml` coordinates generated services, ports, "
            "volumes, and dependencies."
        )

    if ".env.example" in normalized:
        descriptions.append(
            "- `.env.example` provides example local environment settings."
        )

    return descriptions


def _project_structure_section(paths: list[str]) -> str:
    """Build the generated project structure section."""

    return (
        "## Generated Project Structure\n\n"
        "```text\n"
        f"{_tree_from_paths(paths)}\n"
        "```\n\n"
        "### Major files and directories\n\n"
        + "\n".join(
            _major_file_descriptions(paths)
        )
        + "\n"
    )


def _unsupported_section(
    components: list[str],
) -> str:
    """Document modeled components that did not generate implementation."""

    if not components:
        return ""

    lines = [
        "## Architecture Components Not Implemented",
        "",
        "The following components remain represented in `architecture.json`, but "
        "did not produce implementation-specific files because their selected "
        "technology is unsupported or because only one component of that layer "
        "is currently generated:",
        "",
    ]

    lines.extend(
        f"- {component}"
        for component in components
    )

    lines.extend(
        [
            "",
            "These components intentionally do not receive installation, "
            "configuration, or launch instructions.",
        ]
    )

    return "\n".join(lines) + "\n"


def _troubleshooting_section(
    frontend_framework: str | None,
    backend_framework: str | None,
    docker_generated: bool,
) -> str:
    """Build basic troubleshooting guidance for generated technologies."""

    lines = [
        "## Troubleshooting",
        "",
        "### A command is not recognized",
        "",
        "Confirm that the required tool is installed, restart the terminal, and "
        "run the version-check command from the Prerequisites section.",
        "",
    ]

    if backend_framework:
        lines.extend(
            [
                "### Python packages cannot be imported",
                "",
                "Activate the backend virtual environment, then run:",
                "",
                "```bash",
                "pip install -r backend/requirements.txt",
                "```",
                "",
            ]
        )

    if frontend_framework:
        lines.extend(
            [
                "### Frontend dependencies are missing",
                "",
                "Run `npm install` inside the `frontend/` directory. If the "
                "problem continues, remove `node_modules` and reinstall.",
                "",
            ]
        )

    if docker_generated:
        lines.extend(
            [
                "### Docker services do not start",
                "",
                "Confirm Docker is running, validate the Compose file with "
                "`docker compose config`, and inspect logs with "
                "`docker compose logs`.",
                "",
                "### A port is already in use",
                "",
                "Stop the conflicting process or update the host-side port in "
                "`docker-compose.yml` or `.env` before starting again.",
                "",
                "### Environment values are not being applied",
                "",
                "Confirm that `.env` exists in the project root and restart the "
                "affected service after changing the file.",
                "",
            ]
        )

    lines.extend(
        [
            "### The database initialization script did not run",
            "",
            "Initialization scripts usually run only when a database volume is "
            "created. For disposable local data, stop the project with "
            "`docker compose down -v` and start it again.",
        ]
    )

    return "\n".join(lines) + "\n"


def _continuing_development_section(
    frontend_framework: str | None,
    backend_framework: str | None,
    database_engine: str | None,
) -> str:
    """Build recommendations for extending the generated starter."""

    recommendations: list[str] = []

    if frontend_framework:
        recommendations.extend(
            [
                "Create additional frontend pages and reusable components.",
                "Add routing, form validation, loading states, and error "
                "handling.",
            ]
        )

    if backend_framework:
        recommendations.extend(
            [
                "Replace starter endpoints with application-specific routes "
                "and service logic.",
                "Add request validation, authentication, authorization, and "
                "automated tests.",
            ]
        )

    if database_engine:
        recommendations.extend(
            [
                "Expand the starter database schema for application entities.",
                "Add a data-access or ORM layer and database migrations.",
            ]
        )

    recommendations.extend(
        [
            "Store secrets outside source control and replace example "
            "credentials before deployment.",
            "Add continuous integration, production configuration, logging, "
            "monitoring, and deployment automation.",
        ]
    )

    return (
        "## Continuing Development\n\n"
        + "\n".join(
            f"- {item}"
            for item in _unique(recommendations)
        )
        + "\n"
    )


def _capabilities_section(
    model: ArchitectureModel,
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
) -> str:
    """Describe what the generated starter currently provides."""

    capabilities: list[str] = [
        "Preserves the complete architecture model in `architecture.json`.",
    ]

    if frontend_result.get("frontend_framework"):
        capabilities.append(
            "Includes a generated browser-based frontend starter."
        )

    if backend_result.get("framework"):
        capabilities.append(
            "Includes a generated backend service with health and example "
            "endpoints."
        )

    if backend_result.get(
        "generated_backend_rest_connection_ids"
    ):
        capabilities.append(
            "Includes generated backend REST route scaffolding."
        )

    if frontend_result.get(
        "generated_frontend_rest_connection_ids"
    ):
        capabilities.append(
            "Includes a reusable frontend REST API client."
        )

    if database_result.get("database_engine"):
        capabilities.append(
            "Includes a database initialization script."
        )

    if docker_result.get("docker_generated"):
        capabilities.append(
            "Includes Docker and Docker Compose development configuration."
        )

    component_count = len(
        getattr(model, "components", [])
    )
    connection_count = len(
        getattr(model, "connections", [])
    )

    return (
        "## Purpose and Capabilities\n\n"
        "This generated starter translates the supported portions of the "
        "architecture into an extensible application foundation. The source "
        f"architecture contains **{component_count} component(s)** and "
        f"**{connection_count} connection(s)**.\n\n"
        + "\n".join(
            f"- {capability}"
            for capability in capabilities
        )
        + "\n"
    )


def _build_readme(
    model: ArchitectureModel,
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
) -> tuple[str, list[str], list[str]]:
    """Build complete README Markdown and its generation metadata."""

    project_name = str(
        getattr(model, "name", None)
        or "ArchVision Project"
    ).strip()

    frontend_framework = (
        str(
            frontend_result.get(
                "frontend_framework"
            )
            or ""
        ).strip().lower()
        or None
    )

    backend_framework = (
        str(
            backend_result.get("framework")
            or ""
        ).strip().lower()
        or None
    )

    database_engine = (
        str(
            database_result.get(
                "database_engine"
            )
            or ""
        ).strip().lower()
        or None
    )

    docker_generated = bool(
        docker_result.get("docker_generated")
    )

    technologies = _supported_technologies(
        frontend_result,
        backend_result,
        database_result,
        docker_result,
    )

    generated_files = _all_generated_files(
        frontend_result,
        backend_result,
        database_result,
        docker_result,
    )

    unsupported_components = _unsupported_components(
        frontend_result,
        backend_result,
        database_result,
    )

    sections: list[tuple[str, str]] = [
        (
            "Project Summary",
            (
                f"# {project_name}\n\n"
                f"{_project_summary(model)}\n\n"
                "> Generated by ArchVision AI. Review generated source, "
                "configuration, credentials, and dependency versions before "
                "production use.\n"
            ),
        ),
        (
            "Purpose and Capabilities",
            _capabilities_section(
                model,
                frontend_result,
                backend_result,
                database_result,
                docker_result,
            ),
        ),
        (
            "Supported Technologies",
            _technology_section(
                technologies
            ),
        ),
        (
            "Prerequisites",
            _prerequisites_section(
                technologies
            ),
        ),
        (
            "Quick Start",
            _quick_start_section(
                frontend_framework,
                backend_framework,
                database_engine,
                docker_generated,
            ),
        ),
        (
            "Environment Configuration",
            _environment_section(
                frontend_framework,
                database_engine,
                docker_generated,
            ),
        ),
        (
            "Frontend Setup",
            _frontend_setup_section(
                frontend_framework
            ),
        ),
        (
            "Backend Setup",
            _backend_setup_section(
                backend_framework
            ),
        ),
        (
            "Database Setup",
            _database_setup_section(
                database_engine,
                docker_generated,
            ),
        ),
        (
            "Docker Setup",
            _docker_setup_section(
                docker_generated
            ),
        ),
        (
            "Generated Project Structure",
            _project_structure_section(
                generated_files
            ),
        ),
        (
            "Architecture Components Not Implemented",
            _unsupported_section(
                unsupported_components
            ),
        ),
        (
            "Troubleshooting",
            _troubleshooting_section(
                frontend_framework,
                backend_framework,
                docker_generated,
            ),
        ),
        (
            "Continuing Development",
            _continuing_development_section(
                frontend_framework,
                backend_framework,
                database_engine,
            ),
        ),
    ]

    included_sections = [
        name
        for name, section in sections
        if section.strip()
    ]

    markdown = "\n\n".join(
        section.strip()
        for _, section in sections
        if section.strip()
    )

    return (
        markdown.rstrip() + "\n",
        technologies,
        included_sections,
    )


def generate_readme_file(
    project_dir: Path,
    model: ArchitectureModel,
    frontend_result: dict[str, Any],
    backend_result: dict[str, Any],
    database_result: dict[str, Any],
    docker_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Generate README.md for the completed starter project.

    The README is built after the frontend, backend, database, and Docker
    generators have run. This ensures documentation is based on supported
    technologies that actually produced generated files rather than every
    technology represented in the architecture.
    """

    project_path = Path(project_dir)
    project_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    (
        readme_content,
        documented_technologies,
        generated_sections,
    ) = _build_readme(
        model,
        frontend_result,
        backend_result,
        database_result,
        docker_result,
    )

    readme_file = (
        project_path
        / "README.md"
    )

    readme_file.write_text(
        readme_content,
        encoding="utf-8",
    )

    return {
        "generated_readme_files": [
            str(
                readme_file.relative_to(
                    project_path,
                )
            ).replace("\\", "/")
        ],
        "documented_technologies": (
            documented_technologies
        ),
        "generated_readme_sections": (
            generated_sections
        ),
    }