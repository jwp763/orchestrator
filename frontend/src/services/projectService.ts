/**
 * Project-specific API operations
 */
import { apiClient, type ApiResponse } from './api';
import type {
  ProjectResponse,
  ProjectWithTasksResponse,
  ProjectListResponse,
  ProjectCreateRequest,
  ProjectUpdateRequest,
} from '../types/api';

export class ProjectService {
  /**
   * Get all projects with optional filtering
   */
  async getProjects(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    priority?: string;
    tags?: string[];
  }): Promise<ApiResponse<ProjectListResponse>> {
    const queryParams = { ...params };
    if (params?.tags) {
      // Convert array to comma-separated string for query params
      (queryParams as any).tags = params.tags.join(',');
    }
    return apiClient.get<ProjectListResponse>('/api/projects', queryParams);
  }

  /**
   * Get a specific project by ID
   */
  async getProject(id: string): Promise<ApiResponse<ProjectResponse>> {
    return apiClient.get<ProjectResponse>(`/api/projects/${id}`);
  }

  /**
   * Get a project with all its tasks
   */
  async getProjectWithTasks(id: string): Promise<ApiResponse<ProjectWithTasksResponse>> {
    return apiClient.get<ProjectWithTasksResponse>(`/api/projects/${id}/tasks`);
  }

  /**
   * Create a new project
   */
  async createProject(project: ProjectCreateRequest): Promise<ApiResponse<ProjectResponse>> {
    return apiClient.post<ProjectResponse>('/api/projects', project);
  }

  /**
   * Update an existing project
   */
  async updateProject(id: string, updates: ProjectUpdateRequest): Promise<ApiResponse<ProjectResponse>> {
    return apiClient.put<ProjectResponse>(`/api/projects/${id}`, updates);
  }

  /**
   * Delete a project
   */
  async deleteProject(id: string): Promise<ApiResponse<void>> {
    return apiClient.delete<void>(`/api/projects/${id}`);
  }

  /**
   * Get all tasks for a specific project
   */
  async getProjectTasks(
    projectId: string,
    params?: {
      page?: number;
      per_page?: number;
      status?: string;
      priority?: string;
    }
  ): Promise<ApiResponse<any>> {
    return apiClient.get<any>(`/api/projects/${projectId}/tasks`, params);
  }

  /**
   * Batch update project status
   */
  async updateProjectsStatus(
    projectIds: string[],
    status: 'planning' | 'active' | 'on_hold' | 'completed' | 'archived'
  ): Promise<ApiResponse<ProjectResponse[]>> {
    return apiClient.put<ProjectResponse[]>('/api/projects/batch-status', {
      project_ids: projectIds,
      status,
    });
  }

  /**
   * Get project statistics
   */
  async getProjectStats(id: string): Promise<ApiResponse<{
    total_tasks: number;
    completed_tasks: number;
    total_estimated_minutes: number;
    total_actual_minutes: number;
    completion_percentage: number;
  }>> {
    return apiClient.get<any>(`/api/projects/${id}/stats`);
  }

  /**
   * Archive multiple projects
   */
  async archiveProjects(projectIds: string[]): Promise<ApiResponse<void>> {
    return apiClient.put<void>('/api/projects/archive', {
      project_ids: projectIds,
    });
  }

  /**
   * Duplicate a project with optional tasks
   */
  async duplicateProject(
    id: string,
    options?: {
      include_tasks?: boolean;
      new_name?: string;
    }
  ): Promise<ApiResponse<ProjectResponse>> {
    return apiClient.post<ProjectResponse>(`/api/projects/${id}/duplicate`, options);
  }
}

// Create and export default project service instance
export const projectService = new ProjectService();