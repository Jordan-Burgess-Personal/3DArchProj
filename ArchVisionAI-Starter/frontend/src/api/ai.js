import { api } from './client'

const GENERATE_ENDPOINT = '/api/ai/generate'
const FEEDBACK_ENDPOINT = '/api/ai/feedback'

export function getAIErrorMessage(
  error,
  fallbackMessage = 'The AI request could not be completed.',
) {
  if (error?.code === 'ECONNABORTED') {
    return (
      'The AI request took too long. ' +
      'Try using a shorter or more focused prompt.'
    )
  }

  if (!error?.response) {
    return (
      'Unable to connect to the AI service. ' +
      'Confirm that the FastAPI backend is running.'
    )
  }

  const detail = error.response.data?.detail

  if (typeof detail === 'string' && detail.trim()) {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const firstError = detail[0]

    if (typeof firstError?.msg === 'string') {
      return firstError.msg
    }
  }

  return fallbackMessage
}

function validateArchitecture(architecture) {
  if (
    !architecture ||
    typeof architecture !== 'object' ||
    Array.isArray(architecture)
  ) {
    throw new Error(
      'The AI service returned an invalid architecture.',
    )
  }

  if (!Array.isArray(architecture.components)) {
    throw new Error(
      'The proposal did not contain a components array.',
    )
  }

  if (!Array.isArray(architecture.connections)) {
    throw new Error(
      'The proposal did not contain a connections array.',
    )
  }

  return architecture
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

  return {
    summary,

    architecture: validateArchitecture(
      proposal.architecture,
    ),

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

  if (
    !currentModel ||
    typeof currentModel !== 'object'
  ) {
    throw new Error(
      'The current architecture is unavailable.',
    )
  }

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
  if (!model || typeof model !== 'object') {
    throw new Error(
      'There is no valid architecture available for review.',
    )
  }

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