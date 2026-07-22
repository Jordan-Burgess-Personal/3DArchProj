import { Download } from 'lucide-react'

import Sidebar from './components/Sidebar'
import AIAssistant from './components/AIAssistant'
import SelectedNodePanel from './components/SelectedNodePanel'
import ConnectionBuilderPanel from './components/ConnectionBuilderPanel'
import ConnectionEditorPanel from './components/ConnectionEditorPanel'
import ArchitectureCanvas from './three/ArchitectureCanvas'

export default function App() {
  return (
    <div className="flex h-screen w-screen flex-col overflow-hidden bg-slate-950 text-white">

      {/* Header */}
      <header className="flex h-14 items-center justify-between border-b border-slate-800 bg-slate-950 px-6">

        <h1 className="text-2xl font-bold tracking-tight">
          ArchVision <span className="text-indigo-400">AI</span>
        </h1>

        <button
          className="
            flex items-center gap-2
            rounded-lg
            bg-indigo-600
            px-5
            py-2
            text-sm
            font-medium
            transition
            hover:bg-indigo-500
          "
        >
          <Download size={18} />
          Export Project
        </button>

      </header>

      {/* Main Workspace */}
      <main className="flex flex-1 overflow-hidden">

        {/* Left Sidebar */}
        <aside className="w-64 border-r border-slate-800 bg-slate-950">
          <Sidebar />
        </aside>

        {/* 3D Canvas */}
        <section className="relative flex-1 overflow-hidden">

          <ArchitectureCanvas />

          {/* Floating Editors */}

          <SelectedNodePanel />

          <ConnectionBuilderPanel />

          <ConnectionEditorPanel />

        </section>

        {/* Right AI Panel */}
        <aside className="w-80 border-l border-slate-800 bg-slate-950">
          <AIAssistant />
        </aside>

      </main>

    </div>
  )
}