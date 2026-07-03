import { Plus, Box, Database, Server } from 'lucide-react'
import { useArchitectureStore } from '../store/architectureStore'

export default function Sidebar() {
  const addComponent = useArchitectureStore((s) => s.addComponent)
  const createNode = (type) => {
    const id = `${type}-${Date.now()}`
    addComponent({ id, type, name: `${type} node`, technology: '', position: { x: Math.random() * 4 - 2, y: 0, z: Math.random() * 4 - 2 } })
  }
  return (
    <aside className="w-72 bg-slate-950/90 border-r border-slate-800 p-4 space-y-4">
      <h2 className="text-xl font-bold">Components</h2>
      <button onClick={() => createNode('frontend')} className="w-full p-3 rounded-lg bg-slate-800 flex gap-2"><Box /> Frontend</button>
      <button onClick={() => createNode('backend')} className="w-full p-3 rounded-lg bg-slate-800 flex gap-2"><Server /> Backend</button>
      <button onClick={() => createNode('database')} className="w-full p-3 rounded-lg bg-slate-800 flex gap-2"><Database /> Database</button>
      <button onClick={() => createNode('service')} className="w-full p-3 rounded-lg bg-indigo-600 flex gap-2"><Plus /> Custom Component</button>
    </aside>
  )
}
