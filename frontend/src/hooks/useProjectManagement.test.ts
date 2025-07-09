import { renderHook, act } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { useProjectManagement } from './useProjectManagement';
import { mockProjects, mockTasks } from '../mocks';

describe('useProjectManagement', () => {
  it('initializes with provided projects and tasks', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    expect(result.current.projects).toEqual(mockProjects);
    expect(result.current.tasks).toEqual(mockTasks);
    expect(result.current.selectedProject).toEqual(mockProjects[0]);
    expect(result.current.selectedTask).toBeNull();
    expect(result.current.isProjectCollapsed).toBe(false);
  });

  it('handles project selection', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    act(() => {
      result.current.handleProjectSelect(mockProjects[1]);
    });

    expect(result.current.selectedProject).toEqual(mockProjects[1]);
    expect(result.current.selectedTask).toBeNull(); // Should clear selected task
  });

  it('handles task selection', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    act(() => {
      result.current.handleTaskSelect(mockTasks[0]);
    });

    expect(result.current.selectedTask).toEqual(mockTasks[0]);
  });

  it('handles project updates', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    const updatedProject = { ...mockProjects[0], name: 'Updated Project Name' };

    act(() => {
      result.current.handleUpdateProject(updatedProject);
    });

    expect(result.current.projects[0]).toEqual(updatedProject);
    expect(result.current.selectedProject).toEqual(updatedProject);
  });

  it('handles task updates', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    const updatedTask = { ...mockTasks[0], title: 'Updated Task Title' };

    act(() => {
      result.current.handleTaskSelect(mockTasks[0]);
    });

    act(() => {
      result.current.handleUpdateTask(updatedTask);
    });

    expect(result.current.tasks[0]).toEqual(updatedTask);
    expect(result.current.selectedTask).toEqual(updatedTask);
  });

  it('toggles project collapse state', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    expect(result.current.isProjectCollapsed).toBe(false);

    act(() => {
      result.current.handleToggleProjectCollapse();
    });

    expect(result.current.isProjectCollapsed).toBe(true);

    act(() => {
      result.current.handleToggleProjectCollapse();
    });

    expect(result.current.isProjectCollapsed).toBe(false);
  });

  it('gets tasks for a specific project', () => {
    const { result } = renderHook(() => useProjectManagement(mockProjects, mockTasks));

    const project1Tasks = result.current.getTasksForProject('1');
    const project2Tasks = result.current.getTasksForProject('2');

    expect(project1Tasks).toHaveLength(2);
    expect(project2Tasks).toHaveLength(1);
    expect(project1Tasks[0].project_id).toBe('1');
    expect(project2Tasks[0].project_id).toBe('2');
  });

  it('handles empty initial data', () => {
    const { result } = renderHook(() => useProjectManagement([], []));

    expect(result.current.projects).toEqual([]);
    expect(result.current.tasks).toEqual([]);
    expect(result.current.selectedProject).toBeNull();
    expect(result.current.selectedTask).toBeNull();
  });
});