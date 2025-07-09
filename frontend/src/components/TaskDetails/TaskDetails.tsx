import React, { useState, useEffect } from 'react';
import { Check, X, Tag, Link } from 'lucide-react';
import type { Task, TaskDetailsProps } from '../../types';
import { TaskStatus, Priority } from '../../types';
import { getStatusColor, getPriorityColor } from '../../utils';

export const TaskDetails: React.FC<TaskDetailsProps> = ({ task, onClose, onUpdate }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState<Task>(task);

  useEffect(() => {
    setEditedTask(task);
  }, [task]);

  const handleSave = () => {
    onUpdate(editedTask);
    setIsEditing(false);
  };

  const handleCancel = () => {
    setEditedTask(task);
    setIsEditing(false);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-gray-900">
              {isEditing ? (
                <input
                  type="text"
                  value={editedTask.title}
                  onChange={(e) => setEditedTask({ ...editedTask, title: e.target.value })}
                  className="w-full border border-gray-300 rounded px-2 py-1"
                  data-testid="task-title-input"
                />
              ) : (
                task.title
              )}
            </h2>
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
                <>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50"
                    data-testid="edit-button"
                  >
                    Edit
                  </button>
                  <button
                    onClick={onClose}
                    className="p-2 text-gray-500 hover:bg-gray-100 rounded"
                    data-testid="close-button"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </>
              )}
            </div>
          </div>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            {isEditing ? (
              <textarea
                value={editedTask.description || ''}
                onChange={(e) => setEditedTask({ ...editedTask, description: e.target.value })}
                className="w-full border border-gray-300 rounded px-3 py-2"
                rows={3}
                data-testid="task-description-input"
              />
            ) : (
              <p className="text-gray-600">{task.description || 'No description'}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              {isEditing ? (
                <select
                  value={editedTask.status}
                  onChange={(e) => setEditedTask({ ...editedTask, status: e.target.value as TaskStatus })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  data-testid="task-status-select"
                >
                  {Object.values(TaskStatus).map(status => (
                    <option key={status} value={status}>{status}</option>
                  ))}
                </select>
              ) : (
                <div className="flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${getStatusColor(task.status)}`} />
                  <span>{task.status}</span>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
              {isEditing ? (
                <select
                  value={editedTask.priority}
                  onChange={(e) => setEditedTask({ ...editedTask, priority: e.target.value as Priority })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  data-testid="task-priority-select"
                >
                  {Object.values(Priority).map(priority => (
                    <option key={priority} value={priority}>{priority}</option>
                  ))}
                </select>
              ) : (
                <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPriorityColor(task.priority)}`}>
                  {task.priority}
                </span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Assignee</label>
              {isEditing ? (
                <input
                  type="text"
                  value={editedTask.assignee || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, assignee: e.target.value || null })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  data-testid="task-assignee-input"
                />
              ) : (
                <span className="text-gray-600">{task.assignee || 'Unassigned'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
              {isEditing ? (
                <input
                  type="date"
                  value={editedTask.due_date || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, due_date: e.target.value || null })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  data-testid="task-due-date-input"
                />
              ) : (
                <span className="text-gray-600">{task.due_date || 'Not set'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Estimated Time</label>
              {isEditing ? (
                <input
                  type="number"
                  value={editedTask.estimated_minutes || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, estimated_minutes: parseInt(e.target.value) || null })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="Minutes"
                  data-testid="task-estimated-minutes-input"
                />
              ) : (
                <span className="text-gray-600">{task.estimated_minutes ? `${task.estimated_minutes} minutes` : 'Not set'}</span>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Actual Time</label>
              {isEditing ? (
                <input
                  type="number"
                  value={editedTask.actual_minutes || ''}
                  onChange={(e) => setEditedTask({ ...editedTask, actual_minutes: parseInt(e.target.value) || 0 })}
                  className="w-full border border-gray-300 rounded px-3 py-2"
                  placeholder="Minutes"
                  data-testid="task-actual-minutes-input"
                />
              ) : (
                <span className="text-gray-600">{task.actual_minutes ? `${task.actual_minutes} minutes` : 'Not tracked'}</span>
              )}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tags</label>
            <div className="flex flex-wrap gap-2">
              {task.tags?.map((tag, index) => (
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
              {task.motion_task_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-50 text-blue-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Motion: {task.motion_task_id}
                </span>
              )}
              {task.linear_issue_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-50 text-purple-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Linear: {task.linear_issue_id}
                </span>
              )}
              {task.notion_task_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-gray-100 text-gray-700 rounded text-sm">
                  <Link className="w-3 h-3" />
                  Notion: {task.notion_task_id}
                </span>
              )}
              {task.gitlab_issue_id && (
                <span className="inline-flex items-center gap-1 px-3 py-1 bg-orange-50 text-orange-600 rounded text-sm">
                  <Link className="w-3 h-3" />
                  GitLab: {task.gitlab_issue_id}
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};