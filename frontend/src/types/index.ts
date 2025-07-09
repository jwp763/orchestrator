// Enums
export const ProjectStatus = {
  PLANNING: 'PLANNING',
  ACTIVE: 'ACTIVE',
  ON_HOLD: 'ON_HOLD',
  COMPLETED: 'COMPLETED',
  ARCHIVED: 'ARCHIVED'
} as const;

export const Priority = {
  CRITICAL: 'CRITICAL',
  HIGH: 'HIGH',
  MEDIUM: 'MEDIUM',
  LOW: 'LOW',
  BACKLOG: 'BACKLOG'
} as const;

export const TaskStatus = {
  TODO: 'TODO',
  IN_PROGRESS: 'IN_PROGRESS',
  REVIEW: 'REVIEW',
  DONE: 'DONE',
  BLOCKED: 'BLOCKED'
} as const;

// Type definitions
export type ProjectStatus = typeof ProjectStatus[keyof typeof ProjectStatus];
export type Priority = typeof Priority[keyof typeof Priority];
export type TaskStatus = typeof TaskStatus[keyof typeof TaskStatus];

// Core interfaces
export interface Project {
  id: string;
  name: string;
  description: string;
  status: ProjectStatus;
  priority: Priority;
  tags: string[];
  due_date: string;
  start_date: string;
  motion_project_link: string | null;
  linear_project_link: string | null;
  notion_page_link: string | null;
  gitlab_project_link: string | null;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  project_id: string;
  status: TaskStatus;
  priority: Priority;
  parent_id: string | null;
  estimated_minutes: number | null;
  actual_minutes: number;
  dependencies: string[];
  due_date: string | null;
  created_at: string;
  updated_at: string;
  assignee: string | null;
  tags: string[];
  attachments: string[];
  notes: string;
  completion_percentage: number;
  metadata: Record<string, any>;
  motion_task_id?: string;
  linear_issue_id?: string;
  notion_task_id?: string;
  gitlab_issue_id?: string;
}

// Component props interfaces
export interface ProjectSidebarProps {
  projects: Project[];
  selectedProject: Project | null;
  onProjectSelect: (project: Project) => void;
  onAddProject: () => void;
}

export interface ProjectDetailsProps {
  project: Project;
  onUpdate: (project: Project) => void;
  isCollapsed: boolean;
  onToggleCollapse: () => void;
}

export interface TaskCardProps {
  task: Task;
  onClick: () => void;
}

export interface TaskDetailsProps {
  task: Task;
  onClose: () => void;
  onUpdate: (task: Task) => void;
}

export interface NaturalLanguageEditorProps {
  selectedProject: Project | null;
  selectedTask: Task | null;
  onApplyChanges: (changes: Change[]) => void;
}

export interface Change {
  type: 'project' | 'task';
  taskId?: string;
  field: string;
  oldValue: any;
  newValue: any;
  display: string;
}

// Status and priority mappings
export type StatusColorMap = Record<string, string>;
export type PriorityColorMap = Record<string, string>;