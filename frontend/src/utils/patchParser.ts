import type { Change } from '../types';
import type { PlannerResponse } from '../types/api';

export interface PatchOperation {
  op: 'create' | 'update' | 'delete';
  project_id?: string;
  task_id?: string;
  [key: string]: any;
}

export interface ProjectPatch extends PatchOperation {
  name?: string;
  description?: string;
  status?: string;
  priority?: string;
  tags?: string[];
  due_date?: string;
  start_date?: string;
  estimated_total_minutes?: number;
}

export interface TaskPatch extends PatchOperation {
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  due_date?: string;
  estimated_minutes?: number;
  assignee?: string;
  tags?: string[];
}

export interface RawPatch {
  project_patches: ProjectPatch[];
  task_patches: TaskPatch[];
}

/**
 * Convert a PlannerResponse into Change objects for display
 */
export function parseResponseToChanges(response: PlannerResponse): Change[] {
  const changes: Change[] = [];
  
  // Handle simple project/task metadata format (current implementation)
  if (response.project) {
    changes.push({
      type: 'project',
      field: 'name',
      oldValue: null,
      newValue: response.project.name,
      display: `Create project: ${response.project.name}`
    });
    
    if (response.project.description) {
      changes.push({
        type: 'project',
        field: 'description',
        oldValue: null,
        newValue: response.project.description,
        display: `Set description: ${response.project.description}`
      });
    }
    
    if (response.project.status) {
      changes.push({
        type: 'project',
        field: 'status',
        oldValue: null,
        newValue: response.project.status,
        display: `Set status: ${response.project.status}`
      });
    }
    
    if (response.project.priority) {
      changes.push({
        type: 'project',
        field: 'priority',
        oldValue: null,
        newValue: response.project.priority,
        display: `Set priority: ${response.project.priority}`
      });
    }
    
    if (response.project.tags && response.project.tags.length > 0) {
      changes.push({
        type: 'project',
        field: 'tags',
        oldValue: null,
        newValue: response.project.tags,
        display: `Add tags: ${response.project.tags.join(', ')}`
      });
    }
    
    if (response.project.estimated_total_minutes) {
      const hours = Math.round(response.project.estimated_total_minutes / 60);
      changes.push({
        type: 'project',
        field: 'estimated_total_minutes',
        oldValue: null,
        newValue: response.project.estimated_total_minutes,
        display: `Set estimate: ${response.project.estimated_total_minutes} minutes (${hours} hours)`
      });
    }
  }
  
  // Handle task metadata
  if (response.tasks && response.tasks.length > 0) {
    response.tasks.forEach((task, index) => {
      const taskId = `task-${index + 1}`;
      
      changes.push({
        type: 'task',
        taskId,
        field: 'title',
        oldValue: null,
        newValue: task.title,
        display: `Create task: ${task.title}`
      });
      
      if (task.description) {
        changes.push({
          type: 'task',
          taskId,
          field: 'description',
          oldValue: null,
          newValue: task.description,
          display: `Set description: ${task.description}`
        });
      }
      
      if (task.status) {
        changes.push({
          type: 'task',
          taskId,
          field: 'status',
          oldValue: null,
          newValue: task.status,
          display: `Set status: ${task.status}`
        });
      }
      
      if (task.priority) {
        changes.push({
          type: 'task',
          taskId,
          field: 'priority',
          oldValue: null,
          newValue: task.priority,
          display: `Set priority: ${task.priority}`
        });
      }
      
      if (task.estimated_minutes) {
        const hours = Math.round(task.estimated_minutes / 60 * 10) / 10; // Round to 1 decimal
        changes.push({
          type: 'task',
          taskId,
          field: 'estimated_minutes',
          oldValue: null,
          newValue: task.estimated_minutes,
          display: `Set estimate: ${task.estimated_minutes} minutes (${hours} hours)`
        });
      }
    });
  }
  
  // Handle raw patch data for more detailed changes
  if (response.raw_patch) {
    const additionalChanges = parseRawPatchToChanges(response.raw_patch);
    changes.push(...additionalChanges);
  }
  
  return changes;
}

/**
 * Convert raw patch data into Change objects
 */
export function parseRawPatchToChanges(rawPatch: any): Change[] {
  const changes: Change[] = [];
  
  if (!rawPatch || typeof rawPatch !== 'object') {
    return changes;
  }
  
  // Parse project patches
  if (rawPatch.project_patches && Array.isArray(rawPatch.project_patches)) {
    rawPatch.project_patches.forEach((patch: ProjectPatch) => {
      const projectChanges = parseProjectPatch(patch);
      changes.push(...projectChanges);
    });
  }
  
  // Parse task patches
  if (rawPatch.task_patches && Array.isArray(rawPatch.task_patches)) {
    rawPatch.task_patches.forEach((patch: TaskPatch) => {
      const taskChanges = parseTaskPatch(patch);
      changes.push(...taskChanges);
    });
  }
  
  return changes;
}

/**
 * Convert a project patch to Change objects
 */
function parseProjectPatch(patch: ProjectPatch): Change[] {
  const changes: Change[] = [];
  
  // Skip if we already processed this through project metadata
  if (patch.op === 'create' && patch.name) {
    return changes; // Handled by project metadata parsing
  }
  
  Object.entries(patch).forEach(([key, value]) => {
    if (key === 'op' || key === 'project_id' || value === null || value === undefined) {
      return;
    }
    
    const displayValue = Array.isArray(value) ? value.join(', ') : String(value);
    const operation = patch.op === 'create' ? 'Create' : 
                     patch.op === 'update' ? 'Update' : 'Delete';
    
    changes.push({
      type: 'project',
      field: key,
      oldValue: patch.op === 'create' ? null : 'current value',
      newValue: value,
      display: `${operation} ${key}: ${displayValue}`
    });
  });
  
  return changes;
}

/**
 * Convert a task patch to Change objects
 */
function parseTaskPatch(patch: TaskPatch): Change[] {
  const changes: Change[] = [];
  const taskId = patch.task_id || 'new-task';
  
  // Skip if we already processed this through task metadata
  if (patch.op === 'create' && patch.title) {
    return changes; // Handled by task metadata parsing
  }
  
  Object.entries(patch).forEach(([key, value]) => {
    if (key === 'op' || key === 'task_id' || key === 'project_id' || value === null || value === undefined) {
      return;
    }
    
    const displayValue = Array.isArray(value) ? value.join(', ') : String(value);
    const operation = patch.op === 'create' ? 'Create' : 
                     patch.op === 'update' ? 'Update' : 'Delete';
    
    changes.push({
      type: 'task',
      taskId,
      field: key,
      oldValue: patch.op === 'create' ? null : 'current value',
      newValue: value,
      display: `${operation} ${key}: ${displayValue}`
    });
  });
  
  return changes;
}


