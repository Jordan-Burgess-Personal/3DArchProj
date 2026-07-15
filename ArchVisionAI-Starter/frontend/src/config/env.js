const apiBaseUrl = import.meta.env.VITE_API_BASE_URL
const appName = import.meta.env.VITE_APP_NAME || 'ArchVision AI'

if (!apiBaseUrl) {
  throw new Error(
    'VITE_API_BASE_URL is not configured. ' +
      'Create the root .env file using .env.example as a guide.',
  )
}

export const env = Object.freeze({
  apiBaseUrl: apiBaseUrl.replace(/\/+$/, ''),
  appName,
  isDevelopment: import.meta.env.DEV,
  isProduction: import.meta.env.PROD,
})