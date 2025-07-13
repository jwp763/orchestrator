/**
 * Integration tests for useProjectManagement hook with service layer
 * 
 * Tests the hook's interaction with ProjectService and TaskService,
 * including error handling, state management, and data conversion
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useProjectManagement } from '../useProjectManagement';
import { projectService } from '../../services/projectService';
import { taskService } from '../../services/taskService';
import type { 
  ProjectResponse, 
  TaskResponse,
  ProjectListResponse,
  TaskListResponse,
  ProjectWithTasksResponse 
} from '../../types/api';

// Mock the services
vi.mock('../../services/projectService');
vi.mock('../../services/taskService');

const mockProjectService = vi.mocked(projectService);
const mockTaskService = vi.mocked(taskService);

describe('useProjectManagement Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockProject: ProjectResponse = {
    id: 'proj-1',
    name: 'Test Project',
    description: 'Test description',
    status: 'active',
    priority: 'high',
    tags: ['test'],
    created_by: 'user1',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z'
  };

  const mockTask: TaskResponse = {
    id: 'task-1',
    title: 'Test Task',
    description: 'Test task description',
    status: 'todo',
    priority: 'medium',
    project_id: 'proj-1',
    created_by: 'user1',
    created_at: '2025-01-01T00:00:00Z',
    updated_at: '2025-01-01T00:00:00Z',
    dependencies: [],
    tags: [],
    attachments: [],
    metadata: {}
  };

  describe('initial load and data conversion', () => {
    it('should load projects on mount and convert API format', async () => {
      const mockResponse: ProjectListResponse = {
        projects: [mockProject],
        total: 1,
        page: 1,
        total_pages: 1
      };

      // Mock empty projects for initial load (no auto-selection)
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [], total: 0, page: 1, total_pages: 1 }
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial state to be set
      await waitFor(() => {
        expect(result.current.projectsLoading).toBe(false);
      });

      expect(result.current.projects).toHaveLength(0);
      expect(result.current.error).toBeNull();
      expect(result.current.selectedProject).toBeNull();
      expect(mockProjectService.getProjects).toHaveBeenCalledTimes(1);
    });

    it('should auto-select first project and load its tasks', async () => {
      const mockProjectResponse: ProjectListResponse = {
        projects: [mockProject],
        total: 1,
        page: 1,
        total_pages: 1
      };

      const mockTaskResponse: TaskListResponse = {
        tasks: [mockTask],
        total: 1,
        page: 1,
        total_pages: 1
      };

      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: mockProjectResponse
      });

      mockTaskService.getTasks.mockResolvedValueOnce({
        success: true,
        data: mockTaskResponse
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load and auto-selection
      await waitFor(() => {
        expect(result.current.selectedProject).toBeTruthy();
        expect(result.current.tasks).toHaveLength(1);
      });

      expect(result.current.selectedProject?.id).toBe('proj-1');
      expect(result.current.tasks[0]).toEqual({
        id: 'task-1',
        title: 'Test Task',
        description: 'Test task description',
        project_id: 'proj-1',
        status: 'TODO',
        priority: 'MEDIUM',
        parent_id: undefined,
        estimated_minutes: undefined,
        actual_minutes: undefined,
        dependencies: [],
        due_date: undefined,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        assignee: undefined,
        tags: [],
        attachments: [],
        notes: '',
        completion_percentage: undefined,
        metadata: {},
        motion_task_id: undefined,
        linear_issue_id: undefined,
        notion_task_id: undefined,
        gitlab_issue_id: undefined,
      });
      expect(mockTaskService.getTasks).toHaveBeenCalledWith({ project_id: 'proj-1' });
    });
  });

  describe('project management operations', () => {
    it('should create new project successfully', async () => {
      const newProject = { ...mockProject, id: 'new-proj-1', name: 'New Project' };
      
      mockProjectService.createProject.mockResolvedValueOnce({
        success: true,
        data: newProject
      });

      const { result } = renderHook(() => useProjectManagement());

      const projectData = {
        name: 'New Project',
        description: 'New project description'
      };

      let createdProject;
      await act(async () => {
        createdProject = await result.current.handleNewProject(projectData);
      });

      expect(createdProject).toBeTruthy();
      expect(mockProjectService.createProject).toHaveBeenCalledWith({
        ...projectData,
        created_by: 'current-user'
      });
      
      // Should update projects list and select new project
      expect(result.current.projects).toContainEqual(
        expect.objectContaining({ name: 'New Project' })
      );
      expect(result.current.selectedProject?.name).toBe('New Project');
    });

    it('should handle project creation error', async () => {
      mockProjectService.createProject.mockResolvedValueOnce({
        success: false,
        error: 'Failed to create project'
      });

      const { result } = renderHook(() => useProjectManagement());

      let createdProject;
      await act(async () => {
        createdProject = await result.current.handleNewProject({
          name: 'New Project',
          description: 'New project description'
        });
      });

      expect(createdProject).toBeNull();
      expect(result.current.error).toBe('Failed to create project');
    });

    it('should update project successfully', async () => {
      // First load initial projects
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
      });

      const updatedProject = { ...mockProject, name: 'Updated Project' };
      mockProjectService.updateProject.mockResolvedValueOnce({
        success: true,
        data: updatedProject
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.projects).toHaveLength(1);
      });

      // Convert to frontend format for update
      const frontendProject = {
        id: 'proj-1',
        name: 'Updated Project',
        description: 'Test description',
        status: 'ACTIVE' as const,
        priority: 'HIGH' as const,
        tags: ['test'],
        due_date: '',
        start_date: '',
        motion_project_link: null,
        linear_project_link: null,
        notion_page_link: null,
        gitlab_project_link: null,
      };

      let result_;
      await act(async () => {
        result_ = await result.current.handleUpdateProject(frontendProject);
      });

      expect(result_).toBeTruthy();
      expect(mockProjectService.updateProject).toHaveBeenCalledWith('proj-1', {
        name: 'Updated Project',
        description: 'Test description',
        status: 'active',
        priority: 'high',
        tags: ['test'],
        due_date: undefined,
        start_date: undefined,
        motion_project_id: undefined,
        linear_project_id: undefined,
        notion_page_id: undefined,
        gitlab_project_id: undefined,
      });
    });

    it('should delete project successfully', async () => {
      // First load initial projects
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
      });

      mockProjectService.deleteProject.mockResolvedValueOnce({
        success: true,
        data: {}
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load and auto-selection
      await waitFor(() => {
        expect(result.current.selectedProject).toBeTruthy();
      });

      let deleteResult;
      await act(async () => {
        deleteResult = await result.current.handleDeleteProject('proj-1');
      });

      expect(deleteResult).toBe(true);
      expect(result.current.projects).toHaveLength(0);
      expect(result.current.selectedProject).toBeNull();
      expect(mockProjectService.deleteProject).toHaveBeenCalledWith('proj-1');
    });
  });

  describe('task management operations', () => {
    it('should create new task successfully', async () => {
      // Setup initial state with selected project
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
      });

      mockTaskService.getTasks.mockResolvedValueOnce({
        success: true,
        data: { tasks: [], total: 0, page: 1, total_pages: 1 }
      });

      const newTask = { ...mockTask, id: 'new-task-1', title: 'New Task' };
      mockTaskService.createTask.mockResolvedValueOnce({
        success: true,
        data: newTask
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.selectedProject).toBeTruthy();
      });

      const taskData = {
        title: 'New Task',
        description: 'New task description',
        project_id: 'proj-1'
      };

      let createdTask;
      await act(async () => {
        createdTask = await result.current.handleNewTask(taskData);
      });

      expect(createdTask).toBeTruthy();
      expect(mockTaskService.createTask).toHaveBeenCalledWith({
        ...taskData,
        created_by: 'current-user'
      });
      expect(result.current.tasks).toContainEqual(
        expect.objectContaining({ title: 'New Task' })
      );
    });

    it('should update task successfully', async () => {
      // Setup initial state
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
      });

      mockTaskService.getTasks.mockResolvedValueOnce({
        success: true,
        data: { tasks: [mockTask], total: 1, page: 1, total_pages: 1 }
      });

      const updatedTask = { ...mockTask, title: 'Updated Task' };
      mockTaskService.updateTask.mockResolvedValueOnce({
        success: true,
        data: updatedTask
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.tasks).toHaveLength(1);
      });

      // Convert to frontend format for update
      const frontendTask = {
        id: 'task-1',
        title: 'Updated Task',
        description: 'Test task description',
        project_id: 'proj-1',
        status: 'TODO' as const,
        priority: 'MEDIUM' as const,
        parent_id: undefined,
        estimated_minutes: undefined,
        actual_minutes: undefined,
        dependencies: [],
        due_date: undefined,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        assignee: undefined,
        tags: [],
        attachments: [],
        notes: '',
        completion_percentage: undefined,
        metadata: {},
        motion_task_id: undefined,
        linear_issue_id: undefined,
        notion_task_id: undefined,
        gitlab_issue_id: undefined,
      };

      let result_;
      await act(async () => {
        result_ = await result.current.handleUpdateTask(frontendTask);
      });

      expect(result_).toBeTruthy();
      expect(mockTaskService.updateTask).toHaveBeenCalledWith('task-1', {
        title: 'Updated Task',
        description: 'Test task description',
        status: 'todo',
        priority: 'medium',
        tags: [],
        estimated_minutes: undefined,
        actual_minutes: undefined,
        due_date: undefined,
        assignee: undefined,
        parent_id: undefined,
        completion_percentage: undefined,
        dependencies: [],
        notes: undefined,
        metadata: {},
        motion_task_id: undefined,
        linear_issue_id: undefined,
        notion_task_id: undefined,
        gitlab_issue_id: undefined,
      });
    });
  });

  describe('project selection and task loading', () => {
    it('should load tasks when project is selected', async () => {
      const { result } = renderHook(() => useProjectManagement());

      const mockTaskResponse: TaskListResponse = {
        tasks: [mockTask],
        total: 1,
        page: 1,
        total_pages: 1
      };

      mockTaskService.getTasks.mockResolvedValueOnce({
        success: true,
        data: mockTaskResponse
      });

      const testProject = {
        id: 'proj-1',
        name: 'Test Project',
        description: 'Test description',
        status: 'ACTIVE' as const,
        priority: 'HIGH' as const,
        tags: ['test'],
        due_date: '',
        start_date: '',
        motion_project_link: null,
        linear_project_link: null,
        notion_page_link: null,
        gitlab_project_link: null,
      };

      await act(async () => {
        await result.current.handleProjectSelect(testProject);
      });

      await waitFor(() => {
        expect(result.current.tasks).toHaveLength(1);
      });

      expect(result.current.selectedProject).toEqual(testProject);
      expect(result.current.selectedTask).toBeNull();
      expect(mockTaskService.getTasks).toHaveBeenCalledWith({ project_id: 'proj-1' });
    });

    it('should handle task selection', () => {
      const { result } = renderHook(() => useProjectManagement());

      const testTask = {
        id: 'task-1',
        title: 'Test Task',
        description: '',
        project_id: 'proj-1',
        status: 'TODO' as const,
        priority: 'MEDIUM' as const,
        parent_id: undefined,
        estimated_minutes: undefined,
        actual_minutes: undefined,
        dependencies: [],
        due_date: undefined,
        created_at: '2025-01-01T00:00:00Z',
        updated_at: '2025-01-01T00:00:00Z',
        assignee: undefined,
        tags: [],
        attachments: [],
        notes: '',
        completion_percentage: undefined,
        metadata: {},
        motion_task_id: undefined,
        linear_issue_id: undefined,
        notion_task_id: undefined,
        gitlab_issue_id: undefined,
      };

      act(() => {
        result.current.handleTaskSelect(testTask);
      });

      expect(result.current.selectedTask).toEqual(testTask);
    });
  });

  describe('error handling and loading states', () => {
    it('should handle project loading error', async () => {
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: false,
        error: 'Failed to load projects'
      });

      const { result } = renderHook(() => useProjectManagement());

      await waitFor(() => {
        expect(result.current.error).toBe('Failed to load projects');
      });

      expect(result.current.projects).toHaveLength(0);
    });

    it('should manage loading states correctly', async () => {
      // Mock a delayed response
      mockProjectService.getProjects.mockImplementationOnce(
        () => new Promise(resolve => setTimeout(() => resolve({
          success: true,
          data: { projects: [], total: 0, page: 1, total_pages: 1 }
        }), 100))
      );

      const { result } = renderHook(() => useProjectManagement());

      expect(result.current.projectsLoading).toBe(true);

      await waitFor(() => {
        expect(result.current.projectsLoading).toBe(false);
      });
    });

    it('should clear error state', async () => {
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: false,
        error: 'Test error'
      });

      const { result } = renderHook(() => useProjectManagement());

      await waitFor(() => {
        expect(result.current.error).toBe('Test error');
      });

      act(() => {
        result.current.clearError();
      });

      expect(result.current.error).toBeNull();
    });
  });

  describe('utility functions', () => {
    it('should get tasks for specific project', async () => {
      // Setup with multiple projects and tasks
      mockProjectService.getProjects.mockResolvedValueOnce({
        success: true,
        data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
      });

      const task1 = { ...mockTask, id: 'task-1', project_id: 'proj-1' };
      const task2 = { ...mockTask, id: 'task-2', project_id: 'proj-2' };

      mockTaskService.getTasks.mockResolvedValueOnce({
        success: true,
        data: { tasks: [task1], total: 1, page: 1, total_pages: 1 }
      });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.tasks).toHaveLength(1);
      });

      // Test getTasksForProject with the existing task
      const proj1Tasks = result.current.getTasksForProject('proj-1');
      expect(proj1Tasks).toHaveLength(1);
      expect(proj1Tasks[0].id).toBe('task-1');
      
      // Test with non-existent project
      const noTasks = result.current.getTasksForProject('proj-nonexistent');
      expect(noTasks).toHaveLength(0);
    });

    it('should toggle project collapse state', () => {
      const { result } = renderHook(() => useProjectManagement());

      expect(result.current.isProjectCollapsed).toBe(false);

      act(() => {
        result.current.handleToggleProjectCollapse();
      });

      expect(result.current.isProjectCollapsed).toBe(true);
    });

    it('should refresh data', async () => {
      // Setup initial load
      mockProjectService.getProjects
        .mockResolvedValueOnce({
          success: true,
          data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
        })
        .mockResolvedValueOnce({
          success: true,
          data: { projects: [mockProject], total: 1, page: 1, total_pages: 1 }
        });

      mockTaskService.getTasks
        .mockResolvedValueOnce({
          success: true,
          data: { tasks: [mockTask], total: 1, page: 1, total_pages: 1 }
        })
        .mockResolvedValueOnce({
          success: true,
          data: { tasks: [mockTask], total: 1, page: 1, total_pages: 1 }
        });

      const { result } = renderHook(() => useProjectManagement());

      // Wait for initial load
      await waitFor(() => {
        expect(result.current.selectedProject).toBeTruthy();
      });

      // Clear mocks to verify refresh calls
      vi.clearAllMocks();

      await act(async () => {
        await result.current.refresh();
      });

      expect(mockProjectService.getProjects).toHaveBeenCalledTimes(1);
      expect(mockTaskService.getTasks).toHaveBeenCalledTimes(1);
    });
  });
});