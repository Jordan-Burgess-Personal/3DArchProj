import {
  useEffect,
  useMemo,
  useState,
} from 'react'

import {
  AlertCircle,
  CheckCircle2,
  Code2,
  Database,
  Download,
  Folder,
  Loader2,
  Server,
  X,
} from 'lucide-react'

import { exportStarterProject } from '../../api/export'
import { useArchitectureStore } from '../../store/architectureStore'

import ArchitecturePreview from './ArchitecturePreview'
import BackendPreview from './BackendPreview'
import DatabasePreview from './DatabasePreview'
import DockerPreview from './DockerPreview'
import FrontendPreview from './FrontendPreview'
import ProjectRootPreview from './ProjectRootPreview'


const UNKNOWN_PROJECT_NAME =
  'Untitled Architecture'


function normalizeText(value) {
  return String(value ?? '')
    .trim()
    .toLowerCase()
}


function addUniqueTechnology(
  technologyMap,
  category,
  technology,
) {
  if (!technology) {
    return
  }

  const normalizedTechnology =
    normalizeText(technology)

  const alreadyExists =
    technologyMap[category].some(
      (item) =>
        normalizeText(item) ===
        normalizedTechnology,
    )

  if (!alreadyExists) {
    technologyMap[category].push(
      technology,
    )
  }
}


function getComponentSearchText(
  component,
) {
  return [
    component?.name,
    component?.label,
    component?.type,
    component?.componentType,
    component?.component_type,
    component?.technology,
    component?.framework,
    component?.category,
    component?.templateId,
    component?.template_id,
    component?.metadata?.technology,
    component?.metadata?.framework,
    component?.metadata?.database,
    component?.metadata?.provider,
    component?.metadata?.runtime,
  ]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
}


function detectTechnologies(
  components,
) {
  const technologies = {
    frontend: [],
    backend: [],
    database: [],
    infrastructure: [],
    ai: [],
  }

  components.forEach(
    (component) => {
      const searchText =
        getComponentSearchText(
          component,
        )

      if (
        searchText.includes('react') ||
        searchText.includes('vite')
      ) {
        addUniqueTechnology(
          technologies,
          'frontend',
          'React',
        )
      }

      if (
        searchText.includes(
          'tailwind',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'frontend',
          'Tailwind CSS',
        )
      }

      if (
        searchText.includes(
          'next.js',
        ) ||
        searchText.includes(
          'nextjs',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'frontend',
          'Next.js',
        )
      }

      if (
        searchText.includes('vue')
      ) {
        addUniqueTechnology(
          technologies,
          'frontend',
          'Vue',
        )
      }

      if (
        searchText.includes(
          'angular',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'frontend',
          'Angular',
        )
      }

      if (
        searchText.includes(
          'fastapi',
        ) ||
        searchText.includes(
          'fast api',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'backend',
          'FastAPI',
        )
      }

      if (
        searchText.includes(
          'flask',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'backend',
          'Flask',
        )
      }

      if (
        searchText.includes(
          'express',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'backend',
          'Express',
        )
      }

      if (
        searchText.includes(
          'django',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'backend',
          'Django',
        )
      }

      if (
        searchText.includes(
          'postgres',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'database',
          'PostgreSQL',
        )
      }

      if (
        searchText.includes(
          'mongodb',
        ) ||
        searchText.includes(
          'mongo db',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'database',
          'MongoDB',
        )
      }

      if (
        searchText.includes(
          'mysql',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'database',
          'MySQL',
        )
      }

      if (
        searchText.includes(
          'sqlite',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'database',
          'SQLite',
        )
      }

      if (
        searchText.includes(
          'redis',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'database',
          'Redis',
        )
      }

      if (
        searchText.includes(
          'docker',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'infrastructure',
          'Docker',
        )
      }

      if (
        searchText.includes(
          'kubernetes',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'infrastructure',
          'Kubernetes',
        )
      }

      if (
        searchText.includes(
          'aws',
        ) ||
        searchText.includes(
          'amazon web services',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'infrastructure',
          'AWS',
        )
      }

      if (
        searchText.includes(
          'azure',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'infrastructure',
          'Microsoft Azure',
        )
      }

      if (
        searchText.includes(
          'google cloud',
        ) ||
        searchText.includes(
          'gcp',
        )
      ) {
        addUniqueTechnology(
          technologies,
          'infrastructure',
          'Google Cloud',
        )
      }

      if (
        searchText.includes(
          'openai',
        ) ||
        searchText.includes('gpt')
      ) {
        addUniqueTechnology(
          technologies,
          'ai',
          'OpenAI',
        )
      }
    },
  )

  return technologies
}


function getFrontendFramework(
  components,
) {
  const frontendComponent =
    components.find(
      (component) => {
        const searchText =
          getComponentSearchText(
            component,
          )

        return (
          searchText.includes(
            'react',
          ) ||
          searchText.includes(
            'vite',
          )
        )
      },
    )

  if (!frontendComponent) {
    return null
  }

  const searchText =
    getComponentSearchText(
      frontendComponent,
    )

  if (
    searchText.includes('react')
  ) {
    return 'React'
  }

  if (
    searchText.includes('vite')
  ) {
    return 'Vite'
  }

  return null
}


function getBackendFramework(
  components,
) {
  const backendComponent =
    components.find(
      (component) => {
        const searchText =
          getComponentSearchText(
            component,
          )

        return (
          searchText.includes(
            'fastapi',
          ) ||
          searchText.includes(
            'fast api',
          ) ||
          searchText.includes(
            'flask',
          )
        )
      },
    )

  if (!backendComponent) {
    return null
  }

  const searchText =
    getComponentSearchText(
      backendComponent,
    )

  if (
    searchText.includes(
      'fastapi',
    ) ||
    searchText.includes(
      'fast api',
    )
  ) {
    return 'FastAPI'
  }

  if (
    searchText.includes('flask')
  ) {
    return 'Flask'
  }

  return null
}


function getDatabaseEngine(
  components,
) {
  const databaseComponent =
    components.find(
      (component) => {
        const searchText =
          getComponentSearchText(
            component,
          )

        return (
          normalizeText(
            component?.type,
          ) === 'database' ||
          searchText.includes(
            'postgres',
          ) ||
          searchText.includes(
            'mysql',
          ) ||
          searchText.includes(
            'mongodb',
          ) ||
          searchText.includes(
            'mongo db',
          ) ||
          searchText.includes(
            'sqlite',
          )
        )
      },
    )

  if (!databaseComponent) {
    return null
  }

  const searchText =
    getComponentSearchText(
      databaseComponent,
    )

  if (
    searchText.includes(
      'postgresql',
    ) ||
    searchText.includes(
      'postgres',
    )
  ) {
    return 'postgresql'
  }

  if (
    searchText.includes(
      'mongodb',
    ) ||
    searchText.includes(
      'mongo db',
    )
  ) {
    return 'mongodb'
  }

  if (
    searchText.includes(
      'mysql',
    )
  ) {
    return 'mysql'
  }

  if (
    searchText.includes(
      'sqlite',
    )
  ) {
    return 'sqlite'
  }

  return null
}


function hasDatabaseComponent(
  components,
) {
  return components.some(
    (component) => {
      const searchText =
        getComponentSearchText(
          component,
        )

      return (
        normalizeText(
          component?.type,
        ) === 'database' ||
        searchText.includes(
          'database',
        )
      )
    },
  )
}


function getOpenedProject({
  openedProjectId,
  projects,
}) {
  if (!openedProjectId) {
    return null
  }

  return (
    projects.find(
      (project) =>
        String(project.id) ===
        String(openedProjectId),
    ) || null
  )
}


function getProjectStatus({
  openedProjectId,
  projects,
}) {
  const openedProject =
    getOpenedProject({
      openedProjectId,
      projects,
    })

  if (!openedProject) {
    return 'Unsaved'
  }

  return (
    openedProject.status ||
    'Draft'
  )
}


function getProjectDescription({
  model,
  openedProjectId,
  projects,
}) {
  if (
    typeof model?.description ===
      'string' &&
    model.description.trim()
  ) {
    return model.description.trim()
  }

  const openedProject =
    getOpenedProject({
      openedProjectId,
      projects,
    })

  if (
    typeof openedProject
      ?.description ===
      'string' &&
    openedProject.description.trim()
  ) {
    return (
      openedProject.description.trim()
    )
  }

  return 'No project description has been provided.'
}


function StatusBadge({
  status,
}) {
  const normalizedStatus =
    normalizeText(status)

  const classNames = {
    active:
      'border-emerald-400/30 bg-emerald-400/10 text-emerald-300',
    draft:
      'border-amber-400/30 bg-amber-400/10 text-amber-300',
    completed:
      'border-blue-400/30 bg-blue-400/10 text-blue-300',
    archived:
      'border-slate-400/30 bg-slate-400/10 text-slate-300',
    unsaved:
      'border-fuchsia-400/30 bg-fuchsia-400/10 text-fuchsia-300',
  }

  const className =
    classNames[
      normalizedStatus
    ] || classNames.draft

  return (
    <span
      className={[
        'inline-flex rounded-full border',
        'px-2.5 py-1 text-xs',
        'font-semibold capitalize',
        className,
      ].join(' ')}
    >
      {status || 'Draft'}
    </span>
  )
}


function TechnologyCategory({
  title,
  technologies,
  icon,
}) {
  if (!technologies.length) {
    return null
  }

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
      <div className="flex items-center gap-2">
        <span className="text-cyan-300">
          {icon}
        </span>

        <h4 className="text-sm font-semibold text-white">
          {title}
        </h4>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {technologies.map(
          (technology) => (
            <span
              key={technology}
              className={[
                'rounded-full border',
                'border-slate-600',
                'bg-slate-800 px-3 py-1',
                'text-xs text-slate-200',
              ].join(' ')}
            >
              {technology}
            </span>
          ),
        )}
      </div>
    </div>
  )
}


function getExportSuccessMessage(
  result,
) {
  if (
    typeof result?.message ===
    'string'
  ) {
    return result.message
  }

  if (
    typeof result?.project_path ===
    'string'
  ) {
    return `Project generated at ${result.project_path}`
  }

  if (
    typeof result?.output_path ===
    'string'
  ) {
    return `Project generated at ${result.output_path}`
  }

  if (
    typeof result?.path ===
    'string'
  ) {
    return `Project generated at ${result.path}`
  }

  return 'The starter project was generated successfully.'
}


export default function ExportPreviewModal({
  isOpen,
  onClose,
}) {
  const [
    isExporting,
    setIsExporting,
  ] = useState(false)

  const [
    exportError,
    setExportError,
  ] = useState('')

  const [
    exportSuccess,
    setExportSuccess,
  ] = useState('')

  const model =
    useArchitectureStore(
      (state) => state.model,
    )

  const projectName =
    useArchitectureStore(
      (state) =>
        state.projectName,
    )

  const projects =
    useArchitectureStore(
      (state) => state.projects,
    )

  const openedProjectId =
    useArchitectureStore(
      (state) =>
        state.openedProjectId,
    )

  const serializeModelForApi =
    useArchitectureStore(
      (state) =>
        state.serializeModelForApi,
    )

  const components = useMemo(
    () =>
      Array.isArray(
        model?.components,
      )
        ? model.components
        : [],
    [model?.components],
  )

  const connections = useMemo(
    () =>
      Array.isArray(
        model?.connections,
      )
        ? model.connections
        : [],
    [model?.connections],
  )

  const displayProjectName =
    projectName?.trim() ||
    model?.name?.trim() ||
    UNKNOWN_PROJECT_NAME

  const technologies = useMemo(
    () =>
      detectTechnologies(
        components,
      ),
    [components],
  )

  const frontendFramework =
    useMemo(
      () =>
        getFrontendFramework(
          components,
        ),
      [components],
    )

  const backendFramework =
    useMemo(
      () =>
        getBackendFramework(
          components,
        ),
      [components],
    )
  const databaseEngine = useMemo(
    () =>
      getDatabaseEngine(
        components,
      ),
    [components],
  )

  const containsDatabase =
    useMemo(
      () =>
        hasDatabaseComponent(
          components,
        ),
      [components],
    )

    const dockerServiceCount =
  useMemo(
    () => {
      let count = 0

      if (frontendFramework) {
        count += 1
      }

      if (backendFramework) {
        count += 1
      }

      if (
        databaseEngine &&
        databaseEngine !== 'sqlite'
      ) {
        count += 1
      }

      return count
    },
    [
      frontendFramework,
      backendFramework,
      databaseEngine,
    ],
  )

  const projectStatus = useMemo(
    () =>
      getProjectStatus({
        openedProjectId,
        projects,
      }),
    [
      openedProjectId,
      projects,
    ],
  )

  const projectDescription =
    useMemo(
      () =>
        getProjectDescription({
          model,
          openedProjectId,
          projects,
        }),
      [
        model,
        openedProjectId,
        projects,
      ],
    )

  const technologyCount =
    useMemo(
      () =>
        Object.values(
          technologies,
        ).reduce(
          (
            total,
            category,
          ) =>
            total +
            category.length,
          0,
        ),
      [technologies],
    )

  useEffect(() => {
    if (!isOpen) {
      return undefined
    }

    setExportError('')
    setExportSuccess('')

    function handleKeyDown(
      event,
    ) {
      if (
        event.key ===
          'Escape' &&
        !isExporting
      ) {
        onClose()
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
    isOpen,
    isExporting,
    onClose,
  ])

  if (!isOpen) {
    return null
  }

  function handleBackdropMouseDown(
    event,
  ) {
    if (
      event.target ===
        event.currentTarget &&
      !isExporting
    ) {
      onClose()
    }
  }

  async function handleExport() {
    setIsExporting(true)
    setExportError('')
    setExportSuccess('')

    try {
      if (
        typeof serializeModelForApi !==
        'function'
      ) {
        throw new Error(
          'The current architecture could not be prepared for export.',
        )
      }

      const serializedModel =
        serializeModelForApi()

      const exportModel = {
        ...serializedModel,
        name:
          displayProjectName,
        description:
          serializedModel
            ?.description ??
          model?.description ??
          '',
      }

      const result =
        await exportStarterProject(
          exportModel,
        )

      setExportSuccess(
        getExportSuccessMessage(
          result,
        ),
      )
    } catch (error) {
      setExportError(
        error instanceof Error
          ? error.message
          : 'Unable to export the starter project.',
      )
    } finally {
      setIsExporting(false)
    }
  }

  const exportDisabled =
    isExporting ||
    components.length === 0

  return (
    <div
      className={[
        'fixed inset-0 z-50',
        'flex items-center justify-center',
        'bg-slate-950/80 p-4',
        'backdrop-blur-sm',
      ].join(' ')}
      role="presentation"
      onMouseDown={
        handleBackdropMouseDown
      }
    >
      <section
        role="dialog"
        aria-modal="true"
        aria-labelledby="export-preview-title"
        className={[
          'flex max-h-[90vh]',
          'w-full max-w-5xl',
          'flex-col overflow-hidden',
          'rounded-2xl',
          'border border-slate-700',
          'bg-slate-950',
          'shadow-2xl shadow-black/50',
        ].join(' ')}
      >
        <header className="flex items-start justify-between gap-4 border-b border-slate-800 px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-500/15 text-indigo-300">
              <Download
                size={20}
              />
            </div>

            <div>
              <h2
                id="export-preview-title"
                className="text-xl font-semibold text-white"
              >
                Export Project
              </h2>

              <p className="mt-1 text-sm text-slate-400">
                Review the
                architecture and
                generated project
                structure before
                exporting.
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onClose}
            disabled={
              isExporting
            }
            aria-label="Close export preview"
            className={[
              'flex h-9 w-9',
              'items-center justify-center',
              'rounded-lg border',
              'border-slate-700',
              'text-slate-300 transition',
              'hover:border-slate-500',
              'hover:bg-slate-800',
              'hover:text-white',
              'disabled:cursor-not-allowed',
              'disabled:opacity-50',
            ].join(' ')}
          >
            <X size={18} />
          </button>
        </header>

        <div className="min-h-0 flex-1 overflow-y-auto p-6">
          <section>
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-wider text-cyan-300">
                  Current
                  architecture
                </p>

                <h3 className="mt-2 text-2xl font-semibold text-white">
                  {
                    displayProjectName
                  }
                </h3>
              </div>

              <StatusBadge
                status={
                  projectStatus
                }
              />
            </div>

            <p className="mt-4 max-w-3xl text-sm leading-6 text-slate-300">
              {
                projectDescription
              }
            </p>

            <div className="mt-5 grid grid-cols-2 gap-3 sm:grid-cols-4">
              <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Components
                </p>

                <p className="mt-2 text-2xl font-semibold text-white">
                  {
                    components.length
                  }
                </p>
              </div>

              <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Connections
                </p>

                <p className="mt-2 text-2xl font-semibold text-white">
                  {
                    connections.length
                  }
                </p>
              </div>

              <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Technologies
                </p>

                <p className="mt-2 text-2xl font-semibold text-white">
                  {
                    technologyCount
                  }
                </p>
              </div>

              <div className="rounded-xl border border-slate-700 bg-slate-900/70 p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Generated
                  layers
                </p>

                <p className="mt-2 text-2xl font-semibold text-white">
                  {
                    [
                      frontendFramework,
                      backendFramework,
                      databaseEngine,
                    ].filter(Boolean)
                      .length
                  }
                </p>
              </div>
            </div>
          </section>

          <section className="mt-8">
            <h3 className="text-base font-semibold text-white">
              Technologies
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              Technologies detected
              from the components
              currently displayed in
              the workspace.
            </p>

            {technologyCount >
            0 ? (
              <div className="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2">
                <TechnologyCategory
                  title="Frontend"
                  technologies={
                    technologies.frontend
                  }
                  icon={
                    <Code2
                      size={17}
                    />
                  }
                />

                <TechnologyCategory
                  title="Backend"
                  technologies={
                    technologies.backend
                  }
                  icon={
                    <Server
                      size={17}
                    />
                  }
                />

                <TechnologyCategory
                  title="Database"
                  technologies={
                    technologies.database
                  }
                  icon={
                    <Database
                      size={17}
                    />
                  }
                />

                <TechnologyCategory
                  title="Infrastructure"
                  technologies={
                    technologies.infrastructure
                  }
                  icon={
                    <Folder
                      size={17}
                    />
                  }
                />

                <TechnologyCategory
                  title="Artificial Intelligence"
                  technologies={
                    technologies.ai
                  }
                  icon={
                    <Code2
                      size={17}
                    />
                  }
                />
              </div>
            ) : (
              <div className="mt-4 rounded-xl border border-dashed border-slate-700 bg-slate-900/40 p-6 text-sm text-slate-400">
                No recognized
                technologies were
                detected in the
                current architecture.
              </div>
            )}
          </section>

          <section className="mt-8">
            <h3 className="text-base font-semibold text-white">
              Generated file
              structure
            </h3>

            <p className="mt-1 text-sm text-slate-400">
              This preview only
              displays files and
              folders currently
              supported by the
              export generator.
            </p>

            <div className="mt-4 space-y-6">
              <ArchitecturePreview />

              <ProjectRootPreview />

              <DockerPreview
                serviceCount={
                  dockerServiceCount
                }
              />

              <FrontendPreview
                framework={
                  frontendFramework
                }
              />

              <BackendPreview
                framework={
                  backendFramework
                }
              />

              <DatabasePreview
                engine={
                  databaseEngine
                }
                hasDatabaseComponent={
                  containsDatabase
                }
              />
            </div>

            {components.length ===
              0 && (
              <div className="mt-4 flex gap-3 rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-200">
                <AlertCircle
                  size={18}
                  className="mt-0.5 shrink-0"
                />

                <div>
                  <p className="font-semibold">
                    The architecture
                    is empty.
                  </p>

                  <p className="mt-1 leading-6 text-red-100/80">
                    Add at least one
                    component before
                    exporting the
                    project.
                  </p>
                </div>
              </div>
            )}
          </section>

          {exportError && (
            <div className="mt-6 flex gap-3 rounded-xl border border-red-400/30 bg-red-400/10 px-4 py-3 text-sm text-red-200">
              <AlertCircle
                size={18}
                className="mt-0.5 shrink-0"
              />

              <div>
                <p className="font-semibold">
                  Export failed
                </p>

                <p className="mt-1 leading-6">
                  {exportError}
                </p>
              </div>
            </div>
          )}

          {exportSuccess && (
            <div className="mt-6 flex gap-3 rounded-xl border border-emerald-400/30 bg-emerald-400/10 px-4 py-3 text-sm text-emerald-200">
              <CheckCircle2
                size={18}
                className="mt-0.5 shrink-0"
              />

              <div>
                <p className="font-semibold">
                  Export completed
                </p>

                <p className="mt-1 leading-6">
                  {
                    exportSuccess
                  }
                </p>
              </div>
            </div>
          )}
        </div>

        <footer className="flex flex-wrap items-center justify-between gap-3 border-t border-slate-800 px-6 py-4">
          <p className="text-xs text-slate-500">
            The preview does not
            display generated file
            contents.
          </p>

          <div className="flex items-center gap-3">
            <button
              type="button"
              onClick={onClose}
              disabled={
                isExporting
              }
              className={[
                'rounded-lg border',
                'border-slate-600 px-4 py-2',
                'text-sm font-semibold',
                'text-slate-200 transition',
                'hover:border-slate-400',
                'hover:bg-slate-800',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              {exportSuccess
                ? 'Close'
                : 'Cancel'}
            </button>

            <button
              type="button"
              onClick={
                handleExport
              }
              disabled={
                exportDisabled
              }
              className={[
                'flex items-center gap-2',
                'rounded-lg bg-indigo-600',
                'px-4 py-2',
                'text-sm font-semibold',
                'text-white transition',
                'hover:bg-indigo-500',
                'disabled:cursor-not-allowed',
                'disabled:opacity-50',
              ].join(' ')}
            >
              {isExporting ? (
                <>
                  <Loader2
                    size={16}
                    className="animate-spin"
                  />

                  Exporting...
                </>
              ) : (
                <>
                  <Download
                    size={16}
                  />

                  Export Project
                </>
              )}
            </button>
          </div>
        </footer>
      </section>
    </div>
  )
}