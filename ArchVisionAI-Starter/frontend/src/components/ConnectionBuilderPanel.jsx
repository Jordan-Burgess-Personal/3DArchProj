import {
  useMemo,
  useState,
} from 'react'

import {
  Link2,
  Plus,
  Save,
} from 'lucide-react'

import {
  componentCategories,
  findComponentTemplate,
  findConnectionTemplate,
} from '../config/architectureCatalog'

import FloatingPanel from './FloatingPanel'
import { useArchitectureStore } from '../store/architectureStore'

const componentTemplates =
  componentCategories.flatMap(
    (category) =>
      category.items,
  )

export default function ConnectionBuilderPanel() {
  const [label, setLabel] =
    useState('')

  const [
    protocol,
    setProtocol,
  ] = useState('')

  const [
    direction,
    setDirection,
  ] = useState(
    'unidirectional',
  )

  const [
    newTemplateId,
    setNewTemplateId,
  ] = useState(
    componentTemplates[0]?.id ||
      '',
  )

  const [error, setError] =
    useState('')

  const model =
    useArchitectureStore(
      (state) => state.model,
    )

  const activeConnectionTemplateId =
    useArchitectureStore(
      (state) =>
        state.activeConnectionTemplateId,
    )

  const connectionSourceId =
    useArchitectureStore(
      (state) =>
        state.connectionSourceId,
    )

  const connectionTargetIds =
    useArchitectureStore(
      (state) =>
        state.connectionTargetIds,
    )

  const isConnectionBuilderOpen =
    useArchitectureStore(
      (state) =>
        state.isConnectionBuilderOpen,
    )

  const toggleConnectionTarget =
    useArchitectureStore(
      (state) =>
        state.toggleConnectionTarget,
    )

  const addConnectionTarget =
    useArchitectureStore(
      (state) =>
        state.addConnectionTarget,
    )

  const placeComponent =
    useArchitectureStore(
      (state) =>
        state.placeComponent,
    )

  const completeConnectionBuilder =
    useArchitectureStore(
      (state) =>
        state.completeConnectionBuilder,
    )

  const cancelConnectionBuilder =
    useArchitectureStore(
      (state) =>
        state.cancelConnectionBuilder,
    )

  const source = useMemo(
    () =>
      model.components.find(
        (component) =>
          component.id ===
          connectionSourceId,
      ),
    [
      model.components,
      connectionSourceId,
    ],
  )

  const connectionTemplate =
    useMemo(
      () =>
        findConnectionTemplate(
          activeConnectionTemplateId,
        ),
      [
        activeConnectionTemplateId,
      ],
    )

  if (
    !isConnectionBuilderOpen ||
    !source ||
    !connectionTemplate
  ) {
    return null
  }

  const availableTargets =
    model.components.filter(
      (component) =>
        component.id !==
        source.id,
    )

  function handleCreateTarget() {
    const template =
      findComponentTemplate(
        newTemplateId,
      )

    if (!template) {
      setError(
        'Select a valid component type.',
      )
      return
    }

    const targetIndex =
      connectionTargetIds.length

    const result =
      placeComponent(
        template,
        {
          x:
            source.position.x +
            4,
          y:
            source.position.y ??
            0.6,
          z:
            source.position.z +
            targetIndex * 2,
        },
      )

    if (!result.success) {
      setError(
        result.error ||
          'The component could not be created.',
      )
      return
    }

    addConnectionTarget(
      result.component.id,
    )

    setError('')
  }

  function handleCreateConnections() {
    const result =
      completeConnectionBuilder(
        connectionTemplate,
        {
          label:
            label.trim() ||
            connectionTemplate.name,

          protocol:
            protocol.trim() ||
            connectionTemplate.protocol,

          direction,
        },
      )

    if (!result.success) {
      setError(
        result.errors?.join(
          ' ',
        ) ||
          result.error ||
          'Unable to create the connection.',
      )

      return
    }

    setError('')
    setLabel('')
    setProtocol('')
    setDirection(
      'unidirectional',
    )
  }

  const footer = (
    <div className="flex gap-3">
      <button
        type="button"
        onClick={
          handleCreateConnections
        }
        disabled={
          connectionTargetIds.length ===
          0
        }
        className="flex flex-1 items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
      >
        <Save size={16} />

        Create{' '}
        {connectionTargetIds.length >
        1
          ? 'Connections'
          : 'Connection'}
      </button>

      <button
        type="button"
        onClick={
          cancelConnectionBuilder
        }
        className="rounded-lg bg-slate-800 px-4 py-2 text-sm transition hover:bg-slate-700"
      >
        Cancel
      </button>
    </div>
  )

  return (
    <FloatingPanel
      key={`${connectionSourceId}-${activeConnectionTemplateId}`}
      title="Create Connection"
      subtitle={`${connectionTemplate.name}${
        connectionTemplate.protocol
          ? ` · ${connectionTemplate.protocol}`
          : ''
      }`}
      icon={Link2}
      initialPlacement="top-right"
      initialOffset={{
        x: 18,
        y: 18,
      }}
      initialSize={{
        width: 410,
        height: 650,
      }}
      minimumSize={{
        width: 340,
        height: 360,
      }}
      onClose={
        cancelConnectionBuilder
      }
      footer={footer}
    >
      <div className="space-y-5 p-4">
        <div className="rounded-lg border border-indigo-500/40 bg-indigo-500/10 p-3">
          <p className="text-xs font-medium uppercase tracking-wide text-indigo-300">
            Source component
          </p>

          <p className="mt-1 font-semibold">
            {source.name}
          </p>

          <p className="text-xs text-slate-400">
            {source.technology ||
              source.type}
          </p>
        </div>

        <section>
          <h3 className="text-sm font-semibold">
            Existing target components
          </h3>

          <p className="mt-1 text-xs leading-5 text-slate-400">
            Select one or more destination
            components.
          </p>

          <div className="mt-3 space-y-2">
            {availableTargets.map(
              (component) => {
                const isSelected =
                  connectionTargetIds.includes(
                    component.id,
                  )

                return (
                  <button
                    key={
                      component.id
                    }
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
                    ].join(
                      ' ',
                    )}
                  >
                    <span className="min-w-0">
                      <span className="block truncate text-sm font-medium">
                        {
                          component.name
                        }
                      </span>

                      <span className="block truncate text-xs text-slate-400">
                        {component.technology ||
                          component.type}
                      </span>
                    </span>

                    <span
                      className={[
                        'ml-3 h-4 w-4 shrink-0 rounded-full border',
                        isSelected
                          ? 'border-indigo-300 bg-indigo-500'
                          : 'border-slate-500',
                      ].join(
                        ' ',
                      )}
                    />
                  </button>
                )
              },
            )}

            {availableTargets.length ===
              0 && (
              <p className="rounded-lg border border-dashed border-slate-700 p-4 text-center text-sm text-slate-500">
                No other components
                exist yet.
              </p>
            )}
          </div>
        </section>

        <section className="rounded-lg border border-slate-700 bg-slate-900 p-3">
          <h3 className="text-sm font-semibold">
            Create a new target
          </h3>

          <p className="mt-1 text-xs leading-5 text-slate-400">
            The new component will be
            placed near the source and
            selected automatically.
          </p>

          <div className="mt-3 flex gap-2">
            <select
              value={
                newTemplateId
              }
              onChange={(event) =>
                setNewTemplateId(
                  event.target.value,
                )
              }
              className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            >
              {componentCategories.map(
                (category) => (
                  <optgroup
                    key={
                      category.id
                    }
                    label={
                      category.label
                    }
                  >
                    {category.items.map(
                      (item) => (
                        <option
                          key={
                            item.id
                          }
                          value={
                            item.id
                          }
                        >
                          {
                            item.name
                          }
                        </option>
                      ),
                    )}
                  </optgroup>
                ),
              )}
            </select>

            <button
              type="button"
              onClick={
                handleCreateTarget
              }
              className="flex shrink-0 items-center gap-1 rounded-md bg-slate-700 px-3 py-2 text-sm transition hover:bg-slate-600"
            >
              <Plus size={16} />
              Add
            </button>
          </div>
        </section>

        <section className="space-y-3">
          <label className="block">
            <span className="text-sm font-medium">
              Connection label
            </span>

            <input
              value={label}
              onChange={(event) =>
                setLabel(
                  event.target.value,
                )
              }
              placeholder={
                connectionTemplate.name
              }
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Protocol
            </span>

            <input
              value={
                protocol
              }
              onChange={(event) =>
                setProtocol(
                  event.target.value,
                )
              }
              placeholder={
                connectionTemplate.protocol ||
                'Optional'
              }
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">
              Direction
            </span>

            <select
              value={
                direction
              }
              onChange={(event) =>
                setDirection(
                  event.target.value,
                )
              }
              className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            >
              <option value="unidirectional">
                Unidirectional
              </option>

              <option value="bidirectional">
                Bidirectional
              </option>
            </select>
          </label>
        </section>

        {error && (
          <p className="rounded-md border border-red-500/40 bg-red-500/10 p-3 text-sm leading-5 text-red-300">
            {error}
          </p>
        )}
      </div>
    </FloatingPanel>
  )
}