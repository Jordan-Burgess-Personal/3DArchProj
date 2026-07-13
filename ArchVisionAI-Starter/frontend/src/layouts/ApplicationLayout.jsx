import { Outlet, useLocation } from 'react-router-dom'
import NavigationSidebar from '../components/NavigationSidebar'

export default function ApplicationLayout() {
  const location = useLocation()
  const isWorkspace = location.pathname === '/workspace'

  return (
    <div className="h-screen bg-slate-950 text-white">
      <NavigationSidebar />

      <div className="flex h-full min-w-0 flex-col">
        <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
          <h1 className="text-2xl font-bold">
            ArchVision <span className="text-indigo-400">AI</span>
          </h1>

          {isWorkspace && (
            <button
              type="button"
              className="rounded-lg bg-indigo-600 px-4 py-2 hover:bg-indigo-500"
            >
              Export Project
            </button>
          )}
        </header>

        <main
          className={`min-h-0 flex-1 ${
            isWorkspace ? 'overflow-hidden' : 'overflow-auto'
          }`}
        >
          <Outlet />
        </main>
      </div>
    </div>
  )
}