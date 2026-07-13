import { Route, Routes } from 'react-router-dom'
import ArchitectureCanvas from './three/ArchitectureCanvas'
import Sidebar from './components/Sidebar'
import AIAssistant from './components/AIAssistant'
import SelectedNodePanel from './components/SelectedNodePanel'

function Workspace() {
  return (
    <div className="h-screen flex flex-col">
      <header className="h-16 border-b border-slate-800 bg-slate-950 flex items-center px-6 justify-between">
        <h1 className="text-2xl font-bold">
          ArchVision <span className="text-indigo-400">AI</span>
        </h1>

        <button className="px-4 py-2 rounded-lg bg-indigo-600">
          Export Project
        </button>
      </header>

      <main className="flex flex-1 min-h-0">
        <Sidebar />

        <section className="flex-1 min-w-0 relative">
          <ArchitectureCanvas />
          <SelectedNodePanel />
        </section>

        <AIAssistant />
      </main>
    </div>
  )
}

function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">
      <div className="text-center">
        <h1 className="text-4xl font-bold">404</h1>
        <p className="mt-2 text-slate-400">Page not found</p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Workspace />} />
      <Route path="/workspace" element={<Workspace />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}