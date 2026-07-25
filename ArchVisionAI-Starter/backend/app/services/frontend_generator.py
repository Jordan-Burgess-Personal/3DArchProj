from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app.schemas import ArchitectureModel, Component


SUPPORTED_FRONTEND_FRAMEWORKS = {
    "react": "react",
    "vite": "react",
}

FRONTEND_COMPONENT_TYPES = {
    "frontend",
    "client",
    "web",
    "web_app",
    "webapp",
    "ui",
    "user_interface",
}


FRONTEND_GENERATION_CAPABILITIES = [
    {
        "catalog_id": "web-frontend",
        "kind": "component",
        "generator": "frontend",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "React frontend starter files can be generated."
        ),
        "technologies": [
            "React",
            "Vite",
        ],
        "generated_files": [
            "frontend/src/App.jsx",
            "frontend/src/main.jsx",
        ],
    },
    {
        "catalog_id": "rest-api",
        "kind": "connection",
        "generator": "frontend",
        "supported": True,
        "phase": "implemented",
        "reason": (
            "A reusable REST API client is generated for supported "
            "frontend API connections."
        ),
        "technologies": [
            "Fetch API",
            "HTTP",
            "HTTPS",
            "REST",
        ],
        "generated_files": [
            "frontend/src/services/api.js",
        ],
    },
]


def _component_search_text(
    component: Component,
) -> str:
    """
    Combine fields that may identify a frontend framework.

    Framework detection checks the component type, name, technology,
    and description so components such as "React Frontend" or a
    component using "React with Vite" can be recognized.
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


def is_frontend_component(
    component: Component,
) -> bool:
    """
    Return True when the component represents a frontend responsibility.

    Components outside the supported frontend component types remain
    part of architecture.json but do not generate frontend source files.
    """

    component_type = str(
        component.type or ""
    ).strip().lower()

    return (
        component_type
        in FRONTEND_COMPONENT_TYPES
    )


def detect_frontend_framework(
    component: Component,
) -> str | None:
    """
    Detect a supported frontend framework for a component.

    React and React applications configured with Vite are currently
    supported. Unsupported frontend technologies return None.
    """

    if not is_frontend_component(component):
        return None

    searchable_text = _component_search_text(
        component,
    )

    for keyword, framework in (
        SUPPORTED_FRONTEND_FRAMEWORKS.items()
    ):
        if keyword in searchable_text:
            return framework

    return None


def find_supported_frontend(
    model: ArchitectureModel,
) -> tuple[Component | None, str | None]:
    """
    Find the first supported frontend component in the architecture.

    One starter frontend is generated. Additional frontend components
    remain in architecture.json and are reported as skipped.
    """

    for component in model.components:
        framework = detect_frontend_framework(
            component,
        )

        if framework:
            return component, framework

    return None, None


def get_skipped_frontend_components(
    model: ArchitectureModel,
    generated_component_id: str | None = None,
) -> list[str]:
    """
    Return frontend components that did not generate source files.

    This includes unsupported frontend technologies and additional
    supported frontend components appearing after the selected one.
    """

    skipped: list[str] = []

    for component in model.components:
        if not is_frontend_component(component):
            continue

        if (
            generated_component_id is not None
            and component.id
            == generated_component_id
        ):
            continue

        skipped.append(component.name)

    return skipped


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
        getattr(connection, "protocol", None) or ""
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


def get_frontend_rest_connections(
    model: ArchitectureModel,
    frontend_component_id: str,
) -> list[Any]:
    """Return REST connections attached to the generated frontend."""
    return [
        connection
        for connection in getattr(model, "connections", [])
        if (
            is_rest_api_connection(connection)
            and frontend_component_id
            in {
                _connection_source(connection),
                _connection_target(connection),
            }
        )
    ]


def has_frontend_rest_connection(
    model: ArchitectureModel,
    frontend_component_id: str,
) -> bool:
    """Return whether the frontend participates in a REST connection."""
    return bool(
        get_frontend_rest_connections(
            model,
            frontend_component_id,
        )
    )


def _component_summary(
    component: Component,
) -> dict[str, str]:
    """
    Convert an architecture component into data safe for generated JSX.
    """

    return {
        "id": str(component.id),
        "name": component.name,
        "type": component.type,
        "technology": (
            component.technology or
            "Not specified"
        ),
        "description": (
            component.description or
            "No description provided."
        ),
    }


def _connection_summary(
    connection: Any,
) -> dict[str, str]:
    """
    Convert a connection into a small display-safe data structure.

    Attribute access is defensive so generation remains compatible with
    schema variations that use source/target or source_id/target_id.
    """

    source = _connection_source(connection)
    target = _connection_target(connection)

    label = (
        getattr(
            connection,
            "label",
            None,
        )
        or getattr(
            connection,
            "name",
            None,
        )
        or "Connection"
    )

    connection_type = (
        getattr(
            connection,
            "connection_type",
            None,
        )
        or getattr(
            connection,
            "type",
            None,
        )
        or "unspecified"
    )

    return {
        "source": str(source),
        "target": str(target),
        "label": str(label),
        "type": str(connection_type),
    }


def _app_file_content(
    model: ArchitectureModel,
    component: Component,
) -> str:
    """
    Return a generated React App component.

    The generated starter displays project information, architecture
    statistics, components, technologies, and connections.
    """

    project_name = (
        model.name.strip()
        if model.name.strip()
        else "ArchVision Project"
    )

    frontend_name = (
        component.name.strip()
        if component.name.strip()
        else "React Frontend"
    )

    project_description = (
        getattr(
            model,
            "description",
            None,
        )
        or "Starter frontend generated by ArchVision AI."
    )

    components = [
        _component_summary(item)
        for item in model.components
    ]

    connections = [
        _connection_summary(item)
        for item in getattr(
            model,
            "connections",
            [],
        )
    ]

    project_name_json = json.dumps(
        project_name,
    )

    frontend_name_json = json.dumps(
        frontend_name,
    )

    description_json = json.dumps(
        project_description,
    )

    components_json = json.dumps(
        components,
        indent=2,
    )

    connections_json = json.dumps(
        connections,
        indent=2,
    )

    return f"""const projectName = {project_name_json}
const frontendName = {frontend_name_json}
const projectDescription = {description_json}

const architectureComponents = {components_json}

const architectureConnections = {connections_json}

const styles = {{
  page: {{
    minHeight: '100vh',
    margin: 0,
    padding: '48px 24px',
    background:
      'linear-gradient(135deg, #020617 0%, #111827 55%, #172554 100%)',
    color: '#f8fafc',
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, sans-serif',
  }},
  container: {{
    width: '100%',
    maxWidth: '1120px',
    margin: '0 auto',
  }},
  badge: {{
    display: 'inline-flex',
    alignItems: 'center',
    border: '1px solid rgba(129, 140, 248, 0.45)',
    borderRadius: '999px',
    padding: '6px 12px',
    background: 'rgba(99, 102, 241, 0.12)',
    color: '#c7d2fe',
    fontSize: '12px',
    fontWeight: 700,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  }},
  title: {{
    margin: '18px 0 10px',
    fontSize: 'clamp(36px, 7vw, 64px)',
    lineHeight: 1.05,
  }},
  description: {{
    maxWidth: '760px',
    margin: 0,
    color: '#cbd5e1',
    fontSize: '17px',
    lineHeight: 1.7,
  }},
  grid: {{
    display: 'grid',
    gridTemplateColumns:
      'repeat(auto-fit, minmax(220px, 1fr))',
    gap: '16px',
    marginTop: '32px',
  }},
  card: {{
    border: '1px solid rgba(148, 163, 184, 0.2)',
    borderRadius: '16px',
    padding: '20px',
    background: 'rgba(15, 23, 42, 0.78)',
    boxShadow: '0 18px 45px rgba(0, 0, 0, 0.22)',
  }},
  cardTitle: {{
    margin: 0,
    color: '#f8fafc',
    fontSize: '17px',
  }},
  muted: {{
    color: '#94a3b8',
  }},
  statValue: {{
    margin: '8px 0 0',
    fontSize: '34px',
    fontWeight: 800,
  }},
  section: {{
    marginTop: '42px',
  }},
  sectionTitle: {{
    margin: '0 0 16px',
    fontSize: '24px',
  }},
  componentGrid: {{
    display: 'grid',
    gridTemplateColumns:
      'repeat(auto-fit, minmax(260px, 1fr))',
    gap: '16px',
  }},
  technology: {{
    display: 'inline-block',
    marginTop: '12px',
    borderRadius: '999px',
    padding: '5px 10px',
    background: 'rgba(34, 211, 238, 0.12)',
    color: '#a5f3fc',
    fontSize: '12px',
    fontWeight: 700,
  }},
  list: {{
    display: 'grid',
    gap: '12px',
    margin: 0,
    padding: 0,
    listStyle: 'none',
  }},
  connection: {{
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '12px',
    border: '1px solid rgba(148, 163, 184, 0.18)',
    borderRadius: '12px',
    padding: '14px 16px',
    background: 'rgba(15, 23, 42, 0.6)',
  }},
  empty: {{
    border: '1px dashed rgba(148, 163, 184, 0.3)',
    borderRadius: '14px',
    padding: '24px',
    color: '#94a3b8',
    textAlign: 'center',
  }},
  footer: {{
    marginTop: '48px',
    paddingTop: '24px',
    borderTop: '1px solid rgba(148, 163, 184, 0.18)',
    color: '#64748b',
    fontSize: '13px',
  }},
}}

function ComponentCard({{ item }}) {{
  return (
    <article style={{styles.card}}>
      <p
        style={{{{
          ...styles.muted,
          margin: '0 0 8px',
          fontSize: '12px',
          fontWeight: 700,
          letterSpacing: '0.08em',
          textTransform: 'uppercase',
        }}}}
      >
        {{item.type}}
      </p>

      <h3 style={{styles.cardTitle}}>
        {{item.name}}
      </h3>

      <p
        style={{{{
          ...styles.muted,
          margin: '10px 0 0',
          lineHeight: 1.6,
        }}}}
      >
        {{item.description}}
      </p>

      <span style={{styles.technology}}>
        {{item.technology}}
      </span>
    </article>
  )
}}

function App() {{
  return (
    <main style={{styles.page}}>
      <div style={{styles.container}}>
        <header>
          <span style={{styles.badge}}>
            Generated React Starter
          </span>

          <h1 style={{styles.title}}>
            {{projectName}}
          </h1>

          <p style={{styles.description}}>
            {{projectDescription}}
          </p>
        </header>

        <section style={{styles.grid}}>
          <article style={{styles.card}}>
            <p style={{styles.muted}}>
              Frontend service
            </p>

            <p style={{styles.statValue}}>
              {{frontendName}}
            </p>
          </article>

          <article style={{styles.card}}>
            <p style={{styles.muted}}>
              Components
            </p>

            <p style={{styles.statValue}}>
              {{architectureComponents.length}}
            </p>
          </article>

          <article style={{styles.card}}>
            <p style={{styles.muted}}>
              Connections
            </p>

            <p style={{styles.statValue}}>
              {{architectureConnections.length}}
            </p>
          </article>
        </section>

        <section style={{styles.section}}>
          <h2 style={{styles.sectionTitle}}>
            Architecture Components
          </h2>

          {{architectureComponents.length > 0 ? (
            <div style={{styles.componentGrid}}>
              {{architectureComponents.map((item) => (
                <ComponentCard
                  key={{item.id}}
                  item={{item}}
                />
              ))}}
            </div>
          ) : (
            <div style={{styles.empty}}>
              No architecture components were provided.
            </div>
          )}}
        </section>

        <section style={{styles.section}}>
          <h2 style={{styles.sectionTitle}}>
            Architecture Connections
          </h2>

          {{architectureConnections.length > 0 ? (
            <ul style={{styles.list}}>
              {{architectureConnections.map(
                (connection, index) => (
                  <li
                    key={{`${{connection.source}}-${{connection.target}}-${{index}}`}}
                    style={{styles.connection}}
                  >
                    <div>
                      <strong>
                        {{connection.label}}
                      </strong>

                      <div
                        style={{{{
                          ...styles.muted,
                          marginTop: '5px',
                        }}}}
                      >
                        {{connection.source}}
                        {' → '}
                        {{connection.target}}
                      </div>
                    </div>

                    <span style={{styles.technology}}>
                      {{connection.type}}
                    </span>
                  </li>
                ),
              )}}
            </ul>
          ) : (
            <div style={{styles.empty}}>
              No architecture connections were provided.
            </div>
          )}}
        </section>

        <footer style={{styles.footer}}>
          Generated by ArchVision AI. Replace this starter
          interface with your application-specific design.
        </footer>
      </div>
    </main>
  )
}}

export default App
"""


def _api_service_content() -> str:
    """Return a reusable Fetch API client for generated REST connections."""
    return """const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  'http://localhost:8000'


async function request(path, options = {}) {
  const normalizedPath = path.startsWith('/')
    ? path
    : `/${path}`

  const response = await fetch(
    `${API_BASE_URL}${normalizedPath}`,
    {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(options.headers || {}),
      },
    },
  )

  if (!response.ok) {
    const message =
      `API request failed with status ${response.status}`
    throw new Error(message)
  }

  if (response.status === 204) {
    return null
  }

  const contentType =
    response.headers.get('content-type') || ''

  if (!contentType.includes('application/json')) {
    return response.text()
  }

  return response.json()
}


export function get(path, options = {}) {
  return request(path, { ...options, method: 'GET' })
}


export function post(path, body, options = {}) {
  return request(path, {
    ...options,
    method: 'POST',
    body: JSON.stringify(body),
  })
}


export function put(path, body, options = {}) {
  return request(path, {
    ...options,
    method: 'PUT',
    body: JSON.stringify(body),
  })
}


export function patch(path, body, options = {}) {
  return request(path, {
    ...options,
    method: 'PATCH',
    body: JSON.stringify(body),
  })
}


export function remove(path, options = {}) {
  return request(path, { ...options, method: 'DELETE' })
}


export { API_BASE_URL, request }
"""


def _main_file_content() -> str:
    """Return the generated React application entry point."""

    return """import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import App from './App.jsx'


const rootElement = document.getElementById('root')

if (!rootElement) {
  throw new Error(
    'Unable to start the React application because #root was not found.',
  )
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
"""


def generate_frontend_files(
    project_dir: Path,
    model: ArchitectureModel,
) -> dict[str, Any]:
    """
    Generate React starter source files for the architecture.

    This function always generates:

    - frontend/src/App.jsx
    - frontend/src/main.jsx

    When the selected frontend participates in a REST API connection, it
    also generates:

    - frontend/src/services/api.js

    It intentionally does not generate package.json, index.html,
    stylesheets, backend files, database files, Docker configuration,
    requirements, or README documentation.
    """

    component, framework = find_supported_frontend(
        model,
    )

    if component is None or framework is None:
        return {
            "frontend_framework": None,
            "generated_frontend_component_id": None,
            "generated_frontend_files": [],
            "generated_frontend_rest_connection_ids": [],
            "skipped_frontend_components": (
                get_skipped_frontend_components(
                    model,
                )
            ),
        }

    frontend_src_dir = (
        Path(project_dir)
        / "frontend"
        / "src"
    )

    frontend_src_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    app_file = frontend_src_dir / "App.jsx"
    main_file = frontend_src_dir / "main.jsx"

    app_file.write_text(
        _app_file_content(
            model,
            component,
        ),
        encoding="utf-8",
    )

    main_file.write_text(
        _main_file_content(),
        encoding="utf-8",
    )

    generated_files = [
        str(
            app_file.relative_to(project_dir)
        ).replace("\\", "/"),
        str(
            main_file.relative_to(project_dir)
        ).replace("\\", "/"),
    ]

    rest_connections = get_frontend_rest_connections(
        model,
        str(component.id),
    )

    if rest_connections:
        services_dir = frontend_src_dir / "services"
        services_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        api_service_file = services_dir / "api.js"
        api_service_file.write_text(
            _api_service_content(),
            encoding="utf-8",
        )

        generated_files.append(
            str(
                api_service_file.relative_to(project_dir)
            ).replace("\\", "/")
        )

    return {
        "frontend_framework": framework,
        "generated_frontend_component_id": (
            component.id
        ),
        "generated_frontend_files": (
            generated_files
        ),
        "generated_frontend_rest_connection_ids": [
            str(getattr(connection, "id", ""))
            for connection in rest_connections
        ],
        "skipped_frontend_components": (
            get_skipped_frontend_components(
                model,
                generated_component_id=component.id,
            )
        ),
    }