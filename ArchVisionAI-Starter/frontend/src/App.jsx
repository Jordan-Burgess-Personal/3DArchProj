import { Route, Routes } from 'react-router-dom'
import ApplicationLayout from './layouts/ApplicationLayout'
import Dashboard from './pages/Dashboard'
import ArchitectureCanvas from './three/ArchitectureCanvas'
import Sidebar from './components/Sidebar'
import AIAssistant from './components/AIAssistant'
import SelectedNodePanel from './components/SelectedNodePanel'

function Workspace() {
  return (
    <div className="flex h-full min-h-0">
      <Sidebar />

      <section className="relative min-w-0 flex-1">
        <ArchitectureCanvas />
        <SelectedNodePanel />
      </section>

      <AIAssistant />
    </div>
  )
}

function NotFound() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
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
      <Route element={<ApplicationLayout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspace" element={<Workspace />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  )
}