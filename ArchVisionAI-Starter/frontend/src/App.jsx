import ArchitectureCanvas from './three/ArchitectureCanvas'
import Sidebar from './components/Sidebar'
import AIAssistant from './components/AIAssistant'

export default function App() {
  return (
    <div className="h-screen flex flex-col">
      <header className="h-16 border-b border-slate-800 bg-slate-950 flex items-center px-6 justify-between">
        <h1 className="text-2xl font-bold">ArchVision</h1>
        <button className="px-4 py-2 rounded-lg bg-indigo-600">Export Project</button>
      </header>
      <main className="flex flex-1 min-h-0">
        <Sidebar />
        <section className="flex-1 min-w-0">
          <ArchitectureCanvas />
        </section>
        <AIAssistant />
      </main>
    </div>
  )
}
