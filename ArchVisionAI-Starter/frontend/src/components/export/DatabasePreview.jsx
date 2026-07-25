import {
  AlertCircle,
  Database,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'


const DATABASE_DISPLAY_NAMES = {
  postgresql: 'PostgreSQL',
  mysql: 'MySQL',
  mongodb: 'MongoDB',
  sqlite: 'SQLite',
}


function normalizeEngine(engine) {
  return String(engine ?? '')
    .trim()
    .toLowerCase()
}


function getDatabaseDisplayName(
  engine,
) {
  const normalizedEngine =
    normalizeEngine(engine)

  return (
    DATABASE_DISPLAY_NAMES[
      normalizedEngine
    ] || engine
  )
}


function createDatabaseNodes(
  engine,
) {
  const normalizedEngine =
    normalizeEngine(engine)

  if (normalizedEngine === 'mongodb') {
    return [
      {
        id: 'database-init-js',
        name: 'init.js',
        type: 'file',
        label: 'Initialization',
      },
    ]
  }

  return [
    {
      id: 'database-init-sql',
      name: 'init.sql',
      type: 'file',
      label: 'Initialization',
    },
  ]
}


export default function DatabasePreview({
  engine,
  hasDatabaseComponent = false,
}) {
  if (!engine) {
    if (!hasDatabaseComponent) {
      return null
    }

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
            className="mt-0.5 shrink-0 text-amber-300"
          />

          <div>
            <h4 className="text-sm font-semibold text-amber-100">
              Database files will not be generated
            </h4>

            <p className="mt-1 text-sm leading-6 text-amber-100/80">
              The current database generator
              supports PostgreSQL, MySQL,
              MongoDB, and SQLite. Unsupported
              database components remain in
              architecture.json but are not
              added to the generated project.
            </p>
          </div>
        </div>
      </section>
    )
  }

  const displayName =
    getDatabaseDisplayName(
      engine,
    )

  return (
    <section>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={[
              'flex h-8 w-8',
              'items-center justify-center',
              'rounded-lg',
              'bg-violet-400/10',
              'text-violet-300',
            ].join(' ')}
          >
            <Database size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Database
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Generated database initialization
              files.
            </p>
          </div>
        </div>

        <span
          className={[
            'inline-flex items-center',
            'rounded-full border',
            'border-violet-400/30',
            'bg-violet-400/10',
            'px-2.5 py-1',
            'text-xs font-semibold',
            'text-violet-200',
          ].join(' ')}
        >
          {displayName}
        </span>
      </div>

      <ExportFileTree
        root={{
          id: 'database-root-folder',
          name: 'database',
          label: displayName,
        }}
        nodes={createDatabaseNodes(
          engine,
        )}
        defaultExpanded
        emptyMessage="No database files are available for export."
      />
    </section>
  )
}