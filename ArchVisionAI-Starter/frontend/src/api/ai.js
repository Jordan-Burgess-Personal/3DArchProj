import { api } from './client'
import {
  assertValidArchitecture,
} from '../utils/validateArchitecture'

const GENERATE_ENDPOINT = '/api/ai/generate'
const FEEDBACK_ENDPOINT = '/api/ai/feedback'

export function getAIValidationErrors(error) {
  if (
    Array.isArray(
      error?.validationErrors,
    )
  ) {
    return error.validationErrors
  }

  const detail =
    error?.response?.data?.detail

  if (
    detail &&
    typeof detail === 'object' &&
    Array.isArray(detail.errors)
  ) {
    return detail.errors.filter(
      (message) =>
        typeof message === 'string',
    )
  }

  return []
}

export function getAIErrorMessage(
  error,
  fallbackMessage =
    'The AI request could not be completed.',
) {
  if (error?.code === 'ECONNABORTED') {
    return (
      'The AI request took too long. ' +
      'Try using a shorter or more focused prompt.'
    )
  }

  if (!error?.response) {
    if (
      error instanceof Error &&
      error.message
    ) {
      return error.message
    }

    return (
      'Unable to connect to the AI service. ' +
      'Confirm that the FastAPI backend is running.'
    )
  }

  const detail =
    error.response.data?.detail

  if (
    detail &&
    typeof detail === 'object' &&
    typeof detail.message === 'string'
  ) {
    return detail.message
  }

  if (
    typeof detail === 'string' &&
    detail.trim()
  ) {
    return detail
  }

  if (
    Array.isArray(detail) &&
    detail.length > 0
  ) {
    const firstError = detail[0]

    if (
      typeof firstError?.msg === 'string'
    ) {
      return firstError.msg
    }
  }

  return fallbackMessage
}

function validateChanges(changes) {
  const normalized = changes || {}

  return {
    addedComponentIds: Array.isArray(
      normalized.added_component_ids,
    )
      ? normalized.added_component_ids
      : [],
    updatedComponentIds: Array.isArray(
      normalized.updated_component_ids,
    )
      ? normalized.updated_component_ids
      : [],
    removedComponentIds: Array.isArray(
      normalized.removed_component_ids,
    )
      ? normalized.removed_component_ids
      : [],
    addedConnectionIds: Array.isArray(
      normalized.added_connection_ids,
    )
      ? normalized.added_connection_ids
      : [],
    removedConnectionIds: Array.isArray(
      normalized.removed_connection_ids,
    )
      ? normalized.removed_connection_ids
      : [],
  }
}

function validateGeneratedProposal(proposal) {
  if (
    !proposal ||
    typeof proposal !== 'object' ||
    Array.isArray(proposal)
  ) {
    throw new Error(
      'The AI service returned an invalid proposal response.',
    )
  }

  const summary = String(
    proposal.summary || '',
  ).trim()

  if (!summary) {
    throw new Error(
      'The generated proposal did not include a summary.',
    )
  }

  const architecture =
    assertValidArchitecture(
      proposal.architecture,
      'The generated architecture failed validation.',
    )

  return {
    summary,
    architecture,
    changes: validateChanges(
      proposal.changes,
    ),
  }
}

export async function generateArchitecture(
  prompt,
  currentModel,
) {
  const cleanedPrompt = String(
    prompt || '',
  ).trim()

  if (!cleanedPrompt) {
    throw new Error(
      'Enter a description of the architecture change you want.',
    )
  }

  assertValidArchitecture(
    currentModel,
    'The current architecture is invalid and cannot be sent for AI generation.',
  )

  const response = await api.post(
    GENERATE_ENDPOINT,
    {
      prompt: cleanedPrompt,
      current_model: currentModel,
    },
    {
      timeout: 60000,
    },
  )

  return validateGeneratedProposal(
    response.data,
  )
}

export async function getArchitectureFeedback(
  model,
) {
  assertValidArchitecture(
    model,
    'The current architecture is invalid and cannot be reviewed.',
  )

  const response = await api.post(
    FEEDBACK_ENDPOINT,
    {
      model,
    },
  )

  const suggestions =
    response.data?.suggestions

  if (!Array.isArray(suggestions)) {
    throw new Error(
      'The AI service returned an invalid feedback response.',
    )
  }

  return suggestions
}
