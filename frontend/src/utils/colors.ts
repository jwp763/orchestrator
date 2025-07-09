import type { StatusColorMap, PriorityColorMap } from '../types';

/**
 * Returns the appropriate CSS class for status indicators
 * @param status - The status string
 * @returns CSS class string for the status color
 */
export const getStatusColor = (status: string): string => {
  const colors: StatusColorMap = {
    PLANNING: 'bg-gray-500',
    ACTIVE: 'bg-green-500',
    ON_HOLD: 'bg-yellow-500',
    COMPLETED: 'bg-blue-500',
    ARCHIVED: 'bg-gray-400',
    TODO: 'bg-gray-500',
    IN_PROGRESS: 'bg-yellow-500',
    REVIEW: 'bg-purple-500',
    DONE: 'bg-green-500',
    BLOCKED: 'bg-red-500'
  };
  return colors[status] || 'bg-gray-400';
};

/**
 * Returns the appropriate CSS classes for priority indicators
 * @param priority - The priority string
 * @returns CSS class string for the priority styling
 */
export const getPriorityColor = (priority: string): string => {
  const colors: PriorityColorMap = {
    CRITICAL: 'text-red-600 bg-red-50 border-red-200',
    HIGH: 'text-orange-600 bg-orange-50 border-orange-200',
    MEDIUM: 'text-yellow-600 bg-yellow-50 border-yellow-200',
    LOW: 'text-green-600 bg-green-50 border-green-200',
    BACKLOG: 'text-gray-600 bg-gray-50 border-gray-200'
  };
  return colors[priority] || 'text-gray-600 bg-gray-50 border-gray-200';
};