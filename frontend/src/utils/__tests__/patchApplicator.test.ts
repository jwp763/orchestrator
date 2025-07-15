import { describe, it, expect, vi, beforeEach } from 'vitest';
import { applyChanges } from '../patchApplicator';
import type { Change, Project, Task } from '../../types';
import { projectService } from '../../services/projectService';
import { taskService } from '../../services/taskService';

// Mock the services
vi.mock('../../services/projectService', () => ({
  projectService: {
    createProject: vi.fn(),
    updateProject: vi.fn(),
  },
}));

vi.mock('../../services/taskService', () => ({
  taskService: {
    createTask: vi.fn(),
    updateTask: vi.fn(),
  },
}));

describe('patchApplicator', () => {
  const mockProject: Project = {
    id: 'proj-123',
    name: 'Test Project',
    description: 'Test description',
    status: 'ACTIVE',
    priority: 'HIGH',
    tags: ['test'],
    due_date: '2025-12-31',
    start_date: '2025-01-01',
    motion_project_link: null,
    linear_project_link: null,
    notion_page_link: null,
    gitlab_project_link: null,
  };

  const mockTask: Task = {
    id: 'task-123',
    title: 'Test Task',
    description: 'Test task description',
    project_id: 'proj-123',
    status: 'TODO',
    priority: 'MEDIUM',
    tags: ['test'],
    estimated_minutes: 60,
    actual_minutes: 0,
    due_date: '2025-12-31',
    assignee: 'user@example.com',
    parent_id: null,
    depth: 0,
    sort_order: 0,
    completion_percentage: 0,
    dependencies: [],
    attachments: [],
    notes: '',
    metadata: {},
    motion_task_link: null,
    linear_task_link: null,
    notion_task_link: null,
    gitlab_task_link: null,
  };

  const mockContext = {
    selectedProject: mockProject,
    existingTasks: [mockTask],
    currentUser: 'user@example.com',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('applyChanges', () => {
    it('should handle empty changes array', async () => {
      const result = await applyChanges([], mockContext);

      expect(result).toEqual({
        success: true,
        createdProjects: [],
        createdTasks: [],
        updatedProjects: [],
        updatedTasks: [],
        errors: [],
      });
    });

    it('should create new project from changes', async () => {
      const changes: Change[] = [
        {
          type: 'project',
          field: 'name',
          oldValue: null,
          newValue: 'New Project',
          display: 'Create project: New Project',
        },
        {
          type: 'project',
          field: 'description',
          oldValue: null,
          newValue: 'New project description',
          display: 'Set description: New project description',
        },
        {
          type: 'project',
          field: 'priority',
          oldValue: null,
          newValue: 'high',
          display: 'Set priority: high',
        },
      ];

      const mockCreatedProject = {
        id: 'proj-456',
        name: 'New Project',
        description: 'New project description',
        status: 'planning',
        priority: 'high',
        tags: [],
      };

      vi.mocked(projectService.createProject).mockResolvedValue(mockCreatedProject);

      const result = await applyChanges(changes, {
        ...mockContext,
        selectedProject: null, // No existing project
      });

      expect(result.success).toBe(true);
      expect(result.createdProjects).toHaveLength(1);
      expect(result.createdProjects[0].name).toBe('New Project');
      expect(projectService.createProject).toHaveBeenCalledWith({
        created_by: 'user@example.com',
        name: 'New Project',
        description: 'New project description',
        status: 'planning',
        priority: 'high',
        tags: [],
      });
    });

    it('should update existing project from changes', async () => {
      const changes: Change[] = [
        {
          type: 'project',
          field: 'name',
          oldValue: 'Old Name',
          newValue: 'Updated Name',
          display: 'Update name: Updated Name',
        },
        {
          type: 'project',
          field: 'priority',
          oldValue: 'medium',
          newValue: 'high',
          display: 'Update priority: high',
        },
      ];

      const mockUpdatedProject = {
        ...mockProject,
        name: 'Updated Name',
        priority: 'high',
      };

      vi.mocked(projectService.updateProject).mockResolvedValue(mockUpdatedProject);

      const result = await applyChanges(changes, mockContext);

      expect(result.success).toBe(true);
      expect(result.updatedProjects).toHaveLength(1);
      expect(result.updatedProjects[0].name).toBe('Updated Name');
      expect(projectService.updateProject).toHaveBeenCalledWith('proj-123', {
        name: 'Updated Name',
        priority: 'high',
      });
    });

    it('should create new task from changes', async () => {
      const changes: Change[] = [
        {
          type: 'task',
          taskId: 'task-1', // Placeholder ID
          field: 'title',
          oldValue: null,
          newValue: 'New Task',
          display: 'Create task: New Task',
        },
        {
          type: 'task',
          taskId: 'task-1',
          field: 'description',
          oldValue: null,
          newValue: 'Task description',
          display: 'Set description: Task description',
        },
        {
          type: 'task',
          taskId: 'task-1',
          field: 'priority',
          oldValue: null,
          newValue: 'high',
          display: 'Set priority: high',
        },
      ];

      const mockCreatedTask = {
        id: 'task-456',
        title: 'New Task',
        description: 'Task description',
        project_id: 'proj-123',
        status: 'todo',
        priority: 'high',
      };

      vi.mocked(taskService.createTask).mockResolvedValue(mockCreatedTask);

      const result = await applyChanges(changes, mockContext);

      expect(result.success).toBe(true);
      expect(result.createdTasks).toHaveLength(1);
      expect(result.createdTasks[0].title).toBe('New Task');
      expect(taskService.createTask).toHaveBeenCalledWith({
        project_id: 'proj-123',
        created_by: 'user@example.com',
        title: 'New Task',
        description: 'Task description',
        status: 'todo',
        priority: 'high',
        tags: [],
        estimated_minutes: 0,
        completion_percentage: 0,
        dependencies: [],
        metadata: {},
      });
    });

    it('should update existing task from changes', async () => {
      const changes: Change[] = [
        {
          type: 'task',
          taskId: 'task-123', // Real task ID
          field: 'title',
          oldValue: 'Old Title',
          newValue: 'Updated Title',
          display: 'Update title: Updated Title',
        },
        {
          type: 'task',
          taskId: 'task-123',
          field: 'status',
          oldValue: 'todo',
          newValue: 'in_progress',
          display: 'Update status: in_progress',
        },
      ];

      const mockUpdatedTask = {
        ...mockTask,
        title: 'Updated Title',
        status: 'in_progress',
      };

      vi.mocked(taskService.updateTask).mockResolvedValue(mockUpdatedTask);

      const result = await applyChanges(changes, mockContext);

      expect(result.success).toBe(true);
      expect(result.updatedTasks).toHaveLength(1);
      expect(result.updatedTasks[0].title).toBe('Updated Title');
      expect(taskService.updateTask).toHaveBeenCalledWith('task-123', {
        title: 'Updated Title',
        status: 'in_progress',
      });
    });

    it('should handle mixed project and task changes', async () => {
      const changes: Change[] = [
        {
          type: 'project',
          field: 'name',
          oldValue: 'Old Name',
          newValue: 'Updated Name',
          display: 'Update name: Updated Name',
        },
        {
          type: 'task',
          taskId: 'task-1',
          field: 'title',
          oldValue: null,
          newValue: 'New Task',
          display: 'Create task: New Task',
        },
      ];

      const mockUpdatedProject = { ...mockProject, name: 'Updated Name' };
      const mockCreatedTask = { id: 'task-456', title: 'New Task', project_id: 'proj-123' };

      vi.mocked(projectService.updateProject).mockResolvedValue(mockUpdatedProject);
      vi.mocked(taskService.createTask).mockResolvedValue(mockCreatedTask);

      const result = await applyChanges(changes, mockContext);

      expect(result.success).toBe(true);
      expect(result.updatedProjects).toHaveLength(1);
      expect(result.createdTasks).toHaveLength(1);
      expect(projectService.updateProject).toHaveBeenCalled();
      expect(taskService.createTask).toHaveBeenCalled();
    });

    it('should handle errors gracefully', async () => {
      const changes: Change[] = [
        {
          type: 'project',
          field: 'name',
          oldValue: null,
          newValue: 'New Project',
          display: 'Create project: New Project',
        },
      ];

      vi.mocked(projectService.createProject).mockRejectedValue(new Error('API Error'));

      const result = await applyChanges(changes, {
        ...mockContext,
        selectedProject: null,
      });

      expect(result.success).toBe(false);
      expect(result.errors).toContain('Project operation failed: API Error');
    });

    it('should fail when creating task without selected project', async () => {
      const changes: Change[] = [
        {
          type: 'task',
          taskId: 'task-1',
          field: 'title',
          oldValue: null,
          newValue: 'New Task',
          display: 'Create task: New Task',
        },
      ];

      const result = await applyChanges(changes, {
        ...mockContext,
        selectedProject: null,
      });

      expect(result.success).toBe(false);
      expect(result.errors).toContain('Task operation failed: Cannot create task without a selected project');
    });

    it('should handle task not found for updates', async () => {
      const changes: Change[] = [
        {
          type: 'task',
          taskId: 'nonexistent-task',
          field: 'title',
          oldValue: 'Old Title',
          newValue: 'New Title',
          display: 'Update title: New Title',
        },
      ];

      const result = await applyChanges(changes, mockContext);

      expect(result.success).toBe(false);
      expect(result.errors).toContain('Task not found: nonexistent-task');
    });
  });
});