/**
 * Task-specific API operations
 */
import { apiClient, type ApiResponse } from './api';
import type {
  TaskResponse,
  TaskWithSubtasksResponse,
  TaskListResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
} from '../types/api';

export class TaskService {
  /**
   * Get all tasks with optional filtering
   */
  async getTasks(params?: {
    page?: number;
    per_page?: number;
    project_id?: string;
    status?: string;
    priority?: string;
    assignee?: string;
    parent_id?: string;
    tags?: string[];
  }): Promise<ApiResponse<TaskListResponse>> {
    const queryParams = { ...params };
    if (params?.tags) {
      // Convert array to comma-separated string for query params
      (queryParams as any).tags = params.tags.join(',');
    }
    return apiClient.get<TaskListResponse>('/api/tasks', queryParams);
  }

  /**
   * Get a specific task by ID
   */
  async getTask(id: string): Promise<ApiResponse<TaskResponse>> {
    return apiClient.get<TaskResponse>(`/api/tasks/${id}`);
  }

  /**
   * Get a task with all its subtasks
   */
  async getTaskWithSubtasks(id: string): Promise<ApiResponse<TaskWithSubtasksResponse>> {
    return apiClient.get<TaskWithSubtasksResponse>(`/api/tasks/${id}/subtasks`);
  }

  /**
   * Create a new task
   */
  async createTask(task: TaskCreateRequest): Promise<ApiResponse<TaskResponse>> {
    return apiClient.post<TaskResponse>('/api/tasks', task);
  }

  /**
   * Update an existing task
   */
  async updateTask(id: string, updates: TaskUpdateRequest): Promise<ApiResponse<TaskResponse>> {
    return apiClient.put<TaskResponse>(`/api/tasks/${id}`, updates);
  }

  /**
   * Delete a task
   */
  async deleteTask(id: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/tasks/${id}`);
  }

  /**
   * Get all subtasks for a specific task
   */
  async getSubtasks(
    parentId: string,
    params?: {
      page?: number;
      per_page?: number;
      status?: string;
      priority?: string;
    }
  ): Promise<ApiResponse<TaskListResponse>> {
    return apiClient.get<TaskListResponse>(`/api/tasks/${parentId}/subtasks`, params);
  }

  /**
   * Update task status
   */
  async updateTaskStatus(
    id: string,
    status: 'todo' | 'in_progress' | 'blocked' | 'in_review' | 'completed' | 'cancelled'
  ): Promise<ApiResponse<TaskResponse>> {
    return apiClient.put<TaskResponse>(`/api/tasks/${id}/status`, { status });
  }

  /**
   * Update task completion percentage
   */
  async updateTaskProgress(id: string, completion_percentage: number): Promise<ApiResponse<TaskResponse>> {
    return apiClient.put<TaskResponse>(`/api/tasks/${id}/progress`, { completion_percentage });
  }

  /**
   * Batch update task status
   */
  async updateTasksStatus(
    taskIds: string[],
    status: 'todo' | 'in_progress' | 'blocked' | 'in_review' | 'completed' | 'cancelled'
  ): Promise<ApiResponse<TaskResponse[]>> {
    return apiClient.put<TaskResponse[]>('/api/tasks/batch-status', {
      task_ids: taskIds,
      status,
    });
  }

  /**
   * Reorder tasks within a project or parent task
   */
  async reorderTasks(
    tasks: Array<{ id: string; sort_order: number }>
  ): Promise<ApiResponse<TaskResponse[]>> {
    return apiClient.put<TaskResponse[]>('/api/tasks/reorder', { tasks });
  }

  /**
   * Move task to different project or parent
   */
  async moveTask(
    id: string,
    destination: {
      project_id?: string;
      parent_id?: string | null;
      sort_order?: number;
    }
  ): Promise<ApiResponse<TaskResponse>> {
    return apiClient.put<TaskResponse>(`/api/tasks/${id}/move`, destination);
  }

  /**
   * Copy task to different location
   */
  async copyTask(
    id: string,
    destination: {
      project_id?: string;
      parent_id?: string | null;
      include_subtasks?: boolean;
    }
  ): Promise<ApiResponse<TaskResponse>> {
    return apiClient.post<TaskResponse>(`/api/tasks/${id}/copy`, destination);
  }

  /**
   * Get task dependencies
   */
  async getTaskDependencies(id: string): Promise<ApiResponse<{
    dependencies: TaskResponse[];
    dependents: TaskResponse[];
  }>> {
    return apiClient.get<any>(`/api/tasks/${id}/dependencies`);
  }

  /**
   * Add task dependency
   */
  async addTaskDependency(id: string, dependsOnId: string): Promise<ApiResponse<TaskResponse>> {
    return apiClient.post<TaskResponse>(`/api/tasks/${id}/dependencies`, {
      depends_on_id: dependsOnId,
    });
  }

  /**
   * Remove task dependency
   */
  async removeTaskDependency(id: string, dependsOnId: string): Promise<ApiResponse<TaskResponse>> {
    return apiClient.delete<TaskResponse>(`/api/tasks/${id}/dependencies/${dependsOnId}`);
  }

  /**
   * Get task time tracking
   */
  async getTaskTimeTracking(id: string): Promise<ApiResponse<{
    estimated_minutes: number | null;
    actual_minutes: number;
    time_entries: Array<{
      id: string;
      start_time: string;
      end_time: string | null;
      duration_minutes: number;
      description: string | null;
    }>;
  }>> {
    return apiClient.get<any>(`/api/tasks/${id}/time-tracking`);
  }

  /**
   * Start time tracking for a task
   */
  async startTimeTracking(id: string, description?: string): Promise<ApiResponse<any>> {
    return apiClient.post<any>(`/api/tasks/${id}/time-tracking/start`, { description });
  }

  /**
   * Stop time tracking for a task
   */
  async stopTimeTracking(id: string): Promise<ApiResponse<any>> {
    return apiClient.post<any>(`/api/tasks/${id}/time-tracking/stop`);
  }

  /**
   * Decompose task into subtasks using AI
   */
  async decomposeTask(
    id: string,
    options?: {
      target_count?: number;
      include_description?: boolean;
    }
  ): Promise<ApiResponse<TaskResponse[]>> {
    return apiClient.post<TaskResponse[]>(`/api/tasks/${id}/decompose`, options);
  }

  /**
   * Search tasks by text
   */
  async searchTasks(query: string, params?: {
    project_id?: string;
    status?: string[];
    priority?: string[];
  }): Promise<ApiResponse<TaskListResponse>> {
    return apiClient.get<TaskListResponse>('/api/tasks/search', {
      q: query,
      ...params,
    });
  }
}

// Create and export default task service instance
export const taskService = new TaskService();