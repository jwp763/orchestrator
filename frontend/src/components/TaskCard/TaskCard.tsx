import React from 'react';
import { Calendar, User } from 'lucide-react';
import type { Task } from '../../types';
import { getStatusColor, getPriorityColor } from '../../utils';

interface TaskCardProps {
  task: Task;
  onClick: () => void;
  isSelected?: boolean;
}

export const TaskCard: React.FC<TaskCardProps> = ({ task, onClick, isSelected = false }) => {
  const getTimeProgress = (): number | null => {
    if (!task.estimated_minutes || !task.actual_minutes) return null;
    const percentage = Math.min((task.actual_minutes / task.estimated_minutes) * 100, 100);
    return percentage;
  };

  return (
    <div
      onClick={onClick}
      data-testid="task-card"
      className={`p-4 bg-white border rounded-lg cursor-pointer transition-all ${
        isSelected ? 'border-blue-500 shadow-md' : 'border-gray-200 hover:border-gray-300 hover:shadow-sm'
      }`}
    >
      <div className="flex items-start justify-between mb-2">
        <h3 className="font-medium text-gray-900 flex-1">{task.title}</h3>
        <div className={`w-2 h-2 rounded-full mt-1.5 ${getStatusColor(task.status)}`} />
      </div>

      <div className="space-y-2">
        {task.description && (
          <p className="text-sm text-gray-600 line-clamp-2">{task.description}</p>
        )}

        <div className="flex items-center gap-4 text-sm">
          {task.assignee && (
            <div className="flex items-center gap-1 text-gray-600">
              <User className="w-3 h-3" />
              <span>{task.assignee}</span>
            </div>
          )}
          {task.due_date && (
            <div className="flex items-center gap-1 text-gray-600">
              <Calendar className="w-3 h-3" />
              <span>{task.due_date}</span>
            </div>
          )}
          <span className={`px-2 py-0.5 rounded text-xs font-medium ${getPriorityColor(task.priority)}`}>
            {task.priority}
          </span>
        </div>

        {getTimeProgress() !== null && (
          <div className="mt-2">
            <div className="flex items-center justify-between text-xs text-gray-600 mb-1">
              <span>{task.actual_minutes}m / {task.estimated_minutes}m</span>
              <span>{Math.round(getTimeProgress()!)}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-1.5">
              <div
                className="bg-blue-600 h-1.5 rounded-full"
                style={{ width: `${getTimeProgress()}%` }}
              />
            </div>
          </div>
        )}

        {task.tags && task.tags.length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {task.tags.map((tag, index) => (
              <span key={index} className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};