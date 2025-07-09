import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { TaskDetails } from './TaskDetails';
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
  motion_task_id: 'MOT-123',
  linear_issue_id: 'LIN-456',
  notion_task_id: 'NOT-789',
  gitlab_issue_id: 'GIT-012',
};

describe('TaskDetails', () => {
  const mockOnClose = vi.fn();
  const mockOnUpdate = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders task details correctly', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('This is a test task description')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('John Doe')).toBeInTheDocument();
    expect(screen.getByText('2024-03-15')).toBeInTheDocument();
    expect(screen.getByText('120 minutes')).toBeInTheDocument();
    expect(screen.getByText('60 minutes')).toBeInTheDocument();
  });

  it('renders tags correctly', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    expect(screen.getByText('frontend')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('renders external links correctly', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    expect(screen.getByText('Motion: MOT-123')).toBeInTheDocument();
    expect(screen.getByText('Linear: LIN-456')).toBeInTheDocument();
    expect(screen.getByText('Notion: NOT-789')).toBeInTheDocument();
    expect(screen.getByText('GitLab: GIT-012')).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('close-button'));
    expect(mockOnClose).toHaveBeenCalledTimes(1);
  });

  it('enters edit mode when edit button is clicked', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    expect(screen.getByTestId('task-title-input')).toBeInTheDocument();
    expect(screen.getByTestId('save-button')).toBeInTheDocument();
    expect(screen.getByTestId('cancel-button')).toBeInTheDocument();
  });

  it('updates task title in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const titleInput = screen.getByTestId('task-title-input');
    fireEvent.change(titleInput, { target: { value: 'Updated Task Title' } });
    
    expect(titleInput).toHaveValue('Updated Task Title');
  });

  it('updates task description in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const descriptionInput = screen.getByTestId('task-description-input');
    fireEvent.change(descriptionInput, { target: { value: 'Updated description' } });
    
    expect(descriptionInput).toHaveValue('Updated description');
  });

  it('updates task status in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const statusSelect = screen.getByTestId('task-status-select');
    fireEvent.change(statusSelect, { target: { value: 'DONE' } });
    
    expect(statusSelect).toHaveValue('DONE');
  });

  it('updates task priority in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const prioritySelect = screen.getByTestId('task-priority-select');
    fireEvent.change(prioritySelect, { target: { value: 'CRITICAL' } });
    
    expect(prioritySelect).toHaveValue('CRITICAL');
  });

  it('updates task assignee in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const assigneeInput = screen.getByTestId('task-assignee-input');
    fireEvent.change(assigneeInput, { target: { value: 'Jane Smith' } });
    
    expect(assigneeInput).toHaveValue('Jane Smith');
  });

  it('updates task due date in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const dueDateInput = screen.getByTestId('task-due-date-input');
    fireEvent.change(dueDateInput, { target: { value: '2024-04-01' } });
    
    expect(dueDateInput).toHaveValue('2024-04-01');
  });

  it('updates estimated minutes in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const estimatedInput = screen.getByTestId('task-estimated-minutes-input');
    fireEvent.change(estimatedInput, { target: { value: '180' } });
    
    expect(estimatedInput).toHaveValue(180);
  });

  it('updates actual minutes in edit mode', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const actualInput = screen.getByTestId('task-actual-minutes-input');
    fireEvent.change(actualInput, { target: { value: '90' } });
    
    expect(actualInput).toHaveValue(90);
  });

  it('saves changes when save button is clicked', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const titleInput = screen.getByTestId('task-title-input');
    fireEvent.change(titleInput, { target: { value: 'Updated Task Title' } });
    
    fireEvent.click(screen.getByTestId('save-button'));
    
    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockTask,
      title: 'Updated Task Title',
    });
  });

  it('cancels changes when cancel button is clicked', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    
    const titleInput = screen.getByTestId('task-title-input');
    fireEvent.change(titleInput, { target: { value: 'Updated Task Title' } });
    
    fireEvent.click(screen.getByTestId('cancel-button'));
    
    expect(mockOnUpdate).not.toHaveBeenCalled();
    expect(screen.getByText('Test Task')).toBeInTheDocument();
  });

  it('handles task without optional fields', () => {
    const minimalTask: Task = {
      ...mockTask,
      description: '',
      assignee: null,
      due_date: null,
      estimated_minutes: null,
      actual_minutes: 0,
      tags: [],
      motion_task_id: undefined,
      linear_issue_id: undefined,
      notion_task_id: undefined,
      gitlab_issue_id: undefined,
    };
    
    render(<TaskDetails task={minimalTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    expect(screen.getByText('No description')).toBeInTheDocument();
    expect(screen.getByText('Unassigned')).toBeInTheDocument();
    expect(screen.getAllByText('Not set')).toHaveLength(2); // Due Date and Estimated Time
    expect(screen.getByText('Not tracked')).toBeInTheDocument();
  });

  it('exits edit mode after saving', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    expect(screen.getByTestId('task-title-input')).toBeInTheDocument();
    
    fireEvent.click(screen.getByTestId('save-button'));
    expect(screen.queryByTestId('task-title-input')).not.toBeInTheDocument();
  });

  it('exits edit mode after canceling', () => {
    render(<TaskDetails task={mockTask} onClose={mockOnClose} onUpdate={mockOnUpdate} />);
    
    fireEvent.click(screen.getByTestId('edit-button'));
    expect(screen.getByTestId('task-title-input')).toBeInTheDocument();
    
    fireEvent.click(screen.getByTestId('cancel-button'));
    expect(screen.queryByTestId('task-title-input')).not.toBeInTheDocument();
  });
});