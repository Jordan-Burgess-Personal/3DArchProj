import { useState } from 'react'
import {
  Boxes,
  ChevronLeft,
  ChevronRight,
  LayoutDashboard,
} from 'lucide-react'
import { NavLink } from 'react-router-dom'

const linkClasses = ({ isActive }) =>
  [
    'flex items-center gap-3 rounded-lg px-4 py-3 text-sm font-medium transition',
    isActive
      ? 'bg-indigo-600 text-white'
      : 'text-slate-400 hover:bg-slate-800 hover:text-white',
  ].join(' ')

export default function NavigationSidebar() {
  const [isPinned, setIsPinned] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const [ignoreHover, setIgnoreHover] = useState(false)

  const isOpen = isPinned || isHovered

  function handleMouseEnter() {
    if (!ignoreHover) {
      setIsHovered(true)
    }
  }

  function handleMouseLeave() {
    setIsHovered(false)
    setIgnoreHover(false)
  }

  function handleOpen() {
    setIsPinned(true)
    setIgnoreHover(false)
  }

  function handleClose() {
    setIsPinned(false)
    setIsHovered(false)

    // Prevent the mouse hover from immediately reopening it.
    setIgnoreHover(true)
  }

  function handleNavigation() {
    setIsPinned(false)
    setIsHovered(false)
    setIgnoreHover(true)
  }

  return (
    <div
      onMouseEnter={handleMouseEnter}
      onMouseLeave={handleMouseLeave}
      className={[
        'fixed inset-y-0 left-0 z-50 transition-[width] duration-200',
        isOpen ? 'w-64' : 'w-10',
      ].join(' ')}
    >
      <button
        type="button"
        aria-label="Open navigation"
        aria-expanded={isOpen}
        onClick={handleOpen}
        className={[
          'absolute left-0 top-1/2 flex h-16 w-10 -translate-y-1/2',
          'items-center justify-center rounded-r-md border border-l-0',
          'border-slate-700 bg-slate-900/90 pl-1 text-slate-300',
          'transition hover:bg-slate-800',
          isOpen ? 'pointer-events-none opacity-0' : 'opacity-100',
        ].join(' ')}
      >
        <ChevronRight size={18} />
      </button>

      <aside
        className={[
          'h-full w-64 border-r border-slate-800 bg-slate-950 shadow-2xl',
          'transition-transform duration-200',
          isOpen ? 'translate-x-0' : '-translate-x-full',
        ].join(' ')}
      >
        <div className="flex h-16 items-center gap-3 border-b border-slate-800 px-4">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-indigo-600 font-bold">
            AV
          </span>

          <span className="flex-1 text-lg font-semibold">
            ArchVision
          </span>

          <button
            type="button"
            aria-label="Close navigation"
            onClick={handleClose}
            className="rounded-lg p-2 text-slate-400 hover:bg-slate-800 hover:text-white"
          >
            <ChevronLeft size={20} />
          </button>
        </div>

        <nav className="flex flex-col gap-2 p-3">
          <NavLink
            to="/dashboard"
            className={linkClasses}
            onClick={handleNavigation}
          >
            <LayoutDashboard size={21} />
            <span>Dashboard</span>
          </NavLink>

          <NavLink
            to="/workspace"
            className={linkClasses}
            onClick={handleNavigation}
          >
            <Boxes size={21} />
            <span>Workspace</span>
          </NavLink>
        </nav>
      </aside>
    </div>
  )
}