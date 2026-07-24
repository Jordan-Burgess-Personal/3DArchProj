import { api } from './client'

const GENERATE_ENDPOINT = '/api/ai/generate'
const FEEDBACK_ENDPOINT = '/api/ai/feedback'

/**
 * Return a useful error message for failed AI requests.
 *
 * Axios errors may contain:
 * - a backend validation message in response.data.detail
 * - a timeout code
 * - no response when the backend cannot be reached
 */
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

/**
 * Ensure the AI service returned an architecture structure
 * that can be passed to the existing Zustand setModel action.
 */
function validateGeneratedArchitecture(architecture) {
  if (
    !architecture ||
    typeof architecture !== 'object' ||
    Array.isArray(architecture)
  ) {
    throw new Error(
      'The AI service returned an invalid architecture response.',
    )
  }

  if (!Array.isArray(architecture.components)) {
    throw new Error(
      'The generated architecture did not contain a components array.',
    )
  }

  if (!Array.isArray(architecture.connections)) {
    throw new Error(
      'The generated architecture did not contain a connections array.',
    )
  }

  if (architecture.components.length === 0) {
    throw new Error(
      'The AI service did not generate any architecture components.',
    )
  }

  return architecture
}

/**
 * Generate an architecture from a natural-language prompt.
 */
export async function generateArchitecture(prompt) {
  const cleanedPrompt = String(prompt || '').trim()

  if (!cleanedPrompt) {
    throw new Error(
      'Enter a description of the software system you want to generate.',
    )
  }

  const response = await api.post(
    GENERATE_ENDPOINT,
    {
      prompt: cleanedPrompt,
    },
    {
      /*
       * AI requests may take longer than ordinary REST requests,
       * especially when the OpenAI API is being used.
       */
      timeout: 60000,
    },
  )

  return validateGeneratedArchitecture(
    response.data,
  )
}

/**
 * Request improvement suggestions for the current architecture.
 */
export async function getArchitectureFeedback(model) {
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

  const suggestions = response.data?.suggestions

  if (!Array.isArray(suggestions)) {
    throw new Error(
      'The AI service returned an invalid feedback response.',
    )
  }

  return suggestions
}