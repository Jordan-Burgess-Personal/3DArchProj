import { create } from 'zustand'

const starterModel = {
  name: 'ArchVision AI Demo',
  description: '',
  components: [
    {
      id: 'frontend',
      type: 'frontend',
      name: 'React Frontend',
      technology: 'React',
      position: { x: -3, y: 0, z: 0 },
    },
    {
      id: 'backend',
      type: 'backend',
      name: 'FastAPI Backend',
      technology: 'FastAPI',
      position: { x: 0, y: 0, z: 0 },
    },
    {
      id: 'database',
      type: 'database',
      name: 'PostgreSQL Database',
      technology: 'PostgreSQL',
      position: { x: 3, y: 0, z: 0 },
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
    direction: connection.direction || 'unidirectional',
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

export const useArchitectureStore = create((set, get) => ({
  model: starterModel,

  selectedId: null,
  selectedConnectionId: null,

  /*
   * Replace the entire architecture model.
   * Used when loading a project or applying an AI-generated architecture.
   */
  setModel: (model) =>
    set({
      model: {
        name: model?.name || 'Untitled Architecture',
        description: model?.description || '',
        components: Array.isArray(model?.components)
          ? model.components
          : [],
        connections: Array.isArray(model?.connections)
          ? model.connections.map(normalizeConnection)
          : [],
      },
      selectedId: null,
      selectedConnectionId: null,
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
   * Component CRUD
   */
  addComponent: (component) =>
    set((state) => ({
      model: {
        ...state.model,
        components: [
          ...state.model.components,
          component,
        ],
      },
    })),

  updateComponent: (id, updates) =>
    set((state) => ({
      model: {
        ...state.model,
        components: state.model.components.map(
          (component) =>
            component.id === id
              ? { ...component, ...updates }
              : component,
        ),
      },
    })),

  moveComponent: (id, position) =>
    set((state) => ({
      model: {
        ...state.model,
        components: state.model.components.map(
          (component) =>
            component.id === id
              ? { ...component, position }
              : component,
        ),
      },
    })),

  removeComponent: (id) =>
    set((state) => {
      const removedConnectionIds = state.model.connections
        .filter(
          (connection) =>
            connection.source === id ||
            connection.target === id,
        )
        .map((connection) => connection.id)

      return {
        model: {
          ...state.model,
          components: state.model.components.filter(
            (component) => component.id !== id,
          ),
          connections: state.model.connections.filter(
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

    const sourceExists = state.model.components.some(
      (component) => component.id === source,
    )

    const targetExists = state.model.components.some(
      (component) => component.id === target,
    )

    if (!sourceExists || !targetExists) {
      return {
        success: false,
        error:
          'The source or target component does not exist.',
      }
    }

    const normalizedConnection = normalizeConnection({
      source,
      target,
      connectionType,
      protocol,
      direction,
      label,
      metadata,
    })

    const duplicateExists = connectionExists(
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
      connection: normalizedConnection,
    }
  },

  updateConnection: (id, updates) => {
    const state = get()

    const existingConnection =
      state.model.connections.find(
        (connection) => connection.id === id,
      )

    if (!existingConnection) {
      return {
        success: false,
        error: 'The connection does not exist.',
      }
    }

    const updatedConnection =
      normalizeConnection({
        ...existingConnection,
        ...updates,
        id: existingConnection.id,
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

    const sourceExists = state.model.components.some(
      (component) =>
        component.id === updatedConnection.source,
    )

    const targetExists = state.model.components.some(
      (component) =>
        component.id === updatedConnection.target,
    )

    if (!sourceExists || !targetExists) {
      return {
        success: false,
        error:
          'The source or target component does not exist.',
      }
    }

    const duplicateExists =
      state.model.connections
        .filter(
          (connection) => connection.id !== id,
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
      (component) => component.id === id,
    ),

  getConnection: (id) =>
    get().model.connections.find(
      (connection) => connection.id === id,
    ),

  getConnectionsForComponent: (componentId) =>
    get().model.connections.filter(
      (connection) =>
        connection.source === componentId ||
        connection.target === componentId,
    ),

  getOutgoingConnections: (componentId) =>
    get().model.connections.filter(
      (connection) =>
        connection.source === componentId,
    ),

  getIncomingConnections: (componentId) =>
    get().model.connections.filter(
      (connection) =>
        connection.target === componentId,
    ),

  /*
   * Convert the frontend model to the backend's expected naming.
   * This will be useful later for save-project API requests.
   */
  serializeModelForApi: () => {
    const { model } = get()

    return {
      ...model,
      connections: model.connections.map(
        (connection) => ({
          id: connection.id,
          source: connection.source,
          target: connection.target,
          connection_type:
            connection.connectionType,
          protocol: connection.protocol,
          direction: connection.direction,
          label: connection.label,
          metadata: connection.metadata,
        }),
      ),
    }
  },
}))