import {
  AlertCircle,
  Code2,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'


const SUPPORTED_FRONTEND_FRAMEWORKS = [
  'React',
  'Vite',
]


function normalizeFramework(framework) {
  return String(framework ?? '')
    .trim()
    .toLowerCase()
}


function isSupportedFrontendFramework(
  framework,
) {
  const normalizedFramework =
    normalizeFramework(framework)

  return SUPPORTED_FRONTEND_FRAMEWORKS.some(
    (supportedFramework) =>
      normalizeFramework(
        supportedFramework,
      ) === normalizedFramework,
  )
}


function createFrontendNodes() {
  return [
    {
      id: 'frontend-dockerfile',
      name: 'Dockerfile',
      type: 'file',
      label: 'Docker',
    },
    {
      id: 'frontend-dockerignore',
      name: '.dockerignore',
      type: 'file',
      label: 'Docker',
    },
    {
      id: 'frontend-src-folder',
      name: 'src',
      type: 'folder',
      nodes: [
        {
          id: 'frontend-app-file',
          name: 'App.jsx',
          type: 'file',
        },
        {
          id: 'frontend-main-file',
          name: 'main.jsx',
          type: 'file',
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
        'border-indigo-400/30',
        'bg-indigo-400/10',
        'px-2.5 py-1',
        'text-xs font-semibold',
        'text-indigo-200',
      ].join(' ')}
    >
      {framework}
    </span>
  )
}


export default function FrontendPreview({
  framework,
}) {
  const supported =
    isSupportedFrontendFramework(
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
              Frontend files will not be generated
            </h4>

            <p className="mt-1 text-sm leading-6 text-amber-100/80">
              The current frontend generator
              supports React and Vite.
              Select a supported frontend
              component to include frontend
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
              'bg-indigo-400/10',
              'text-indigo-300',
            ].join(' ')}
          >
            <Code2 size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Frontend
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Generated frontend source and
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
          id: 'frontend-root-folder',
          name: 'frontend',
          label: framework,
        }}
        nodes={createFrontendNodes()}
        defaultExpanded
        emptyMessage="No frontend files are available for export."
      />
    </section>
  )
}