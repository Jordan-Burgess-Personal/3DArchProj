import {
  Box,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'


function createDockerNodes() {
  return [
    {
      id: 'docker-compose-file',
      name: 'docker-compose.yml',
      type: 'file',
      label: 'Docker Compose',
    },
    {
      id: 'docker-env-example',
      name: '.env.example',
      type: 'file',
      label: 'Environment',
    },
  ]
}


export default function DockerPreview({
  serviceCount = 0,
}) {
  return (
    <section>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <span
            className={[
              'flex h-8 w-8',
              'items-center justify-center',
              'rounded-lg',
              'bg-blue-400/10',
              'text-blue-300',
            ].join(' ')}
          >
            <Box size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Docker
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Root container configuration for
              supported architecture layers.
            </p>
          </div>
        </div>

        <span
          className={[
            'inline-flex items-center',
            'rounded-full border',
            'border-blue-400/30',
            'bg-blue-400/10',
            'px-2.5 py-1',
            'text-xs font-semibold',
            'text-blue-200',
          ].join(' ')}
        >
          {serviceCount}{' '}
          {serviceCount === 1
            ? 'service'
            : 'services'}
        </span>
      </div>

      <ExportFileTree
        nodes={createDockerNodes()}
        defaultExpanded
        emptyMessage="No Docker configuration files are available for export."
      />
    </section>
  )
}