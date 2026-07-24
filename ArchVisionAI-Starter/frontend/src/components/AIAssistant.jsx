import { useState } from 'react'

import {
  generateArchitecture,
  getAIErrorMessage,
  getArchitectureFeedback,
} from '../api/ai'
import { useArchitectureStore } from '../store/architectureStore'

const DEFAULT_PROMPT =
  'Create a React frontend, FastAPI backend, ' +
  'PostgreSQL database, and OpenAI integration'

export default function AIAssistant() {
  const [prompt, setPrompt] = useState(
    DEFAULT_PROMPT,
  )

  const [suggestions, setSuggestions] =
    useState([])

  const [isGenerating, setIsGenerating] =
    useState(false)

  const [
    isRequestingFeedback,
    setIsRequestingFeedback,
  ] = useState(false)

  const [errorMessage, setErrorMessage] =
    useState('')

  const [successMessage, setSuccessMessage] =
    useState('')

  const model = useArchitectureStore(
    (state) => state.model,
  )

  const setModel = useArchitectureStore(
    (state) => state.setModel,
  )

  const cleanedPrompt = prompt.trim()

  async function handleGenerate(event) {
    event.preventDefault()

    if (isGenerating) {
      return
    }

    if (!cleanedPrompt) {
      setErrorMessage(
        'Describe the software system you want to generate.',
      )

      setSuccessMessage('')

      return
    }

    setIsGenerating(true)
    setErrorMessage('')
    setSuccessMessage('')
    setSuggestions([])

    try {
      const generatedArchitecture =
        await generateArchitecture(
          cleanedPrompt,
        )

      /*
       * setModel places the generated components and
       * connections into the existing Architecture Builder
       * state. The 3D canvas then rerenders from that state.
       */
      setModel(generatedArchitecture)

      const componentCount =
        generatedArchitecture.components.length

      const connectionCount =
        generatedArchitecture.connections.length

      setSuccessMessage(
        `Generated ${componentCount} ${
          componentCount === 1
            ? 'component'
            : 'components'
        } and ${connectionCount} ${
          connectionCount === 1
            ? 'connection'
            : 'connections'
        }.`,
      )
    } catch (error) {
      const message =
        error instanceof Error &&
        !error?.response
          ? error.message
          : getAIErrorMessage(
              error,
              'The architecture could not be generated.',
            )

      setErrorMessage(message)
    } finally {
      setIsGenerating(false)
    }
  }

  async function handleFeedback() {
    if (isRequestingFeedback) {
      return
    }

    if (!model?.components?.length) {
      setErrorMessage(
        'Add or generate at least one component before requesting feedback.',
      )

      return
    }

    setIsRequestingFeedback(true)
    setErrorMessage('')
    setSuccessMessage('')

    try {
      const feedback =
        await getArchitectureFeedback(
          model,
        )

      setSuggestions(feedback)
    } catch (error) {
      const message =
        error instanceof Error &&
        !error?.response
          ? error.message
          : getAIErrorMessage(
              error,
              'Architecture feedback is currently unavailable.',
            )

      setErrorMessage(message)
    } finally {
      setIsRequestingFeedback(false)
    }
  }

  function handlePromptChange(event) {
    setPrompt(event.target.value)

    if (errorMessage) {
      setErrorMessage('')
    }

    if (successMessage) {
      setSuccessMessage('')
    }
  }

  return (
    <aside className="flex h-full min-h-0 w-full flex-col overflow-hidden bg-slate-950 text-white">
      <header className="shrink-0 border-b border-slate-800 p-4">
        <h2 className="text-xl font-bold text-indigo-300">
          AI Assistant
        </h2>

        <p className="mt-2 text-sm leading-5 text-slate-400">
          Describe a software system to generate an
          editable starting architecture.
        </p>
      </header>

      <div className="min-h-0 flex-1 space-y-4 overflow-y-auto p-4">
        <form
          onSubmit={handleGenerate}
          className="space-y-3"
        >
          <div>
            <label
              htmlFor="architecture-prompt"
              className="mb-2 block text-sm font-medium text-slate-200"
            >
              Architecture prompt
            </label>

            <textarea
              id="architecture-prompt"
              value={prompt}
              onChange={handlePromptChange}
              disabled={isGenerating}
              maxLength={5000}
              rows={7}
              placeholder={[
                'Example: Create an e-commerce ',
                'platform with a React frontend, ',
                'FastAPI backend, authentication ',
                'service, PostgreSQL database, ',
                'Redis cache, and payment API.',
              ].join('')}
              className={[
                'w-full resize-none rounded-lg',
                'border border-slate-700',
                'bg-slate-900 p-3',
                'text-sm leading-6 text-white',
                'outline-none transition',
                'placeholder:text-slate-500',
                'focus:border-indigo-400',
                'focus:ring-2',
                'focus:ring-indigo-500/20',
                'disabled:cursor-not-allowed',
                'disabled:opacity-60',
              ].join(' ')}
            />

            <div className="mt-1 flex items-start justify-between gap-3 text-xs text-slate-500">
              <span>
                Include the components, technologies,
                and communication requirements.
              </span>

              <span className="shrink-0">
                {prompt.length}/5000
              </span>
            </div>
          </div>

          <button
            type="submit"
            disabled={
              isGenerating ||
              !cleanedPrompt
            }
            className={[
              'w-full rounded-lg',
              'bg-indigo-600 p-3',
              'font-medium text-white',
              'transition',
              'hover:bg-indigo-500',
              'disabled:cursor-not-allowed',
              'disabled:bg-indigo-900',
              'disabled:text-indigo-300',
            ].join(' ')}
          >
            {isGenerating
              ? 'Generating Architecture...'
              : 'Generate Model'}
          </button>
        </form>

        {errorMessage && (
          <div
            role="alert"
            className={[
              'rounded-lg border',
              'border-red-400/30',
              'bg-red-400/10 p-3',
              'text-sm leading-5',
              'text-red-200',
            ].join(' ')}
          >
            <strong className="font-semibold">
              Request failed.
            </strong>{' '}
            {errorMessage}
          </div>
        )}

        {successMessage && (
          <div
            role="status"
            className={[
              'rounded-lg border',
              'border-emerald-400/30',
              'bg-emerald-400/10 p-3',
              'text-sm leading-5',
              'text-emerald-200',
            ].join(' ')}
          >
            <strong className="font-semibold">
              Architecture generated.
            </strong>{' '}
            {successMessage}
          </div>
        )}

        <div className="border-t border-slate-800 pt-4">
          <button
            type="button"
            onClick={handleFeedback}
            disabled={
              isGenerating ||
              isRequestingFeedback ||
              !model?.components?.length
            }
            className={[
              'w-full rounded-lg',
              'bg-slate-800 p-3',
              'font-medium text-white',
              'transition',
              'hover:bg-slate-700',
              'disabled:cursor-not-allowed',
              'disabled:opacity-50',
            ].join(' ')}
          >
            {isRequestingFeedback
              ? 'Reviewing Architecture...'
              : 'Get Architecture Feedback'}
          </button>
        </div>

        {suggestions.length > 0 && (
          <section>
            <h3 className="mb-2 text-sm font-semibold text-slate-200">
              Architecture feedback
            </h3>

            <ul className="space-y-2 text-sm text-slate-200">
              {suggestions.map(
                (suggestion, index) => (
                  <li
                    key={`${index}-${suggestion}`}
                    className={[
                      'rounded-lg border',
                      'border-slate-800',
                      'bg-slate-900 p-3',
                      'leading-5',
                    ].join(' ')}
                  >
                    {suggestion}
                  </li>
                ),
              )}
            </ul>
          </section>
        )}
      </div>
    </aside>
  )
}