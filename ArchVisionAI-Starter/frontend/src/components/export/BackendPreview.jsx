import {
  AlertCircle,
  Server,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'


const SUPPORTED_BACKEND_FRAMEWORKS = [
  'FastAPI',
  'Flask',
]


function normalizeFramework(framework) {
  return String(framework ?? '')
    .trim()
    .toLowerCase()
}


function isSupportedBackendFramework(
  framework,
) {
  const normalizedFramework =
    normalizeFramework(framework)

  return SUPPORTED_BACKEND_FRAMEWORKS.some(
    (supportedFramework) =>
      normalizeFramework(
        supportedFramework,
      ) === normalizedFramework,
  )
}


function createBackendNodes() {
  return [
    {
      id: 'backend-dockerfile',
      name: 'Dockerfile',
      type: 'file',
      label: 'Docker',
    },
    {
      id: 'backend-dockerignore',
      name: '.dockerignore',
      type: 'file',
      label: 'Docker',
    },
    {
      id: 'backend-app-folder',
      name: 'app',
      type: 'folder',
      nodes: [
        {
          id: 'backend-init-file',
          name: '__init__.py',
          type: 'file',
        },
        {
          id: 'backend-main-file',
          name: 'main.py',
          type: 'file',
        },
        {
          id: 'backend-routes-folder',
          name: 'routes',
          type: 'folder',
          nodes: [],
        },
        {
          id: 'backend-services-folder',
          name: 'services',
          type: 'folder',
          nodes: [],
        },
      ],
    },
  ]
}


function FrameworkBadge({
  framework,
}) {
  if (!framework) {
    return null
  }

  return (
    <span
      className={[
        'inline-flex items-center',
        'rounded-full border',
        'border-cyan-400/30',
        'bg-cyan-400/10',
        'px-2.5 py-1',
        'text-xs font-semibold',
        'text-cyan-200',
      ].join(' ')}
    >
      {framework}
    </span>
  )
}


export default function BackendPreview({
  framework,
}) {
  const supported =
    isSupportedBackendFramework(
      framework,
    )

  if (!supported) {
    return (
      <section
        className={[
          'rounded-xl border',
          'border-amber-400/30',
          'bg-amber-400/10',
          'p-4',
        ].join(' ')}
      >
        <div className="flex items-start gap-3">
          <AlertCircle
            size={18}
            className={[
              'mt-0.5 shrink-0',
              'text-amber-300',
            ].join(' ')}
          />

          <div>
            <h4 className="text-sm font-semibold text-amber-100">
              Backend files will not be generated
            </h4>

            <p className="mt-1 text-sm leading-6 text-amber-100/80">
              The current backend generator
              supports FastAPI and Flask.
              Select a supported backend
              component to include backend
              source and Docker files in the
              export.
            </p>
          </div>
        </div>
      </section>
    )
  }

  return (
    <section>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={[
              'flex h-8 w-8',
              'items-center justify-center',
              'rounded-lg',
              'bg-cyan-400/10',
              'text-cyan-300',
            ].join(' ')}
          >
            <Server size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Backend
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Generated backend source and
              container files.
            </p>
          </div>
        </div>

        <FrameworkBadge
          framework={framework}
        />
      </div>

      <ExportFileTree
        root={{
          id: 'backend-root-folder',
          name: 'backend',
          label: framework,
        }}
        nodes={createBackendNodes()}
        defaultExpanded
        emptyMessage="No backend files are available for export."
      />
    </section>
  )
}