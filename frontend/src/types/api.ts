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
  sort_order?: number;
  completion_percentage?: number;
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
  parent_id?: string | null;
  completion_percentage?: number;
  dependencies?: string[];
  notes?: string;
  metadata?: Record<string, any>;
  motion_task_id?: string;
  linear_issue_id?: string;
  notion_task_id?: string;
  gitlab_issue_id?: string;
}

// Planner API Types (aligned with backend)

export interface PlannerConfig {
  provider: 'openai' | 'anthropic' | 'gemini' | 'xai';
  model_name?: string; // Fixed: was 'model', backend uses 'model_name'
  create_milestones: boolean;
  max_milestones: number;
  max_retries: number;
  retry_delay?: number; // Added: backend has this field
}

export interface PlannerRequest {
  idea: string;
  config?: PlannerConfig;
  context?: Record<string, any>;
}

// New types to match backend models
export interface ProjectMetadata {
  name: string;
  description: string;
  status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived';
  priority: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  tags: string[];
  estimated_total_minutes?: number;
  estimated_total_hours?: number; // Computed field from backend
}

export interface TaskMetadata {
  title: string;
  description: string;
  status: 'todo' | 'in_progress' | 'blocked' | 'in_review' | 'completed' | 'cancelled';
  priority: 'critical' | 'high' | 'medium' | 'low' | 'backlog';
  estimated_minutes?: number;
  estimated_hours?: number; // Computed field from backend
}

export interface PlannerResponse {
  success: boolean;
  project?: ProjectMetadata; // Changed from ProjectData
  tasks: TaskMetadata[]; // Changed from TaskData[]
  raw_patch?: Record<string, any>; // Added: backend includes this
  metadata?: Record<string, any>; // Added: includes provider info, cache stats
  error?: string; // Changed from message to error
}

// Provider-related types
export interface ProviderModel {
  name: string;
  display_name: string; // Added: backend has this
  description?: string; // Made optional to match backend
  is_default: boolean; // Added: backend has this
}

export interface ProviderInfo {
  name: string;
  display_name: string;
  models: ProviderModel[];
  is_available: boolean; // Added: indicates if API key is configured
  is_default: boolean; // Added: indicates default provider
}

export interface ProvidersResponse {
  providers: ProviderInfo[]; // Changed from Provider[] to ProviderInfo[]
  default_provider: string; // Added: backend includes this
}

export interface ConfigResponse {
  default_config: PlannerConfig;
  provider_info: ProvidersResponse; // Changed from providers to provider_info
}

export interface ErrorResponse {
  error: string;
  details?: Record<string, any>; // Changed from string to Record
  code?: string;
}

// Cache statistics type (new)
export interface CacheStats {
  cache_size: number;
  max_cache_size: number;
  hits: number;
  misses: number;
  hit_rate: number;
  cache_keys: string[];
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