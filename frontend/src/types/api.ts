// API Request/Response Types based on FastAPI backend models

// Project API Types
export interface ProjectResponse {
  id: string;
  name: string;
  description: string | null;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
  priority: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags: string[];
  due_date: string | null;
  start_date: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
  task_count: number;
  completed_task_count: number;
  motion_project_id: string | null;
  linear_project_id: string | null;
  notion_page_id: string | null;
  gitlab_project_id: string | null;
}

export interface ProjectWithTasksResponse extends ProjectResponse {
  tasks: TaskResponse[];
}

export interface ProjectListResponse {
  projects: ProjectResponse[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ProjectCreateRequest {
  name: string;
  description?: string;
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
  priority?: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags?: string[];
  due_date?: string;
  start_date?: string;
  created_by: string;
  motion_project_id?: string;
  linear_project_id?: string;
  notion_page_id?: string;
  gitlab_project_id?: string;
}

export interface ProjectUpdateRequest {
  name?: string;
  description?: string;
  status?: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
  priority?: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags?: string[];
  due_date?: string;
  start_date?: string;
  motion_project_id?: string;
  linear_project_id?: string;
  notion_page_id?: string;
  gitlab_project_id?: string;
}

// Task API Types
export interface TaskResponse {
  id: string;
  project_id: string;
  parent_id: string | null;
  title: string;
  description: string | null;
  status: 'todo' | 'in_progress' | 'blocked' | 'completed';
  priority: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags: string[];
  estimated_minutes: number | null;
  actual_minutes: number;
  due_date: string | null;
  assignee: string | null;
  depth: number;
  sort_order: number;
  completion_percentage: number;
  dependencies: string[];
  attachments: any[];
  notes: string | null;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
  created_by: string;
  motion_task_id: string | null;
  linear_issue_id: string | null;
  notion_task_id: string | null;
  gitlab_issue_id: string | null;
}

export interface TaskWithSubtasksResponse extends TaskResponse {
  subtasks: TaskResponse[];
}

export interface TaskListResponse {
  tasks: TaskResponse[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface TaskCreateRequest {
  project_id: string;
  parent_id?: string;
  title: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'blocked' | 'completed';
  priority?: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags?: string[];
  estimated_minutes?: number;
  due_date?: string;
  assignee?: string;
  dependencies?: string[];
  metadata?: Record<string, any>;
  created_by: string;
  motion_task_id?: string;
  linear_issue_id?: string;
  notion_task_id?: string;
  gitlab_issue_id?: string;
}

export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  status?: 'todo' | 'in_progress' | 'blocked' | 'completed';
  priority?: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags?: string[];
  estimated_minutes?: number;
  actual_minutes?: number;
  due_date?: string;
  assignee?: string;
  parent_id?: string;
  dependencies?: string[];
  metadata?: Record<string, any>;
  motion_task_id?: string;
  linear_issue_id?: string;
  notion_task_id?: string;
  gitlab_issue_id?: string;
}

// Existing planner types continue below...

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
  idea: string
  config?: PlannerConfig
  context?: Record<string, any>
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