import { useArchitectureStore } from '../store/architectureStore'

export default function SelectedNodePanel() {
  const selectedId = useArchitectureStore((s) => s.selectedId)
  const components = useArchitectureStore((s) => s.model.components)
  const removeComponent = useArchitectureStore((s) => s.removeComponent)
  const clearSelection = useArchitectureStore((s) => s.clearSelection)

  const selected = components.find((c) => c.id === selectedId)
  if (!selected) return null

  return (
    <div className="absolute bottom-4 left-1/2 -translate-x-1/2 bg-slate-900 border border-slate-700 rounded-lg p-4 flex items-center gap-4 shadow-lg">
      <span className="font-semibold">{selected.name}</span>
      <button
        onClick={() => removeComponent(selected.id)}
        className="px-3 py-1.5 rounded-md bg-red-600 text-sm"
      >
        Delete
      </button>
      <button
        onClick={clearSelection}
        className="px-3 py-1.5 rounded-md bg-slate-700 text-sm"
      >
        Deselect
      </button>
    </div>
  )
}