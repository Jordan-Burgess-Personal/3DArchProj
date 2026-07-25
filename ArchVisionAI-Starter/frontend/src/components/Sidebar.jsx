import {
  useMemo,
  useState,
} from 'react'

import {
  AlertTriangle,
  ChevronDown,
  ChevronRight,
  Component,
  Link2,
  RefreshCw,
  Search,
  X,
} from 'lucide-react'

import {
  componentCategories,
  connectionCategories,
  getComponentGenerationSupport,
  getConnectionGenerationSupport,
} from '../config/architectureCatalog'

import { useGenerationSupport } from '../hooks/useGenerationSupport'
import { useArchitectureStore } from '../store/architectureStore'

import GenerationSupportBadge from './GenerationSupportBadge'


function CatalogSection({
  category,
  selectedId,
  onSelect,
  itemType,
  isGenerationSupportLoading,
}) {
  const [isOpen, setIsOpen] =
    useState(true)

  return (
    <section className="border-b border-slate-800 py-2 last:border-b-0">
      <button
        type="button"
        onClick={() =>
          setIsOpen(
            (current) => !current,
          )
        }
        className="flex w-full min-w-0 items-center gap-2 px-3 py-2 text-left text-sm font-semibold text-slate-300 transition hover:text-white"
      >
        {isOpen ? (
          <ChevronDown
            size={16}
            className="shrink-0"
          />
        ) : (
          <ChevronRight
            size={16}
            className="shrink-0"
          />
        )}

        <span className="truncate">
          {category.label}
        </span>
      </button>

      {isOpen && (
        <div className="space-y-2 px-2 pb-2">
          {category.items.map(
            (item) => {
              const isSelected =
                item.id === selectedId

              const isGenerationSupported =
                item.generationSupport
                  ?.supported === true

              const Icon =
                itemType === 'component'
                  ? item.icon
                  : Link2

              return (
                <button
                  key={item.id}
                  type="button"
                  onClick={() =>
                    onSelect(item.id)
                  }
                  title={
                    item.generationSupport
                      ?.reason
                  }
                  className={[
                    'w-full min-w-0 rounded-lg border px-3 py-3 text-left transition',
                    isSelected
                      ? [
                          'border-indigo-400',
                          'bg-indigo-600/25',
                          'text-white',
                          'ring-1 ring-indigo-400',
                        ].join(' ')
                      : isGenerationSupported
                        ? [
                            'border-emerald-400/20',
                            'bg-slate-800/80',
                            'text-slate-300',
                            'hover:border-emerald-400/50',
                            'hover:bg-emerald-400/5',
                            'hover:text-white',
                          ].join(' ')
                        : [
                            'border-slate-700/60',
                            'bg-slate-900/60',
                            'text-slate-300',
                            'hover:border-slate-500',
                            'hover:bg-slate-800',
                            'hover:text-white',
                          ].join(' '),
                  ].join(' ')}
                >
                  <span className="flex min-w-0 items-start gap-3">
                    <span
                      className={[
                        'flex h-9 w-9 shrink-0',
                        'items-center justify-center',
                        'rounded-md',
                        isSelected
                          ? 'bg-indigo-500 text-white'
                          : isGenerationSupported
                            ? [
                                'bg-emerald-400/10',
                                'text-emerald-300',
                              ].join(' ')
                            : [
                                'bg-slate-700',
                                'text-slate-300',
                              ].join(' '),
                      ].join(' ')}
                    >
                      {Icon && (
                        <Icon size={18} />
                      )}
                    </span>

                    <span className="min-w-0 flex-1">
                      <span className="block truncate text-sm font-medium">
                        {item.name}
                      </span>

                      <span className="mt-0.5 block truncate text-xs text-slate-400">
                        {itemType ===
                        'component'
                          ? item.technology ||
                            item.type
                          : item.protocol ||
                            item.connectionType}
                      </span>

                      <span className="mt-2 block">
                        <GenerationSupportBadge
                          support={
                            item.generationSupport
                          }
                          isLoading={
                            isGenerationSupportLoading
                          }
                          compact
                        />
                      </span>
                    </span>
                  </span>
                </button>
              )
            },
          )}
        </div>
      )}
    </section>
  )
}


export default function Sidebar() {
  const [search, setSearch] =
    useState('')

  const {
    generationSupport,
    isLoading:
      isGenerationSupportLoading,
    error: generationSupportError,
    reloadGenerationSupport,
  } = useGenerationSupport()

  const sidebarTab =
    useArchitectureStore(
      (state) => state.sidebarTab,
    )

  const activeComponentTemplateId =
    useArchitectureStore(
      (state) =>
        state.activeComponentTemplateId,
    )

  const activeConnectionTemplateId =
    useArchitectureStore(
      (state) =>
        state.activeConnectionTemplateId,
    )

  const setSidebarTab =
    useArchitectureStore(
      (state) =>
        state.setSidebarTab,
    )

  const toggleComponentPlacement =
    useArchitectureStore(
      (state) =>
        state.toggleComponentPlacement,
    )

  const clearComponentPlacement =
    useArchitectureStore(
      (state) =>
        state.clearComponentPlacement,
    )

  const toggleConnectionTemplate =
    useArchitectureStore(
      (state) =>
        state.toggleConnectionTemplate,
    )

  const clearConnectionTemplate =
    useArchitectureStore(
      (state) =>
        state.clearConnectionTemplate,
    )

  const normalizedSearch =
    search.trim().toLowerCase()

  const visibleComponentCategories =
    useMemo(
      () =>
        componentCategories
          .map((category) => ({
            ...category,

            items:
              category.items
                .map((item) => ({
                  ...item,
                  generationSupport:
                    getComponentGenerationSupport(
                      item,
                      generationSupport,
                    ),
                }))
                .filter(
                  (item) =>
                    [
                      item.name,
                      item.type,
                      item.technology,
                      item.description,
                      item.generationSupport
                        ?.label,
                      item.generationSupport
                        ?.reason,
                      ...(
                        item.generationSupport
                          ?.technologies || []
                      ),
                      ...(
                        item.generationSupport
                          ?.generators || []
                      ),
                    ]
                      .filter(Boolean)
                      .join(' ')
                      .toLowerCase()
                      .includes(
                        normalizedSearch,
                      ),
                ),
          }))
          .filter(
            (category) =>
              category.items.length >
              0,
          ),
      [
        generationSupport,
        normalizedSearch,
      ],
    )

  const visibleConnectionCategories =
    useMemo(
      () =>
        connectionCategories
          .map((category) => ({
            ...category,

            items:
              category.items
                .map((item) => ({
                  ...item,
                  generationSupport:
                    getConnectionGenerationSupport(
                      item,
                      generationSupport,
                    ),
                }))
                .filter(
                  (item) =>
                    [
                      item.name,
                      item.connectionType,
                      item.protocol,
                      item.description,
                      item.generationSupport
                        ?.label,
                      item.generationSupport
                        ?.reason,
                      ...(
                        item.generationSupport
                          ?.technologies || []
                      ),
                      ...(
                        item.generationSupport
                          ?.generators || []
                      ),
                    ]
                      .filter(Boolean)
                      .join(' ')
                      .toLowerCase()
                      .includes(
                        normalizedSearch,
                      ),
                ),
          }))
          .filter(
            (category) =>
              category.items.length >
              0,
          ),
      [
        generationSupport,
        normalizedSearch,
      ],
    )

  const hasActiveComponent =
    sidebarTab === 'components' &&
    activeComponentTemplateId !==
      null

  const hasActiveConnection =
    sidebarTab === 'connections' &&
    activeConnectionTemplateId !==
      null

  function handleTabChange(tab) {
    setSearch('')
    setSidebarTab(tab)
  }

  function cancelActiveTool() {
    if (
      sidebarTab === 'components'
    ) {
      clearComponentPlacement()
      return
    }

    clearConnectionTemplate()
  }

  return (
    <aside className="box-border flex h-full min-h-0 w-full min-w-0 flex-col overflow-hidden bg-slate-950 text-white">
      <div className="shrink-0 border-b border-slate-800 p-3">
        <div
          role="tablist"
          aria-label="Architecture tools"
          className="grid w-full min-w-0 grid-cols-2 gap-1 rounded-lg bg-slate-900 p-1"
        >
          <button
            type="button"
            role="tab"
            aria-selected={
              sidebarTab ===
              'components'
            }
            onClick={() =>
              handleTabChange(
                'components',
              )
            }
            className={[
              'flex min-w-0 items-center',
              'justify-center gap-2',
              'rounded-md px-2 py-2',
              'text-xs font-medium',
              'transition',
              sidebarTab ===
              'components'
                ? [
                    'bg-indigo-600',
                    'text-white shadow',
                  ].join(' ')
                : [
                    'text-slate-400',
                    'hover:text-white',
                  ].join(' '),
            ].join(' ')}
          >
            <Component
              size={15}
              className="shrink-0"
            />

            <span className="truncate">
              Components
            </span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={
              sidebarTab ===
              'connections'
            }
            onClick={() =>
              handleTabChange(
                'connections',
              )
            }
            className={[
              'flex min-w-0 items-center',
              'justify-center gap-2',
              'rounded-md px-2 py-2',
              'text-xs font-medium',
              'transition',
              sidebarTab ===
              'connections'
                ? [
                    'bg-indigo-600',
                    'text-white shadow',
                  ].join(' ')
                : [
                    'text-slate-400',
                    'hover:text-white',
                  ].join(' '),
            ].join(' ')}
          >
            <Link2
              size={15}
              className="shrink-0"
            />

            <span className="truncate">
              Connections
            </span>
          </button>
        </div>

        <div className="relative mt-3">
          <Search
            size={16}
            className={[
              'absolute left-3 top-1/2',
              '-translate-y-1/2',
              'text-slate-500',
            ].join(' ')}
          />

          <input
            type="search"
            value={search}
            onChange={(event) =>
              setSearch(
                event.target.value,
              )
            }
            placeholder={
              sidebarTab ===
              'components'
                ? 'Search components'
                : 'Search connections'
            }
            className={[
              'w-full min-w-0',
              'rounded-lg border',
              'border-slate-700',
              'bg-slate-900',
              'py-2 pl-9 pr-3',
              'text-sm outline-none',
              'placeholder:text-slate-500',
              'focus:border-indigo-500',
            ].join(' ')}
          />
        </div>

        <div className="mt-3 flex flex-wrap gap-2 text-[10px]">
          <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-2 py-1 font-semibold text-emerald-300">
            <span
              className="h-1.5 w-1.5 rounded-full bg-emerald-300"
              aria-hidden="true"
            />

            Generation Supported
          </span>

          <span className="inline-flex items-center gap-1.5 rounded-full border border-slate-500/40 bg-slate-700/40 px-2 py-1 font-semibold text-slate-300">
            <span
              className="h-1.5 w-1.5 rounded-full bg-slate-400"
              aria-hidden="true"
            />

            Modeling Only
          </span>
        </div>

        {generationSupportError && (
          <div className="mt-3 rounded-lg border border-amber-500/30 bg-amber-500/10 p-2.5">
            <div className="flex items-start gap-2">
              <AlertTriangle
                size={15}
                className="mt-0.5 shrink-0 text-amber-300"
              />

              <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-amber-200">
                  Generation support unavailable
                </p>

                <p className="mt-1 text-[11px] leading-4 text-slate-300">
                  {generationSupportError.message}
                </p>
              </div>

              <button
                type="button"
                onClick={
                  reloadGenerationSupport
                }
                aria-label="Retry loading generation support"
                title="Retry"
                className="shrink-0 rounded-md p-1 text-amber-300 transition hover:bg-amber-400/10 hover:text-amber-200"
              >
                <RefreshCw size={14} />
              </button>
            </div>
          </div>
        )}
      </div>

      {(hasActiveComponent ||
        hasActiveConnection) && (
        <div className="shrink-0 border-b border-indigo-500/30 bg-indigo-500/10 p-3">
          <div className="flex items-start justify-between gap-3">
            <div className="min-w-0">
              <p className="truncate text-sm font-semibold text-indigo-200">
                {hasActiveComponent
                  ? 'Placement active'
                  : 'Connection active'}
              </p>

              <p className="mt-1 text-xs leading-5 text-slate-300">
                {hasActiveComponent
                  ? 'Left-click the grid to place the selected component. Right-click to cancel.'
                  : 'Click a source component to begin the connection. Right-click to cancel.'}
              </p>
            </div>

            <button
              type="button"
              aria-label="Cancel selected tool"
              onClick={
                cancelActiveTool
              }
              className={[
                'shrink-0 rounded-md p-1',
                'text-slate-400 transition',
                'hover:bg-slate-800',
                'hover:text-white',
              ].join(' ')}
            >
              <X size={17} />
            </button>
          </div>
        </div>
      )}

      <div className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden">
        {sidebarTab ===
        'components'
          ? visibleComponentCategories.map(
              (category) => (
                <CatalogSection
                  key={category.id}
                  category={category}
                  selectedId={
                    activeComponentTemplateId
                  }
                  onSelect={
                    toggleComponentPlacement
                  }
                  itemType="component"
                  isGenerationSupportLoading={
                    isGenerationSupportLoading
                  }
                />
              ),
            )
          : visibleConnectionCategories.map(
              (category) => (
                <CatalogSection
                  key={category.id}
                  category={category}
                  selectedId={
                    activeConnectionTemplateId
                  }
                  onSelect={
                    toggleConnectionTemplate
                  }
                  itemType="connection"
                  isGenerationSupportLoading={
                    isGenerationSupportLoading
                  }
                />
              ),
            )}

        {(sidebarTab ===
        'components'
          ? visibleComponentCategories
          : visibleConnectionCategories
        ).length === 0 && (
          <p className="px-4 py-8 text-center text-sm text-slate-500">
            No matching items were
            found.
          </p>
        )}
      </div>

      <div className="shrink-0 border-t border-slate-800 p-3 text-xs leading-5 text-slate-400">
        {sidebarTab ===
        'components'
          ? 'Select a component, then left-click the grid to place it. Modeling-only components remain available for architecture design.'
          : 'Select a connection type, then choose a source component. Modeling-only connections remain available for architecture design.'}
      </div>
    </aside>
  )
}