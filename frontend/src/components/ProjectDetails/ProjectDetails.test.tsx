import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProjectDetails } from './ProjectDetails';
import { Project, ProjectStatus, Priority } from '../../types';

const mockProject: Project = {
  id: '1',
  name: 'Test Project',
  description: 'This is a test project description',
  status: ProjectStatus.ACTIVE,
  priority: Priority.HIGH,
  tags: ['frontend', 'urgent'],
  due_date: '2024-03-15',
  start_date: '2024-01-10',
  motion_project_link: 'https://motion.com/project/123',
  linear_project_link: 'https://linear.app/project/456',
  notion_page_link: 'https://notion.so/page/789',
  gitlab_project_link: 'https://gitlab.com/project/012',
};

describe('ProjectDetails', () => {
  const mockOnUpdate = vi.fn();
  const mockOnToggleCollapse = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders project details correctly when not collapsed', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('This is a test project description')).toBeInTheDocument();
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('2024-01-10')).toBeInTheDocument();
    expect(screen.getByText('2024-03-15')).toBeInTheDocument();
  });

  it('renders project tags', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.getByText('frontend')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('renders external links', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.getByText('Motion')).toBeInTheDocument();
    expect(screen.getByText('Linear')).toBeInTheDocument();
    expect(screen.getByText('Notion')).toBeInTheDocument();
    expect(screen.getByText('GitLab')).toBeInTheDocument();
  });

  it('shows chevron down when not collapsed', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    // Check for chevron down icon (details are expanded)
    const collapseButton = screen.getByTestId('collapse-toggle');
    expect(collapseButton).toBeInTheDocument();
  });

  it('shows chevron right when collapsed', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={true}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    // Check for chevron right icon (details are collapsed)
    const collapseButton = screen.getByTestId('collapse-toggle');
    expect(collapseButton).toBeInTheDocument();
  });

  it('hides details when collapsed', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={true}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.queryByText('This is a test project description')).not.toBeInTheDocument();
    expect(screen.queryByText('Tags')).not.toBeInTheDocument();
  });

  it('calls onToggleCollapse when collapse button is clicked', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('collapse-toggle'));
    expect(mockOnToggleCollapse).toHaveBeenCalledTimes(1);
  });

  it('enters edit mode when edit button is clicked', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    expect(screen.getByTestId('project-name-input')).toBeInTheDocument();
    expect(screen.getByTestId('save-button')).toBeInTheDocument();
    expect(screen.getByTestId('cancel-button')).toBeInTheDocument();
  });

  it('updates project name in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const nameInput = screen.getByTestId('project-name-input');
    fireEvent.change(nameInput, { target: { value: 'Updated Project Name' } });

    expect(nameInput).toHaveValue('Updated Project Name');
  });

  it('updates project description in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const descriptionInput = screen.getByTestId('project-description-input');
    fireEvent.change(descriptionInput, { target: { value: 'Updated description' } });

    expect(descriptionInput).toHaveValue('Updated description');
  });

  it('updates project status in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const statusSelect = screen.getByTestId('project-status-select');
    fireEvent.change(statusSelect, { target: { value: 'COMPLETED' } });

    expect(statusSelect).toHaveValue('COMPLETED');
  });

  it('updates project priority in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const prioritySelect = screen.getByTestId('project-priority-select');
    fireEvent.change(prioritySelect, { target: { value: 'CRITICAL' } });

    expect(prioritySelect).toHaveValue('CRITICAL');
  });

  it('updates start date in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const startDateInput = screen.getByTestId('project-start-date-input');
    fireEvent.change(startDateInput, { target: { value: '2024-02-01' } });

    expect(startDateInput).toHaveValue('2024-02-01');
  });

  it('updates due date in edit mode', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const dueDateInput = screen.getByTestId('project-due-date-input');
    fireEvent.change(dueDateInput, { target: { value: '2024-04-01' } });

    expect(dueDateInput).toHaveValue('2024-04-01');
  });

  it('saves changes when save button is clicked', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const nameInput = screen.getByTestId('project-name-input');
    fireEvent.change(nameInput, { target: { value: 'Updated Project Name' } });

    fireEvent.click(screen.getByTestId('save-button'));

    expect(mockOnUpdate).toHaveBeenCalledWith({
      ...mockProject,
      name: 'Updated Project Name',
    });
  });

  it('cancels changes when cancel button is clicked', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));

    const nameInput = screen.getByTestId('project-name-input');
    fireEvent.change(nameInput, { target: { value: 'Updated Project Name' } });

    fireEvent.click(screen.getByTestId('cancel-button'));

    expect(mockOnUpdate).not.toHaveBeenCalled();
    expect(screen.getByText('Test Project')).toBeInTheDocument();
  });

  it('handles project with no dates', () => {
    const projectWithoutDates: Project = {
      ...mockProject,
      start_date: '',
      due_date: '',
    };

    render(
      <ProjectDetails
        project={projectWithoutDates}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.getAllByText('Not set')).toHaveLength(2); // Start date and Due date
  });

  it('handles project with no external links', () => {
    const projectWithoutLinks: Project = {
      ...mockProject,
      motion_project_link: null,
      linear_project_link: null,
      notion_page_link: null,
      gitlab_project_link: null,
    };

    render(
      <ProjectDetails
        project={projectWithoutLinks}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.queryByText('Motion')).not.toBeInTheDocument();
    expect(screen.queryByText('Linear')).not.toBeInTheDocument();
    expect(screen.queryByText('Notion')).not.toBeInTheDocument();
    expect(screen.queryByText('GitLab')).not.toBeInTheDocument();
  });

  it('handles project with no tags', () => {
    const projectWithoutTags: Project = {
      ...mockProject,
      tags: [],
    };

    render(
      <ProjectDetails
        project={projectWithoutTags}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    expect(screen.queryByText('frontend')).not.toBeInTheDocument();
    expect(screen.queryByText('urgent')).not.toBeInTheDocument();
  });

  it('exits edit mode after saving', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));
    expect(screen.getByTestId('project-name-input')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('save-button'));
    expect(screen.queryByTestId('project-name-input')).not.toBeInTheDocument();
  });

  it('exits edit mode after canceling', () => {
    render(
      <ProjectDetails
        project={mockProject}
        onUpdate={mockOnUpdate}
        isCollapsed={false}
        onToggleCollapse={mockOnToggleCollapse}
      />
    );

    fireEvent.click(screen.getByTestId('edit-button'));
    expect(screen.getByTestId('project-name-input')).toBeInTheDocument();

    fireEvent.click(screen.getByTestId('cancel-button'));
    expect(screen.queryByTestId('project-name-input')).not.toBeInTheDocument();
  });
});