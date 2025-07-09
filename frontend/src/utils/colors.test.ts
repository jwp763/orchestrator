import { describe, it, expect } from 'vitest';
import { getStatusColor, getPriorityColor } from './colors';

describe('getStatusColor', () => {
  it('should return correct color for project statuses', () => {
    expect(getStatusColor('PLANNING')).toBe('bg-gray-500');
    expect(getStatusColor('ACTIVE')).toBe('bg-green-500');
    expect(getStatusColor('ON_HOLD')).toBe('bg-yellow-500');
    expect(getStatusColor('COMPLETED')).toBe('bg-blue-500');
    expect(getStatusColor('ARCHIVED')).toBe('bg-gray-400');
  });

  it('should return correct color for task statuses', () => {
    expect(getStatusColor('TODO')).toBe('bg-gray-500');
    expect(getStatusColor('IN_PROGRESS')).toBe('bg-yellow-500');
    expect(getStatusColor('REVIEW')).toBe('bg-purple-500');
    expect(getStatusColor('DONE')).toBe('bg-green-500');
    expect(getStatusColor('BLOCKED')).toBe('bg-red-500');
  });

  it('should return default color for unknown status', () => {
    expect(getStatusColor('UNKNOWN')).toBe('bg-gray-400');
    expect(getStatusColor('')).toBe('bg-gray-400');
  });
});

describe('getPriorityColor', () => {
  it('should return correct color for all priorities', () => {
    expect(getPriorityColor('CRITICAL')).toBe('text-red-600 bg-red-50 border-red-200');
    expect(getPriorityColor('HIGH')).toBe('text-orange-600 bg-orange-50 border-orange-200');
    expect(getPriorityColor('MEDIUM')).toBe('text-yellow-600 bg-yellow-50 border-yellow-200');
    expect(getPriorityColor('LOW')).toBe('text-green-600 bg-green-50 border-green-200');
    expect(getPriorityColor('BACKLOG')).toBe('text-gray-600 bg-gray-50 border-gray-200');
  });

  it('should return default color for unknown priority', () => {
    expect(getPriorityColor('UNKNOWN')).toBe('text-gray-600 bg-gray-50 border-gray-200');
    expect(getPriorityColor('')).toBe('text-gray-600 bg-gray-50 border-gray-200');
  });
});