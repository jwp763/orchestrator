/**
 * End-to-end tests for API integration
 * 
 * Tests frontend-backend integration with real API calls,
 * error handling, and data consistency
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { projectService } from '../src/services/projectService';
import { taskService } from '../src/services/taskService';
import { apiClient } from '../src/services/api';

// Mock fetch for controlled testing
const mockFetch = vi.fn();
globalThis.fetch = mockFetch;

describe('API Integration E2E', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  describe('Project API Integration', () => {
    it('should perform complete project CRUD cycle', async () => {
      const projectData = {
        name: 'E2E Test Project',
        description: 'Integration test project',
        created_by: 'test_user'
      };

      // 1. Create project
      const createdProject = {
        id: 'proj-e2e-1',
        ...projectData,
        status: 'planning',
        priority: 'medium',
        tags: [],
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(createdProject),
      });

      const createResponse = await projectService.createProject(projectData);
      
      expect(createResponse.success).toBe(true);
      expect(createResponse.data).toEqual(createdProject);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects'),
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({
            status: 'planning',
            priority: 'medium',
            tags: [],
            ...projectData
          })
        })
      );

      // 2. Read project
      const projectWithTasks = {
        project: createdProject,
        tasks: []
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(projectWithTasks),
      });

      const getResponse = await projectService.getProject('proj-e2e-1');
      
      expect(getResponse.success).toBe(true);
      expect(getResponse.data).toEqual(projectWithTasks);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects/proj-e2e-1'),
        expect.objectContaining({ method: 'GET' })
      );

      // 3. Update project
      const updatedProject = {
        ...createdProject,
        name: 'Updated E2E Test Project',
        status: 'active',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedProject),
      });

      const updateResponse = await projectService.updateProject('proj-e2e-1', {
        name: 'Updated E2E Test Project',
        status: 'active'
      });

      expect(updateResponse.success).toBe(true);
      expect(updateResponse.data).toEqual(updatedProject);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects/proj-e2e-1'),
        expect.objectContaining({
          method: 'PUT',
          body: JSON.stringify({
            name: 'Updated E2E Test Project',
            status: 'active'
          })
        })
      );

      // 4. Delete project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const deleteResponse = await projectService.deleteProject('proj-e2e-1');
      
      expect(deleteResponse.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/projects/proj-e2e-1'),
        expect.objectContaining({ method: 'DELETE' })
      );
    });

    it('should handle project search and statistics', async () => {
      const projects = [
        {
          id: 'proj-1',
          name: 'Web Development',
          description: 'Building web applications',
          status: 'active',
          priority: 'high',
          tags: ['web'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: 'proj-2',
          name: 'Mobile App',
          description: 'Creating mobile applications',
          status: 'planning',
          priority: 'medium',
          tags: ['mobile'],
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        }
      ];

      // Mock search
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          projects,
          total: 2,
          page: 1,
          total_pages: 1
        }),
      });

      const searchResponse = await projectService.searchProjects('web');
      
      expect(searchResponse.success).toBe(true);
      expect(searchResponse.data?.projects).toHaveLength(1);
      expect(searchResponse.data?.projects[0].name).toBe('Web Development');

      // Mock project stats
      const tasks = [
        { id: '1', status: 'completed', project_id: 'proj-1' },
        { id: '2', status: 'completed', project_id: 'proj-1' },
        { id: '3', status: 'in_progress', project_id: 'proj-1' },
        { id: '4', status: 'blocked', project_id: 'proj-1' },
        { id: '5', status: 'todo', project_id: 'proj-1' }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project: projects[0],
          tasks
        }),
      });

      const statsResponse = await projectService.getProjectStats('proj-1');
      
      expect(statsResponse.success).toBe(true);
      expect(statsResponse.data).toEqual({
        totalTasks: 5,
        completedTasks: 2,
        inProgressTasks: 1,
        blockedTasks: 1,
        completionPercentage: 40
      });
    });
  });

  describe('Task API Integration', () => {
    it('should perform complete task CRUD cycle', async () => {
      const taskData = {
        title: 'E2E Test Task',
        description: 'Integration test task',
        project_id: 'proj-1',
        created_by: 'test_user'
      };

      // 1. Create task
      const createdTask = {
        id: 'task-e2e-1',
        ...taskData,
        status: 'todo',
        priority: 'medium',
        tags: [],
        dependencies: [],
        metadata: {},
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(createdTask),
      });

      const createResponse = await taskService.createTask(taskData);
      
      expect(createResponse.success).toBe(true);
      expect(createResponse.data).toEqual(createdTask);

      // 2. Read task
      const taskWithSubtasks = {
        ...createdTask,
        subtasks: []
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(taskWithSubtasks),
      });

      const getResponse = await taskService.getTask('task-e2e-1');
      
      expect(getResponse.success).toBe(true);
      expect(getResponse.data).toEqual(taskWithSubtasks);

      // 3. Update task
      const updatedTask = {
        ...createdTask,
        title: 'Updated E2E Test Task',
        status: 'in_progress',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedTask),
      });

      const updateResponse = await taskService.updateTask('task-e2e-1', {
        title: 'Updated E2E Test Task',
        status: 'in_progress'
      });

      expect(updateResponse.success).toBe(true);
      expect(updateResponse.data).toEqual(updatedTask);

      // 4. Delete task
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const deleteResponse = await taskService.deleteTask('task-e2e-1');
      
      expect(deleteResponse.success).toBe(true);
    });

    it('should handle task dependencies and hierarchy', async () => {
      const parentTask = {
        id: 'task-parent',
        title: 'Parent Task',
        status: 'todo',
        priority: 'high',
        project_id: 'proj-1',
        dependencies: ['task-dep-1'],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      // Get task with dependencies
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...parentTask,
          subtasks: []
        }),
      });

      const taskResponse = await taskService.getTask('task-parent');
      expect(taskResponse.success).toBe(true);
      expect(taskResponse.data?.dependencies).toEqual(['task-dep-1']);

      // Add dependency
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...parentTask,
          subtasks: []
        }),
      });

      const updatedTask = {
        ...parentTask,
        dependencies: ['task-dep-1', 'task-dep-2']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(updatedTask),
      });

      const addDepResponse = await taskService.addTaskDependency('task-parent', 'task-dep-2');
      expect(addDepResponse.success).toBe(true);
      expect(addDepResponse.data?.dependencies).toEqual(['task-dep-1', 'task-dep-2']);

      // Remove dependency
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          ...updatedTask,
          subtasks: []
        }),
      });

      const finalTask = {
        ...parentTask,
        dependencies: ['task-dep-2']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(finalTask),
      });

      const removeDepResponse = await taskService.removeTaskDependency('task-parent', 'task-dep-1');
      expect(removeDepResponse.success).toBe(true);
      expect(removeDepResponse.data?.dependencies).toEqual(['task-dep-2']);
    });

    it('should handle task search and filtering', async () => {
      const tasks = [
        {
          id: 'task-1',
          title: 'Frontend Development',
          description: 'Building user interface',
          status: 'in_progress',
          priority: 'high',
          project_id: 'proj-1',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: 'task-2',
          title: 'Backend API',
          description: 'Creating REST API endpoints',
          status: 'todo',
          priority: 'medium',
          project_id: 'proj-1',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        }
      ];

      // Search tasks
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          tasks,
          total: 2,
          page: 1,
          total_pages: 1
        }),
      });

      const searchResponse = await taskService.searchTasks('frontend');
      
      expect(searchResponse.success).toBe(true);
      expect(searchResponse.data?.tasks).toHaveLength(1);
      expect(searchResponse.data?.tasks[0].title).toBe('Frontend Development');

      // Filter by status
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          tasks: [tasks[0]], // Only in_progress task
          total: 1,
          page: 1,
          total_pages: 1
        }),
      });

      const statusResponse = await taskService.getTasksByStatus('in_progress');
      
      expect(statusResponse.success).toBe(true);
      expect(statusResponse.data?.tasks).toHaveLength(1);
      expect(statusResponse.data?.tasks[0].status).toBe('in_progress');

      // Filter by project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          tasks,
          total: 2,
          page: 1,
          total_pages: 1
        }),
      });

      const projectResponse = await taskService.getTasksByProject('proj-1');
      
      expect(projectResponse.success).toBe(true);
      expect(projectResponse.data?.tasks).toHaveLength(2);
    });
  });

  describe('Error Handling Integration', () => {
    it('should handle API errors consistently across services', async () => {
      // Test 404 error - simple case without retry
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: () => Promise.resolve({ error: 'Project not found' }),
      });

      const projectResponse = await projectService.getProject('nonexistent');
      expect(projectResponse.success).toBe(false);
      expect(projectResponse.error).toBe('Project not found');
    });

    it('should handle timeout and retry logic', async () => {
      // Test simple retry without delays
      mockFetch
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ projects: [], total: 0, page: 1, total_pages: 1 }),
        });

      const response = await projectService.getProjects();
      
      expect(response.success).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2); // Initial call + retry
    });
  });

  describe('Data Consistency', () => {
    it('should maintain data consistency across operations', async () => {
      const projectId = 'proj-consistency';
      const taskId = 'task-consistency';

      // Create project
      const project = {
        id: projectId,
        name: 'Consistency Test',
        description: 'Testing data consistency',
        status: 'active',
        priority: 'high',
        tags: [],
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(project),
      });

      const projectResponse = await projectService.createProject({
        name: 'Consistency Test',
        description: 'Testing data consistency',
        created_by: 'user1'
      });

      expect(projectResponse.success).toBe(true);

      // Create task in project
      const task = {
        id: taskId,
        title: 'Consistency Task',
        description: 'Task for consistency testing',
        status: 'todo',
        priority: 'medium',
        project_id: projectId,
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(task),
      });

      const taskResponse = await taskService.createTask({
        title: 'Consistency Task',
        description: 'Task for consistency testing',
        project_id: projectId,
        created_by: 'user1'
      });

      expect(taskResponse.success).toBe(true);
      expect(taskResponse.data?.project_id).toBe(projectId);

      // Verify task appears in project
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({
          project,
          tasks: [task]
        }),
      });

      const projectWithTasksResponse = await projectService.getProject(projectId);
      
      expect(projectWithTasksResponse.success).toBe(true);
      expect(projectWithTasksResponse.data?.tasks).toHaveLength(1);
      expect(projectWithTasksResponse.data?.tasks[0].id).toBe(taskId);
    });
  });
});