import {
  useCallback,
  useEffect,
  useState,
} from 'react'

import {
  getGenerationSupport,
} from '../api/generationSupport'


const EMPTY_SUPPORT_MANIFEST = {
  schema_version: '1.0',
  components: {},
  connections: {},
}


export function useGenerationSupport() {
  const [
    generationSupport,
    setGenerationSupport,
  ] = useState(
    EMPTY_SUPPORT_MANIFEST,
  )

  const [
    isLoading,
    setIsLoading,
  ] = useState(true)

  const [
    error,
    setError,
  ] = useState(null)

  const [
    reloadKey,
    setReloadKey,
  ] = useState(0)

  const reloadGenerationSupport = useCallback(
    () => {
      setReloadKey((currentValue) => (
        currentValue + 1
      ))
    },
    [],
  )

  useEffect(() => {
    const controller = new AbortController()

    async function loadGenerationSupport() {
      setIsLoading(true)
      setError(null)

      try {
        const result = await getGenerationSupport({
          signal: controller.signal,
        })

        setGenerationSupport({
          schema_version: (
            result?.schema_version
            || '1.0'
          ),
          components: (
            result?.components
            || {}
          ),
          connections: (
            result?.connections
            || {}
          ),
        })
      } catch (requestError) {
        if (requestError.name === 'AbortError') {
          return
        }

        setGenerationSupport(
          EMPTY_SUPPORT_MANIFEST,
        )

        setError(
          requestError instanceof Error
            ? requestError
            : new Error(
              'Unable to load project-generation support.',
            ),
        )
      } finally {
        if (!controller.signal.aborted) {
          setIsLoading(false)
        }
      }
    }

    loadGenerationSupport()

    return () => {
      controller.abort()
    }
  }, [reloadKey])

  const getComponentSupport = useCallback(
    (catalogId) => (
      generationSupport.components[
        catalogId
      ] || null
    ),
    [generationSupport.components],
  )

  const getConnectionSupport = useCallback(
    (catalogId) => (
      generationSupport.connections[
        catalogId
      ] || null
    ),
    [generationSupport.connections],
  )

  return {
    generationSupport,
    isLoading,
    error,
    reloadGenerationSupport,
    getComponentSupport,
    getConnectionSupport,
  }
}