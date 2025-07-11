import { renderHook, act, waitFor } from '@testing-library/react';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useProjectManagement } from './useProjectManagement';
import { mockProjects, mockTasks } from '../mocks';

// Mock the services
vi.mock('../services/projectService', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn(),
  },
}));

vi.mock('../services/taskService', () => ({
  taskService: {
    getTasks: vi.fn(),
    createTask: vi.fn(),
    updateTask: vi.fn(),
    deleteTask: vi.fn(),
  },
}));

import { projectService } from '../services/projectService';
import { taskService } from '../services/taskService';

describe('useProjectManagement', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Setup default mock responses
    (projectService.getProjects as any).mockResolvedValue({
      success: true,
      data: {
        projects: [
          {
            id: '1',
            name: 'Test Project',
            description: 'Test Description',
            status: 'planning',
            priority: 'medium',
            tags: [],
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
            due_date: null,
            start_date: null,
            created_by: 'test-user',
          },
        ],
        total: 1,
        page: 1,
        per_page: 20,
        has_next: false,
        has_prev: false,
      },
    });
    
    (taskService.getTasks as any).mockResolvedValue({
      success: true,
      data: {
        tasks: [],
        total: 0,
        page: 1,
        per_page: 20,
        has_next: false,
        has_prev: false,
      },
    });
  });

  it('initializes with empty state and loads projects', async () => {
    const { result } = renderHook(() => useProjectManagement());

    // Initially should be empty
    expect(result.current.projects).toEqual([]);
    expect(result.current.tasks).toEqual([]);
    expect(result.current.selectedProject).toBeNull();
    expect(result.current.selectedTask).toBeNull();
    expect(result.current.isProjectCollapsed).toBe(false);

    // Wait for projects to load
    await waitFor(() => {
      expect(result.current.projects).toHaveLength(1);
    });

    expect(result.current.projects[0].name).toBe('Test Project');
    expect(result.current.selectedProject).toStrictEqual(result.current.projects[0]);
  });

  it('handles project selection', async () => {
    const { result } = renderHook(() => useProjectManagement());

    // Wait for initial load
    await waitFor(() => {
      expect(result.current.projects).toHaveLength(1);
    });

    const secondProject = { 
      ...result.current.projects[0], 
      id: '2', 
      name: 'Second Project' 
    };

    act(() => {
      result.current.handleProjectSelect(secondProject);
    });

    expect(result.current.selectedProject).toEqual(secondProject);
  });

  it('handles task selection', async () => {
    const { result } = renderHook(() => useProjectManagement());

    const testTask = {
      id: '1',
      project_id: '1',
      title: 'Test Task',
      description: 'Test Description',
      status: 'todo' as const,
      priority: 'medium' as const,
      tags: [],
      sort_order: 0,
      completion_percentage: 0,
      dependencies: [],
      metadata: {},
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      created_by: 'test-user',
    };

    act(() => {
      result.current.handleTaskSelect(testTask);
    });

    expect(result.current.selectedTask).toEqual(testTask);
  });

  it('handles project updates', async () => {
    const { result } = renderHook(() => useProjectManagement());

    // Mock update response
    (projectService.updateProject as any).mockResolvedValue({
      success: true,
      data: {
        id: '1',
        name: 'Updated Project',
        description: 'Updated Description',
        status: 'active',
        priority: 'high',
        tags: [],
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        due_date: null,
        start_date: null,
        created_by: 'test-user',
      },
    });

    // Wait for initial load
    await waitFor(() => {
      expect(result.current.projects).toHaveLength(1);
    });

    const updatedProject = {
      ...result.current.projects[0],
      name: 'Updated Project',
      description: 'Updated Description',
    };

    await act(async () => {
      await result.current.handleUpdateProject(updatedProject);
    });

    expect(projectService.updateProject).toHaveBeenCalledWith(
      updatedProject.id,
      expect.objectContaining({
        name: 'Updated Project',
        description: 'Updated Description',
      })
    );
  });

  it('handles task updates', async () => {
    const { result } = renderHook(() => useProjectManagement());

    // Mock update response
    (taskService.updateTask as any).mockResolvedValue({
      success: true,
      data: {
        id: '1',
        project_id: '1',
        title: 'Updated Task',
        description: 'Updated Description',
        status: 'in-progress',
        priority: 'high',
        tags: [],
        sort_order: 0,
        completion_percentage: 50,
        dependencies: [],
        metadata: {},
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
        created_by: 'test-user',
        attachments: [],
        notes: '',
        assignee: null,
        due_date: null,
        estimated_minutes: null,
        actual_minutes: null,
        parent_task_id: null,
        depth: 0,
        motion_task_id: null,
        linear_issue_id: null,
        notion_task_id: null,
        gitlab_issue_id: null,
      },
    });

    const updatedTask = {
      id: '1',
      project_id: '1',
      title: 'Updated Task',
      description: 'Updated Description',
      status: 'in-progress' as const,
      priority: 'high' as const,
      tags: [],
      sort_order: 0,
      completion_percentage: 50,
      dependencies: [],
      metadata: {},
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z',
      created_by: 'test-user',
    };

    await act(async () => {
      await result.current.handleUpdateTask(updatedTask);
    });

    expect(taskService.updateTask).toHaveBeenCalledWith(
      updatedTask.id,
      expect.objectContaining({
        title: 'Updated Task',
        description: 'Updated Description',
        status: 'in-progress',
        priority: 'high',
        completion_percentage: 50,
      })
    );
  });

  it('toggles project collapse state', async () => {
    const { result } = renderHook(() => useProjectManagement());

    expect(result.current.isProjectCollapsed).toBe(false);

    act(() => {
      result.current.handleToggleProjectCollapse();
    });

    expect(result.current.isProjectCollapsed).toBe(true);
  });

  it('gets tasks for a specific project', async () => {
    const { result } = renderHook(() => useProjectManagement());

    // Mock tasks response
    (taskService.getTasks as any).mockResolvedValue({
      success: true,
      data: {
        tasks: [
          {
            id: '1',
            project_id: '1',
            title: 'Task 1',
            description: 'Description 1',
            status: 'todo',
            priority: 'medium',
            tags: [],
            sort_order: 0,
            completion_percentage: 0,
            dependencies: [],
            metadata: {},
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
            created_by: 'test-user',
            attachments: [],
            notes: '',
            assignee: null,
            due_date: null,
            estimated_minutes: null,
            actual_minutes: null,
            parent_task_id: null,
            depth: 0,
            motion_task_id: null,
            linear_issue_id: null,
            notion_task_id: null,
            gitlab_issue_id: null,
          },
          {
            id: '2',
            project_id: '1',
            title: 'Task 2',
            description: 'Description 2',
            status: 'in_progress',
            priority: 'high',
            tags: [],
            sort_order: 1,
            completion_percentage: 25,
            dependencies: [],
            metadata: {},
            created_at: '2023-01-01T00:00:00Z',
            updated_at: '2023-01-01T00:00:00Z',
            created_by: 'test-user',
            attachments: [],
            notes: '',
            assignee: null,
            due_date: null,
            estimated_minutes: null,
            actual_minutes: null,
            parent_task_id: null,
            depth: 0,
            motion_task_id: null,
            linear_issue_id: null,
            notion_task_id: null,
            gitlab_issue_id: null,
          },
        ],
        total: 2,
        page: 1,
        per_page: 20,
        has_next: false,
        has_prev: false,
      },
    });

    // Wait for initial load and tasks to load
    await waitFor(() => {
      expect(result.current.tasks).toHaveLength(2);
    });

    const projectTasks = result.current.getTasksForProject('1');
    expect(projectTasks).toHaveLength(2);
  });

  it('handles empty initial data', async () => {
    // Mock empty responses
    (projectService.getProjects as any).mockResolvedValue({
      success: true,
      data: {
        projects: [],
        total: 0,
        page: 1,
        per_page: 20,
        has_next: false,
        has_prev: false,
      },
    });

    const { result } = renderHook(() => useProjectManagement());

    // Wait for load to complete
    await waitFor(() => {
      expect(result.current.projectsLoading).toBe(false);
    });

    expect(result.current.projects).toEqual([]);
    expect(result.current.tasks).toEqual([]);
    expect(result.current.selectedProject).toBeNull();
  });
});