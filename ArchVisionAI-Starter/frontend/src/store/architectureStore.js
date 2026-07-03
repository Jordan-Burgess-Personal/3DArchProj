import { create } from 'zustand'

const starterModel = {
  name: 'ArchVision',
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

export const useArchitectureStore = create((set) => ({
  model: starterModel,
  selectedId: null,
  setModel: (model) => set({ model }),
  select: (id) => set({ selectedId: id }),
  addComponent: (component) => set((state) => ({
    model: { ...state.model, components: [...state.model.components, component] }
  })),
}))
