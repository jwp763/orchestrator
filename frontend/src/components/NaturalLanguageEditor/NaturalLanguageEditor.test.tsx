import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { NaturalLanguageEditor } from './NaturalLanguageEditor';
import { Project, Task, Change, ProjectStatus, Priority, TaskStatus } from '../../types';

const mockProject: Project = {
  id: '1',
  name: 'Test Project',
  description: 'Test project description',
  status: ProjectStatus.ACTIVE,
  priority: Priority.MEDIUM,
  tags: ['test'],
  due_date: '2024-03-15',
  start_date: '2024-01-10',
  motion_project_link: null,
  linear_project_link: null,
  notion_page_link: null,
  gitlab_project_link: null,
};

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'Test task description',
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
  assignee: null,
  tags: [],
  attachments: [],
  notes: '',
  completion_percentage: 50,
  metadata: {},
};

describe('NaturalLanguageEditor', () => {
  const mockOnApplyChanges = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the natural language input', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    expect(screen.getByTestId('nl-input')).toBeInTheDocument();
    expect(screen.getByTestId('generate-changes-button')).toBeInTheDocument();
  });

  it('renders example commands', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    expect(screen.getByText('Example Commands:')).toBeInTheDocument();
    expect(screen.getByText('• "Set priority to high and due next Friday"')).toBeInTheDocument();
    expect(screen.getByText('• "Assign all design tasks to Sarah"')).toBeInTheDocument();
  });

  it('updates input value when typing', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high' } });

    expect(input).toHaveValue('Set priority to high');
  });

  it('disables generate button when input is empty', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const button = screen.getByTestId('generate-changes-button');
    expect(button).toBeDisabled();
  });

  it('enables generate button when input has content', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high' } });

    const button = screen.getByTestId('generate-changes-button');
    expect(button).not.toBeDisabled();
  });

  it('shows processing state when generating changes', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    expect(screen.getByText('Processing...')).toBeInTheDocument();
    expect(button).toBeDisabled();
  });

  it('generates changes for high priority command', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high priority' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(screen.getByText('Project')).toBeInTheDocument();
    expect(screen.getByText('- priority: MEDIUM')).toBeInTheDocument();
    expect(screen.getByText('+ priority: HIGH')).toBeInTheDocument();
  });

  it('generates changes for due date command', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set due next week' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(screen.getByText('Project')).toBeInTheDocument();
    expect(screen.getByText('- due_date: 2024-03-15')).toBeInTheDocument();
  });

  it('generates changes for assignee command', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'assign to john' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(screen.getByText('Task: 1')).toBeInTheDocument();
    expect(screen.getByText('- assignee: None')).toBeInTheDocument();
    expect(screen.getByText('+ assignee: John Smith')).toBeInTheDocument();
  });

  it('applies individual changes', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high priority' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    const applyButton = screen.getByTestId('apply-change-0');
    fireEvent.click(applyButton);

    expect(mockOnApplyChanges).toHaveBeenCalledWith([
      expect.objectContaining({
        type: 'project',
        field: 'priority',
        oldValue: Priority.MEDIUM,
        newValue: Priority.HIGH,
      }),
    ]);
  });

  it('rejects individual changes', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high priority' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    const rejectButton = screen.getByTestId('reject-change-0');
    fireEvent.click(rejectButton);

    expect(screen.queryByTestId('change-item')).not.toBeInTheDocument();
  });

  it('applies all changes', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high priority due next week' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    const applyAllButton = screen.getByTestId('apply-all-button');
    fireEvent.click(applyAllButton);

    expect(mockOnApplyChanges).toHaveBeenCalledWith(
      expect.arrayContaining([
        expect.objectContaining({
          type: 'project',
          field: 'priority',
          newValue: Priority.HIGH,
        }),
        expect.objectContaining({
          type: 'project',
          field: 'due_date',
        }),
      ])
    );
  });

  it('rejects all changes', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'Set priority to high priority' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Proposed Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    const rejectAllButton = screen.getByTestId('reject-all-button');
    fireEvent.click(rejectAllButton);

    expect(screen.queryByText('Proposed Changes')).not.toBeInTheDocument();
    expect(screen.getByTestId('nl-input')).toHaveValue('');
  });

  it('handles empty project and task', () => {
    render(
      <NaturalLanguageEditor
        selectedProject={null}
        selectedTask={null}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    expect(screen.getByTestId('nl-input')).toBeInTheDocument();
    expect(screen.getByTestId('generate-changes-button')).toBeInTheDocument();
  });

  it('shows no changes when no matching patterns', async () => {
    render(
      <NaturalLanguageEditor
        selectedProject={mockProject}
        selectedTask={mockTask}
        onApplyChanges={mockOnApplyChanges}
      />
    );

    const input = screen.getByTestId('nl-input');
    fireEvent.change(input, { target: { value: 'random text with no patterns' } });

    const button = screen.getByTestId('generate-changes-button');
    fireEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Generate Changes')).toBeInTheDocument();
    }, { timeout: 2000 });

    expect(screen.queryByText('Proposed Changes')).not.toBeInTheDocument();
  });
});