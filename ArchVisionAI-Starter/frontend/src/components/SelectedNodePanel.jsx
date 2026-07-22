import {
  Box,
  Trash2,
} from 'lucide-react'

import FloatingPanel from './FloatingPanel'
import { useArchitectureStore } from '../store/architectureStore'

export default function SelectedNodePanel() {
  const selectedId =
    useArchitectureStore(
      (state) =>
        state.selectedId,
    )

  const components =
    useArchitectureStore(
      (state) =>
        state.model.components,
    )

  const updateComponent =
    useArchitectureStore(
      (state) =>
        state.updateComponent,
    )

  const removeComponent =
    useArchitectureStore(
      (state) =>
        state.removeComponent,
    )

  const clearSelection =
    useArchitectureStore(
      (state) =>
        state.clearSelection,
    )

  const selected =
    components.find(
      (component) =>
        component.id ===
        selectedId,
    )

  if (!selected) {
    return null
  }

  function updateField(
    field,
    value,
  ) {
    updateComponent(
      selected.id,
      {
        [field]: value,
      },
    )
  }

  function updatePosition(
    axis,
    value,
  ) {
    const numericValue =
      Number(value)

    updateComponent(
      selected.id,
      {
        position: {
          ...selected.position,

          [axis]:
            Number.isFinite(
              numericValue,
            )
              ? numericValue
              : 0,
        },
      },
    )
  }

  const deleteButton = (
    <button
      type="button"
      onClick={() =>
        removeComponent(
          selected.id,
        )
      }
      className="flex w-full items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium transition hover:bg-red-500"
    >
      <Trash2 size={16} />
      Delete Component
    </button>
  )

  return (
    <FloatingPanel
      key={selected.id}
      title="Component Details"
      subtitle="Changes update the canvas immediately."
      icon={Box}
      initialPlacement="top-left"
      initialOffset={{
        x: 12,
        y: 145,
      }}
      initialSize={{
        width: 360,
        height: 600,
      }}
      minimumSize={{
        width: 310,
        height: 320,
      }}
      onClose={
        clearSelection
      }
      footer={deleteButton}
    >
      <div className="space-y-4 p-4">
        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Name
          </span>

          <input
            value={
              selected.name || ''
            }
            onChange={(event) =>
              updateField(
                'name',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Technology
          </span>

          <input
            value={
              selected.technology ||
              ''
            }
            onChange={(event) =>
              updateField(
                'technology',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Description
          </span>

          <textarea
            rows={4}
            value={
              selected.description ||
              ''
            }
            onChange={(event) =>
              updateField(
                'description',
                event.target.value,
              )
            }
            className="mt-1 w-full resize-y rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Color
          </span>

          <div className="mt-1 flex gap-2">
            <input
              type="color"
              value={
                selected.color ||
                '#475569'
              }
              onChange={(event) =>
                updateField(
                  'color',
                  event.target.value,
                )
              }
              className="h-10 w-12 shrink-0 cursor-pointer rounded border border-slate-700 bg-slate-900"
            />

            <input
              value={
                selected.color ||
                '#475569'
              }
              onChange={(event) =>
                updateField(
                  'color',
                  event.target.value,
                )
              }
              className="min-w-0 flex-1 rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
            />
          </div>
        </label>

        <section>
          <h3 className="text-xs font-medium text-slate-300">
            Grid Position
          </h3>

          <div className="mt-2 grid grid-cols-3 gap-2">
            {[
              'x',
              'y',
              'z',
            ].map((axis) => (
              <label
                key={axis}
                className="block min-w-0"
              >
                <span className="text-xs uppercase text-slate-500">
                  {axis}
                </span>

                <input
                  type="number"
                  step="0.5"
                  value={
                    selected.position?.[
                      axis
                    ] ?? 0
                  }
                  onChange={(
                    event,
                  ) =>
                    updatePosition(
                      axis,
                      event.target
                        .value,
                    )
                  }
                  className="mt-1 w-full min-w-0 rounded-md border border-slate-700 bg-slate-900 px-2 py-2 text-sm outline-none focus:border-indigo-500"
                />
              </label>
            ))}
          </div>
        </section>

        <div className="rounded-md bg-slate-900 p-3 text-xs leading-5 text-slate-400">
          <p>
            Type:{' '}
            {selected.type}
          </p>

          <p>
            Category:{' '}
            {selected.category ||
              'custom'}
          </p>

          <p className="mt-1 break-all">
            ID: {selected.id}
          </p>
        </div>
      </div>
    </FloatingPanel>
  )
}