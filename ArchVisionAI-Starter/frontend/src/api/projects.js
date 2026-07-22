import { api } from './client'

const PROJECTS_ENDPOINT = '/api/projects'

function normalizeProjectSummary(project = {}) {
  return {
    id: String(project.id || ''),
    name: project.name || 'Untitled Project',
    description: project.description || '',
    status: project.status || 'draft',
    schemaVersion:
      project.schema_version ||
      project.schemaVersion ||
      '1.0',
    componentCount: Number(
      project.component_count ??
        project.componentCount ??
        0,
    ),
    connectionCount: Number(
      project.connection_count ??
        project.connectionCount ??
        0,
    ),
    createdAt:
      project.created_at ||
      project.createdAt ||
      null,
    updatedAt:
      project.updated_at ||
      project.updatedAt ||
      null,
  }
}

function getProjectApiError(
  error,
  fallbackMessage,
) {
  const responseMessage =
    error?.response?.data?.detail ||
    error?.response?.data?.message

  if (typeof responseMessage === 'string') {
    return responseMessage
  }

  if (
    Array.isArray(responseMessage) &&
    responseMessage.length > 0
  ) {
    return responseMessage
      .map(
        (item) =>
          item?.msg ||
          String(item),
      )
      .join(' ')
  }

  if (error?.code === 'ECONNABORTED') {
    return 'The project request timed out. Please try again.'
  }

  if (!error?.response) {
    return 'Unable to connect to the project service. Confirm that the backend is running.'
  }

  return fallbackMessage
}

export async function getProjectSummaries() {
  try {
    const response = await api.get(
      PROJECTS_ENDPOINT,
    )

    const projects = Array.isArray(
      response.data,
    )
      ? response.data
      : []

    return projects
      .map(normalizeProjectSummary)
      .filter(
        (project) =>
          Boolean(project.id),
      )
  } catch (error) {
    throw new Error(
      getProjectApiError(
        error,
        'Unable to retrieve the project list.',
      ),
    )
  }
}

export {
  getProjectApiError,
  normalizeProjectSummary,
}