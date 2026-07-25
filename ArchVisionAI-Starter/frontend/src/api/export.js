const EXPORT_STARTER_URL =
  'http://127.0.0.1:8000/export/starter'

async function getErrorMessage(response) {
  const contentType =
    response.headers.get('content-type') || ''

  if (
    contentType.includes(
      'application/json',
    )
  ) {
    const body = await response
      .json()
      .catch(() => null)

    if (
      typeof body?.detail ===
      'string'
    ) {
      return body.detail
    }

    if (
      typeof body?.message ===
      'string'
    ) {
      return body.message
    }

    if (
      Array.isArray(body?.detail)
    ) {
      return body.detail
        .map((item) => {
          if (
            typeof item?.msg ===
            'string'
          ) {
            return item.msg
          }

          return String(item)
        })
        .join(' ')
    }
  }

  const text = await response
    .text()
    .catch(() => '')

  if (text.trim()) {
    return text.trim()
  }

  return 'Unable to generate the starter project.'
}

function getDownloadFileName(
  response,
  model,
) {
  const contentDisposition =
    response.headers.get(
      'content-disposition',
    )

  if (contentDisposition) {
    const utf8Match =
      contentDisposition.match(
        /filename\*=UTF-8''([^;]+)/i,
      )

    if (utf8Match?.[1]) {
      return decodeURIComponent(
        utf8Match[1],
      )
    }

    const regularMatch =
      contentDisposition.match(
        /filename="?([^";]+)"?/i,
      )

    if (regularMatch?.[1]) {
      return regularMatch[1]
    }
  }

  const projectName =
    String(model?.name || '')
      .trim()
      .replace(
        /[^a-zA-Z0-9_-]+/g,
        '-',
      )
      .replace(/^-+|-+$/g, '')
      .toLowerCase() ||
    'archvision-project'

  return `${projectName}.zip`
}

function downloadBlob(
  blob,
  fileName,
) {
  const objectUrl =
    window.URL.createObjectURL(blob)

  const downloadLink =
    document.createElement('a')

  downloadLink.href = objectUrl
  downloadLink.download = fileName
  downloadLink.style.display = 'none'

  document.body.appendChild(
    downloadLink,
  )

  downloadLink.click()
  downloadLink.remove()

  window.setTimeout(() => {
    window.URL.revokeObjectURL(
      objectUrl,
    )
  }, 1000)
}

export async function exportStarterProject(
  model,
) {
  if (
    !model ||
    typeof model !== 'object'
  ) {
    throw new Error(
      'A valid architecture model is required for export.',
    )
  }

  let response

  try {
    response = await fetch(
      EXPORT_STARTER_URL,
      {
        method: 'POST',
        headers: {
          'Content-Type':
            'application/json',
        },
        body: JSON.stringify(model),
      },
    )
  } catch (error) {
    console.error(
      'Starter project export request failed:',
      error,
    )

    throw new Error(
      'Unable to connect to the export service at 127.0.0.1:8000. Confirm that the FastAPI backend is running.',
    )
  }

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response),
    )
  }

  const blob = await response.blob()

  if (blob.size === 0) {
    throw new Error(
      'The export service returned an empty project archive.',
    )
  }

  const fileName =
    getDownloadFileName(
      response,
      model,
    )

  downloadBlob(blob, fileName)

  return {
    success: true,
    filename: fileName,
    message:
      `${fileName} was generated and downloaded successfully.`,
  }
}