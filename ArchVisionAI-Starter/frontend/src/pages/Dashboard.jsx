import { FolderPlus, Plus } from 'lucide-react'
import { Link } from 'react-router-dom'

export default function Dashboard() {
  return (
    <div className="min-h-full bg-slate-950 px-6 py-8 text-white">
      <div className="mx-auto max-w-7xl">
        <section className="flex flex-col gap-6 border-b border-slate-800 pb-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-medium text-indigo-300">
              Project dashboard
            </p>

            <h1 className="mt-2 text-3xl font-bold tracking-tight">
              Your architectures
            </h1>

            <p className="mt-2 max-w-2xl text-slate-400">
              Create a new software architecture or continue working on an
              existing project.
            </p>
          </div>

          <Link
            to="/workspace"
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-medium hover:bg-indigo-500"
          >
            <Plus size={20} />
            New architecture
          </Link>
        </section>

        <section className="py-8">
          <div className="mb-5">
            <h2 className="text-xl font-semibold">Projects</h2>

            <p className="mt-1 text-sm text-slate-400">
              Your saved architecture projects will appear here.
            </p>
          </div>

          <div className="flex min-h-72 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600/20 text-indigo-300">
              <FolderPlus size={28} />
            </span>

            <h3 className="mt-5 text-lg font-semibold">
              No projects created yet
            </h3>

            <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">
              Create your first architecture to begin designing its frontend,
              backend, database, and supporting services.
            </p>

            <Link
              to="/workspace"
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-medium hover:bg-indigo-500"
            >
              <Plus size={18} />
              Create architecture
            </Link>
          </div>
        </section>
      </div>
    </div>
  )
}