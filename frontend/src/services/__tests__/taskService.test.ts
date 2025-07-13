/**
 * Tests for TaskService
 * 
 * Tests task CRUD operations, filtering, dependency management, and search functionality
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { TaskService } from '../taskService';
import { ApiClient } from '../api';
import type {
  TaskResponse,
  TaskWithSubtasksResponse,
  TaskListResponse,
  TaskCreateRequest,
  TaskUpdateRequest,
} from '../../types/api';

// Mock ApiClient
const mockApiClient = {
  get: vi.fn(),
  post: vi.fn(),
  put: vi.fn(),
  delete: vi.fn(),
} as any;

describe('TaskService', () => {
  let taskService: TaskService;

  beforeEach(() => {
    taskService = new TaskService(mockApiClient);
    vi.clearAllMocks();
  });

  describe('constructor', () => {
    it('should create instance with provided ApiClient', () => {
      const service = new TaskService(mockApiClient);
      expect(service).toBeInstanceOf(TaskService);
    });

    it('should create instance with default ApiClient', () => {
      const service = new TaskService();
      expect(service).toBeInstanceOf(TaskService);
    });
  });

  describe('getTasks', () => {
    it('should get tasks without parameters', async () => {
      const mockResponse: TaskListResponse = {
        tasks: [
          {
            id: '1',
            title: 'Test Task',
            description: 'Test description',
            status: 'todo',
            priority: 'medium',
            project_id: 'proj-1',
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

      const response = await taskService.getTasks();

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockResponse);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks');
    });

    it('should get tasks with all query parameters', async () => {
      const mockResponse: TaskListResponse = {
        tasks: [],
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
        project_id: 'proj-1',
        parent_id: 'task-1',
        status: 'in_progress',
        priority: 'high',
        assignee: 'user1'
      };

      await taskService.getTasks(params);

      expect(mockApiClient.get).toHaveBeenCalledWith(
        '/api/tasks?skip=10&limit=20&project_id=proj-1&parent_id=task-1&status=in_progress&priority=high&assignee=user1'
      );
    });

    it('should handle partial parameters', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: { tasks: [], total: 0, page: 1, total_pages: 1 }
      });

      await taskService.getTasks({ project_id: 'proj-1', status: 'todo' });

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?project_id=proj-1&status=todo');
    });
  });

  describe('getTask', () => {
    it('should get task by ID with subtasks', async () => {
      const mockTask: TaskWithSubtasksResponse = {
        id: '1',
        title: 'Test Task',
        description: 'Test description',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj-1',
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        subtasks: []
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTask
      });

      const response = await taskService.getTask('1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockTask);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks/1');
    });
  });

  describe('createTask', () => {
    it('should create task with defaults', async () => {
      const mockTask: TaskResponse = {
        id: '1',
        title: 'New Task',
        description: 'New description',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj-1',
        tags: [],
        dependencies: [],
        metadata: {},
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockTask
      });

      const createRequest: TaskCreateRequest = {
        title: 'New Task',
        description: 'New description',
        project_id: 'proj-1',
        created_by: 'user1'
      };

      const response = await taskService.createTask(createRequest);

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockTask);
      expect(mockApiClient.post).toHaveBeenCalledWith('/api/tasks', {
        status: 'todo',
        priority: 'medium',
        tags: [],
        dependencies: [],
        metadata: {},
        ...createRequest
      });
    });

    it('should create task with custom values', async () => {
      const mockTask: TaskResponse = {
        id: '1',
        title: 'Custom Task',
        description: 'Custom description',
        status: 'in_progress',
        priority: 'high',
        project_id: 'proj-1',
        tags: ['custom'],
        dependencies: ['task-2'],
        metadata: { custom: 'value' },
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z'
      };

      mockApiClient.post.mockResolvedValueOnce({
        success: true,
        data: mockTask
      });

      const createRequest: TaskCreateRequest = {
        title: 'Custom Task',
        description: 'Custom description',
        status: 'in_progress',
        priority: 'high',
        project_id: 'proj-1',
        tags: ['custom'],
        dependencies: ['task-2'],
        metadata: { custom: 'value' },
        created_by: 'user1'
      };

      await taskService.createTask(createRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/tasks', createRequest);
    });
  });

  describe('updateTask', () => {
    it('should update task', async () => {
      const mockTask: TaskResponse = {
        id: '1',
        title: 'Updated Task',
        description: 'Updated description',
        status: 'in_progress',
        priority: 'high',
        project_id: 'proj-1',
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockTask
      });

      const updateRequest: TaskUpdateRequest = {
        title: 'Updated Task',
        status: 'in_progress'
      };

      const response = await taskService.updateTask('1', updateRequest);

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockTask);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', updateRequest);
    });
  });

  describe('deleteTask', () => {
    it('should delete task', async () => {
      mockApiClient.delete.mockResolvedValueOnce({
        success: true,
        data: undefined
      });

      const response = await taskService.deleteTask('1');

      expect(response.success).toBe(true);
      expect(mockApiClient.delete).toHaveBeenCalledWith('/api/tasks/1');
    });
  });

  describe('getSubtasks', () => {
    it('should get subtasks for parent task', async () => {
      const mockResponse: TaskListResponse = {
        tasks: [
          {
            id: '2',
            title: 'Subtask 1',
            status: 'todo',
            priority: 'medium',
            project_id: 'proj-1',
            parent_id: 'task-1',
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

      const response = await taskService.getSubtasks('task-1');

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockResponse);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?parent_id=task-1');
    });
  });

  describe('convenience methods', () => {
    beforeEach(() => {
      mockApiClient.put.mockResolvedValue({
        success: true,
        data: { id: '1', title: 'Test Task' }
      });
    });

    it('should update task status', async () => {
      await taskService.updateTaskStatus('1', 'completed');
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { status: 'completed' });
    });

    it('should update task priority', async () => {
      await taskService.updateTaskPriority('1', 'high');
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { priority: 'high' });
    });
  });

  describe('filtering methods', () => {
    beforeEach(() => {
      mockApiClient.get.mockResolvedValue({
        success: true,
        data: { tasks: [], total: 0, page: 1, total_pages: 1 }
      });
    });

    it('should get tasks by project', async () => {
      await taskService.getTasksByProject('proj-1');
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?project_id=proj-1');
    });

    it('should get tasks by status', async () => {
      await taskService.getTasksByStatus('in_progress');
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?status=in_progress');
    });

    it('should get tasks by priority', async () => {
      await taskService.getTasksByPriority('high');
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?priority=high');
    });

    it('should get tasks by assignee', async () => {
      await taskService.getTasksByAssignee('user1');
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?assignee=user1');
    });
  });

  describe('moveTask', () => {
    it('should move task to different project', async () => {
      const mockTask: TaskResponse = {
        id: '1',
        title: 'Moved Task',
        status: 'todo',
        priority: 'medium',
        project_id: 'proj-2',
        created_by: 'user1',
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-02T00:00:00Z'
      };

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockTask
      });

      const response = await taskService.moveTask('1', { project_id: 'proj-2' });

      expect(response.success).toBe(true);
      expect(response.data).toEqual(mockTask);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { project_id: 'proj-2' });
    });

    it('should move task to different parent', async () => {
      await taskService.moveTask('1', { parent_id: 'task-2' });
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { parent_id: 'task-2' });
    });

    it('should move task to no parent', async () => {
      await taskService.moveTask('1', { parent_id: null });
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { parent_id: null });
    });
  });

  describe('dependency management', () => {
    const mockTaskWithDependencies: TaskWithSubtasksResponse = {
      id: '1',
      title: 'Test Task',
      status: 'todo',
      priority: 'medium',
      project_id: 'proj-1',
      dependencies: ['task-2', 'task-3'],
      created_by: 'user1',
      created_at: '2025-01-01T00:00:00Z',
      updated_at: '2025-01-01T00:00:00Z',
      subtasks: []
    };

    it('should update task dependencies', async () => {
      const dependencies = ['task-4', 'task-5'];
      
      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: { ...mockTaskWithDependencies, dependencies }
      });

      const response = await taskService.updateTaskDependencies('1', dependencies);

      expect(response.success).toBe(true);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { dependencies });
    });

    it('should add task dependency', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTaskWithDependencies
      });

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: { ...mockTaskWithDependencies, dependencies: ['task-2', 'task-3', 'task-4'] }
      });

      const response = await taskService.addTaskDependency('1', 'task-4');

      expect(response.success).toBe(true);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { 
        dependencies: ['task-2', 'task-3', 'task-4'] 
      });
    });

    it('should not add duplicate dependency', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTaskWithDependencies
      });

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: mockTaskWithDependencies
      });

      await taskService.addTaskDependency('1', 'task-2');

      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { 
        dependencies: ['task-2', 'task-3'] 
      });
    });

    it('should remove task dependency', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTaskWithDependencies
      });

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: { ...mockTaskWithDependencies, dependencies: ['task-3'] }
      });

      const response = await taskService.removeTaskDependency('1', 'task-2');

      expect(response.success).toBe(true);
      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { 
        dependencies: ['task-3'] 
      });
    });

    it('should handle failed task fetch for dependency operations', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: false,
        error: 'Task not found'
      });

      const response = await taskService.addTaskDependency('1', 'task-4');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Failed to get current task data');
    });

    it('should handle task with no existing dependencies', async () => {
      const taskWithoutDeps = { ...mockTaskWithDependencies, dependencies: undefined };
      
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: taskWithoutDeps
      });

      mockApiClient.put.mockResolvedValueOnce({
        success: true,
        data: { ...taskWithoutDeps, dependencies: ['task-4'] }
      });

      await taskService.addTaskDependency('1', 'task-4');

      expect(mockApiClient.put).toHaveBeenCalledWith('/api/tasks/1', { 
        dependencies: ['task-4'] 
      });
    });
  });

  describe('searchTasks', () => {
    const mockTasks: TaskListResponse = {
      tasks: [
        {
          id: '1',
          title: 'Web Development Task',
          description: 'Building a web interface',
          status: 'todo',
          priority: 'high',
          project_id: 'proj-1',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '2',
          title: 'Mobile App Feature',
          description: 'Creating mobile functionality',
          status: 'in_progress',
          priority: 'medium',
          project_id: 'proj-1',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        },
        {
          id: '3',
          title: 'API Integration',
          description: 'Integrating external APIs',
          status: 'todo',
          priority: 'low',
          project_id: 'proj-2',
          created_by: 'user1',
          created_at: '2025-01-01T00:00:00Z',
          updated_at: '2025-01-01T00:00:00Z'
        }
      ],
      total: 3,
      page: 1,
      total_pages: 1
    };

    it('should search tasks by title', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTasks
      });

      const response = await taskService.searchTasks('web');

      expect(response.success).toBe(true);
      expect(response.data?.tasks).toHaveLength(1);
      expect(response.data?.tasks[0].title).toBe('Web Development Task');
      expect(response.data?.total).toBe(1);
    });

    it('should search tasks by description', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTasks
      });

      const response = await taskService.searchTasks('functionality');

      expect(response.success).toBe(true);
      expect(response.data?.tasks).toHaveLength(1);
      expect(response.data?.tasks[0].title).toBe('Mobile App Feature');
    });

    it('should search tasks within specific project', async () => {
      const proj1Tasks = {
        ...mockTasks,
        tasks: mockTasks.tasks.filter(t => t.project_id === 'proj-1')
      };

      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: proj1Tasks
      });

      const response = await taskService.searchTasks('app', 'proj-1');

      expect(response.success).toBe(true);
      expect(mockApiClient.get).toHaveBeenCalledWith('/api/tasks?project_id=proj-1');
    });

    it('should be case insensitive', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTasks
      });

      const response = await taskService.searchTasks('WEB');

      expect(response.success).toBe(true);
      expect(response.data?.tasks).toHaveLength(1);
      expect(response.data?.tasks[0].title).toBe('Web Development Task');
    });

    it('should return empty results for no matches', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: true,
        data: mockTasks
      });

      const response = await taskService.searchTasks('nonexistent');

      expect(response.success).toBe(true);
      expect(response.data?.tasks).toHaveLength(0);
      expect(response.data?.total).toBe(0);
    });

    it('should handle failed tasks fetch', async () => {
      mockApiClient.get.mockResolvedValueOnce({
        success: false,
        error: 'Failed to fetch tasks'
      });

      const response = await taskService.searchTasks('web');

      expect(response.success).toBe(false);
      expect(response.error).toBe('Failed to fetch tasks');
    });
  });
});