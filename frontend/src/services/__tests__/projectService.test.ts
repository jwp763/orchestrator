/**
 * Tests for ProjectService
 * 
 * Tests project CRUD operations, statistics calculation, and search functionality
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ProjectService } from '../projectService';
import { ApiClient } from '../api';
import type {
  ProjectResponse,
  ProjectWithTasksResponse,
  ProjectListResponse,
  ProjectCreateRequest,
  ProjectUpdateRequest,
  TaskResponse,
} from '../../types/api';

// Mock ApiClient
const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
} as any;

describe('ProjectService', () => {
  let projectService: ProjectService;

  beforeEach(() => {
    projectService = new ProjectService(mockApiClient);
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create instance with provided ApiClient', () => {
      const service = new ProjectService(mockApiClient);
      expect(service).toBeInstanceOf(ProjectService);
    });

    it('should create instance with default ApiClient', () => {
      const service = new ProjectService();
      expect(service).toBeInstanceOf(ProjectService);
    });
  });

  describe('getProjects', () => {
    it('should get projects without parameters', async () => {
      const mockResponse: ProjectListResponse = {
        projects: [
          {
            id: '1',
            name: 'Test Project',
            description: 'Test description',
            status: 'active',
            priority: 'high',
            tags: ['test'],
            created_by: 'user1',
            created_at: '2025-01-01T00:00:00Z',
            updated_at: '2025-01-01T00:00:00Z'
          }
        ],
        total: 1,
        page: 1,
        total_pages: 1
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockResponse
      });

      const response = await projectService.getProjects();

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockResponse);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/projects');
    });

    it('should get projects with query parameters', async () => {
      const mockResponse: ProjectListResponse = {
        projects: [],
        total: 0,
        page: 1,
        total_pages: 1
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockResponse
      });

      const params = {
        skip: 10,
        limit: 20,
        status: 'active',
        priority: 'high'
      };

      await projectService.getProjects(params);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/api/projects?skip=10&limit=20&status=active&priority=high'
      );
    });

    it('should handle empty parameters', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: { projects: [], total: 0, page: 1, total_pages: 1 }
      });

      await projectService.getProjects({});

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/projects');
    });

    it('should handle partial parameters', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: { projects: [], total: 0, page: 1, total_pages: 1 }
      });

      await projectService.getProjects({ skip: 5, status: 'active' });

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/projects?skip=5&status=active');
    });
  });

  describe('getProject', () => {
    it('should get project by ID', async () => {
      const mockProject: ProjectWithTasksResponse = {
        project: {
          id: '1',
          name: 'Test Project',
          description: 'Test description',
          status: 'active',
          priority: 'high',
          tags: ['test'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        tasks: []
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const response = await projectService.getProject('1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockProject);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/projects/1');
    });
  });

  describe('createProject', () => {
    it('should create project with defaults', async () => {
      const mockProject: ProjectResponse = {
        id: '1',
        name: 'New Project',
        description: 'New description',
        status: 'planning',
        priority: 'medium',
        tags: [],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const createRequest: ProjectCreateRequest = {
        name: 'New Project',
        description: 'New description',
        created_by: 'user1'
      };

      const response = await projectService.createProject(createRequest);

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockProject);
      expect(mockApiClient.post).toHaveBeenCalledWith('/api/projects', {
        status: 'planning',
        priority: 'medium',
        tags: [],
        ...createRequest
      });
    });

    it('should create project with custom values', async () => {
      const mockProject: ProjectResponse = {
        id: '1',
        name: 'Custom Project',
        description: 'Custom description',
        status: 'active',
        priority: 'high',
        tags: ['custom'],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const createRequest: ProjectCreateRequest = {
        name: 'Custom Project',
        description: 'Custom description',
        status: 'active',
        priority: 'high',
        tags: ['custom'],
        created_by: 'user1'
      };

      await projectService.createProject(createRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/projects', createRequest);
    });
  });

  describe('updateProject', () => {
    it('should update project', async () => {
      const mockProject: ProjectResponse = {
        id: '1',
        name: 'Updated Project',
        description: 'Updated description',
        status: 'active',
        priority: 'high',
        tags: ['updated'],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const updateRequest: ProjectUpdateRequest = {
        name: 'Updated Project',
        status: 'active'
      };

      const response = await projectService.updateProject('1', updateRequest);

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockProject);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/projects/1', updateRequest);
    });
  });

  describe('deleteProject', () => {
    it('should delete project', async () => {
      mockApiClient.delete.mockResolvedValueOnce({
        success: true,
        data: undefined
      });

      const response = await projectService.deleteProject('1');

      expect(response.success).toBe(true);
      expect(mockApiClient.delete).toHaveBeenCalledWith('/api/projects/1');
    });
  });

  describe('getProjectTasks', () => {
    it('should get project tasks', async () => {
      const mockTasks: TaskResponse[] = [
        {
          id: '1',
          title: 'Test Task',
          description: 'Test task description',
          status: 'todo',
          priority: 'medium',
          project_id: '1',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        }
      ];

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTasks
      });

      const response = await projectService.getProjectTasks('1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockTasks);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/projects/1/tasks');
    });
  });

  describe('updateProjectStatus', () => {
    it('should update project status', async () => {
      const mockProject: ProjectResponse = {
        id: '1',
        name: 'Test Project',
        description: 'Test description',
        status: 'completed',
        priority: 'medium',
        tags: [],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const response = await projectService.updateProjectStatus('1', 'completed');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockProject);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/projects/1', { status: 'completed' });
    });
  });

  describe('updateProjectPriority', () => {
    it('should update project priority', async () => {
      const mockProject: ProjectResponse = {
        id: '1',
        name: 'Test Project',
        description: 'Test description',
        status: 'active',
        priority: 'high',
        tags: [],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockProject
      });

      const response = await projectService.updateProjectPriority('1', 'high');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockProject);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/projects/1', { priority: 'high' });
    });
  });

  describe('getProjectStats', () => {
    it('should calculate project statistics', async () => {
      const mockTasks: TaskResponse[] = [
        { id: '1', title: 'Task 1', status: 'completed', priority: 'medium', project_id: '1', created_by: 'user1', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '2', title: 'Task 2', status: 'completed', priority: 'medium', project_id: '1', created_by: 'user1', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '3', title: 'Task 3', status: 'in_progress', priority: 'medium', project_id: '1', created_by: 'user1', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '4', title: 'Task 4', status: 'blocked', priority: 'medium', project_id: '1', created_by: 'user1', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' },
        { id: '5', title: 'Task 5', status: 'todo', priority: 'medium', project_id: '1', created_by: 'user1', created_at: '2025-01-01T00:00:00Z', updated_at: '2025-01-01T00:00:00Z' }
      ];

      const mockProjectResponse: ProjectWithTasksResponse = {
        project: {
          id: '1',
          name: 'Test Project',
          description: 'Test description',
          status: 'active',
          priority: 'medium',
          tags: [],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        tasks: mockTasks
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjectResponse
      });

      const response = await projectService.getProjectStats('1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual({
        totalTasks: 5,
        completedTasks: 2,
        inProgressTasks: 1,
        blockedTasks: 1,
        completionPercentage: 40
      });
    });

    it('should handle project with no tasks', async () => {
      const mockProjectResponse: ProjectWithTasksResponse = {
        project: {
          id: '1',
          name: 'Empty Project',
          description: 'Project with no tasks',
          status: 'active',
          priority: 'medium',
          tags: [],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        tasks: []
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjectResponse
      });

      const response = await projectService.getProjectStats('1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual({
        totalTasks: 0,
        completedTasks: 0,
        inProgressTasks: 0,
        blockedTasks: 0,
        completionPercentage: 0
      });
    });

    it('should handle failed project fetch', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: false,
        error: 'Project not found'
      });

      const response = await projectService.getProjectStats('1');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Failed to get project data');
      expect(response.data).toEqual({
        totalTasks: 0,
        completedTasks: 0,
        inProgressTasks: 0,
        blockedTasks: 0,
        completionPercentage: 0
      });
    });
  });

  describe('searchProjects', () => {
    const mockProjects: ProjectListResponse = {
      projects: [
        {
          id: '1',
          name: 'Web Development',
          description: 'Building a web application',
          status: 'active',
          priority: 'high',
          tags: ['web'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '2',
          name: 'Mobile App',
          description: 'Creating a mobile application',
          status: 'planning',
          priority: 'medium',
          tags: ['mobile'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '3',
          name: 'API Integration',
          description: 'Integrating third-party APIs',
          status: 'active',
          priority: 'low',
          tags: ['api'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        }
      ],
      total: 3,
      page: 1,
      total_pages: 1
    };

    it('should search projects by name', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjects
      });

      const response = await projectService.searchProjects('web');

      expect(response.success).toBe(true);
      expect(response.data?.projects).toHaveLength(1);
      expect(response.data?.projects[0].name).toBe('Web Development');
      expect(response.data?.total).toBe(1);
    });

    it('should search projects by description', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjects
      });

      const response = await projectService.searchProjects('application');

      expect(response.success).toBe(true);
      expect(response.data?.projects).toHaveLength(2);
      expect(response.data?.total).toBe(2);
    });

    it('should be case insensitive', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjects
      });

      const response = await projectService.searchProjects('WEB');

      expect(response.success).toBe(true);
      expect(response.data?.projects).toHaveLength(1);
      expect(response.data?.projects[0].name).toBe('Web Development');
    });

    it('should return empty results for no matches', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockProjects
      });

      const response = await projectService.searchProjects('nonexistent');

      expect(response.success).toBe(true);
      expect(response.data?.projects).toHaveLength(0);
      expect(response.data?.total).toBe(0);
    });

    it('should handle failed projects fetch', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: false,
        error: 'Failed to fetch projects'
      });

      const response = await projectService.searchProjects('web');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Failed to fetch projects');
    });
  });
});