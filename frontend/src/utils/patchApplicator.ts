import type { Change, Project, Task } from '../types';
import { projectService } from '../services/projectService';
import { taskService } from '../services/taskService';
import type { 
  ProjectCreateRequest, 
  TaskCreateRequest, 
  ProjectUpdateRequest, 
  TaskUpdateRequest 
} from '../types/api';

export interface PatchApplicationResult {
  success: boolean;
  createdProjects: Project[];
  createdTasks: Task[];
  updatedProjects: Project[];
  updatedTasks: Task[];
  errors: string[];
}

export interface PatchApplicationContext {
  selectedProject?: Project | null;
  existingTasks: Task[];
  currentUser: string;
}

/**
 * Apply a collection of changes to the backend services
 */
export async function applyChanges(
  changes: Change[], 
  context: PatchApplicationContext
): Promise<PatchApplicationResult> {
  const result: PatchApplicationResult = {
    success: true,
    createdProjects: [],
    createdTasks: [],
    updatedProjects: [],
    updatedTasks: [],
    errors: []
  };

  // Separate changes by type and operation
  const projectChanges = changes.filter(c => c.type === 'project');
  const taskChanges = changes.filter(c => c.type === 'task');
  
  // Group changes by target (for batch operations)
  const projectChangeGroups = groupProjectChanges(projectChanges);
  const taskChangeGroups = groupTaskChanges(taskChanges, context.existingTasks);

  try {
    // 1. Apply project changes first (projects must exist before tasks)
    for (const group of projectChangeGroups) {
      try {
        if (group.isNewProject) {
          const createdProject = await createProjectFromChanges(group.changes, context);
          result.createdProjects.push(createdProject);
          // Update context for task creation
          context.selectedProject = createdProject;
        } else if (context.selectedProject) {
          const updatedProject = await updateProjectFromChanges(group.changes, context.selectedProject);
          result.updatedProjects.push(updatedProject);
        }
      } catch (error) {
        result.success = false;
        result.errors.push(`Project operation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

    // 2. Apply task changes after projects are created/updated
    for (const group of taskChangeGroups) {
      try {
        if (group.isNewTask) {
          const createdTask = await createTaskFromChanges(group.changes, context);
          result.createdTasks.push(createdTask);
        } else {
          const existingTask = context.existingTasks.find(t => t.id === group.taskId);
          if (existingTask) {
            const updatedTask = await updateTaskFromChanges(group.changes, existingTask);
            result.updatedTasks.push(updatedTask);
          } else {
            result.errors.push(`Task not found: ${group.taskId}`);
            result.success = false;
          }
        }
      } catch (error) {
        result.success = false;
        result.errors.push(`Task operation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
      }
    }

  } catch (error) {
    result.success = false;
    result.errors.push(`Application failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
  }

  return result;
}

interface ProjectChangeGroup {
  isNewProject: boolean;
  changes: Change[];
}

interface TaskChangeGroup {
  isNewTask: boolean;
  taskId: string;
  changes: Change[];
}

/**
 * Group project changes by target project
 */
function groupProjectChanges(changes: Change[]): ProjectChangeGroup[] {
  // For now, assume all project changes are for the same target
  // In the future, we might support multi-project operations
  if (changes.length === 0) return [];
  
  return [{
    isNewProject: changes.some(c => c.oldValue === null), // New project if any field starts as null
    changes
  }];
}

/**
 * Group task changes by target task
 */
function groupTaskChanges(changes: Change[], existingTasks: Task[]): TaskChangeGroup[] {
  const groups = new Map<string, TaskChangeGroup>();
  const existingTaskIds = new Set(existingTasks.map(t => t.id));
  
  for (const change of changes) {
    if (change.type !== 'task' || !change.taskId) continue;
    
    const taskId = change.taskId;
    if (!groups.has(taskId)) {
      groups.set(taskId, {
        // A task is new if it's not in existing tasks AND matches placeholder pattern
        isNewTask: !existingTaskIds.has(taskId) && /^task-\d+$/.test(taskId),
        taskId,
        changes: []
      });
    }
    
    groups.get(taskId)!.changes.push(change);
  }
  
  return Array.from(groups.values());
}

/**
 * Create a new project from changes
 */
async function createProjectFromChanges(changes: Change[], context: PatchApplicationContext): Promise<Project> {
  const projectData: Partial<ProjectCreateRequest> = {
    created_by: context.currentUser,
    name: 'New Project', // Default name
    description: '',
    status: 'planning',
    priority: 'medium',
    tags: []
  };

  // Apply changes to build the project data
  for (const change of changes) {
    switch (change.field) {
      case 'name':
        projectData.name = String(change.newValue);
        break;
      case 'description':
        projectData.description = String(change.newValue);
        break;
      case 'status':
        projectData.status = change.newValue as any;
        break;
      case 'priority':
        projectData.priority = change.newValue as any;
        break;
      case 'tags':
        projectData.tags = Array.isArray(change.newValue) ? change.newValue : [change.newValue];
        break;
      case 'due_date':
        projectData.due_date = String(change.newValue);
        break;
      case 'start_date':
        projectData.start_date = String(change.newValue);
        break;
    }
  }

  const response = await projectService.createProject(projectData as ProjectCreateRequest);
  return convertProjectResponse(response);
}

/**
 * Update an existing project from changes
 */
async function updateProjectFromChanges(changes: Change[], project: Project): Promise<Project> {
  const updateData: Partial<ProjectUpdateRequest> = {};

  // Apply changes to build the update data
  for (const change of changes) {
    switch (change.field) {
      case 'name':
        updateData.name = String(change.newValue);
        break;
      case 'description':
        updateData.description = String(change.newValue);
        break;
      case 'status':
        updateData.status = change.newValue as any;
        break;
      case 'priority':
        updateData.priority = change.newValue as any;
        break;
      case 'tags':
        updateData.tags = Array.isArray(change.newValue) ? change.newValue : [change.newValue];
        break;
      case 'due_date':
        updateData.due_date = String(change.newValue);
        break;
      case 'start_date':
        updateData.start_date = String(change.newValue);
        break;
    }
  }

  const response = await projectService.updateProject(project.id, updateData);
  return convertProjectResponse(response);
}

/**
 * Create a new task from changes
 */
async function createTaskFromChanges(changes: Change[], context: PatchApplicationContext): Promise<Task> {
  if (!context.selectedProject) {
    throw new Error('Cannot create task without a selected project');
  }

  const taskData: Partial<TaskCreateRequest> = {
    project_id: context.selectedProject.id,
    created_by: context.currentUser,
    title: 'New Task', // Default title
    description: '',
    status: 'todo',
    priority: 'medium',
    tags: [],
    estimated_minutes: 0,
    completion_percentage: 0,
    dependencies: [],
    metadata: {}
  };

  // Apply changes to build the task data
  for (const change of changes) {
    switch (change.field) {
      case 'title':
        taskData.title = String(change.newValue);
        break;
      case 'description':
        taskData.description = String(change.newValue);
        break;
      case 'status':
        taskData.status = change.newValue as any;
        break;
      case 'priority':
        taskData.priority = change.newValue as any;
        break;
      case 'tags':
        taskData.tags = Array.isArray(change.newValue) ? change.newValue : [change.newValue];
        break;
      case 'estimated_minutes':
        taskData.estimated_minutes = Number(change.newValue);
        break;
      case 'due_date':
        taskData.due_date = String(change.newValue);
        break;
      case 'assignee':
        taskData.assignee = String(change.newValue);
        break;
    }
  }

  const response = await taskService.createTask(taskData as TaskCreateRequest);
  return convertTaskResponse(response);
}

/**
 * Update an existing task from changes
 */
async function updateTaskFromChanges(changes: Change[], task: Task): Promise<Task> {
  const updateData: Partial<TaskUpdateRequest> = {};

  // Apply changes to build the update data
  for (const change of changes) {
    switch (change.field) {
      case 'title':
        updateData.title = String(change.newValue);
        break;
      case 'description':
        updateData.description = String(change.newValue);
        break;
      case 'status':
        updateData.status = change.newValue as any;
        break;
      case 'priority':
        updateData.priority = change.newValue as any;
        break;
      case 'tags':
        updateData.tags = Array.isArray(change.newValue) ? change.newValue : [change.newValue];
        break;
      case 'estimated_minutes':
        updateData.estimated_minutes = Number(change.newValue);
        break;
      case 'due_date':
        updateData.due_date = String(change.newValue);
        break;
      case 'assignee':
        updateData.assignee = String(change.newValue);
        break;
    }
  }

  const response = await taskService.updateTask(task.id, updateData);
  return convertTaskResponse(response);
}

/**
 * Convert API response to frontend Project type
 */
function convertProjectResponse(response: any): Project {
  return {
    id: response.id,
    name: response.name || '',
    description: response.description || '',
    status: response.status ? response.status.toUpperCase() as any : 'PLANNING',
    priority: response.priority ? response.priority.toUpperCase() as any : 'MEDIUM',
    tags: response.tags || [],
    due_date: response.due_date || '',
    start_date: response.start_date || '',
    motion_project_link: response.motion_project_id || null,
    linear_project_link: response.linear_project_id || null,
    notion_page_link: response.notion_page_id || null,
    gitlab_project_link: response.gitlab_project_id || null,
  };
}

/**
 * Convert API response to frontend Task type
 */
function convertTaskResponse(response: any): Task {
  return {
    id: response.id,
    title: response.title || '',
    description: response.description || '',
    project_id: response.project_id,
    status: response.status ? response.status.toUpperCase().replace('-', '_') as any : 'TODO',
    priority: response.priority ? response.priority.toUpperCase() as any : 'MEDIUM',
    parent_id: response.parent_id || null,
    estimated_minutes: response.estimated_minutes || null,
    actual_minutes: response.actual_minutes || 0,
    dependencies: response.dependencies || [],
    due_date: response.due_date || null,
    created_at: response.created_at || new Date().toISOString(),
    updated_at: response.updated_at || new Date().toISOString(),
    assignee: response.assignee || null,
    tags: response.tags || [],
    attachments: response.attachments || [],
    notes: response.notes || '',
    completion_percentage: response.completion_percentage || 0,
    metadata: response.metadata || {},
    motion_task_id: response.motion_task_id || undefined,
    linear_issue_id: response.linear_issue_id || undefined,
    notion_task_id: response.notion_task_id || undefined,
    gitlab_issue_id: response.gitlab_issue_id || undefined,
  };
}