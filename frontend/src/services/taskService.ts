/**
 * Task-specific API operations
 */
import { ApiClient, type ApiResponse } from './api';
import type {
  TaskResponse,
  TaskWithSubtasksResponse,
  TaskListResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
} from '../types/api';

export class TaskService {
  private apiClient: ApiClient;

  constructor(apiClient?: ApiClient) {
    this.apiClient = apiClient || new ApiClient();
  }

  /**
   * Get all tasks with optional filtering
   */
  async getTasks(params?: {
    skip?: number;
    limit?: number;
    project_id?: string;
    parent_id?: string;
    status?: string;
    priority?: string;
    assignee?: string;
  }): Promise<ApiResponse<TaskListResponse>> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.project_id) queryParams.append('project_id', params.project_id);
    if (params?.parent_id) queryParams.append('parent_id', params.parent_id);
    if (params?.status) queryParams.append('status', params.status);
    if (params?.priority) queryParams.append('priority', params.priority);
    if (params?.assignee) queryParams.append('assignee', params.assignee);

    const endpoint = `/api/tasks${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.apiClient.get<TaskListResponse>(endpoint);
  }

  /**
   * Get a specific task by ID with its subtasks
   */
  async getTask(id: string): Promise<ApiResponse<TaskWithSubtasksResponse>> {
    return this.apiClient.get<TaskWithSubtasksResponse>(`/api/tasks/${id}`);
  }

  /**
   * Create a new task
   */
  async createTask(task: TaskCreateRequest): Promise<ApiResponse<TaskResponse>> {
    // Ensure required fields have defaults
    const taskData: TaskCreateRequest = {
      status: 'todo',
      priority: 'medium',
      tags: [],
      dependencies: [],
      metadata: {},
      ...task
    };
    return this.apiClient.post<TaskResponse>('/api/tasks', taskData);
  }

  /**
   * Update an existing task
   */
  async updateTask(id: string, updates: TaskUpdateRequest): Promise<ApiResponse<TaskResponse>> {
    return this.apiClient.put<TaskResponse>(`/api/tasks/${id}`, updates);
  }

  /**
   * Delete a task
   */
  async deleteTask(id: string): Promise<ApiResponse<void>> {
    return this.apiClient.delete<void>(`/api/tasks/${id}`);
  }

  /**
   * Get all subtasks for a specific task
   */
  async getSubtasks(parentId: string): Promise<ApiResponse<TaskListResponse>> {
    return this.getTasks({ parent_id: parentId });
  }

  /**
   * Update task status
   */
  async updateTaskStatus(id: string, status: TaskUpdateRequest['status']): Promise<ApiResponse<TaskResponse>> {
    return this.updateTask(id, { status });
  }

  /**
   * Update task priority
   */
  async updateTaskPriority(id: string, priority: TaskUpdateRequest['priority']): Promise<ApiResponse<TaskResponse>> {
    return this.updateTask(id, { priority });
  }

  /**
   * Get tasks by project ID
   */
  async getTasksByProject(projectId: string): Promise<ApiResponse<TaskListResponse>> {
    return this.getTasks({ project_id: projectId });
  }

  /**
   * Get tasks by status
   */
  async getTasksByStatus(status: TaskResponse['status']): Promise<ApiResponse<TaskListResponse>> {
    return this.getTasks({ status });
  }

  /**
   * Get tasks by priority
   */
  async getTasksByPriority(priority: TaskResponse['priority']): Promise<ApiResponse<TaskListResponse>> {
    return this.getTasks({ priority });
  }

  /**
   * Get tasks by assignee
   */
  async getTasksByAssignee(assignee: string): Promise<ApiResponse<TaskListResponse>> {
    return this.getTasks({ assignee });
  }

  /**
   * Move task to different parent or project
   */
  async moveTask(id: string, destination: {
    project_id?: string;
    parent_id?: string | null;
  }): Promise<ApiResponse<TaskResponse>> {
    return this.updateTask(id, destination);
  }

  /**
   * Update task dependencies
   */
  async updateTaskDependencies(id: string, dependencies: string[]): Promise<ApiResponse<TaskResponse>> {
    return this.updateTask(id, { dependencies });
  }

  /**
   * Add task dependency
   */
  async addTaskDependency(id: string, dependsOnId: string): Promise<ApiResponse<TaskResponse>> {
    const currentTask = await this.getTask(id);
    if (!currentTask.success || !currentTask.data) {
      return {
        success: false,
        error: 'Failed to get current task data',
        status: 500,
        data: {} as TaskResponse
      };
    }

    const existingDependencies = currentTask.data.dependencies || [];
    const updatedDependencies = [...new Set([...existingDependencies, dependsOnId])];
    
    return this.updateTask(id, { dependencies: updatedDependencies });
  }

  /**
   * Remove task dependency
   */
  async removeTaskDependency(id: string, dependsOnId: string): Promise<ApiResponse<TaskResponse>> {
    const currentTask = await this.getTask(id);
    if (!currentTask.success || !currentTask.data) {
      return {
        success: false,
        error: 'Failed to get current task data',
        status: 500,
        data: {} as TaskResponse
      };
    }

    const existingDependencies = currentTask.data.dependencies || [];
    const updatedDependencies = existingDependencies.filter(dep => dep !== dependsOnId);
    
    return this.updateTask(id, { dependencies: updatedDependencies });
  }

  /**
   * Search tasks by title or description
   */
  async searchTasks(query: string, projectId?: string): Promise<ApiResponse<TaskListResponse>> {
    // Get all tasks and filter client-side
    const params = projectId ? { project_id: projectId } : {};
    const allTasks = await this.getTasks(params);
    
    if (!allTasks.success || !allTasks.data) {
      return allTasks;
    }

    const filteredTasks = allTasks.data.tasks.filter(task => 
      task.title.toLowerCase().includes(query.toLowerCase()) ||
      (task.description && task.description.toLowerCase().includes(query.toLowerCase()))
    );

    return {
      success: true,
      data: {
        ...allTasks.data,
        tasks: filteredTasks,
        total: filteredTasks.length
      },
      status: 200
    };
  }
}

// Create and export default task service instance
export const taskService = new TaskService();