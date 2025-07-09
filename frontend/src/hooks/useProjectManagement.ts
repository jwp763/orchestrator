import { useState } from 'react';
import type { Project, Task, Change } from '../types';

export const useProjectManagement = (initialProjects: Project[], initialTasks: Task[]) => {
  const [projects, setProjects] = useState<Project[]>(initialProjects);
  const [tasks, setTasks] = useState<Task[]>(initialTasks);
  const [selectedProject, setSelectedProject] = useState<Project | null>(
    initialProjects.length > 0 ? initialProjects[0] : null
  );
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isProjectCollapsed, setIsProjectCollapsed] = useState(false);

  const handleProjectSelect = (project: Project) => {
    setSelectedProject(project);
    setSelectedTask(null);
  };

  const handleTaskSelect = (task: Task | null) => {
    setSelectedTask(task);
  };

  const handleNewProject = () => {
    // In a real app, this would open a modal or form
    console.log('New project requested');
  };

  const handleUpdateProject = (updatedProject: Project) => {
    setProjects(projects.map(p => p.id === updatedProject.id ? updatedProject : p));
    if (selectedProject?.id === updatedProject.id) {
      setSelectedProject(updatedProject);
    }
  };

  const handleUpdateTask = (updatedTask: Task) => {
    setTasks(tasks.map(t => t.id === updatedTask.id ? updatedTask : t));
    if (selectedTask?.id === updatedTask.id) {
      setSelectedTask(updatedTask);
    }
  };

  const handleApplyChanges = (changes: Change[]) => {
    changes.forEach(change => {
      if (change.type === 'project' && selectedProject) {
        const updatedProject = { ...selectedProject, [change.field]: change.newValue };
        handleUpdateProject(updatedProject);
      } else if (change.type === 'task' && change.taskId) {
        const task = tasks.find(t => t.id === change.taskId);
        if (task) {
          const updatedTask = { ...task, [change.field]: change.newValue };
          handleUpdateTask(updatedTask);
        }
      }
    });
  };

  const handleToggleProjectCollapse = () => {
    setIsProjectCollapsed(!isProjectCollapsed);
  };

  const getTasksForProject = (projectId: string): Task[] => {
    return tasks.filter(task => task.project_id === projectId);
  };

  return {
    // State
    projects,
    tasks,
    selectedProject,
    selectedTask,
    isProjectCollapsed,
    
    // Actions
    handleProjectSelect,
    handleTaskSelect,
    handleNewProject,
    handleUpdateProject,
    handleUpdateTask,
    handleApplyChanges,
    handleToggleProjectCollapse,
    
    // Utilities
    getTasksForProject,
  };
};