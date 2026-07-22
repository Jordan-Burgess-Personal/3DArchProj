import { Download } from 'lucide-react'
import { Outlet, useLocation } from 'react-router-dom'

import TopHoverNavigation from '../components/TopHoverNavigation'

export default function ApplicationLayout() {
  const location = useLocation()

  const showExportButton =
    location.pathname === '/workspace'

  return (
    <div className="flex h-dvh min-h-0 w-full min-w-0 flex-col overflow-hidden bg-slate-950 text-white">
      <header className="relative z-40 flex h-14 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950 px-5">
        <h1 className="whitespace-nowrap text-xl font-bold tracking-tight">
          ArchVision{' '}
          <span className="text-indigo-400">
            AI
          </span>
        </h1>

        <TopHoverNavigation />

        {showExportButton ? (
          <button
            type="button"
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium transition hover:bg-indigo-500"
          >
            <Download size={16} />
            Export Project
          </button>
        ) : (
          /*
           * This preserves the header balance on pages where
           * the export button is not displayed.
           */
          <div className="w-[136px]" aria-hidden="true" />
        )}
      </header>

      {/*
       * min-h-0 is essential. It allows this region and its children
       * to shrink within the viewport instead of extending below it.
       */}
      <main className="min-h-0 min-w-0 flex-1 overflow-hidden">
        <Outlet />
      </main>
    </div>
  )
}