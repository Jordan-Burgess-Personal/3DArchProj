import { create } from 'zustand'

const starterModel = {
  name: 'ArchVision AI Demo',
  description: '',
  components: [
    {
      id: 'frontend',
      category: 'client',
      type: 'frontend',
      name: 'React Frontend',
      technology: 'React',
      description: 'Browser-based user interface.',
      color: '#0d9488',
      icon: '',
      position: { x: -3, y: 0.6, z: 0 },
      metadata: {},
    },
    {
      id: 'backend',
      category: 'application',
      type: 'backend',
      name: 'FastAPI Backend',
      technology: 'FastAPI',
      description: 'Backend API and business-logic service.',
      color: '#1d4ed8',
      icon: '',
      position: { x: 0, y: 0.6, z: 0 },
      metadata: {},
    },
    {
      id: 'database',
      category: 'data',
      type: 'database',
      name: 'PostgreSQL Database',
      technology: 'PostgreSQL',
      description: 'Relational project data storage.',
      color: '#6d28d9',
      icon: '',
      position: { x: 3, y: 0.6, z: 0 },
      metadata: {},
    },
  ],
  connections: [
    {
      id: 'connection-frontend-backend',
      source: 'frontend',
      target: 'backend',
      connectionType: 'api-call',
      protocol: 'HTTPS',
      direction: 'unidirectional',
      label: 'API requests',
      metadata: {},
    },
    {
      id: 'connection-backend-database',
      source: 'backend',
      target: 'database',
      connectionType: 'data-access',
      protocol: 'PostgreSQL',
      direction: 'unidirectional',
      label: 'Reads and writes data',
      metadata: {},
    },
  ],
}

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

function normalizeComponent(component) {
  return {
    id:
      component.id ||
      createComponentId(component.type || 'component'),
    category: component.category || 'custom',
    type: component.type || 'custom',
    name: component.name || 'Untitled Component',
    technology: component.technology || '',
    description: component.description || '',
    color: component.color || '#475569',
    icon: component.icon || '',
    position: {
      x: Number(component.position?.x) || 0,
      y: Number(component.position?.y) || 0.6,
      z: Number(component.position?.z) || 0,
    },
    metadata: component.metadata || {},
  }
}

function normalizeConnection(connection) {
  return {
    id: connection.id || createConnectionId(),
    source: connection.source,
    target: connection.target,
    connectionType:
      connection.connectionType ||
      connection.connection_type ||
      'dependency',
    protocol: connection.protocol || '',
    direction:
      connection.direction || 'unidirectional',
    label: connection.label || '',
    metadata: connection.metadata || {},
  }
}

function connectionExists(
  connections,
  {
    source,
    target,
    connectionType,
    protocol,
    label,
  },
) {
  return connections.some(
    (connection) =>
      connection.source === source &&
      connection.target === target &&
      connection.connectionType === connectionType &&
      connection.protocol === protocol &&
      connection.label === label,
  )
}

export const useArchitectureStore = create(
  (set, get) => ({
    model: starterModel,

    selectedId: null,
    selectedConnectionId: null,

    sidebarTab: 'components',
    activeComponentTemplateId: null,
    activeConnectionTemplateId: null,
    isDraggingComponent: false,

    /*
     * Replace the entire architecture model.
     * Used when loading a saved project or applying
     * an AI-generated architecture.
     */
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
        isDraggingComponent: false,
      }),

    /*
     * Component selection
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

    /*
     * Connection selection
     */
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
     * Sidebar tabs and tool selection
     */
    setSidebarTab: (tab) => {
      if (
        !['components', 'connections'].includes(tab)
      ) {
        return
      }

      set({
        sidebarTab: tab,
        activeComponentTemplateId:
          tab === 'components'
            ? get().activeComponentTemplateId
            : null,
        activeConnectionTemplateId:
          tab === 'connections'
            ? get().activeConnectionTemplateId
            : null,
      })
    },

    toggleComponentPlacement: (templateId) =>
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
      })),

    clearComponentPlacement: () =>
      set({
        activeComponentTemplateId: null,
      }),

    toggleConnectionTemplate: (templateId) =>
      set((state) => ({
        sidebarTab: 'connections',
        activeConnectionTemplateId:
          state.activeConnectionTemplateId ===
          templateId
            ? null
            : templateId,
        activeComponentTemplateId: null,
        selectedId: null,
        selectedConnectionId: null,
      })),

    clearConnectionTemplate: () =>
      set({
        activeConnectionTemplateId: null,
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

      const component =
        normalizeComponent({
          id: createComponentId(
            template.type || 'component',
          ),
          category:
            template.category || 'custom',
          type:
            template.type || 'custom',
          name:
            template.name ||
            'Untitled Component',
          technology:
            template.technology || '',
          description:
            template.description || '',
          color:
            template.color || '#475569',
          icon:
            template.iconName || '',
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
      const state = get()

      const existingComponent =
        state.model.components.find(
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

      set((currentState) => ({
        model: {
          ...currentState.model,
          components:
            currentState.model.components.map(
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
      const state = get()

      const existingComponent =
        state.model.components.find(
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
        x:
          Number(position?.x) ||
          0,
        y:
          Number(position?.y) ||
          0.6,
        z:
          Number(position?.z) ||
          0,
      }

      set((currentState) => ({
        model: {
          ...currentState.model,
          components:
            currentState.model.components.map(
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
        }
      }),

    /*
     * Connection CRUD
     */
    addConnection: ({
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
          source,
          target,
          connectionType,
          protocol,
          direction,
          label,
          metadata,
        })

      const duplicateExists =
        connectionExists(
          state.model.connections,
          normalizedConnection,
        )

      if (duplicateExists) {
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

      const duplicateExists =
        state.model.connections
          .filter(
            (connection) =>
              connection.id !== id,
          )
          .some(
            (connection) =>
              connection.source ===
                updatedConnection.source &&
              connection.target ===
                updatedConnection.target &&
              connection.connectionType ===
                updatedConnection.connectionType &&
              connection.protocol ===
                updatedConnection.protocol &&
              connection.label ===
                updatedConnection.label,
          )

      if (duplicateExists) {
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

    /*
     * Lookup helpers
     */
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

    getConnectionsForComponent: (
      componentId,
    ) =>
      get().model.connections.filter(
        (connection) =>
          connection.source ===
            componentId ||
          connection.target ===
            componentId,
      ),

    getOutgoingConnections: (
      componentId,
    ) =>
      get().model.connections.filter(
        (connection) =>
          connection.source ===
          componentId,
      ),

    getIncomingConnections: (
      componentId,
    ) =>
      get().model.connections.filter(
        (connection) =>
          connection.target ===
          componentId,
      ),

    /*
     * Convert frontend camelCase properties into
     * the backend API's expected naming.
     */
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
              metadata:
                connection.metadata,
            }),
          ),
      }
    },
  }),
)