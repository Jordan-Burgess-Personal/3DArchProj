const DEFAULT_API_BASE_URL =
  'http://127.0.0.1:8001'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL
  || DEFAULT_API_BASE_URL
).replace(/\/+$/, '')

const GENERATION_SUPPORT_URL =
  `${API_BASE_URL}/api/generation-support`

export async function getGenerationSupport({
  signal,
} = {}) {
  const response = await fetch(
    GENERATION_SUPPORT_URL,
    {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
      signal,
    },
  )

  if (!response.ok) {
    let errorMessage = (
      'Unable to load project-generation support.'
    )

    try {
      const errorData = await response.json()

      if (
        typeof errorData?.detail === 'string'
        && errorData.detail.trim()
      ) {
        errorMessage = errorData.detail
      }
    } catch {
      // Preserve the default error message when the response
      // does not contain valid JSON.
    }

    throw new Error(errorMessage)
  }

  return response.json()
}