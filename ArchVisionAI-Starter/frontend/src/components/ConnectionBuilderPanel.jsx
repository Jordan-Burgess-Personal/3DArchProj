import { useMemo, useState } from 'react'
import {
  Link2,
  Plus,
  Save,
  X,
} from 'lucide-react'

import {
  componentCategories,
  findComponentTemplate,
  findConnectionTemplate,
} from '../config/architectureCatalog'
import { useArchitectureStore } from '../store/architectureStore'

const componentTemplates =
  componentCategories.flatMap(
    (category) => category.items,
  )

export default function ConnectionBuilderPanel() {
  const [label, setLabel] = useState('')
  const [protocol, setProtocol] = useState('')
  const [newTemplateId, setNewTemplateId] =
    useState(componentTemplates[0]?.id || '')
  const [error, setError] = useState('')

  const model = useArchitectureStore(
    (state) => state.model,
  )

  const activeConnectionTemplateId =
    useArchitectureStore(
      (state) => state.activeConnectionTemplateId,
    )

  const connectionSourceId = useArchitectureStore(
    (state) => state.connectionSourceId,
  )

  const connectionTargetIds = useArchitectureStore(
    (state) => state.connectionTargetIds,
  )

  const isConnectionBuilderOpen =
    useArchitectureStore(
      (state) => state.isConnectionBuilderOpen,
    )

  const toggleConnectionTarget =
    useArchitectureStore(
      (state) => state.toggleConnectionTarget,
    )

  const addConnectionTarget =
    useArchitectureStore(
      (state) => state.addConnectionTarget,
    )

  const placeComponent = useArchitectureStore(
    (state) => state.placeComponent,
  )

  const completeConnectionBuilder =
    useArchitectureStore(
      (state) => state.completeConnectionBuilder,
    )

  const cancelConnectionBuilder =
    useArchitectureStore(
      (state) => state.cancelConnectionBuilder,
    )

  const source = useMemo(
    () =>
      model.components.find(
        (component) =>
          component.id === connectionSourceId,
      ),
    [model.components, connectionSourceId],
  )

  const connectionTemplate = useMemo(
    () =>
      findConnectionTemplate(
        activeConnectionTemplateId,
      ),
    [activeConnectionTemplateId],
  )

  if (
    !isConnectionBuilderOpen ||
    !source ||
    !connectionTemplate
  ) {
    return null
  }

  const availableTargets = model.components.filter(
    (component) => component.id !== source.id,
  )

  function handleCreateTarget() {
    const template =
      findComponentTemplate(newTemplateId)

    if (!template) {
      setError('Select a valid component type.')
      return
    }

    const offset =
      model.components.length % 3

    const result = placeComponent(template, {
      x: source.position.x + 4,
      y: source.position.y ?? 0.6,
      z: source.position.z + offset * 2,
    })

    if (!result.success) {
      setError(result.error)
      return
    }

    addConnectionTarget(result.component.id)
    setError('')
  }

  function handleCreateConnections() {
    const result = completeConnectionBuilder(
      connectionTemplate,
      {
        label:
          label.trim() ||
          connectionTemplate.name,
        protocol:
          protocol.trim() ||
          connectionTemplate.protocol,
      },
    )

    if (!result.success) {
      setError(
        result.errors?.join(' ') ||
          result.error ||
          'Unable to create the connection.',
      )
      return
    }

    setError('')
    setLabel('')
    setProtocol('')
  }

  return (
    <div className="absolute right-5 top-5 z-40 flex max-h-[calc(100%-2.5rem)] w-[390px] flex-col overflow-hidden rounded-xl border border-slate-700 bg-slate-950 text-white shadow-2xl">
      <header className="flex items-start justify-between border-b border-slate-800 p-4">
        <div>
          <div className="flex items-center gap-2">
            <Link2
              size={18}
              className="text-indigo-400"
            />

            <h2 className="font-semibold">
              Create Connection
            </h2>
          </div>

          <p className="mt-1 text-xs text-slate-400">
            {connectionTemplate.name}
            {connectionTemplate.protocol
              ? ` · ${connectionTemplate.protocol}`
              : ''}
          </p>
        </div>

        <button
          type="button"
          onClick={cancelConnectionBuilder}
          aria-label="Close connection builder"
          className="rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
        >
          <X size={18} />
        </button>
      </header>

      <div className="min-h-0 flex-1 overflow-y-auto p-4">
        <div className="rounded-lg border border-indigo-500/40 bg-indigo-500/10 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-indigo-300">
            Source component
          </p>

          <p className="mt-1 font-semibold">
            {source.name}
          </p>

          <p className="text-xs text-slate-400">
            {source.technology || source.type}
          </p>
        </div>

        <section className="mt-5">
          <h3 className="text-sm font-semibold">
            Existing target components
          </h3>

          <p className="mt-1 text-xs text-slate-400">
            Select one or more destination components.
          </p>

          <div className="mt-3 space-y-2">
            {availableTargets.map((component) => {
              const isSelected =
                connectionTargetIds.includes(
                  component.id,
                )

              return (
                <button
                  key={component.id}
                  type="button"
                  onClick={() =>
                    toggleConnectionTarget(
                      component.id,
                    )
                  }
                  className={[
                    'flex w-full items-center justify-between rounded-lg border p-3 text-left transition',
                    isSelected
                      ? 'border-indigo-400 bg-indigo-500/20'
                      : 'border-slate-700 bg-slate-900 hover:border-slate-500',
                  ].join(' ')}
                >
                  <span>
                    <span className="block text-sm font-medium">
                      {component.name}
                    </span>

                    <span className="block text-xs text-slate-400">
                      {component.technology ||
                        component.type}
                    </span>
                  </span>

                  <span
                    className={[
                      'h-4 w-4 rounded-full border',
                      isSelected
                        ? 'border-indigo-300 bg-indigo-500'
                        : 'border-slate-500',
                    ].join(' ')}
                  />
                </button>
              )
            })}

            {availableTargets.length === 0 && (
              <p className="rounded-lg border border-dashed border-slate-700 p-4 text-center text-sm text-slate-500">
                No other components exist yet.
              </p>
            )}
          </div>
        </section>

        <section className="mt-5 rounded-lg border border-slate-700 bg-slate-900 p-3">
          <h3 className="text-sm font-semibold">
            Create a new target
          </h3>

          <p className="mt-1 text-xs text-slate-400">
            The new component will be placed near the
            source and selected as a target.
          </p>

          <div className="mt-3 flex gap-2">
            <select
              value={newTemplateId}
              onChange={(event) =>
                setNewTemplateId(event.target.value)
              }
              className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            >
              {componentCategories.map((category) => (
                <optgroup
                  key={category.id}
                  label={category.label}
                >
                  {category.items.map((item) => (
                    <option
                      key={item.id}
                      value={item.id}
                    >
                      {item.name}
                    </option>
                  ))}
                </optgroup>
              ))}
            </select>

            <button
              type="button"
              onClick={handleCreateTarget}
              className="flex items-center gap-1 rounded-md bg-slate-700 px-3 py-2 text-sm hover:bg-slate-600"
            >
              <Plus size={16} />
              Add
            </button>
          </div>
        </section>

        <section className="mt-5 space-y-3">
          <div>
            <label
              htmlFor="connection-label"
              className="text-sm font-medium"
            >
              Connection label
            </label>

            <input
              id="connection-label"
              value={label}
              onChange={(event) =>
                setLabel(event.target.value)
              }
              placeholder={connectionTemplate.name}
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label
              htmlFor="connection-protocol"
              className="text-sm font-medium"
            >
              Protocol
            </label>

            <input
              id="connection-protocol"
              value={protocol}
              onChange={(event) =>
                setProtocol(event.target.value)
              }
              placeholder={
                connectionTemplate.protocol ||
                'Optional'
              }
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </div>
        </section>

        {error && (
          <p className="mt-4 rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
            {error}
          </p>
        )}
      </div>

      <footer className="flex gap-3 border-t border-slate-800 p-4">
        <button
          type="button"
          onClick={handleCreateConnections}
          disabled={
            connectionTargetIds.length === 0
          }
          className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Save size={16} />
          Create{' '}
          {connectionTargetIds.length > 1
            ? 'Connections'
            : 'Connection'}
        </button>

        <button
          type="button"
          onClick={cancelConnectionBuilder}
          className="rounded-lg bg-slate-800 px-4 py-2 text-sm hover:bg-slate-700"
        >
          Cancel
        </button>
      </footer>
    </div>
  )
}