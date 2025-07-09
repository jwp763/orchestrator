import React from 'react';
import { Plus, AlertCircle } from 'lucide-react';
import type { Task, ProjectSidebarProps } from '../../types';
import { getStatusColor, getPriorityColor } from '../../utils';

interface ProjectSidebarInternalProps extends ProjectSidebarProps {
  tasks: Task[]; // Need tasks to calculate task count
}

export const ProjectSidebar: React.FC<ProjectSidebarInternalProps> = ({ 
  projects, 
  selectedProject, 
  onProjectSelect, 
  onAddProject,
  tasks 
}) => {
  const getTaskCount = (projectId: string): string => {
    const projectTasks = tasks.filter(t => t.project_id === projectId);
    const completedTasks = projectTasks.filter(t => t.status === 'DONE').length;
    return `${completedTasks}/${projectTasks.length}`;
  };

  return (
    <div className="w-64 bg-gray-50 border-r border-gray-200 h-full flex flex-col">
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={onAddProject}
          className="w-full flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          New Project
        </button>
      </div>
      <div className="flex-1 overflow-y-auto">
        {projects.map((project) => (
          <div
            key={project.id}
            data-testid="project-item"
            onClick={() => onProjectSelect(project)}
            className={`p-4 cursor-pointer hover:bg-gray-100 border-b border-gray-100 ${
              selectedProject?.id === project.id ? 'bg-blue-50 border-l-4 border-l-blue-600' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <h3 className="font-medium text-gray-900 truncate flex-1">{project.name}</h3>
              <div className={`w-2 h-2 rounded-full mt-1.5 ${getStatusColor(project.status)}`} />
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">{getTaskCount(project.id)} tasks</span>
              <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(project.priority)}`}>
                {project.priority}
              </span>
            </div>
            {project.due_date && new Date(project.due_date) < new Date() && (
              <div className="flex items-center gap-1 mt-2 text-red-600 text-xs">
                <AlertCircle className="w-3 h-3" />
                Overdue
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};