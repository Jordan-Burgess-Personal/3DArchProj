import { Trash2, X } from 'lucide-react'

import { connectionCategories } from '../config/architectureCatalog'
import { useArchitectureStore } from '../store/architectureStore'

const connectionTemplates =
  connectionCategories.flatMap(
    (category) =>
      category.items.map((item) => ({
        ...item,
        categoryLabel: category.label,
      })),
  )

export default function ConnectionEditorPanel() {
  const selectedConnectionId =
    useArchitectureStore(
      (state) =>
        state.selectedConnectionId,
    )

  const components = useArchitectureStore(
    (state) => state.model.components,
  )

  const connections =
    useArchitectureStore(
      (state) =>
        state.model.connections,
    )

  const updateConnection =
    useArchitectureStore(
      (state) =>
        state.updateConnection,
    )

  const removeConnection =
    useArchitectureStore(
      (state) =>
        state.removeConnection,
    )

  const clearConnectionSelection =
    useArchitectureStore(
      (state) =>
        state.clearConnectionSelection,
    )

  const selected = connections.find(
    (connection) =>
      connection.id ===
      selectedConnectionId,
  )

  if (!selected) {
    return null
  }

  function updateField(field, value) {
    updateConnection(selected.id, {
      [field]: value,
    })
  }

  function changeTemplate(templateId) {
    const template =
      connectionTemplates.find(
        (item) =>
          item.id === templateId,
      )

    if (!template) {
      return
    }

    updateConnection(selected.id, {
      templateId: template.id,
      connectionType:
        template.connectionType,
      protocol: template.protocol || '',
      label:
        selected.label ||
        template.name,
    })
  }

  return (
    <div className="absolute bottom-5 right-5 z-30 w-[380px] overflow-hidden rounded-xl border border-slate-700 bg-slate-950 text-white shadow-2xl">
      <header className="flex items-start justify-between border-b border-slate-800 p-4">
        <div>
          <h2 className="font-semibold">
            Connection Details
          </h2>

          <p className="mt-1 text-xs text-slate-400">
            Edit the relationship between components.
          </p>
        </div>

        <button
          type="button"
          onClick={
            clearConnectionSelection
          }
          className="rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
          aria-label="Close connection editor"
        >
          <X size={18} />
        </button>
      </header>

      <div className="max-h-[60vh] space-y-4 overflow-y-auto p-4">
        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Connection Type
          </span>

          <select
            value={
              selected.templateId || ''
            }
            onChange={(event) =>
              changeTemplate(
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            <option value="">
              Custom Connection
            </option>

            {connectionCategories.map(
              (category) => (
                <optgroup
                  key={category.id}
                  label={category.label}
                >
                  {category.items.map(
                    (item) => (
                      <option
                        key={item.id}
                        value={item.id}
                      >
                        {item.name}
                      </option>
                    ),
                  )}
                </optgroup>
              ),
            )}
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Source Component
          </span>

          <select
            value={selected.source}
            onChange={(event) =>
              updateField(
                'source',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            {components
              .filter(
                (component) =>
                  component.id !==
                  selected.target,
              )
              .map((component) => (
                <option
                  key={component.id}
                  value={component.id}
                >
                  {component.name}
                </option>
              ))}
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Target Component
          </span>

          <select
            value={selected.target}
            onChange={(event) =>
              updateField(
                'target',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          >
            {components
              .filter(
                (component) =>
                  component.id !==
                  selected.source,
              )
              .map((component) => (
                <option
                  key={component.id}
                  value={component.id}
                >
                  {component.name}
                </option>
              ))}
          </select>
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Label
          </span>

          <input
            value={selected.label || ''}
            onChange={(event) =>
              updateField(
                'label',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Protocol
          </span>

          <input
            value={
              selected.protocol || ''
            }
            onChange={(event) =>
              updateField(
                'protocol',
                event.target.value,
              )
            }
            className="mt-1 w-full rounded-md border border-slate-700 bg-slate-900 px-3 py-2 text-sm outline-none focus:border-indigo-500"
          />
        </label>

        <label className="block">
          <span className="text-xs font-medium text-slate-300">
            Direction
          </span>

          <select
            value={
              selected.direction ||
              'unidirectional'
            }
            onChange={(event) =>
              updateField(
                'direction',
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

        <div className="rounded-md bg-slate-900 p-3 text-xs text-slate-400">
          <p>
            Relationship:{' '}
            {selected.connectionType}
          </p>

          <p className="mt-1 break-all">
            ID: {selected.id}
          </p>
        </div>
      </div>

      <footer className="border-t border-slate-800 p-4">
        <button
          type="button"
          onClick={() =>
            removeConnection(
              selected.id,
            )
          }
          className="flex w-full items-center justify-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium hover:bg-red-500"
        >
          <Trash2 size={16} />
          Delete Connection
        </button>
      </footer>
    </div>
  )
}