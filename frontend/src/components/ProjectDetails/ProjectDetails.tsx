import React, { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, Check, X, Tag, Link } from 'lucide-react';
import type { Project, ProjectDetailsProps } from '../../types';
import { ProjectStatus, Priority } from '../../types';
import { getStatusColor, getPriorityColor } from '../../utils';

export const ProjectDetails: React.FC<ProjectDetailsProps> = ({ 
  project, 
  onUpdate, 
  isCollapsed, 
  onToggleCollapse 
}) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedProject, setEditedProject] = useState<Project>(project);

  useEffect(() => {
    setEditedProject(project);
  }, [project]);

  const handleSave = () => {
    onUpdate(editedProject);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedProject(project);
    setIsEditing(false);
  };

  return (
    <div className="bg-white border-b border-gray-200">
      <div className="p-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <button
              onClick={onToggleCollapse}
              className="p-1 hover:bg-gray-100 rounded"
              data-testid="collapse-toggle"
            >
              {isCollapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? (
                <input
                  type="text"
                  value={editedProject.name}
                  onChange={(e) => setEditedProject({ ...editedProject, name: e.target.value })}
                  className="border border-gray-300 rounded px-2 py-1"
                  data-testid="project-name-input"
                />
              ) : (
                project.name
              )}
            </h2>
          </div>
          <div className="flex items-center gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  className="p-2 text-green-600 hover:bg-green-50 rounded"
                  data-testid="save-button"
                >
                  <Check className="w-4 h-4" />
                </button>
                <button
                  onClick={handleCancel}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                  data-testid="cancel-button"
                >
                  <X className="w-4 h-4" />
                </button>
              </>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                data-testid="edit-button"
              >
                Edit
              </button>
            )}
          </div>
        </div>

        {!isCollapsed && (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
              {isEditing ? (
                <textarea
                  value={editedProject.description}
                  onChange={(e) => setEditedProject({ ...editedProject, description: e.target.value })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  rows={3}
                  data-testid="project-description-input"
                />
              ) : (
                <p className="text-gray-600">{project.description}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                {isEditing ? (
                  <select
                    value={editedProject.status}
                    onChange={(e) => setEditedProject({ ...editedProject, status: e.target.value as ProjectStatus })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    data-testid="project-status-select"
                  >
                    {Object.values(ProjectStatus).map(status => (
                      <option key={status} value={status}>{status}</option>
                    ))}
                  </select>
                ) : (
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(project.status)}`} />
                    <span>{project.status}</span>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                {isEditing ? (
                  <select
                    value={editedProject.priority}
                    onChange={(e) => setEditedProject({ ...editedProject, priority: e.target.value as Priority })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    data-testid="project-priority-select"
                  >
                    {Object.values(Priority).map(priority => (
                      <option key={priority} value={priority}>{priority}</option>
                    ))}
                  </select>
                ) : (
                  <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(project.priority)}`}>
                    {project.priority}
                  </span>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Start Date</label>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedProject.start_date || ''}
                    onChange={(e) => setEditedProject({ ...editedProject, start_date: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    data-testid="project-start-date-input"
                  />
                ) : (
                  <span className="text-gray-600">{project.start_date || 'Not set'}</span>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                {isEditing ? (
                  <input
                    type="date"
                    value={editedProject.due_date || ''}
                    onChange={(e) => setEditedProject({ ...editedProject, due_date: e.target.value })}
                    className="w-full border border-gray-300 rounded px-3 py-2"
                    data-testid="project-due-date-input"
                  />
                ) : (
                  <span className="text-gray-600">{project.due_date || 'Not set'}</span>
                )}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
              <div className="flex flex-wrap gap-2">
                {project.tags?.map((tag, index) => (
                  <span key={index} className="inline-flex items-center gap-1 px-2 py-1 bg-gray-100 text-gray-700 rounded-full text-sm">
                    <Tag className="w-3 h-3" />
                    {tag}
                  </span>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">External Links</label>
              <div className="flex flex-wrap gap-2">
                {project.motion_project_link && (
                  <a href={project.motion_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-600 rounded hover:bg-blue-100">
                    <Link className="w-3 h-3" />
                    Motion
                  </a>
                )}
                {project.linear_project_link && (
                  <a href={project.linear_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 text-purple-600 rounded hover:bg-purple-100">
                    <Link className="w-3 h-3" />
                    Linear
                  </a>
                )}
                {project.notion_page_link && (
                  <a href={project.notion_page_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                    <Link className="w-3 h-3" />
                    Notion
                  </a>
                )}
                {project.gitlab_project_link && (
                  <a href={project.gitlab_project_link} target="_blank" rel="noopener noreferrer" className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 text-orange-600 rounded hover:bg-orange-100">
                    <Link className="w-3 h-3" />
                    GitLab
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};