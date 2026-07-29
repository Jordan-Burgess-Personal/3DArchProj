import { useMemo, useState } from 'react'

import {
  generateArchitecture,
  getAIErrorMessage,
  getAIValidationErrors,
  getArchitectureFeedback,
} from '../api/ai'
import {
  validateArchitecture,
} from '../utils/validateArchitecture'
import { useArchitectureStore } from '../store/architectureStore'

const DEFAULT_PROMPT =
  'Add a database and security layer to the existing backend.'

function ProposalList({
  title,
  ids,
  nameById,
}) {
  if (!ids.length) {
    return null
  }

  return (
    <div>
      <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-400">
        {title}
      </h4>

      <ul className="mt-1 space-y-1 text-sm text-slate-200">
        {ids.map((id) => (
          <li key={id}>
            • {nameById.get(id) || id}
          </li>
        ))}
      </ul>
    </div>
  )
}

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
  const [pendingProposal, setPendingProposal] =
    useState(null)
  const [
    proposalValidationErrors,
    setProposalValidationErrors,
  ] = useState([])

  const model = useArchitectureStore(
    (state) => state.model,
  )

  const applyArchitectureProposal =
    useArchitectureStore(
      (state) =>
        state.applyArchitectureProposal,
    )

  const cleanedPrompt = prompt.trim()

  const proposalComponentNames = useMemo(() => {
    const entries =
      pendingProposal?.architecture?.components?.map(
        (component) => [
          component.id,
          component.name || component.id,
        ],
      ) || []

    return new Map(entries)
  }, [pendingProposal])

  const proposalConnectionNames = useMemo(() => {
    const entries =
      pendingProposal?.architecture?.connections?.map(
        (connection) => [
          connection.id,
          connection.label ||
            `${connection.source} → ${connection.target}`,
        ],
      ) || []

    return new Map(entries)
  }, [pendingProposal])

  async function handleGenerate(event) {
    event.preventDefault()

    if (isGenerating) {
      return
    }

    if (!cleanedPrompt) {
      setErrorMessage(
        'Describe the architecture change you want to propose.',
      )
      setSuccessMessage('')
      return
    }

    setIsGenerating(true)
    setErrorMessage('')
    setSuccessMessage('')
    setSuggestions([])
    setPendingProposal(null)
    setProposalValidationErrors([])

    try {
      // generateArchitecture() already validates the proposal internally
      // (via assertValidArchitecture) and throws if it's invalid, so by
      // the time we get here the proposal is guaranteed structurally valid.
      const proposal =
        await generateArchitecture(
          cleanedPrompt,
          model,
        )

      setPendingProposal(proposal)
      setProposalValidationErrors([])
      setSuccessMessage(
        'A proposed change is ready for review. The canvas has not been modified.',
      )
    } catch (error) {
      const message =
        error instanceof Error &&
        !error?.response
          ? error.message
          : getAIErrorMessage(
              error,
              'The architecture proposal could not be generated.',
            )

      setProposalValidationErrors(
        getAIValidationErrors(error),
      )
      setErrorMessage(message)
    } finally {
      setIsGenerating(false)
    }
  }

  function handleApproveProposal() {
    if (!pendingProposal) {
      return
    }

    // pendingProposal.architecture was already validated when it was
    // generated (generateArchitecture throws on an invalid proposal) and
    // is never mutated afterward, so no need to re-validate it here.
    // The store's own applyArchitectureProposal result is still checked
    // below, since that's a genuine runtime outcome we don't control.
    const validation =
    validateArchitecture(
      pendingProposal.architecture,
    )

    if (!validation.valid) {
      setProposalValidationErrors(
        validation.errors,
      )
      setErrorMessage(
        'The generated architecture could not be applied because it failed validation.',
      )
      return
    }
    
    const result =
      applyArchitectureProposal(
        pendingProposal.architecture,
      )

    if (result?.success === false) {
      setProposalValidationErrors(
        result.errors || [],
      )
      setErrorMessage(
        result.error ||
          'The proposal could not be applied.',
      )
      return
    }

    setPendingProposal(null)
    setProposalValidationErrors([])
    setErrorMessage('')
    setSuccessMessage(
      'The approved architecture changes were applied.',
    )
  }

  function handleRejectProposal() {
    setPendingProposal(null)
    setProposalValidationErrors([])
    setErrorMessage('')
    setSuccessMessage(
      'The proposed changes were discarded. The current architecture was left unchanged.',
    )
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

  const changes =
    pendingProposal?.changes || {
      addedComponentIds: [],
      updatedComponentIds: [],
      removedComponentIds: [],
      addedConnectionIds: [],
      removedConnectionIds: [],
    }

  return (
    <aside className="flex h-full min-h-0 w-full flex-col overflow-hidden bg-slate-950 text-white">
      <header className="shrink-0 border-b border-slate-800 p-4">
        <h2 className="text-xl font-bold text-indigo-300">
          AI Assistant
        </h2>

        <p className="mt-2 text-sm leading-5 text-slate-400">
          Describe additions or edits to the current
          architecture. Proposed changes require approval.
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
              Architecture change
            </label>

            <textarea
              id="architecture-prompt"
              value={prompt}
              onChange={handlePromptChange}
              disabled={isGenerating}
              maxLength={5000}
              rows={7}
              placeholder={[
                'Example: Add a security layer ',
                'between the existing backend ',
                'and a new PostgreSQL database.',
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
                Existing work and positions are preserved
                unless removal or movement is requested.
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
              ? 'Generating Proposal...'
              : 'Generate Proposal'}
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

        {proposalValidationErrors.length > 0 && (
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
              Architecture validation errors
            </strong>

            <ul className="mt-2 list-disc space-y-1 pl-5">
              {proposalValidationErrors.map(
                (validationError, index) => (
                  <li
                    key={`${index}-${validationError}`}
                  >
                    {validationError}
                  </li>
                ),
              )}
            </ul>
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
            {successMessage}
          </div>
        )}

        {pendingProposal && (
          <section className="space-y-3 rounded-lg border border-indigo-400/40 bg-indigo-500/10 p-3">
            <div>
              <h3 className="text-sm font-semibold text-indigo-200">
                Proposed architecture changes
              </h3>

              <p className="mt-1 text-sm leading-5 text-slate-200">
                {pendingProposal.summary}
              </p>
            </div>

            <div className="space-y-3 rounded-md bg-slate-950/60 p-3">
              <ProposalList
                title="Components to add"
                ids={changes.addedComponentIds}
                nameById={proposalComponentNames}
              />

              <ProposalList
                title="Components to update"
                ids={changes.updatedComponentIds}
                nameById={proposalComponentNames}
              />

              <ProposalList
                title="Components to remove"
                ids={changes.removedComponentIds}
                nameById={proposalComponentNames}
              />

              <ProposalList
                title="Connections to add"
                ids={changes.addedConnectionIds}
                nameById={proposalConnectionNames}
              />

              <ProposalList
                title="Connections to remove"
                ids={changes.removedConnectionIds}
                nameById={proposalConnectionNames}
              />

              {!changes.addedComponentIds.length &&
                !changes.updatedComponentIds.length &&
                !changes.removedComponentIds.length &&
                !changes.addedConnectionIds.length &&
                !changes.removedConnectionIds.length && (
                  <p className="text-sm text-slate-400">
                    The proposal does not contain a material
                    change to the current architecture.
                  </p>
                )}
            </div>

            <p className="text-xs leading-5 text-amber-200">
              Review the proposal before applying it. Rejecting
              it leaves the canvas unchanged.
            </p>

            <div className="grid grid-cols-2 gap-2">
              <button
                type="button"
                onClick={handleRejectProposal}
                className="rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm font-medium text-slate-200 transition hover:bg-slate-800"
              >
                Reject
              </button>

              <button
                type="button"
                onClick={handleApproveProposal}
                disabled={
                  proposalValidationErrors.length > 0
                }
                className="rounded-lg bg-emerald-600 px-3 py-2 text-sm font-medium text-white transition hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-emerald-900 disabled:text-emerald-300"
              >
                Approve Changes
              </button>
            </div>
          </section>
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
