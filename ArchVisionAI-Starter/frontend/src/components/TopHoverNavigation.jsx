import {
  FolderKanban,
  FolderPlus,
  Home,
  Menu,
} from 'lucide-react'
import {
  NavLink,
  useNavigate,
} from 'react-router-dom'

import { useArchitectureStore } from '../store/architectureStore'

export default function TopHoverNavigation() {
  const navigate = useNavigate()

  const openProjectManager =
    useArchitectureStore(
      (state) => state.openProjectManager,
    )

  const startNewProject =
    useArchitectureStore(
      (state) => state.startNewProject,
    )

  function handleNewProject() {
    startNewProject()
    navigate('/workspace')
  }

  return (
    <div className="group absolute left-1/2 top-0 z-50 -translate-x-1/2">
      <div className="flex justify-center">
        <div
          className="
            flex h-5 items-center gap-1.5
            rounded-b-lg border-x border-b border-slate-700
            bg-slate-900 px-4
            text-[11px] font-medium text-slate-300
            shadow-lg transition-colors
            group-hover:border-indigo-500
            group-hover:bg-indigo-600
            group-hover:text-white
          "
        >
          <Menu size={12} />
          Menu
        </div>
      </div>

      <nav
        aria-label="Project navigation"
        className="
          pointer-events-none
          absolute left-1/2 top-5
          w-[min(620px,calc(100vw-2rem))]
          -translate-x-1/2 -translate-y-3
          rounded-xl border border-slate-700
          bg-slate-950/98 p-2
          opacity-0 shadow-2xl backdrop-blur
          transition-all duration-200 ease-out

          group-hover:pointer-events-auto
          group-hover:translate-y-0
          group-hover:opacity-100
        "
      >
        <div className="grid grid-cols-3 gap-2">
          <NavLink
            to="/dashboard"
            className={({ isActive }) =>
              [
                'flex min-w-0 items-center gap-3 rounded-lg border p-3 transition',
                isActive
                  ? 'border-indigo-400 bg-indigo-500/20 text-white'
                  : 'border-transparent bg-slate-900 text-slate-300 hover:border-slate-600 hover:bg-slate-800 hover:text-white',
              ].join(' ')
            }
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-800 text-indigo-300">
              <Home size={18} />
            </span>

            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold">
                Home
              </span>

              <span className="mt-0.5 block text-[11px] leading-4 text-slate-400">
                Return to the project home page
              </span>
            </span>
          </NavLink>

          <button
            type="button"
            onClick={openProjectManager}
            className={[
              'flex min-w-0 items-center gap-3',
              'rounded-lg border border-transparent',
              'bg-slate-900 p-3 text-left',
              'text-slate-300 transition',
              'hover:border-slate-600',
              'hover:bg-slate-800 hover:text-white',
            ].join(' ')}
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-800 text-indigo-300">
              <FolderKanban size={18} />
            </span>

            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold">
                Projects
              </span>

              <span className="mt-0.5 block text-[11px] leading-4 text-slate-400">
                View and manage saved projects
              </span>
            </span>
          </button>

          <button
            type="button"
            onClick={handleNewProject}
            className={[
              'flex min-w-0 items-center gap-3',
              'rounded-lg border border-transparent',
              'bg-slate-900 p-3 text-left',
              'text-slate-300 transition',
              'hover:border-slate-600',
              'hover:bg-slate-800 hover:text-white',
            ].join(' ')}
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-800 text-indigo-300">
              <FolderPlus size={18} />
            </span>

            <span className="min-w-0">
              <span className="block truncate text-sm font-semibold">
                New Project
              </span>

              <span className="mt-0.5 block text-[11px] leading-4 text-slate-400">
                Open a blank architecture workspace
              </span>
            </span>
          </button>
        </div>
      </nav>
    </div>
  )
}