import {
  Navigate,
  Route,
  Routes,
} from 'react-router-dom'

import AIAssistant from './components/AIAssistant'
import ConnectionBuilderPanel from './components/ConnectionBuilderPanel'
import ConnectionEditorPanel from './components/ConnectionEditorPanel'
import ProjectManagerModal from './components/projects/ProjectManagerModal'
import SelectedNodePanel from './components/SelectedNodePanel'
import Sidebar from './components/Sidebar'
import ApplicationLayout from './layouts/ApplicationLayout'
import Dashboard from './pages/Dashboard'
import ArchitectureCanvas from './three/ArchitectureCanvas'

function Workspace() {
  return (
    <div className="h-full min-h-0 min-w-0 overflow-hidden bg-slate-950 p-3">
      <div className="flex h-full min-h-0 min-w-0 overflow-hidden rounded-xl border border-slate-700 bg-slate-950 shadow-2xl">
        {/* Component and connection catalog */}
        <div className="box-border min-h-0 w-72 shrink-0 overflow-hidden rounded-l-xl border-r border-slate-700 bg-slate-950">
          <Sidebar />
        </div>

        {/* Three-dimensional workspace */}
        <section className="relative min-h-0 min-w-0 flex-1 overflow-hidden">
          <ArchitectureCanvas />

          <SelectedNodePanel />
          <ConnectionBuilderPanel />
          <ConnectionEditorPanel />
        </section>

        {/* AI assistant */}
        <div className="box-border min-h-0 w-80 shrink-0 overflow-hidden rounded-r-xl border-l border-slate-700 bg-slate-950">
          <AIAssistant />
        </div>
      </div>
    </div>
  )
}

function NotFound() {
  return (
    <div className="flex h-full min-h-0 items-center justify-center bg-slate-950 p-6 text-white">
      <div className="text-center">
        <h1 className="text-5xl font-bold">
          404
        </h1>

        <p className="mt-3 text-slate-400">
          Page not found
        </p>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <>
      <Routes>
        <Route element={<ApplicationLayout />}>
          <Route
            index
            element={
              <Navigate
                to="/dashboard"
                replace
              />
            }
          />

          <Route
            path="/dashboard"
            element={<Dashboard />}
          />

          <Route
            path="/workspace"
            element={<Workspace />}
          />

          <Route
            path="*"
            element={<NotFound />}
          />
        </Route>
      </Routes>

      <ProjectManagerModal />
    </>
  )
}