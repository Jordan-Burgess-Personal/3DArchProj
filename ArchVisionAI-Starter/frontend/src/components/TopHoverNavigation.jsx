import {
  FolderPlus,
  Home,
  LayoutDashboard,
  Menu,
  Network,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const navigationItems = [
  {
    label: 'Home',
    description: 'Return to the project home page',
    to: '/',
    icon: Home,
  },
  {
    label: 'Projects',
    description: 'View and manage saved projects',
    to: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    label: 'New Project',
    description: 'Open a blank architecture workspace',
    to: '/workspace',
    icon: FolderPlus,
  },
]

export default function TopHoverNavigation() {
  return (
    /*
     * The wrapper controls the hover state. Because the dropdown
     * remains inside this wrapper, it stays open while the mouse
     * is over either the trigger or the expanded menu.
     */
    <div className="group absolute left-1/2 top-0 z-50 -translate-x-1/2">
      {/* Small familiar pull-down tab */}
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

      {/* Slide-down panel */}
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
          {navigationItems.map((item) => {
            const Icon = item.icon

            return (
              <NavLink
                key={item.label}
                to={item.to}
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
                  <Icon size={18} />
                </span>

                <span className="min-w-0">
                  <span className="block truncate text-sm font-semibold">
                    {item.label}
                  </span>

                  <span className="mt-0.5 block text-[11px] leading-4 text-slate-400">
                    {item.description}
                  </span>
                </span>
              </NavLink>
            )
          })}
        </div>
      </nav>
    </div>
  )
}