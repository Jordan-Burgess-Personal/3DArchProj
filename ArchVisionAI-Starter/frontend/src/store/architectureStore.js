import { create } from 'zustand'

const starterModel = {
  name: 'ArchVision AI Demo',
  components: [
    { id: 'frontend', type: 'frontend', name: 'React Frontend', technology: 'React', position: { x: -3, y: 0, z: 0 } },
    { id: 'backend', type: 'backend', name: 'FastAPI Backend', technology: 'FastAPI', position: { x: 0, y: 0, z: 0 } },
    { id: 'database', type: 'database', name: 'PostgreSQL Database', technology: 'PostgreSQL', position: { x: 3, y: 0, z: 0 } },
  ],
  connections: [
    { id: 'c1', source: 'frontend', target: 'backend', label: 'API calls' },
    { id: 'c2', source: 'backend', target: 'database', label: 'Data access' },
  ],
}

export const useArchitectureStore = create((set, get) => ({
  model: starterModel,
  selectedId: null,

  setModel: (model) => set({ model }),

  select: (id) => set({ selectedId: id }),
  clearSelection: () => set({ selectedId: null }),

  addComponent: (component) => set((state) => ({
    model: { ...state.model, components: [...state.model.components, component] },
  })),

  updateComponent: (id, updates) => set((state) => ({
    model: {
      ...state.model,
      components: state.model.components.map((c) =>
        c.id === id ? { ...c, ...updates } : c
      ),
    },
  })),

  moveComponent: (id, position) => set((state) => ({
    model: {
      ...state.model,
      components: state.model.components.map((c) =>
        c.id === id ? { ...c, position } : c
      ),
    },
  })),

  removeComponent: (id) => set((state) => ({
    model: {
      ...state.model,
      components: state.model.components.filter((c) => c.id !== id),
      connections: state.model.connections.filter(
        (conn) => conn.source !== id && conn.target !== id
      ),
    },
    selectedId: state.selectedId === id ? null : state.selectedId,
  })),

  addConnection: (source, target, label = '') => set((state) => ({
    model: {
      ...state.model,
      connections: [
        ...state.model.connections,
        { id: `c-${Date.now()}`, source, target, label },
      ],
    },
  })),

  removeConnection: (id) => set((state) => ({
    model: {
      ...state.model,
      connections: state.model.connections.filter((c) => c.id !== id),
    },
  })),

  getComponent: (id) => get().model.components.find((c) => c.id === id),
}))