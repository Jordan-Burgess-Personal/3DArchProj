import { useMemo, useState } from 'react'
import {
  ChevronDown,
  ChevronRight,
  Component,
  Link2,
  Search,
  X,
} from 'lucide-react'

import {
  componentCategories,
  connectionCategories,
} from '../config/architectureCatalog'
import { useArchitectureStore } from '../store/architectureStore'

function CatalogSection({
  category,
  selectedId,
  onSelect,
  type,
}) {
  const [isOpen, setIsOpen] = useState(true)

  return (
    <section className="border-b border-slate-800 py-2 last:border-b-0">
      <button
        type="button"
        onClick={() => setIsOpen((current) => !current)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-sm font-semibold text-slate-300 hover:text-white"
      >
        {isOpen ? (
          <ChevronDown size={16} />
        ) : (
          <ChevronRight size={16} />
        )}

        <span>{category.label}</span>
      </button>

      {isOpen && (
        <div className="space-y-1 px-2 pb-2">
          {category.items.map((item) => {
            const isSelected = item.id === selectedId
            const Icon =
              type === 'component'
                ? item.icon
                : Link2

            return (
              <button
                key={item.id}
                type="button"
                onClick={() => onSelect(item.id)}
                className={[
                  'flex w-full items-center gap-3 rounded-lg border px-3 py-3 text-left transition',
                  isSelected
                    ? 'border-indigo-400 bg-indigo-600/25 text-white ring-1 ring-indigo-400'
                    : 'border-transparent bg-slate-800/80 text-slate-300 hover:border-slate-600 hover:bg-slate-800 hover:text-white',
                ].join(' ')}
              >
                <span
                  className={[
                    'flex h-9 w-9 shrink-0 items-center justify-center rounded-md',
                    isSelected
                      ? 'bg-indigo-500 text-white'
                      : 'bg-slate-700 text-slate-200',
                  ].join(' ')}
                >
                  <Icon size={19} />
                </span>

                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium">
                    {item.name}
                  </span>

                  <span className="mt-0.5 block truncate text-xs text-slate-400">
                    {type === 'component'
                      ? item.technology || item.type
                      : item.protocol || item.connectionType}
                  </span>
                </span>
              </button>
            )
          })}
        </div>
      )}
    </section>
  )
}

export default function Sidebar() {
  const [search, setSearch] = useState('')

  const sidebarTab = useArchitectureStore(
    (state) => state.sidebarTab,
  )

  const activeComponentTemplateId = useArchitectureStore(
    (state) => state.activeComponentTemplateId,
  )

  const activeConnectionTemplateId = useArchitectureStore(
    (state) => state.activeConnectionTemplateId,
  )

  const setSidebarTab = useArchitectureStore(
    (state) => state.setSidebarTab,
  )

  const toggleComponentPlacement = useArchitectureStore(
    (state) => state.toggleComponentPlacement,
  )

  const clearComponentPlacement = useArchitectureStore(
    (state) => state.clearComponentPlacement,
  )

  const toggleConnectionTemplate = useArchitectureStore(
    (state) => state.toggleConnectionTemplate,
  )

  const normalizedSearch = search.trim().toLowerCase()

  const visibleComponentCategories = useMemo(
    () =>
      componentCategories
        .map((category) => ({
          ...category,
          items: category.items.filter((item) =>
            [
              item.name,
              item.type,
              item.technology,
              item.description,
            ]
              .join(' ')
              .toLowerCase()
              .includes(normalizedSearch),
          ),
        }))
        .filter((category) => category.items.length > 0),
    [normalizedSearch],
  )

  const visibleConnectionCategories = useMemo(
    () =>
      connectionCategories
        .map((category) => ({
          ...category,
          items: category.items.filter((item) =>
            [
              item.name,
              item.connectionType,
              item.protocol,
              item.description,
            ]
              .join(' ')
              .toLowerCase()
              .includes(normalizedSearch),
          ),
        }))
        .filter((category) => category.items.length > 0),
    [normalizedSearch],
  )

  const isPlacingComponent =
    sidebarTab === 'components' &&
    activeComponentTemplateId !== null

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-slate-800 bg-slate-950 text-white">
      <div className="border-b border-slate-800 p-3">
        <div
          role="tablist"
          aria-label="Architecture tools"
          className="grid grid-cols-2 rounded-lg bg-slate-900 p-1"
        >
          <button
            type="button"
            role="tab"
            aria-selected={sidebarTab === 'components'}
            onClick={() => setSidebarTab('components')}
            className={[
              'flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition',
              sidebarTab === 'components'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-white',
            ].join(' ')}
          >
            <Component size={17} />
            Components
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={sidebarTab === 'connections'}
            onClick={() => setSidebarTab('connections')}
            className={[
              'flex items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition',
              sidebarTab === 'connections'
                ? 'bg-indigo-600 text-white shadow'
                : 'text-slate-400 hover:text-white',
            ].join(' ')}
          >
            <Link2 size={17} />
            Connections
          </button>
        </div>

        <div className="relative mt-3">
          <Search
            size={16}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500"
          />

          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder={
              sidebarTab === 'components'
                ? 'Search components'
                : 'Search connections'
            }
            className="w-full rounded-lg border border-slate-700 bg-slate-900 py-2 pl-9 pr-3 text-sm outline-none placeholder:text-slate-500 focus:border-indigo-500"
          />
        </div>
      </div>

      {isPlacingComponent && (
        <div className="border-b border-indigo-500/30 bg-indigo-500/10 p-3">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="text-sm font-semibold text-indigo-200">
                Placement active
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-300">
                Left-click the grid to place components.
                Right-click to cancel.
              </p>
            </div>

            <button
              type="button"
              aria-label="Cancel component placement"
              onClick={clearComponentPlacement}
              className="rounded-md p-1 text-slate-400 hover:bg-slate-800 hover:text-white"
            >
              <X size={17} />
            </button>
          </div>
        </div>
      )}

      <div className="min-h-0 flex-1 overflow-y-auto">
        {sidebarTab === 'components'
          ? visibleComponentCategories.map((category) => (
              <CatalogSection
                key={category.id}
                category={category}
                selectedId={activeComponentTemplateId}
                onSelect={toggleComponentPlacement}
                type="component"
              />
            ))
          : visibleConnectionCategories.map((category) => (
              <CatalogSection
                key={category.id}
                category={category}
                selectedId={activeConnectionTemplateId}
                onSelect={toggleConnectionTemplate}
                type="connection"
              />
            ))}

        {(sidebarTab === 'components'
          ? visibleComponentCategories
          : visibleConnectionCategories
        ).length === 0 && (
          <p className="px-4 py-8 text-center text-sm text-slate-500">
            No matching items were found.
          </p>
        )}
      </div>

      {sidebarTab === 'connections' && (
        <div className="border-t border-slate-800 p-3 text-xs leading-5 text-slate-400">
          Select a connection template now. Source and target
          selection will be completed under SCRUM-47.
        </div>
      )}
    </aside>
  )
}