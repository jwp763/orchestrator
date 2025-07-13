/**
 * Project-specific API operations
 */
import { ApiClient, type ApiResponse } from './api';
import type {
  ProjectResponse,
  ProjectWithTasksResponse,
  ProjectListResponse,
  ProjectCreateRequest,
  ProjectUpdateRequest,
  TaskResponse,
} from '../types/api';

export class ProjectService {
  private apiClient: ApiClient;

  constructor(apiClient?: ApiClient) {
    this.apiClient = apiClient || new ApiClient();
  }

  /**
   * Get all projects with optional filtering
   */
  async getProjects(params?: {
    skip?: number;
    limit?: number;
    status?: string;
    priority?: string;
  }): Promise<ApiResponse<ProjectListResponse>> {
    const queryParams = new URLSearchParams();
    if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString());
    if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString());
    if (params?.status) queryParams.append('status', params.status);
    if (params?.priority) queryParams.append('priority', params.priority);

    const endpoint = `/api/projects${queryParams.toString() ? '?' + queryParams.toString() : ''}`;
    return this.apiClient.get<ProjectListResponse>(endpoint);
  }

  /**
   * Get a specific project by ID with its tasks
   */
  async getProject(id: string): Promise<ApiResponse<ProjectWithTasksResponse>> {
    return this.apiClient.get<ProjectWithTasksResponse>(`/api/projects/${id}`);
  }

  /**
   * Create a new project
   */
  async createProject(project: ProjectCreateRequest): Promise<ApiResponse<ProjectResponse>> {
    // Ensure required fields have defaults
    const projectData: ProjectCreateRequest = {
      status: 'planning',
      priority: 'medium',
      tags: [],
      ...project
    };
    return this.apiClient.post<ProjectResponse>('/api/projects', projectData);
  }

  /**
   * Update an existing project
   */
  async updateProject(id: string, updates: ProjectUpdateRequest): Promise<ApiResponse<ProjectResponse>> {
    return this.apiClient.put<ProjectResponse>(`/api/projects/${id}`, updates);
  }

  /**
   * Delete a project
   */
  async deleteProject(id: string): Promise<ApiResponse<void>> {
    return this.apiClient.delete<void>(`/api/projects/${id}`);
  }

  /**
   * Get all tasks for a specific project
   */
  async getProjectTasks(projectId: string): Promise<ApiResponse<TaskResponse[]>> {
    return this.apiClient.get<TaskResponse[]>(`/api/projects/${projectId}/tasks`);
  }

  /**
   * Update project status
   */
  async updateProjectStatus(id: string, status: ProjectUpdateRequest['status']): Promise<ApiResponse<ProjectResponse>> {
    return this.updateProject(id, { status });
  }

  /**
   * Update project priority
   */
  async updateProjectPriority(id: string, priority: ProjectUpdateRequest['priority']): Promise<ApiResponse<ProjectResponse>> {
    return this.updateProject(id, { priority });
  }

  /**
   * Get project statistics
   */
  async getProjectStats(id: string): Promise<ApiResponse<{
    totalTasks: number;
    completedTasks: number;
    inProgressTasks: number;
    blockedTasks: number;
    completionPercentage: number;
  }>> {
    const projectResponse = await this.getProject(id);
    if (!projectResponse.success || !projectResponse.data) {
      return {
        success: false,
        error: 'Failed to get project data',
        status: 500,
        data: {
          totalTasks: 0,
          completedTasks: 0,
          inProgressTasks: 0,
          blockedTasks: 0,
          completionPercentage: 0
        }
      };
    }

    const tasks = projectResponse.data.tasks || [];
    const totalTasks = tasks.length;
    const completedTasks = tasks.filter(task => task.status === 'completed').length;
    const inProgressTasks = tasks.filter(task => task.status === 'in_progress').length;
    const blockedTasks = tasks.filter(task => task.status === 'blocked').length;
    const completionPercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

    return {
      success: true,
      data: {
        totalTasks,
        completedTasks,
        inProgressTasks,
        blockedTasks,
        completionPercentage
      },
      status: 200
    };
  }

  /**
   * Search projects by name or description
   */
  async searchProjects(query: string): Promise<ApiResponse<ProjectListResponse>> {
    // Get all projects and filter client-side
    const allProjects = await this.getProjects();
    
    if (!allProjects.success || !allProjects.data) {
      return allProjects;
    }

    const filteredProjects = allProjects.data.projects.filter(project => 
      project.name.toLowerCase().includes(query.toLowerCase()) ||
      (project.description && project.description.toLowerCase().includes(query.toLowerCase()))
    );

    return {
      success: true,
      data: {
        ...allProjects.data,
        projects: filteredProjects,
        total: filteredProjects.length
      },
      status: 200
    };
  }
}

// Create and export default project service instance
export const projectService = new ProjectService();