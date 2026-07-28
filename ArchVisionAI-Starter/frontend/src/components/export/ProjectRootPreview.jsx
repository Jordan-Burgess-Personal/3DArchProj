import {
  BookOpen,
} from 'lucide-react'

import ExportFileTree from './ExportFileTree'

function createProjectRootNodes() {
  return [
    {
      id: 'project-readme-file',
      name: 'README.md',
      type: 'file',
      label: 'Documentation',
    },
    {
      id: 'project-license-file',
      name: 'LICENSE',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-gitignore-file',
      name: '.gitignore',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-gitattributes-file',
      name: '.gitattributes',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-changelog-file',
      name: 'CHANGELOG.md',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-contributing-file',
      name: 'CONTRIBUTING.md',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-codeowners-file',
      name: 'CODEOWNERS',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-editorconfig-file',
      name: '.editorconfig',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-prettier-file',
      name: '.prettierrc',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-eslint-file',
      name: '.eslintrc.json',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
    {
      id: 'project-package-lock-file',
      name: 'package-lock.json',
      type: 'file',
      label: 'Future',
      hidden: true,
    },
  ].filter((node) => !node.hidden)
}

export default function ProjectRootPreview() {
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
            <BookOpen size={17} />
          </span>

          <div>
            <h4 className="text-sm font-semibold text-white">
              Project Root
            </h4>

            <p className="mt-0.5 text-xs text-slate-400">
              Generated project-level files that will be included in the exported
              starter project.
            </p>
          </div>
        </div>
      </div>

      <ExportFileTree
        root={{
          id: 'project-root-folder',
          name: 'project',
          label: 'Root',
        }}
        nodes={createProjectRootNodes()}
        defaultExpanded
        emptyMessage="No project-level files are available for export."
      />
    </section>
  )
}