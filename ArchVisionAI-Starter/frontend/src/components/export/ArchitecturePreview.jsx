import {
  Braces,
  FileJson,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'


function createArchitectureNodes() {
  return [
    {
      id: 'architecture-json-file',
      name: 'architecture.json',
      type: 'file',
      label: 'Architecture',
    },
  ]
}


export default function ArchitecturePreview() {
  const architectureNodes =
    createArchitectureNodes()

  return (
    <section>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={[
              'flex h-8 w-8',
              'items-center justify-center',
              'rounded-lg',
              'bg-emerald-400/10',
              'text-emerald-300',
            ].join(' ')}
          >
            <Braces size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Architecture
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Serialized architecture data
              describing the exported project.
            </p>
          </div>
        </div>

        <span
          className={[
            'inline-flex items-center gap-1.5',
            'rounded-full border',
            'border-emerald-400/30',
            'bg-emerald-400/10',
            'px-2.5 py-1',
            'text-xs font-semibold',
            'text-emerald-200',
          ].join(' ')}
        >
          <FileJson size={13} />

          JSON
        </span>
      </div>

      <ExportFileTree
        nodes={architectureNodes}
        defaultExpanded
        emptyMessage="The architecture definition is not available for export."
      />
    </section>
  )
}