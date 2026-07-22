import { useState } from 'react'
import { api } from '../api/client'
import { useArchitectureStore } from '../store/architectureStore'

export default function AIAssistant() {
  const [prompt, setPrompt] = useState('Create a React frontend, FastAPI backend, PostgreSQL database, and OpenAI integration')
  const [suggestions, setSuggestions] = useState([])
  const model = useArchitectureStore((s) => s.model)
  const setModel = useArchitectureStore((s) => s.setModel)

  async function generate() {
    const res = await api.post('/api/ai/generate', { prompt })
    setModel(res.data)
  }

  async function getFeedback() {
    const res = await api.post('/api/ai/feedback', { model })
    setSuggestions(res.data.suggestions)
  }

  return (
    <aside className="flex h-full min-h-0 w-full flex-col overflow-hidden bg-slate-950 p-4 text-white">
      <h2 className="text-xl font-bold text-indigo-300">AI Assistant</h2>
      <textarea value={prompt} onChange={(e) => setPrompt(e.target.value)} className="w-full h-32 p-3 rounded-lg bg-slate-900 border border-slate-700" />
      <button onClick={generate} className="w-full p-3 rounded-lg bg-indigo-600">Generate Model</button>
      <button onClick={getFeedback} className="w-full p-3 rounded-lg bg-slate-800">Get Architecture Feedback</button>
      <ul className="space-y-2 text-sm text-slate-200">
        {suggestions.map((s, i) => <li key={i} className="p-3 bg-slate-900 rounded-lg">{s}</li>)}
      </ul>
    </aside>
  )
}
