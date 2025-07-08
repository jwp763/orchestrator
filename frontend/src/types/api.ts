// API Request/Response Types based on FastAPI backend models

export interface PlannerConfig {
  provider: 'openai' | 'anthropic' | 'gemini' | 'xai'
  model: string
  max_retries: number
  create_milestones: boolean
  max_milestones: number
  temperature?: number
  max_tokens?: number
}

export interface PlannerRequest {
  project_idea: string
  config: PlannerConfig
}

export interface ProjectData {
  id: string
  title: string
  description: string
  status: 'active' | 'completed' | 'on_hold'
  priority: 'low' | 'medium' | 'high'
  estimated_hours: number
  created_at: string
  updated_at: string
}

export interface TaskData {
  id: string
  project_id: string
  title: string
  description: string
  status: 'pending' | 'in_progress' | 'completed'
  priority: 'low' | 'medium' | 'high'
  estimated_hours: number
  parent_task_id?: string
  created_at: string
  updated_at: string
}

export interface PlannerResponse {
  success: boolean
  project: ProjectData
  tasks: TaskData[]
  message?: string
}

export interface ProviderModel {
  name: string
  description: string
  max_tokens: number
  supports_tools: boolean
}

export interface Provider {
  name: string
  display_name: string
  models: ProviderModel[]
  default_model: string
}

export interface ProvidersResponse {
  providers: Provider[]
}

export interface ConfigResponse {
  default_config: PlannerConfig
  providers: Provider[]
}

export interface ErrorResponse {
  error: string
  details?: string
  code?: string
}

// Local Storage Types
export interface UserPreferences {
  lastConfig: PlannerConfig
  theme: 'light' | 'dark'
  autoSave: boolean
}

export interface ProjectHistory {
  id: string
  timestamp: string
  project_idea: string
  config: PlannerConfig
  result: PlannerResponse
}