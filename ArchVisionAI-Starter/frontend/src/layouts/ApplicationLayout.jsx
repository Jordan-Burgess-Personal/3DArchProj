import { Outlet } from 'react-router-dom'

export default function ApplicationLayout() {
  return (
    <div className="flex h-screen flex-col bg-slate-950 text-white">
      <header className="flex h-16 shrink-0 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">
        <h1 className="text-2xl font-bold">
          ArchVision <span className="text-indigo-400">AI</span>
        </h1>

        <button
          type="button"
          className="rounded-lg bg-indigo-600 px-4 py-2 hover:bg-indigo-500"
        >
          Export Project
        </button>
      </header>

      <main className="min-h-0 flex-1">
        <Outlet />
      </main>
    </div>
  )
}