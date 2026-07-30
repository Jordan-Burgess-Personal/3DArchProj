import { create } from 'zustand'

import { getProjectSummaries } from '../api/projects'
import {
  validateArchitecture,
} from '../utils/validateArchitecture'

import {
  findComponentTemplate,
  findConnectionTemplate,
} from '../config/architectureCatalog'

function createComponentId(type = 'component') {
  if (
    typeof crypto !== 'undefined' &&
    typeof crypto.randomUUID === 'function'
  ) {
    return `${type}-${crypto.randomUUID()}`
  }

  return `${type}-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`
}

function createConnectionId() {
  if (
    typeof crypto !== 'undefined' &&
    typeof crypto.randomUUID === 'function'
  ) {
    return crypto.randomUUID()
  }

  return `connection-${Date.now()}-${Math.random()
    .toString(36)
    .slice(2)}`
}

function numberOrFallback(value, fallback) {
  const number = Number(value)

  return Number.isFinite(number)
    ? number
    : fallback
}

function componentFromTemplate(
  templateId,
  {
    id,
    name,
    technology,
    description,
    position,
    metadata = {},
  } = {},
) {
  const template = findComponentTemplate(templateId)

  if (!template) {
    return null
  }

  return {
    id:
      id ||
      createComponentId(
        template.type || 'component',
      ),
    templateId,
    category: template.category || 'custom',
    type: template.type || 'custom',
    name:
      name ||
      template.name ||
      'Untitled Component',
    technology:
      technology ?? template.technology ?? '',
    description:
      description ?? template.description ?? '',
    color: template.color || '#475569',
    icon: template.iconName || '',
    position: {
      x: numberOrFallback(position?.x, 0),
      y: numberOrFallback(position?.y, 0.6),
      z: numberOrFallback(position?.z, 0),
    },
    metadata,
  }
}

function normalizeComponent(component = {}) {
  const catalogTemplate = component.templateId
    ? findComponentTemplate(component.templateId)
    : null

  return {
    id:
      component.id ||
      createComponentId(
        component.type || 'component',
      ),
    templateId:
      component.templateId ||
      catalogTemplate?.id ||
      '',
    category:
      component.category ||
      catalogTemplate?.category ||
      'custom',
    type:
      component.type ||
      catalogTemplate?.type ||
      'custom',
    name:
      component.name ||
      catalogTemplate?.name ||
      'Untitled Component',
    technology:
      component.technology ??
      catalogTemplate?.technology ??
      '',
    description:
      component.description ??
      catalogTemplate?.description ??
      '',
    color:
      component.color ||
      catalogTemplate?.color ||
      '#475569',
    icon: component.icon || '',
    position: {
      x: numberOrFallback(
        component.position?.x,
        0,
      ),
      y: numberOrFallback(
        component.position?.y,
        0.6,
      ),
      z: numberOrFallback(
        component.position?.z,
        0,
      ),
    },
    metadata: component.metadata || {},
  }
}

function normalizeConnection(connection = {}) {
  const catalogTemplate = connection.templateId
    ? findConnectionTemplate(
        connection.templateId,
      )
    : null

  return {
    id:
      connection.id ||
      createConnectionId(),
    templateId:
      connection.templateId ||
      catalogTemplate?.id ||
      '',
    source: connection.source,
    target: connection.target,
    connectionType:
      connection.connectionType ||
      connection.connection_type ||
      catalogTemplate?.connectionType ||
      'dependency',
    protocol:
      connection.protocol ??
      catalogTemplate?.protocol ??
      '',
    direction:
      connection.direction ||
      'unidirectional',
    label:
      connection.label ||
      catalogTemplate?.name ||
      '',
    metadata: connection.metadata || {},
  }
}

function connectionExists(
  connections,
  candidate,
  ignoredId = null,
) {
  return connections.some(
    (connection) =>
      connection.id !== ignoredId &&
      connection.source === candidate.source &&
      connection.target === candidate.target &&
      connection.connectionType ===
        candidate.connectionType &&
      connection.protocol ===
        candidate.protocol &&
      connection.label === candidate.label,
  )
}

const starterFrontend = componentFromTemplate(
  'web-frontend',
  {
    id: 'frontend',
    name: 'React Frontend',
    technology: 'React',
    position: {
      x: -3,
      y: 0.6,
      z: 0,
    },
  },
)

const starterBackend = componentFromTemplate(
  'api-service',
  {
    id: 'backend',
    name: 'FastAPI Backend',
    technology: 'FastAPI',
    position: {
      x: 0,
      y: 0.6,
      z: 0,
    },
  },
)

const starterDatabase = componentFromTemplate(
  'relational-database',
  {
    id: 'database',
    name: 'PostgreSQL Database',
    technology: 'PostgreSQL',
    position: {
      x: 3,
      y: 0.6,
      z: 0,
    },
  },
)

const starterModel = {
  name: 'ArchVision AI Demo',
  description: '',
  components: [
    starterFrontend,
    starterBackend,
    starterDatabase,
  ].filter(Boolean),
  connections: [
    normalizeConnection({
      id: 'connection-frontend-backend',
      templateId: 'rest-api',
      source: 'frontend',
      target: 'backend',
      label: 'REST API',
      protocol: 'HTTPS',
    }),
    normalizeConnection({
      id: 'connection-backend-database',
      templateId: 'database-access',
      source: 'backend',
      target: 'database',
      label: 'Database Access',
      protocol: 'PostgreSQL',
    }),
  ],
}

export const useArchitectureStore = create(
  (set, get) => ({
    model: starterModel,
    projectName: starterModel.name,

    projects: [],
    selectedProjectId: null,
    isProjectManagerOpen: false,
    openedProjectId: null,
    isProjectsLoading: false,
    projectsError: null,
    projectsLastRefreshedAt: null,

    selectedId: null,
    selectedConnectionId: null,

    sidebarTab: 'components',
    activeComponentTemplateId: null,
    activeConnectionTemplateId: null,

    isDraggingComponent: false,

    connectionSourceId: null,
    connectionTargetIds: [],
    isConnectionBuilderOpen: false,

    setModel: (model) =>
      set({
        model: {
          name:
            model?.name ||
            'Untitled Architecture',
          description:
            model?.description || '',
          components: Array.isArray(
            model?.components,
          )
            ? model.components.map(
                normalizeComponent,
              )
            : [],
          connections: Array.isArray(
            model?.connections,
          )
            ? model.connections.map(
                normalizeConnection,
              )
            : [],
        },
        selectedId: null,
        selectedConnectionId: null,
        activeComponentTemplateId: null,
        activeConnectionTemplateId: null,
        connectionSourceId: null,
        connectionTargetIds: [],
        isConnectionBuilderOpen: false,
        isDraggingComponent: false,
        projectName:
          model?.name ||
          'Untitled Architecture',
      }),

    resetModel: () =>
      set({
        model: {
          ...structuredClone(starterModel),
          name: 'Untitled Architecture',
        },

        projectName: 'Untitled Architecture',

        selectedId: null,
        selectedConnectionId: null,

        activeComponentTemplateId: null,
        activeConnectionTemplateId: null,

        connectionSourceId: null,
        connectionTargetIds: [],

        isConnectionBuilderOpen: false,
        isDraggingComponent: false,

        selectedProjectId: null,
        openedProjectId: null,
      }),

      startNewProject: () => {
        get().resetModel()

        set({
          isProjectManagerOpen: false,
          projectsError: null,
        })

        return {
          success: true,
        }
      },
    /*
     * Apply an AI-generated architecture proposal after
     * the user explicitly approves the proposed changes.
     */
    applyArchitectureProposal: (proposal) => {
      if (!proposal || typeof proposal !== 'object') {
        return {
          success: false,
          error: 'A valid architecture proposal is required.',
        }
      }

      const proposedComponents = Array.isArray(proposal.components)
        ? proposal.components
        : []

      const proposedConnections = Array.isArray(proposal.connections)
        ? proposal.connections
        : []

      let appliedModel = null

      set((state) => {
        const currentComponentsById = new Map(
          state.model.components.map((component) => [component.id, component]),
        )

        const normalizedComponents = proposedComponents.map((component) => {
          const existing = currentComponentsById.get(component.id)

          return normalizeComponent({
            ...existing,
            ...component,
            position: existing?.position || component.position,
          })
        })

        const componentIds = new Set(
          normalizedComponents.map((component) => component.id),
        )

        const normalizedConnections = proposedConnections
          .map(normalizeConnection)
          .filter(
            (connection) =>
              componentIds.has(connection.source) &&
              componentIds.has(connection.target) &&
              connection.source !== connection.target,
          )

        const selectedId =
          state.selectedId && componentIds.has(state.selectedId)
            ? state.selectedId
            : null

        const selectedConnectionId =
          state.selectedConnectionId &&
          normalizedConnections.some(
            (connection) =>
              connection.id === state.selectedConnectionId,
          )
            ? state.selectedConnectionId
            : null

        appliedModel = {
          name:
            proposal.name ||
            state.model.name ||
            'Untitled Architecture',
          description:
            proposal.description ??
            state.model.description ??
            '',
          components: normalizedComponents,
          connections: normalizedConnections,
        }

        return {
          model: appliedModel,
          projectName: appliedModel.name,
          selectedId,
          selectedConnectionId,
          activeComponentTemplateId: null,
          activeConnectionTemplateId: null,
          connectionSourceId: null,
          connectionTargetIds: [],
          isConnectionBuilderOpen: false,
          isDraggingComponent: false,
        }
      })

      return {
        success: true,
        model: appliedModel,
      }
    },

    /*
     * Project management
     */
    setProjectName: (projectName) => {
      const normalizedName = String(
        projectName ?? '',
      )

      set((state) => ({
        projectName: normalizedName,
        model: {
          ...state.model,
          name: normalizedName,
        },
      }))
    },

    openProjectManager: () => {
      set({
        isProjectManagerOpen: true,
      })

      return get().refreshProjects()
    },

    closeProjectManager: () =>
      set({
        isProjectManagerOpen: false,
        projectsError: null,
      }),

    selectProject: (projectId) => {
      const normalizedProjectId =
        projectId == null
          ? null
          : String(projectId)

      if (normalizedProjectId === null) {
        set({
          selectedProjectId: null,
        })

        return {
          success: true,
          project: null,
        }
      }

      const project = get().projects.find(
        (candidate) =>
          candidate.id ===
          normalizedProjectId,
      )

      if (!project) {
        return {
          success: false,
          error:
            'The selected project is not available.',
        }
      }

      set({
        selectedProjectId: project.id,
      })

      return {
        success: true,
        project,
      }
    },

    clearProjectSelection: () =>
      set({
        selectedProjectId: null,
      }),

    setOpenedProjectId: (projectId) =>
      set({
        openedProjectId:
          projectId == null
            ? null
            : String(projectId),
      }),

    clearOpenedProjectId: () =>
      set({
        openedProjectId: null,
      }),

    refreshProjects: async () => {
      set({
        isProjectsLoading: true,
        projectsError: null,
      })

      try {
        const projects =
          await getProjectSummaries()

        const selectedProjectStillExists =
          projects.some(
            (project) =>
              project.id ===
              get().selectedProjectId,
          )

        set({
          projects,
          selectedProjectId:
            selectedProjectStillExists
              ? get().selectedProjectId
              : null,
          isProjectsLoading: false,
          projectsError: null,
          projectsLastRefreshedAt:
            new Date().toISOString(),
        })

        return {
          success: true,
          projects,
        }
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : 'Unable to retrieve the project list.'

        set({
          isProjectsLoading: false,
          projectsError: message,
        })

        return {
          success: false,
          error: message,
          projects: [],
        }
      }
    },

    /*
     * Selection
     */
    select: (id) =>
      set({
        selectedId: id,
        selectedConnectionId: null,
      }),

    clearSelection: () =>
      set({
        selectedId: null,
        selectedConnectionId: null,
      }),

    selectConnection: (id) =>
      set({
        selectedConnectionId: id,
        selectedId: null,
      }),

    clearConnectionSelection: () =>
      set({
        selectedConnectionId: null,
      }),

    /*
     * Sidebar
     */
    setSidebarTab: (tab) => {
      if (
        ![
          'components',
          'connections',
        ].includes(tab)
      ) {
        return
      }

      set({
        sidebarTab: tab,

        activeComponentTemplateId:
          tab === 'components'
            ? get()
                .activeComponentTemplateId
            : null,

        activeConnectionTemplateId:
          tab === 'connections'
            ? get()
                .activeConnectionTemplateId
            : null,

        connectionSourceId:
          tab === 'connections'
            ? get().connectionSourceId
            : null,

        connectionTargetIds:
          tab === 'connections'
            ? get().connectionTargetIds
            : [],

        isConnectionBuilderOpen:
          tab === 'connections'
            ? get()
                .isConnectionBuilderOpen
            : false,
      })
    },

    toggleComponentPlacement: (
      templateId,
    ) =>
      set((state) => ({
        sidebarTab: 'components',

        activeComponentTemplateId:
          state.activeComponentTemplateId ===
          templateId
            ? null
            : templateId,

        activeConnectionTemplateId: null,

        selectedId: null,
        selectedConnectionId: null,

        connectionSourceId: null,
        connectionTargetIds: [],
        isConnectionBuilderOpen: false,
      })),

    clearComponentPlacement: () =>
      set({
        activeComponentTemplateId: null,
      }),

    toggleConnectionTemplate: (
      templateId,
    ) =>
      set((state) => {
        const isDeselecting =
          state.activeConnectionTemplateId ===
          templateId

        return {
          sidebarTab: 'connections',

          activeConnectionTemplateId:
            isDeselecting
              ? null
              : templateId,

          activeComponentTemplateId: null,

          selectedId: null,
          selectedConnectionId: null,

          connectionSourceId: null,
          connectionTargetIds: [],
          isConnectionBuilderOpen: false,
        }
      }),

    clearConnectionTemplate: () =>
      set({
        activeConnectionTemplateId: null,
        connectionSourceId: null,
        connectionTargetIds: [],
        isConnectionBuilderOpen: false,
      }),

    setDraggingComponent: (
      isDraggingComponent,
    ) =>
      set({
        isDraggingComponent,
      }),

    /*
     * Component CRUD
     */
    addComponent: (component) => {
      const normalizedComponent =
        normalizeComponent(component)

      set((state) => ({
        model: {
          ...state.model,
          components: [
            ...state.model.components,
            normalizedComponent,
          ],
        },
      }))

      return {
        success: true,
        component: normalizedComponent,
      }
    },

    placeComponent: (
      template,
      position,
    ) => {
      if (!template || !position) {
        return {
          success: false,
          error:
            'A component template and position are required.',
        }
      }

      const component = normalizeComponent({
        id: createComponentId(
          template.type || 'component',
        ),
        templateId: template.id,
        category: template.category,
        type: template.type,
        name: template.name,
        technology: template.technology,
        description: template.description,
        color: template.color,
        position,
        metadata: {},
      })

      set((state) => ({
        model: {
          ...state.model,
          components: [
            ...state.model.components,
            component,
          ],
        },
        selectedId: component.id,
        selectedConnectionId: null,
      }))

      return {
        success: true,
        component,
      }
    },

    updateComponent: (id, updates) => {
      const existingComponent =
        get().model.components.find(
          (component) =>
            component.id === id,
        )

      if (!existingComponent) {
        return {
          success: false,
          error:
            'The component does not exist.',
        }
      }

      const updatedComponent =
        normalizeComponent({
          ...existingComponent,
          ...updates,
          id: existingComponent.id,

          position: updates.position
            ? {
                ...existingComponent.position,
                ...updates.position,
              }
            : existingComponent.position,

          metadata: updates.metadata
            ? {
                ...existingComponent.metadata,
                ...updates.metadata,
              }
            : existingComponent.metadata,
        })

      set((state) => ({
        model: {
          ...state.model,
          components:
            state.model.components.map(
              (component) =>
                component.id === id
                  ? updatedComponent
                  : component,
            ),
        },
      }))

      return {
        success: true,
        component: updatedComponent,
      }
    },

    moveComponent: (id, position) => {
      const existingComponent =
        get().model.components.find(
          (component) =>
            component.id === id,
        )

      if (!existingComponent) {
        return {
          success: false,
          error:
            'The component does not exist.',
        }
      }

      const normalizedPosition = {
        x: numberOrFallback(
          position?.x,
          existingComponent.position.x,
        ),
        y: numberOrFallback(
          position?.y,
          existingComponent.position.y,
        ),
        z: numberOrFallback(
          position?.z,
          existingComponent.position.z,
        ),
      }

      set((state) => ({
        model: {
          ...state.model,
          components:
            state.model.components.map(
              (component) =>
                component.id === id
                  ? {
                      ...component,
                      position:
                        normalizedPosition,
                    }
                  : component,
            ),
        },
      }))

      return {
        success: true,
        position: normalizedPosition,
      }
    },

    removeComponent: (id) =>
      set((state) => {
        const removedConnectionIds =
          state.model.connections
            .filter(
              (connection) =>
                connection.source === id ||
                connection.target === id,
            )
            .map(
              (connection) =>
                connection.id,
            )

        const sourceWasRemoved =
          state.connectionSourceId === id

        return {
          model: {
            ...state.model,

            components:
              state.model.components.filter(
                (component) =>
                  component.id !== id,
              ),

            connections:
              state.model.connections.filter(
                (connection) =>
                  connection.source !== id &&
                  connection.target !== id,
              ),
          },

          selectedId:
            state.selectedId === id
              ? null
              : state.selectedId,

          selectedConnectionId:
            removedConnectionIds.includes(
              state.selectedConnectionId,
            )
              ? null
              : state.selectedConnectionId,

          connectionSourceId:
            sourceWasRemoved
              ? null
              : state.connectionSourceId,

          connectionTargetIds:
            state.connectionTargetIds.filter(
              (targetId) =>
                targetId !== id,
            ),

          isConnectionBuilderOpen:
            sourceWasRemoved
              ? false
              : state.isConnectionBuilderOpen,
        }
      }),

    /*
     * Connection builder
     */
    beginConnection: (sourceId) => {
      const state = get()

      if (
        !state.activeConnectionTemplateId
      ) {
        return {
          success: false,
          error:
            'Select a connection type first.',
        }
      }

      const sourceExists =
        state.model.components.some(
          (component) =>
            component.id === sourceId,
        )

      if (!sourceExists) {
        return {
          success: false,
          error:
            'The source component does not exist.',
        }
      }

      set({
        connectionSourceId: sourceId,
        connectionTargetIds: [],
        isConnectionBuilderOpen: true,
        selectedId: sourceId,
        selectedConnectionId: null,
      })

      return {
        success: true,
      }
    },

    toggleConnectionTarget: (
      targetId,
    ) => {
      const state = get()

      if (!state.connectionSourceId) {
        return {
          success: false,
          error:
            'Select a source component first.',
        }
      }

      if (
        targetId ===
        state.connectionSourceId
      ) {
        return {
          success: false,
          error:
            'A component cannot connect to itself.',
        }
      }

      const targetExists =
        state.model.components.some(
          (component) =>
            component.id === targetId,
        )

      if (!targetExists) {
        return {
          success: false,
          error:
            'The target component does not exist.',
        }
      }

      set((currentState) => ({
        connectionTargetIds:
          currentState.connectionTargetIds.includes(
            targetId,
          )
            ? currentState.connectionTargetIds.filter(
                (id) => id !== targetId,
              )
            : [
                ...currentState.connectionTargetIds,
                targetId,
              ],
      }))

      return {
        success: true,
      }
    },

    addConnectionTarget: (targetId) =>
      set((state) => ({
        connectionTargetIds:
          targetId !==
            state.connectionSourceId &&
          !state.connectionTargetIds.includes(
            targetId,
          )
            ? [
                ...state.connectionTargetIds,
                targetId,
              ]
            : state.connectionTargetIds,
      })),

    cancelConnectionBuilder: () =>
      set({
        connectionSourceId: null,
        connectionTargetIds: [],
        isConnectionBuilderOpen: false,
        selectedId: null,
      }),

    completeConnectionBuilder: (
      connectionTemplate,
      overrides = {},
    ) => {
      const state = get()

      if (!state.connectionSourceId) {
        return {
          success: false,
          error:
            'A source component is required.',
        }
      }

      if (
        state.connectionTargetIds.length ===
        0
      ) {
        return {
          success: false,
          error:
            'Select at least one target component.',
        }
      }

      if (!connectionTemplate) {
        return {
          success: false,
          error:
            'A connection template is required.',
        }
      }

      const createdConnections = []
      const errors = []

      state.connectionTargetIds.forEach(
        (targetId) => {
          const result = get().addConnection({
            templateId:
              connectionTemplate.id,
            source:
              state.connectionSourceId,
            target: targetId,
            connectionType:
              overrides.connectionType ||
              connectionTemplate.connectionType,
            protocol:
              overrides.protocol ??
              connectionTemplate.protocol ??
              '',
            direction:
              overrides.direction ||
              'unidirectional',
            label:
              overrides.label ||
              connectionTemplate.name ||
              '',
            metadata:
              overrides.metadata || {},
          })

          if (result.success) {
            createdConnections.push(
              result.connection,
            )
          } else {
            errors.push(result.error)
          }
        },
      )

      set({
        connectionSourceId: null,
        connectionTargetIds: [],
        isConnectionBuilderOpen: false,
        selectedId: null,
        selectedConnectionId:
          createdConnections.at(-1)?.id ||
          null,
      })

      return {
        success:
          createdConnections.length > 0,
        createdConnections,
        errors,
      }
    },

    /*
     * Connection CRUD
     */
    addConnection: ({
      templateId = '',
      source,
      target,
      connectionType = 'dependency',
      protocol = '',
      direction = 'unidirectional',
      label = '',
      metadata = {},
    }) => {
      const state = get()

      if (!source || !target) {
        return {
          success: false,
          error:
            'A source and target component are required.',
        }
      }

      if (source === target) {
        return {
          success: false,
          error:
            'A component cannot be connected to itself.',
        }
      }

      const sourceExists =
        state.model.components.some(
          (component) =>
            component.id === source,
        )

      const targetExists =
        state.model.components.some(
          (component) =>
            component.id === target,
        )

      if (
        !sourceExists ||
        !targetExists
      ) {
        return {
          success: false,
          error:
            'The source or target component does not exist.',
        }
      }

      const normalizedConnection =
        normalizeConnection({
          templateId,
          source,
          target,
          connectionType,
          protocol,
          direction,
          label,
          metadata,
        })

      if (
        connectionExists(
          state.model.connections,
          normalizedConnection,
        )
      ) {
        return {
          success: false,
          error:
            'An identical connection already exists.',
        }
      }

      set((currentState) => ({
        model: {
          ...currentState.model,
          connections: [
            ...currentState.model.connections,
            normalizedConnection,
          ],
        },

        selectedConnectionId:
          normalizedConnection.id,

        selectedId: null,
      }))

      return {
        success: true,
        connection:
          normalizedConnection,
      }
    },

    updateConnection: (id, updates) => {
      const state = get()

      const existingConnection =
        state.model.connections.find(
          (connection) =>
            connection.id === id,
        )

      if (!existingConnection) {
        return {
          success: false,
          error:
            'The connection does not exist.',
        }
      }

      const updatedConnection =
        normalizeConnection({
          ...existingConnection,
          ...updates,
          id: existingConnection.id,

          metadata: updates.metadata
            ? {
                ...existingConnection.metadata,
                ...updates.metadata,
              }
            : existingConnection.metadata,
        })

      if (
        updatedConnection.source ===
        updatedConnection.target
      ) {
        return {
          success: false,
          error:
            'A component cannot be connected to itself.',
        }
      }

      const sourceExists =
        state.model.components.some(
          (component) =>
            component.id ===
            updatedConnection.source,
        )

      const targetExists =
        state.model.components.some(
          (component) =>
            component.id ===
            updatedConnection.target,
        )

      if (
        !sourceExists ||
        !targetExists
      ) {
        return {
          success: false,
          error:
            'The source or target component does not exist.',
        }
      }

      if (
        connectionExists(
          state.model.connections,
          updatedConnection,
          id,
        )
      ) {
        return {
          success: false,
          error:
            'An identical connection already exists.',
        }
      }

      set((currentState) => ({
        model: {
          ...currentState.model,

          connections:
            currentState.model.connections.map(
              (connection) =>
                connection.id === id
                  ? updatedConnection
                  : connection,
            ),
        },
      }))

      return {
        success: true,
        connection: updatedConnection,
      }
    },

    removeConnection: (id) =>
      set((state) => ({
        model: {
          ...state.model,

          connections:
            state.model.connections.filter(
              (connection) =>
                connection.id !== id,
            ),
        },

        selectedConnectionId:
          state.selectedConnectionId === id
            ? null
            : state.selectedConnectionId,
      })),

    getComponent: (id) =>
      get().model.components.find(
        (component) =>
          component.id === id,
      ),

    getConnection: (id) =>
      get().model.connections.find(
        (connection) =>
          connection.id === id,
      ),

    serializeModelForApi: () => {
      const { model } = get()

      return {
        name: model.name,
        description: model.description,

        components:
          model.components.map(
            (component) => ({
              id: component.id,
              category:
                component.category,
              type: component.type,
              name: component.name,
              technology:
                component.technology,
              description:
                component.description,
              color: component.color,
              icon: component.icon,
              position:
                component.position,
              metadata:
                component.metadata,
            }),
          ),

        connections:
          model.connections.map(
            (connection) => ({
              id: connection.id,
              source:
                connection.source,
              target:
                connection.target,
              connection_type:
                connection.connectionType,
              protocol:
                connection.protocol,
              direction:
                connection.direction,
              label:
                connection.label,
              metadata: {
                ...connection.metadata,
                template_id:
                  connection.templateId,
              },
            }),
          ),
      }
    },
  }),
)