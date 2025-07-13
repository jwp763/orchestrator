/**
 * End-to-end tests for project management workflows
 * 
 * Tests complete service integration workflows,
 * including project and task management operations
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { projectService } from '../src/services/projectService';
import { taskService } from '../src/services/taskService';

// Mock fetch for API calls
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('Project Management E2E', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Project Lifecycle', () => {
    it('should complete project CRUD workflow via services', async () => {
      const mockProject = {
        id: 'proj-1',
        name: 'E2E Test Project',
        description: 'End-to-end test project',
        status: 'planning',
        priority: 'high',
        tags: ['test'],
        created_by: 'test_user',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      // Step 1: Create project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockProject),
      });

      const createResponse = await projectService.createProject({
        name: 'E2E Test Project',
        description: 'End-to-end test project',
        created_by: 'test_user'
      });

      expect(createResponse.success).toBe(true);
      expect(createResponse.data).toEqual(mockProject);

      // Step 2: Read project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project: mockProject,
          tasks: []
        }),
      });

      const getResponse = await projectService.getProject('proj-1');
      expect(getResponse.success).toBe(true);
      expect(getResponse.data?.project).toEqual(mockProject);

      // Step 3: Update project
      const updatedProject = { ...mockProject, name: 'Updated E2E Project' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedProject),
      });

      const updateResponse = await projectService.updateProject('proj-1', {
        name: 'Updated E2E Project'
      });

      expect(updateResponse.success).toBe(true);
      expect(updateResponse.data?.name).toBe('Updated E2E Project');

      // Step 4: Delete project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const deleteResponse = await projectService.deleteProject('proj-1');
      expect(deleteResponse.success).toBe(true);

      // Verify all API calls were made
      expect(mockFetch).toHaveBeenCalledTimes(4);
    });
  });

  describe('Task Management', () => {
    it('should complete task CRUD workflow via services', async () => {
      const mockTask = {
        id: 'task-1',
        title: 'E2E Test Task',
        description: 'End-to-end test task',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj-1',
        created_by: 'test_user',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        dependencies: [],
        tags: [],
        attachments: [],
        metadata: {}
      };

      // Step 1: Create task
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTask),
      });

      const createResponse = await taskService.createTask({
        title: 'E2E Test Task',
        description: 'End-to-end test task',
        project_id: 'proj-1',
        created_by: 'test_user'
      });

      expect(createResponse.success).toBe(true);
      expect(createResponse.data).toEqual(mockTask);

      // Step 2: Read task
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...mockTask,
          subtasks: []
        }),
      });

      const getResponse = await taskService.getTask('task-1');
      expect(getResponse.success).toBe(true);
      expect(getResponse.data?.title).toBe('E2E Test Task');

      // Step 3: Update task
      const updatedTask = { ...mockTask, status: 'in_progress' };
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedTask),
      });

      const updateResponse = await taskService.updateTask('task-1', {
        status: 'in_progress'
      });

      expect(updateResponse.success).toBe(true);
      expect(updateResponse.data?.status).toBe('in_progress');

      // Step 4: Delete task
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const deleteResponse = await taskService.deleteTask('task-1');
      expect(deleteResponse.success).toBe(true);

      // Verify all API calls were made
      expect(mockFetch).toHaveBeenCalledTimes(4);
    });
  });

  describe('Error Handling', () => {
    it('should handle service errors gracefully', async () => {
      // Mock API error - 500 errors trigger retry, so mock 3 attempts
      mockFetch
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ error: 'Internal server error' }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ error: 'Internal server error' }),
        })
        .mockResolvedValueOnce({
          ok: false,
          status: 500,
          json: () => Promise.resolve({ error: 'Internal server error' }),
        });

      const response = await projectService.getProject('nonexistent');
      expect(response.success).toBe(false);
      expect(response.error).toBe('Internal server error');
      expect(mockFetch).toHaveBeenCalledTimes(3); // Initial + 2 retries
    }, 10000);

    it('should handle network errors', async () => {
      // Mock network error with retry logic 
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ projects: [], total: 0, page: 1, total_pages: 1 }),
        });

      const response = await projectService.getProjects();
      expect(response.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2); // Initial call + retry
    }, 10000);
  });

  describe('Integration Workflows', () => {
    it('should handle project with tasks workflow', async () => {
      const mockProject = {
        id: 'proj-workflow',
        name: 'Workflow Project',
        description: 'Project for workflow testing',
        status: 'active',
        priority: 'high',
        tags: ['workflow'],
        created_by: 'test_user',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      const mockTask = {
        id: 'task-workflow',
        title: 'Workflow Task',
        description: 'Task for workflow testing',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj-workflow',
        created_by: 'test_user',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        dependencies: [],
        tags: [],
        attachments: [],
        metadata: {}
      };

      // Create project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockProject),
      });

      const projectResponse = await projectService.createProject({
        name: 'Workflow Project',
        description: 'Project for workflow testing',
        created_by: 'test_user'
      });

      expect(projectResponse.success).toBe(true);

      // Create task in project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockTask),
      });

      const taskResponse = await taskService.createTask({
        title: 'Workflow Task',
        description: 'Task for workflow testing',
        project_id: 'proj-workflow',
        created_by: 'test_user'
      });

      expect(taskResponse.success).toBe(true);
      expect(taskResponse.data?.project_id).toBe('proj-workflow');

      // Get project with tasks
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project: mockProject,
          tasks: [mockTask]
        }),
      });

      const projectWithTasksResponse = await projectService.getProject('proj-workflow');
      expect(projectWithTasksResponse.success).toBe(true);
      expect(projectWithTasksResponse.data?.tasks).toHaveLength(1);
      expect(projectWithTasksResponse.data?.tasks[0].id).toBe('task-workflow');
    });
  });
});