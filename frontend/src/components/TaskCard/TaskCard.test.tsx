import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TaskCard } from './TaskCard';
import { Task, TaskStatus, Priority } from '../../types';

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'This is a test task description',
  project_id: '1',
  status: TaskStatus.IN_PROGRESS,
  priority: Priority.HIGH,
  parent_id: null,
  estimated_minutes: 120,
  actual_minutes: 60,
  dependencies: [],
  due_date: '2024-03-15',
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  assignee: 'John Doe',
  tags: ['frontend', 'urgent'],
  attachments: [],
  notes: '',
  completion_percentage: 50,
  metadata: {},
};

describe('TaskCard', () => {
  const mockOnClick = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders task information correctly', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} />);
    
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('This is a test task description')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('2024-03-15')).toBeInTheDocument();
  });

  it('renders task tags', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} />);
    
    expect(screen.getByText('frontend')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('shows time progress when estimated and actual minutes are available', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} />);
    
    expect(screen.getByText('60m / 120m')).toBeInTheDocument();
    expect(screen.getByText('50%')).toBeInTheDocument();
  });

  it('does not show time progress when estimated minutes is null', () => {
    const taskWithoutEstimate = { ...mockTask, estimated_minutes: null };
    render(<TaskCard task={taskWithoutEstimate} onClick={mockOnClick} />);
    
    expect(screen.queryByText('60m /')).not.toBeInTheDocument();
  });

  it('does not show time progress when actual minutes is 0', () => {
    const taskWithoutActual = { ...mockTask, actual_minutes: 0 };
    render(<TaskCard task={taskWithoutActual} onClick={mockOnClick} />);
    
    expect(screen.queryByText('/ 120m')).not.toBeInTheDocument();
  });

  it('handles task without assignee', () => {
    const taskWithoutAssignee = { ...mockTask, assignee: null };
    render(<TaskCard task={taskWithoutAssignee} onClick={mockOnClick} />);
    
    expect(screen.queryByText('John Doe')).not.toBeInTheDocument();
  });

  it('handles task without due date', () => {
    const taskWithoutDueDate = { ...mockTask, due_date: null };
    render(<TaskCard task={taskWithoutDueDate} onClick={mockOnClick} />);
    
    expect(screen.queryByText('2024-03-15')).not.toBeInTheDocument();
  });

  it('handles task without description', () => {
    const taskWithoutDescription = { ...mockTask, description: '' };
    render(<TaskCard task={taskWithoutDescription} onClick={mockOnClick} />);
    
    expect(screen.queryByText('This is a test task description')).not.toBeInTheDocument();
  });

  it('handles task without tags', () => {
    const taskWithoutTags = { ...mockTask, tags: [] };
    render(<TaskCard task={taskWithoutTags} onClick={mockOnClick} />);
    
    expect(screen.queryByText('frontend')).not.toBeInTheDocument();
    expect(screen.queryByText('urgent')).not.toBeInTheDocument();
  });

  it('calls onClick when card is clicked', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} />);
    
    fireEvent.click(screen.getByTestId('task-card'));
    expect(mockOnClick).toHaveBeenCalledTimes(1);
  });

  it('applies selected styling when isSelected is true', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} isSelected={true} />);
    
    const card = screen.getByTestId('task-card');
    expect(card).toHaveClass('border-blue-500', 'shadow-md');
  });

  it('applies default styling when isSelected is false', () => {
    render(<TaskCard task={mockTask} onClick={mockOnClick} isSelected={false} />);
    
    const card = screen.getByTestId('task-card');
    expect(card).toHaveClass('border-gray-200');
    expect(card).not.toHaveClass('border-blue-500', 'shadow-md');
  });

  it('calculates time progress correctly', () => {
    const taskWithProgress = { ...mockTask, actual_minutes: 90, estimated_minutes: 120 };
    render(<TaskCard task={taskWithProgress} onClick={mockOnClick} />);
    
    expect(screen.getByText('75%')).toBeInTheDocument();
  });

  it('caps time progress at 100%', () => {
    const taskWithOverProgress = { ...mockTask, actual_minutes: 150, estimated_minutes: 120 };
    render(<TaskCard task={taskWithOverProgress} onClick={mockOnClick} />);
    
    expect(screen.getByText('100%')).toBeInTheDocument();
  });
});