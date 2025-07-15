import { useState, useEffect, useCallback } from 'react';
import type { Project, Task, Change } from '../types';
import { projectService } from '../services/projectService';
import { taskService } from '../services/taskService';
import { applyChanges } from '../utils/patchApplicator';
import type { 
  ProjectResponse, 
  TaskResponse, 
  ProjectCreateRequest, 
  TaskCreateRequest,
  ProjectUpdateRequest,
  TaskUpdateRequest 
} from '../types/api';

export const useProjectManagement = () => {
  // State management
  const [projects, setProjects] = useState<Project[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isProjectCollapsed, setIsProjectCollapsed] = useState(false);
  
  // Loading and error states
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [projectsLoading, setProjectsLoading] = useState(false);
  const [tasksLoading, setTasksLoading] = useState(false);

  // Convert API response to frontend types
  const convertProjectResponse = (projectResponse: ProjectResponse): Project => ({
    id: projectResponse.id,
    name: projectResponse.name,
    description: projectResponse.description || '',
    status: projectResponse.status.toUpperCase() as any,
    priority: projectResponse.priority.toUpperCase() as any,
    tags: projectResponse.tags,
    due_date: projectResponse.due_date || '',
    start_date: projectResponse.start_date || '',
    motion_project_link: projectResponse.motion_project_id || null,
    linear_project_link: projectResponse.linear_project_id || null,
    notion_page_link: projectResponse.notion_page_id || null,
    gitlab_project_link: projectResponse.gitlab_project_id || null,
  });

  const convertTaskResponse = (taskResponse: TaskResponse): Task => ({
    id: taskResponse.id,
    title: taskResponse.title,
    description: taskResponse.description || '',
    project_id: taskResponse.project_id,
    status: taskResponse.status.toUpperCase().replace('-', '_') as any,
    priority: taskResponse.priority.toUpperCase() as any,
    parent_id: taskResponse.parent_id,
    estimated_minutes: taskResponse.estimated_minutes,
    actual_minutes: taskResponse.actual_minutes,
    dependencies: taskResponse.dependencies,
    due_date: taskResponse.due_date,
    created_at: taskResponse.created_at,
    updated_at: taskResponse.updated_at,
    assignee: taskResponse.assignee,
    tags: taskResponse.tags,
    attachments: taskResponse.attachments.map(a => String(a)),
    notes: taskResponse.notes || '',
    completion_percentage: taskResponse.completion_percentage,
    metadata: taskResponse.metadata,
    motion_task_id: taskResponse.motion_task_id || undefined,
    linear_issue_id: taskResponse.linear_issue_id || undefined,
    notion_task_id: taskResponse.notion_task_id || undefined,
    gitlab_issue_id: taskResponse.gitlab_issue_id || undefined,
  });

  // Load all projects
  const loadProjects = useCallback(async () => {
    setProjectsLoading(true);
    setError(null);
    try {
      const response = await projectService.getProjects();
      if (response.success) {
        const convertedProjects = response.data.projects.map(convertProjectResponse);
        setProjects(convertedProjects);
        
        // Auto-select first project if none selected
        if (!selectedProject && convertedProjects.length > 0) {
          setSelectedProject(convertedProjects[0]);
        }
      } else {
        setError(response.error || 'Failed to load projects');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load projects');
    } finally {
      setProjectsLoading(false);
    }
  }, [selectedProject]);

  // Load tasks for selected project
  const loadTasks = useCallback(async (projectId?: string) => {
    if (!projectId) return;
    
    setTasksLoading(true);
    setError(null);
    try {
      const response = await taskService.getTasks({ project_id: projectId });
      if (response.success) {
        const convertedTasks = response.data.tasks.map(convertTaskResponse);
        setTasks(convertedTasks);
      } else {
        setError(response.error || 'Failed to load tasks');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load tasks');
    } finally {
      setTasksLoading(false);
    }
  }, []);

  // Load initial data
  useEffect(() => {
    loadProjects();
  }, [loadProjects]);

  // Load tasks when project changes
  useEffect(() => {
    if (selectedProject) {
      loadTasks(selectedProject.id);
    }
  }, [selectedProject, loadTasks]);

  // Project selection handler
  const handleProjectSelect = useCallback(async (project: Project) => {
    setSelectedProject(project);
    setSelectedTask(null);
  }, []);

  // Task selection handler
  const handleTaskSelect = useCallback((task: Task | null) => {
    setSelectedTask(task);
  }, []);

  // Create new project
  const handleNewProject = useCallback(async (projectData: Omit<ProjectCreateRequest, 'created_by'>) => {
    setIsLoading(true);
    setError(null);
    try {
      const request: ProjectCreateRequest = {
        ...projectData,
        created_by: 'current-user', // TODO: Replace with actual user ID
      };
      
      const response = await projectService.createProject(request);
      if (response.success) {
        const newProject = convertProjectResponse(response.data);
        setProjects(prev => [...prev, newProject]);
        setSelectedProject(newProject);
        return newProject;
      } else {
        setError(response.error || 'Failed to create project');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create project');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update project
  const handleUpdateProject = useCallback(async (updatedProject: Project) => {
    setIsLoading(true);
    setError(null);
    try {
      const updateData: ProjectUpdateRequest = {
        name: updatedProject.name,
        description: updatedProject.description || undefined,
        status: updatedProject.status.toLowerCase() as any,
        priority: updatedProject.priority.toLowerCase() as any,
        tags: updatedProject.tags,
        due_date: updatedProject.due_date || undefined,
        start_date: updatedProject.start_date || undefined,
        motion_project_id: updatedProject.motion_project_link || undefined,
        linear_project_id: updatedProject.linear_project_link || undefined,
        notion_page_id: updatedProject.notion_page_link || undefined,
        gitlab_project_id: updatedProject.gitlab_project_link || undefined,
      };

      const response = await projectService.updateProject(updatedProject.id, updateData);
      if (response.success) {
        const updated = convertProjectResponse(response.data);
        setProjects(prev => prev.map(p => p.id === updated.id ? updated : p));
        if (selectedProject?.id === updated.id) {
          setSelectedProject(updated);
        }
        return updated;
      } else {
        setError(response.error || 'Failed to update project');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update project');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [selectedProject]);

  // Create new task
  const handleNewTask = useCallback(async (taskData: Omit<TaskCreateRequest, 'created_by'>) => {
    setIsLoading(true);
    setError(null);
    try {
      const request: TaskCreateRequest = {
        ...taskData,
        created_by: 'current-user', // TODO: Replace with actual user ID
      };
      
      const response = await taskService.createTask(request);
      if (response.success) {
        const newTask = convertTaskResponse(response.data);
        setTasks(prev => [...prev, newTask]);
        return newTask;
      } else {
        setError(response.error || 'Failed to create task');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Update task
  const handleUpdateTask = useCallback(async (updatedTask: Task) => {
    setIsLoading(true);
    setError(null);
    try {
      const updateData: TaskUpdateRequest = {
        title: updatedTask.title,
        description: updatedTask.description || undefined,
        status: updatedTask.status.toLowerCase().replace('_', '-') as any,
        priority: updatedTask.priority.toLowerCase() as any,
        tags: updatedTask.tags,
        estimated_minutes: updatedTask.estimated_minutes || undefined,
        actual_minutes: updatedTask.actual_minutes,
        due_date: updatedTask.due_date || undefined,
        assignee: updatedTask.assignee || undefined,
        parent_id: updatedTask.parent_id || undefined,
        completion_percentage: updatedTask.completion_percentage,
        dependencies: updatedTask.dependencies,
        notes: updatedTask.notes || undefined,
        metadata: updatedTask.metadata,
        motion_task_id: updatedTask.motion_task_id || undefined,
        linear_issue_id: updatedTask.linear_issue_id || undefined,
        notion_task_id: updatedTask.notion_task_id || undefined,
        gitlab_issue_id: updatedTask.gitlab_issue_id || undefined,
      };

      const response = await taskService.updateTask(updatedTask.id, updateData);
      if (response.success) {
        const updated = convertTaskResponse(response.data);
        setTasks(prev => prev.map(t => t.id === updated.id ? updated : t));
        if (selectedTask?.id === updated.id) {
          setSelectedTask(updated);
        }
        return updated;
      } else {
        setError(response.error || 'Failed to update task');
        return null;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [selectedTask]);

  // Delete project
  const handleDeleteProject = useCallback(async (projectId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await projectService.deleteProject(projectId);
      if (response.success) {
        setProjects(prev => prev.filter(p => p.id !== projectId));
        if (selectedProject?.id === projectId) {
          setSelectedProject(null);
          setTasks([]);
        }
        return true;
      } else {
        setError(response.error || 'Failed to delete project');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete project');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [selectedProject]);

  // Delete task
  const handleDeleteTask = useCallback(async (taskId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await taskService.deleteTask(taskId);
      if (response.success) {
        setTasks(prev => prev.filter(t => t.id !== taskId));
        if (selectedTask?.id === taskId) {
          setSelectedTask(null);
        }
        return true;
      } else {
        setError(response.error || 'Failed to delete task');
        return false;
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
      return false;
    } finally {
      setIsLoading(false);
    }
  }, [selectedTask]);

  // Apply changes from natural language editor
  const handleApplyChanges = useCallback(async (changes: Change[]) => {
    setError(null);
    setIsLoading(true);
    
    try {
      const result = await applyChanges(changes, {
        selectedProject,
        existingTasks: tasks,
        currentUser: 'user@example.com' // TODO: Get from auth context
      });
      
      if (result.success) {
        // Update local state with created/updated items
        if (result.createdProjects.length > 0) {
          setProjects(prev => [...prev, ...result.createdProjects]);
          // If we created a project and don't have one selected, select the first one
          if (!selectedProject && result.createdProjects.length > 0) {
            setSelectedProject(result.createdProjects[0]);
          }
        }
        
        if (result.updatedProjects.length > 0) {
          setProjects(prev => prev.map(p => {
            const updated = result.updatedProjects.find(up => up.id === p.id);
            return updated || p;
          }));
          
          // Update selected project if it was updated
          const updatedSelectedProject = result.updatedProjects.find(p => p.id === selectedProject?.id);
          if (updatedSelectedProject) {
            setSelectedProject(updatedSelectedProject);
          }
        }
        
        if (result.createdTasks.length > 0) {
          setTasks(prev => [...prev, ...result.createdTasks]);
        }
        
        if (result.updatedTasks.length > 0) {
          setTasks(prev => prev.map(t => {
            const updated = result.updatedTasks.find(ut => ut.id === t.id);
            return updated || t;
          }));
        }
        
        // Refresh to ensure consistency
        await loadProjects();
        if (selectedProject) {
          await loadTasks(selectedProject.id);
        }
      } else {
        setError(result.errors.join(', '));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply changes');
    } finally {
      setIsLoading(false);
    }
  }, [selectedProject, tasks, loadProjects, loadTasks]);

  // Toggle project collapse
  const handleToggleProjectCollapse = useCallback(() => {
    setIsProjectCollapsed(prev => !prev);
  }, []);

  // Get tasks for project
  const getTasksForProject = useCallback((projectId: string): Task[] => {
    return tasks.filter(task => task.project_id === projectId);
  }, [tasks]);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Refresh data
  const refresh = useCallback(async () => {
    await loadProjects();
    if (selectedProject) {
      await loadTasks(selectedProject.id);
    }
  }, [loadProjects, loadTasks, selectedProject]);

  return {
    // State
    projects,
    tasks,
    selectedProject,
    selectedTask,
    isProjectCollapsed,
    
    // Loading states
    isLoading,
    projectsLoading,
    tasksLoading,
    error,
    
    // Actions
    handleProjectSelect,
    handleTaskSelect,
    handleNewProject,
    handleUpdateProject,
    handleNewTask,
    handleUpdateTask,
    handleDeleteProject,
    handleDeleteTask,
    handleApplyChanges,
    handleToggleProjectCollapse,
    clearError,
    refresh,
    
    // Utilities
    getTasksForProject,
  };
};