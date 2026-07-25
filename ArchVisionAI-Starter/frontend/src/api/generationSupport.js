const DEFAULT_API_BASE_URL = 'http://localhost:8000'

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL
  || DEFAULT_API_BASE_URL
).replace(/\/+$/, '')


export async function getGenerationSupport({
  signal,
} = {}) {
  const response = await fetch(
    `${API_BASE_URL}/api/generation-support`,
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