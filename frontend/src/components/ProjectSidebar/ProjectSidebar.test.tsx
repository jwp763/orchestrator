import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { ProjectSidebar } from './ProjectSidebar';
import { Project, Task, ProjectStatus, Priority, TaskStatus } from '../../types';

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'Test Project 1',
    description: 'Test description 1',
    status: ProjectStatus.ACTIVE,
    priority: Priority.HIGH,
    tags: ['frontend'],
    due_date: '2024-03-15',
    start_date: '2024-01-10',
    motion_project_link: null,
    linear_project_link: null,
    notion_page_link: null,
    gitlab_project_link: null,
  },
  {
    id: '2',
    name: 'Test Project 2',
    description: 'Test description 2',
    status: ProjectStatus.PLANNING,
    priority: Priority.MEDIUM,
    tags: ['backend'],
    due_date: '2024-04-01',
    start_date: '2024-03-01',
    motion_project_link: null,
    linear_project_link: null,
    notion_page_link: null,
    gitlab_project_link: null,
  },
];

const mockTasks: Task[] = [
  {
    id: '1',
    title: 'Task 1',
    description: 'Task 1 description',
    project_id: '1',
    status: TaskStatus.DONE,
    priority: Priority.HIGH,
    parent_id: null,
    estimated_minutes: 120,
    actual_minutes: 100,
    dependencies: [],
    due_date: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    assignee: null,
    tags: [],
    attachments: [],
    notes: '',
    completion_percentage: 100,
    metadata: {},
  },
  {
    id: '2',
    title: 'Task 2',
    description: 'Task 2 description',
    project_id: '1',
    status: TaskStatus.TODO,
    priority: Priority.MEDIUM,
    parent_id: null,
    estimated_minutes: 60,
    actual_minutes: 0,
    dependencies: [],
    due_date: null,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    assignee: null,
    tags: [],
    attachments: [],
    notes: '',
    completion_percentage: 0,
    metadata: {},
  },
];

describe('ProjectSidebar', () => {
  const mockOnProjectSelect = vi.fn();
  const mockOnAddProject = vi.fn();

  const defaultProps = {
    projects: mockProjects,
    selectedProject: null,
    onProjectSelect: mockOnProjectSelect,
    onAddProject: mockOnAddProject,
    tasks: mockTasks,
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders project list correctly', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    expect(screen.getByText('Test Project 1')).toBeInTheDocument();
    expect(screen.getByText('Test Project 2')).toBeInTheDocument();
  });

  it('renders New Project button', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    expect(screen.getByText('New Project')).toBeInTheDocument();
  });

  it('calls onAddProject when New Project button is clicked', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    fireEvent.click(screen.getByText('New Project'));
    expect(mockOnAddProject).toHaveBeenCalledTimes(1);
  });

  it('calls onProjectSelect when project is clicked', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    fireEvent.click(screen.getByText('Test Project 1'));
    expect(mockOnProjectSelect).toHaveBeenCalledWith(mockProjects[0]);
  });

  it('highlights selected project', () => {
    render(<ProjectSidebar {...defaultProps} selectedProject={mockProjects[0]} />);
    
    const selectedProject = screen.getByText('Test Project 1').closest('[data-testid="project-item"]');
    expect(selectedProject).toHaveClass('bg-blue-50');
  });

  it('displays task count correctly', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    // Project 1 has 2 tasks, 1 completed
    expect(screen.getByText('1/2 tasks')).toBeInTheDocument();
  });

  it('displays priority badges', () => {
    render(<ProjectSidebar {...defaultProps} />);
    
    expect(screen.getByText('HIGH')).toBeInTheDocument();
    expect(screen.getByText('MEDIUM')).toBeInTheDocument();
  });

  it('shows overdue indicator for past due projects', () => {
    const overdueProjects = [
      {
        ...mockProjects[0],
        due_date: '2020-01-01', // Past date
      },
    ];
    
    render(<ProjectSidebar {...defaultProps} projects={overdueProjects} />);
    
    expect(screen.getByText('Overdue')).toBeInTheDocument();
  });

  it('handles empty project list', () => {
    render(<ProjectSidebar {...defaultProps} projects={[]} />);
    
    expect(screen.getByText('New Project')).toBeInTheDocument();
    expect(screen.queryByText('Test Project 1')).not.toBeInTheDocument();
  });

  it('handles project with no tasks', () => {
    const projectWithNoTasks = [
      {
        ...mockProjects[0],
        id: '999',
      },
    ];
    
    render(<ProjectSidebar {...defaultProps} projects={projectWithNoTasks} />);
    
    expect(screen.getByText('0/0 tasks')).toBeInTheDocument();
  });
});