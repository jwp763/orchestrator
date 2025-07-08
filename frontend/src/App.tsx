import { useState } from 'react'
import { useLocalStorage } from './hooks/useLocalStorage'
import type { PlannerConfig, UserPreferences } from './types/api'

const DEFAULT_CONFIG: PlannerConfig = {
  provider: 'openai',
  model: 'o3',
  max_retries: 2,
  create_milestones: true,
  max_milestones: 5,
  temperature: 0.7,
  max_tokens: 2000,
}

const DEFAULT_PREFERENCES: UserPreferences = {
  lastConfig: DEFAULT_CONFIG,
  theme: 'light',
  autoSave: true,
}

function App() {
  const [preferences] = useLocalStorage<UserPreferences>(
    'orchestrator-preferences',
    DEFAULT_PREFERENCES
  )
  const [projectIdea, setProjectIdea] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implement project generation logic
    console.log('Generating project for:', projectIdea)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Orchestrator
          </h1>
          <p className="text-xl text-gray-600">
            AI-Powered Project Planning & Task Management
          </p>
        </header>

        <main className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label
                  htmlFor="project-idea"
                  className="block text-sm font-medium text-gray-700 mb-2"
                >
                  Project Idea
                </label>
                <textarea
                  id="project-idea"
                  value={projectIdea}
                  onChange={(e) => setProjectIdea(e.target.value)}
                  placeholder="Describe your project idea here..."
                  className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  rows={6}
                  required
                />
              </div>

              <div className="flex justify-between items-center">
                <div className="text-sm text-gray-500">
                  Using {preferences.lastConfig.provider} - {preferences.lastConfig.model}
                </div>
                <button
                  type="submit"
                  className="bg-primary-600 text-white px-6 py-2 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 transition-colors"
                >
                  Generate Project Plan
                </button>
              </div>
            </form>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
