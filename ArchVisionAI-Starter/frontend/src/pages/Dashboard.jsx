import { FolderOpen, Plus } from 'lucide-react'
import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

import { useArchitectureStore } from '../store/architectureStore'

export default function Dashboard() {
  const navigate = useNavigate()
  
  const projects = useArchitectureStore(
    (state) => state.projects,
  )

  const resetModel =
    useArchitectureStore(
      (state) => state.resetModel,
    )

  const isProjectsLoading =
    useArchitectureStore(
      (state) => state.isProjectsLoading,
    )

  const projectsError =
    useArchitectureStore(
      (state) => state.projectsError,
    )

  const refreshProjects =
    useArchitectureStore(
      (state) => state.refreshProjects,
    )

  const selectProject =
    useArchitectureStore(
      (state) => state.selectProject,
    )

  const openProjectManager =
    useArchitectureStore(
      (state) => state.openProjectManager,
    )

  useEffect(() => {
    refreshProjects()
  }, [refreshProjects])

  function createNewArchitecture() {
    resetModel()
    navigate('/workspace')
  }

  function openProject(projectId) {
    selectProject(projectId)
    openProjectManager()
  }

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
              Create a new software architecture or continue
              working on an existing project.
            </p>
          </div>

          <button
            type="button"
            onClick={createNewArchitecture}
            className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-medium hover:bg-indigo-500"
          >
            <Plus size={20} />
            New Architecture
          </button>
        </section>

        <section className="py-8">

          <div className="mb-5 flex items-center justify-between">

            <div>
              <h2 className="text-xl font-semibold">
                Projects
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Saved architecture projects.
              </p>
            </div>

            <button
              onClick={refreshProjects}
              className="rounded-lg border border-slate-700 px-4 py-2 text-sm hover:bg-slate-800"
            >
              Refresh
            </button>

          </div>

          {projectsError && (
            <div className="mb-5 rounded-lg border border-red-500/30 bg-red-500/10 p-4 text-red-300">
              {projectsError}
            </div>
          )}

          {isProjectsLoading ? (

            <div className="flex min-h-72 items-center justify-center rounded-xl border border-slate-700">
              Loading projects...
            </div>

          ) : projects.length === 0 ? (

            <div className="flex min-h-72 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">

              <span className="flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600/20 text-indigo-300">
                <FolderOpen size={28} />
              </span>

              <h3 className="mt-5 text-lg font-semibold">
                No projects found
              </h3>

              <p className="mt-2 max-w-md text-sm leading-6 text-slate-400">
                Create your first architecture to begin
                designing your system.
              </p>

              <button
                type="button"
                onClick={createNewArchitecture}
                className="mt-6 inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 font-medium hover:bg-indigo-500"
              >
                <Plus size={18} />
                Create Architecture
              </button>

            </div>

          ) : (

            <div className="grid gap-5 md:grid-cols-2 xl:grid-cols-3">

              {projects.map((project) => (

                <button
                  key={project.id}
                  onClick={() => openProject(project.id)}
                  className="rounded-xl border border-slate-700 bg-slate-900 p-5 text-left transition hover:border-indigo-500 hover:bg-slate-800"
                >

                  <div className="flex items-start justify-between">

                    <h3 className="text-lg font-semibold">
                      {project.name}
                    </h3>

                    <span className="rounded-full bg-indigo-500/20 px-2 py-1 text-xs text-indigo-300 capitalize">
                      {project.status}
                    </span>

                  </div>

                  <p className="mt-3 line-clamp-3 text-sm text-slate-400">
                    {project.description ||
                      'No description available.'}
                  </p>

                  <div className="mt-5 flex justify-between text-xs text-slate-500">

                    <span>
                      Components: {project.componentCount}
                    </span>

                    <span>
                      Connections: {project.connectionCount}
                    </span>

                  </div>

                </button>

              ))}

            </div>

          )}

        </section>

      </div>
    </div>
  )
}