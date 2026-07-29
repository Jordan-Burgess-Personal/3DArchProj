import {
  ChevronDown,
  ChevronRight,
  File,
  Folder,
  FolderOpen,
} from 'lucide-react'

import { useMemo, useState } from 'react'


function normalizeNodes(nodes) {
  return Array.isArray(nodes) ? nodes : []
}


function hasChildNodes(node) {
  return (
    node?.type === 'folder' &&
    Array.isArray(node?.nodes) &&
    node.nodes.length > 0
  )
}


function collectFolderIds(nodes) {
  const folderIds = []

  normalizeNodes(nodes).forEach((node) => {
    if (node?.type !== 'folder') {
      return
    }

    if (node.id) {
      folderIds.push(node.id)
    }

    if (hasChildNodes(node)) {
      folderIds.push(
        ...collectFolderIds(node.nodes),
      )
    }
  })

  return folderIds
}


function getNodeId({
  node,
  parentPath,
  index,
}) {
  if (node?.id) {
    return String(node.id)
  }

  const nodeName =
    String(node?.name || 'unnamed-node')

  return [
    parentPath,
    nodeName,
    index,
  ]
    .filter(Boolean)
    .join('/')
}


function TreeConnector({
  depth,
  isLast,
}) {
  if (depth <= 0) {
    return null
  }

  return (
    <span
      aria-hidden="true"
      className={[
        'mr-2 shrink-0',
        'font-mono text-slate-600',
      ].join(' ')}
    >
      {isLast ? '└──' : '├──'}
    </span>
  )
}


function TreeNode({
  node,
  depth,
  index,
  siblingCount,
  parentPath,
  expandedFolderIds,
  onToggleFolder,
}) {
  const isFolder =
    node?.type === 'folder'

  const childNodes =
    normalizeNodes(node?.nodes)

  const containsChildren =
    isFolder &&
    childNodes.length > 0

  const nodeId = getNodeId({
    node,
    parentPath,
    index,
  })

  const isExpanded =
    isFolder &&
    expandedFolderIds.has(nodeId)

  const isLast =
    index === siblingCount - 1

  const currentPath = [
    parentPath,
    node?.name || nodeId,
  ]
    .filter(Boolean)
    .join('/')

  const FolderIcon =
    isExpanded
      ? FolderOpen
      : Folder

  function handleToggle() {
    if (!containsChildren) {
      return
    }

    onToggleFolder(nodeId)
  }

  function handleKeyDown(event) {
    if (!containsChildren) {
      return
    }

    if (
      event.key === 'Enter' ||
      event.key === ' '
    ) {
      event.preventDefault()
      onToggleFolder(nodeId)
    }

    if (
      event.key === 'ArrowRight' &&
      !isExpanded
    ) {
      event.preventDefault()
      onToggleFolder(nodeId)
    }

    if (
      event.key === 'ArrowLeft' &&
      isExpanded
    ) {
      event.preventDefault()
      onToggleFolder(nodeId)
    }
  }

  return (
    <div>
      <div
        className={[
          'flex min-h-8 items-center',
          'rounded-md px-1',
          containsChildren
            ? 'cursor-pointer'
            : 'cursor-default',
          'transition-colors',
          containsChildren
            ? 'hover:bg-slate-800/70'
            : '',
          isFolder
            ? 'text-cyan-200'
            : 'text-slate-300',
        ].join(' ')}
        style={{
          paddingLeft:
            `${depth * 24}px`,
        }}
        role={
          containsChildren
            ? 'button'
            : undefined
        }
        tabIndex={
          containsChildren
            ? 0
            : undefined
        }
        aria-expanded={
          containsChildren
            ? isExpanded
            : undefined
        }
        onClick={handleToggle}
        onKeyDown={handleKeyDown}
      >
        <TreeConnector
          depth={depth}
          isLast={isLast}
        />

        {containsChildren ? (
          isExpanded ? (
            <ChevronDown
              size={14}
              className="mr-1 shrink-0 text-slate-500"
            />
          ) : (
            <ChevronRight
              size={14}
              className="mr-1 shrink-0 text-slate-500"
            />
          )
        ) : (
          <span
            aria-hidden="true"
            className="mr-1 inline-block w-3.5 shrink-0"
          />
        )}

        {isFolder ? (
          <FolderIcon
            size={15}
            className="mr-2 shrink-0"
          />
        ) : (
          <File
            size={15}
            className="mr-2 shrink-0"
          />
        )}

        <span className="whitespace-nowrap">
          {node?.name || 'Unnamed'}
        </span>

        {node?.label && (
          <span
            className={[
              'ml-3 rounded-full',
              'border border-slate-600',
              'bg-slate-800 px-2 py-0.5',
              'text-[10px] font-semibold',
              'uppercase tracking-wide',
              'text-slate-400',
            ].join(' ')}
          >
            {node.label}
          </span>
        )}
      </div>

      {containsChildren &&
        isExpanded && (
          <div>
            {childNodes.map(
              (childNode, childIndex) => (
                <TreeNode
                  key={getNodeId({
                    node: childNode,
                    parentPath:
                      currentPath,
                    index:
                      childIndex,
                  })}
                  node={childNode}
                  depth={depth + 1}
                  index={childIndex}
                  siblingCount={
                    childNodes.length
                  }
                  parentPath={
                    currentPath
                  }
                  expandedFolderIds={
                    expandedFolderIds
                  }
                  onToggleFolder={
                    onToggleFolder
                  }
                />
              ),
            )}
          </div>
        )}
    </div>
  )
}


export default function ExportFileTree({
  root,
  nodes,
  title,
  description,
  defaultExpanded = true,
  emptyMessage =
    'No generated files are available for this section.',
  className = '',
}) {
  const normalizedNodes = useMemo(
    () => normalizeNodes(nodes),
    [nodes],
  )

  const rootNode = useMemo(() => {
    if (!root) {
      return null
    }

    if (
      typeof root === 'object' &&
      root !== null
    ) {
      return {
        id:
          root.id ||
          'export-tree-root',
        name:
          root.name ||
          'project',
        type: 'folder',
        nodes:
          Array.isArray(root.nodes)
            ? root.nodes
            : normalizedNodes,
        label: root.label,
      }
    }

    return {
      id: 'export-tree-root',
      name: String(root),
      type: 'folder',
      nodes: normalizedNodes,
    }
  }, [
    root,
    normalizedNodes,
  ])

  const renderedNodes = useMemo(
    () =>
      rootNode
        ? [rootNode]
        : normalizedNodes,
    [
      rootNode,
      normalizedNodes,
    ],
  )

  const initialExpandedFolders =
    useMemo(() => {
      if (!defaultExpanded) {
        return new Set()
      }

      return new Set(
        collectFolderIds(
          renderedNodes,
        ),
      )
    }, [
      defaultExpanded,
      renderedNodes,
    ])

  const [
    expandedFolderIds,
    setExpandedFolderIds,
  ] = useState(
    initialExpandedFolders,
  )

  function handleToggleFolder(
    folderId,
  ) {
    setExpandedFolderIds(
      (currentIds) => {
        const nextIds =
          new Set(currentIds)

        if (
          nextIds.has(folderId)
        ) {
          nextIds.delete(folderId)
        } else {
          nextIds.add(folderId)
        }

        return nextIds
      },
    )
  }

  const hasNodes =
    renderedNodes.length > 0

  return (
    <section
      className={[
        'rounded-xl border',
        'border-slate-700',
        'bg-slate-950/80',
        className,
      ].join(' ')}
    >
      {(title || description) && (
        <header className="border-b border-slate-800 px-4 py-3">
          {title && (
            <h4 className="text-sm font-semibold text-white">
              {title}
            </h4>
          )}

          {description && (
            <p className="mt-1 text-xs leading-5 text-slate-400">
              {description}
            </p>
          )}
        </header>
      )}

      <div className="overflow-x-auto p-4">
        {hasNodes ? (
          <div className="min-w-max font-mono text-sm">
            {renderedNodes.map(
              (node, index) => (
                <TreeNode
                  key={getNodeId({
                    node,
                    parentPath: '',
                    index,
                  })}
                  node={node}
                  depth={0}
                  index={index}
                  siblingCount={
                    renderedNodes.length
                  }
                  parentPath=""
                  expandedFolderIds={
                    expandedFolderIds
                  }
                  onToggleFolder={
                    handleToggleFolder
                  }
                />
              ),
            )}
          </div>
        ) : (
          <div
            className={[
              'rounded-lg border',
              'border-dashed',
              'border-slate-700',
              'bg-slate-900/40',
              'px-4 py-6',
              'text-center text-sm',
              'text-slate-400',
            ].join(' ')}
          >
            {emptyMessage}
          </div>
        )}
      </div>
    </section>
  )
}