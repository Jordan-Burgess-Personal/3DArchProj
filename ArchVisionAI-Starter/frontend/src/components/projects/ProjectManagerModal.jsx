import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import { useNavigate } from 'react-router-dom'
import { api } from '../../api/client'
import { useArchitectureStore } from '../../store/architectureStore'

function formatDate(value) {
  if (!value) {
    return 'Not available'
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return 'Not available'
  }

  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

function ProjectStatusBadge({ status }) {
  const normalizedStatus = String(
    status || 'unknown',
  ).toLowerCase()

  const statusClasses = {
    active:
      'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
    draft:
      'border-amber-400/30 bg-amber-400/10 text-amber-300',
    archived:
      'border-slate-400/30 bg-slate-400/10 text-slate-300',
    completed:
      'border-blue-400/30 bg-blue-400/10 text-blue-300',
  }

  const className =
    statusClasses[normalizedStatus] ||
    'border-slate-400/30 bg-slate-400/10 text-slate-300'

  return (
    <span
      className={[
        'inline-flex rounded-full border px-2.5 py-1',
        'text-xs font-semibold capitalize',
        className,
      ].join(' ')}
    >
      {normalizedStatus}
    </span>
  )
}

function ProjectListItem({
  project,
  isSelected,
  onSelect,
}) {
  function handleClick() {
    onSelect(
      isSelected
        ? null
        : project.id,
    )
  }

  return (
    <button
      type="button"
      onClick={handleClick}
      className={[
        'w-full rounded-xl border p-4 text-left',
        'transition duration-150',
        isSelected
          ? 'border-cyan-400 bg-cyan-400/10'
          : [
              'border-slate-700 bg-slate-900/70',
              'hover:border-slate-500',
              'hover:bg-slate-800/80',
            ].join(' '),
      ].join(' ')}
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="truncate text-sm font-semibold text-white">
            {project.name || 'Untitled Project'}
          </h3>

          <p className="mt-1 line-clamp-2 text-xs leading-5 text-slate-400">
            {project.description ||
              'No project description has been provided.'}
          </p>
        </div>

        <ProjectStatusBadge
          status={project.status}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-2 text-xs text-slate-400">
        <span>
          Components:{' '}
          <strong className="text-slate-200">
            {project.componentCount ?? 0}
          </strong>
        </span>

        <span>
          Connections:{' '}
          <strong className="text-slate-200">
            {project.connectionCount ?? 0}
          </strong>
        </span>
      </div>

      <p className="mt-3 text-xs text-slate-500">
        Updated {formatDate(project.updatedAt)}
      </p>
    </button>
  )
}

function EmptyProjectList() {
  return (
    <div className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
      <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 text-xl">
        ◫
      </div>

      <h3 className="mt-4 text-sm font-semibold text-white">
        No projects found
      </h3>

      <p className="mt-2 max-w-sm text-sm leading-6 text-slate-400">
        Projects saved through ArchVision AI will appear
        here after they have been added to the database.
      </p>
    </div>
  )
}

function ProjectDetails({ project }) {
  if (!project) {
    return (
      <div className="flex h-full min-h-80 flex-col items-center justify-center rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-8 text-center">
        <div className="flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 text-xl">
          ↖
        </div>

        <h3 className="mt-4 text-sm font-semibold text-white">
          Select a project
        </h3>

        <p className="mt-2 max-w-sm text-sm leading-6 text-slate-400">
          Choose a project from the list to review its
          summary and project statistics.
        </p>
      </div>
    )
  }

  return (
    <div className="h-full rounded-xl border border-slate-700 bg-slate-900/70 p-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
            Selected project
          </p>

          <h3 className="mt-2 text-xl font-semibold text-white">
            {project.name || 'Untitled Project'}
          </h3>
        </div>

        <ProjectStatusBadge
          status={project.status}
        />
      </div>

      <p className="mt-4 text-sm leading-6 text-slate-300">
        {project.description ||
          'No project description has been provided.'}
      </p>

      <div className="mt-6 grid grid-cols-2 gap-3">
        <div className="rounded-lg border border-slate-700 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Components
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {project.componentCount ?? 0}
          </p>
        </div>

        <div className="rounded-lg border border-slate-700 bg-slate-950/70 p-4">
          <p className="text-xs uppercase tracking-wide text-slate-500">
            Connections
          </p>

          <p className="mt-2 text-2xl font-semibold text-white">
            {project.connectionCount ?? 0}
          </p>
        </div>
      </div>

      <dl className="mt-6 space-y-4">
        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Schema version
          </dt>

          <dd className="mt-1 text-sm text-slate-200">
            {project.schemaVersion || 'Not available'}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Created
          </dt>

          <dd className="mt-1 text-sm text-slate-200">
            {formatDate(project.createdAt)}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Last updated
          </dt>

          <dd className="mt-1 text-sm text-slate-200">
            {formatDate(project.updatedAt)}
          </dd>
        </div>

        <div>
          <dt className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Project ID
          </dt>

          <dd className="mt-1 break-all font-mono text-xs text-slate-400">
            {project.id}
          </dd>
        </div>
      </dl>
    </div>
  )
}

export default function ProjectManagerModal() {
  const navigate = useNavigate()
  
  const [isSaving, setIsSaving] =
    useState(false)

  const [isOpening, setIsOpening] =
    useState(false)

  const [isDeleting, setIsDeleting] =
    useState(false)

  const [saveMessage, setSaveMessage] =
    useState('')

  const openedProjectId =
    useArchitectureStore(
      (state) => state.openedProjectId,
    )

  const setOpenedProjectId =
    useArchitectureStore(
      (state) => state.setOpenedProjectId,
    )

  const isProjectManagerOpen =
    useArchitectureStore(
      (state) => state.isProjectManagerOpen,
    )

  const projects = useArchitectureStore(
    (state) => state.projects,
  )

  const selectedProjectId =
    useArchitectureStore(
      (state) => state.selectedProjectId,
    )

  const isProjectsLoading =
    useArchitectureStore(
      (state) => state.isProjectsLoading,
    )

  const projectsError =
    useArchitectureStore(
      (state) => state.projectsError,
    )

  const projectsLastRefreshedAt =
    useArchitectureStore(
      (state) =>
        state.projectsLastRefreshedAt,
    )

  const projectName =
    useArchitectureStore(
      (state) => state.projectName,
    )
  
  const setProjectName =
    useArchitectureStore(
      (state) => state.setProjectName,
    )

  const closeProjectManager =
    useArchitectureStore(
      (state) => state.closeProjectManager,
    )

  const selectProject =
    useArchitectureStore(
      (state) => state.selectProject,
    )

  const refreshProjects =
    useArchitectureStore(
      (state) => state.refreshProjects,
    )

  const serializeModelForApi =
    useArchitectureStore(
      (state) =>
        state.serializeModelForApi,
    )

  const setModel =
    useArchitectureStore(
      (state) => state.setModel,
    )

  const selectedProject = useMemo(
    () =>
      projects.find(
        (project) =>
          project.id === selectedProjectId,
      ) || null,
    [projects, selectedProjectId],
  )

  useEffect(() => {
    if (!isProjectManagerOpen) {
      return undefined
    }

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        closeProjectManager()
      }
    }

    window.addEventListener(
      'keydown',
      handleKeyDown,
    )

    return () => {
      window.removeEventListener(
        'keydown',
        handleKeyDown,
      )
    }
  }, [
    isProjectManagerOpen,
    closeProjectManager,
  ])

  if (!isProjectManagerOpen) {
    return null
  }

  function handleBackdropMouseDown(event) {
    if (event.target === event.currentTarget) {
      closeProjectManager()
    }
  }

  function getErrorMessage(
    error,
    fallbackMessage,
  ) {
    const responseDetail =
      error?.response?.data?.detail

    if (typeof responseDetail === 'string') {
      return responseDetail
    }

    if (Array.isArray(responseDetail)) {
      return responseDetail
        .map(
          (item) =>
            item?.msg || String(item),
        )
        .join(' ')
    }

    if (!error?.response) {
      return 'Unable to connect to the project service. Confirm that the backend is running.'
    }

    return fallbackMessage
  }

  async function handleSaveProject() {
    if (!selectedProjectId) {
      setSaveMessage(
        'Select a project to overwrite.',
      )
      return
    }

    const confirmed = window.confirm(
      `Overwrite "${
        selectedProject?.name ||
        'Untitled Project'
      }"? This will replace the existing saved architecture.`,
    )

    if (!confirmed) {
      return
    }

    setIsSaving(true)
    setSaveMessage('')

    try {
      const model = serializeModelForApi()

      const projectData = {
        name:
          projectName?.trim() ||
          model.name?.trim() ||
          'Untitled Project',
        model,
      }

      await api.put(
        `/api/projects/${selectedProjectId}`,
        projectData,
      )

      setOpenedProjectId(
        String(selectedProjectId),
      )

      await refreshProjects()

      selectProject(
        String(selectedProjectId),
      )

      setSaveMessage(
        'Project overwritten successfully.',
      )
    } catch (error) {
      setSaveMessage(
        getErrorMessage(
          error,
          'Unable to overwrite the selected project.',
        ),
      )
    } finally {
      setIsSaving(false)
    }
  }

  async function handleSaveAsNew() {
    setIsSaving(true)
    setSaveMessage('')

    try {
      const model = serializeModelForApi()

      const projectData = {
        name:
          projectName?.trim() ||
          model.name?.trim() ||
          'Untitled Project',
        model,
      }

      const response = await api.post(
        '/api/projects',
        projectData,
      )

      const createdProjectId =
        response?.data?.id

      await refreshProjects()

      if (createdProjectId) {
        const normalizedProjectId =
          String(createdProjectId)

        setOpenedProjectId(
          normalizedProjectId,
        )

        selectProject(
          normalizedProjectId,
        )
      }

      setSaveMessage(
        'New project save created successfully.',
      )
    } catch (error) {
      setSaveMessage(
        getErrorMessage(
          error,
          'Unable to create a new project save.',
        ),
      )
    } finally {
      setIsSaving(false)
    }
  }

  async function handleOpenProject() {

    if (!selectedProjectId) {
      setSaveMessage(
        'Select a project before opening it.',
      )
      return
    }

    setIsOpening(true)
    setSaveMessage('Opening project...')

    try {
      const response = await api.get(
        `/api/projects/${selectedProjectId}`,
      )

      const projectData = response?.data
      const model = projectData?.model

      if (!model) {
        throw new Error(
          'The project response did not include an architecture model.',
        )
      }

      setModel(model)
      setOpenedProjectId(
        String(selectedProjectId),
      )

      setSaveMessage(
        'Project opened successfully.',
      )

      closeProjectManager()
      navigate('/workspace')

    } catch (error) {
      setSaveMessage(
        getErrorMessage(
          error,
          'Unable to open the selected project.',
        ),
      )
    } finally {
      setIsOpening(false)
    }
  }

async function handleDeleteProject() {
  if (!selectedProjectId) {
    setSaveMessage(
      'Select a project before deleting it.',
    )
    return
  }

  const confirmed = window.confirm(
    `Are you sure you want to delete "${
      selectedProject?.name ||
      'Untitled Project'
    }"? This action cannot be undone.`,
  )

  if (!confirmed) {
    return
  }

  setIsDeleting(true)
  setSaveMessage('Deleting project...')

  try {
    await api.delete(
      `/api/projects/${selectedProjectId}`,
    )

    if (
      String(openedProjectId) ===
      String(selectedProjectId)
    ) {
      setOpenedProjectId(null)
    }

    selectProject(null)
    await refreshProjects()

    setSaveMessage(
      'Project deleted successfully.',
    )
  } catch (error) {
    setSaveMessage(
      getErrorMessage(
        error,
        'Unable to delete the selected project.',
      ),
    )
  } finally {
    setIsDeleting(false)
  }
}

  return (
    <div
      className={[
        'fixed inset-0 z-50',
        'flex items-center justify-center',
        'bg-slate-950/80 p-4 backdrop-blur-sm',
      ].join(' ')}
      role="presentation"
      onMouseDown={handleBackdropMouseDown}
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="project-manager-title"
        className={[
          'flex max-h-[90vh] w-full max-w-6xl',
          'flex-col overflow-hidden rounded-2xl',
          'border border-slate-700 bg-slate-950',
          'shadow-2xl shadow-black/50',
        ].join(' ')}
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-800 px-6 py-5">
          <div>
            <h2
              id="project-manager-title"
              className="text-xl font-semibold text-white"
            >
              Project Manager
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Browse and review saved architecture
              projects.
            </p>
          </div>

          <button
            type="button"
            onClick={closeProjectManager}
            aria-label="Close project manager"
            className={[
              'flex h-9 w-9 items-center justify-center',
              'rounded-lg border border-slate-700',
              'text-lg text-slate-300 transition',
              'hover:border-slate-500',
              'hover:bg-slate-800 hover:text-white',
            ].join(' ')}
          >
            ×
          </button>
        </header>

        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 px-6 py-3">
          <div className="text-xs text-slate-500">
            {projectsLastRefreshedAt
              ? `Last refreshed ${formatDate(
                  projectsLastRefreshedAt,
                )}`
              : 'Projects have not been refreshed yet.'}
          </div>

          <button
            type="button"
            onClick={refreshProjects}
            disabled={isProjectsLoading}
            className={[
              'rounded-lg border border-slate-600',
              'bg-slate-800 px-4 py-2',
              'text-sm font-semibold text-slate-100',
              'transition',
              'hover:border-cyan-400',
              'hover:bg-slate-700',
              'disabled:cursor-not-allowed',
              'disabled:opacity-50',
            ].join(' ')}
          >
            {isProjectsLoading
              ? 'Refreshing...'
              : 'Refresh Projects'}
          </button>
        </div>

        {projectsError && (
          <div className="mx-6 mt-5 rounded-lg border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-200">
            <strong className="font-semibold">
              Unable to load projects.
            </strong>{' '}
            {projectsError}
          </div>
        )}

        <div className="border-b border-slate-800 px-6 py-4">
          <label
            htmlFor="project-name"
            className="block text-sm font-semibold text-white"
          >
            Current Project Name
          </label>

          <input
            id="project-name"
            type="text"
            value={projectName}
            onChange={(event) =>
              setProjectName(event.target.value)
            }
            placeholder="Enter a project name"
            maxLength={100}
            disabled={isSaving || isOpening || isDeleting}
            className={[
              'mt-2 w-full rounded-lg',
              'border border-slate-700',
              'bg-slate-900 px-4 py-2',
              'text-white outline-none',
              'placeholder:text-slate-500',
              'focus:border-indigo-500',
              'disabled:cursor-not-allowed',
              'disabled:opacity-50',
            ].join(' ')}
          />
        </div>

        <div className="grid min-h-0 flex-1 grid-cols-1 gap-5 overflow-y-auto p-6 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.8fr)]">
          <div className="min-h-0">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white">
                Saved Projects
              </h3>

              <span className="text-xs text-slate-500">
                {projects.length}{' '}
                {projects.length === 1
                  ? 'project'
                  : 'projects'}
              </span>
            </div>

            {isProjectsLoading &&
            projects.length === 0 ? (
              <div className="flex min-h-64 items-center justify-center rounded-xl border border-slate-700 bg-slate-900/40">
                <p className="text-sm text-slate-400">
                  Loading projects...
                </p>
              </div>
            ) : projects.length === 0 ? (
              <EmptyProjectList />
            ) : (
              <div className="space-y-3">
                {projects.map((project) => (
                  <ProjectListItem
                    key={project.id}
                    project={project}
                    isSelected={
                      selectedProjectId ===
                      project.id
                    }
                    onSelect={selectProject}
                  />
                ))}
              </div>
            )}
          </div>

          <ProjectDetails
            project={selectedProject}
          />
        </div>

        <footer className="flex items-center justify-between gap-3 border-t border-slate-800 px-6 py-4">
          <p
            className={[
              'text-xs',
              saveMessage.includes(
                'successfully',
              )
                ? 'text-emerald-300'
                : saveMessage
                  ? 'text-red-300'
                  : 'text-slate-500',
            ].join(' ')}
          >
            {saveMessage ||
              'Select a project to view its summary.'}
          </p>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={handleOpenProject}
              disabled={
                !selectedProjectId ||
                isOpening ||
                isSaving ||
                isDeleting
              }
              className={[
                'rounded-lg border border-cyan-500',
                'px-4 py-2 text-sm font-semibold',
                'text-cyan-200 transition',
                'hover:bg-cyan-500/10',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              {isOpening
                ? 'Opening...'
                : 'Open Project'}
            </button>

            <button
              type="button"
              onClick={handleDeleteProject}
              disabled={
                !selectedProjectId ||
                isDeleting ||
                isOpening ||
                isSaving
              }
              className={[
                'rounded-lg border border-red-500',
                'px-4 py-2 text-sm font-semibold',
                'text-red-200 transition',
                'hover:bg-red-500/10',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              {isDeleting
                ? 'Deleting...'
                : 'Delete Project'}
            </button>

            <button
              type="button"
              onClick={
                selectedProjectId
                  ? handleSaveProject
                  : handleSaveAsNew
              }
              disabled={
                !projectName.trim() ||
                isSaving ||
                isOpening ||
                isDeleting
              }
              className={[
                'rounded-lg bg-indigo-600',
                'px-4 py-2 text-sm font-semibold',
                'text-white transition',
                'hover:bg-indigo-500',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              {isSaving
                ? 'Saving...'
                : selectedProjectId
                  ? 'Overwrite Project'
                  : 'Save New Project'}
            </button>

            <button
              type="button"
              onClick={closeProjectManager}
              disabled={
                isSaving ||
                isOpening ||
                isDeleting
              }
              className={[
                'rounded-lg border border-slate-600',
                'px-4 py-2 text-sm font-semibold',
                'text-slate-200 transition',
                'hover:border-slate-400',
                'hover:bg-slate-800',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              Close
            </button>
          </div>
        </footer>
      </section>
    </div>
  )
}