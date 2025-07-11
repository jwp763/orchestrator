import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

// Mock the hooks and services
vi.mock('./hooks/useProjectManagement', () => ({
  useProjectManagement: () => ({
    projects: [],
    tasks: [],
    selectedProject: null,
    selectedTask: null,
    isProjectCollapsed: false,
    isLoading: false,
    projectsLoading: false,
    tasksLoading: false,
    error: null,
    handleProjectSelect: vi.fn(),
    handleTaskSelect: vi.fn(),
    handleNewProject: vi.fn(),
    handleUpdateProject: vi.fn(),
    handleNewTask: vi.fn(),
    handleUpdateTask: vi.fn(),
    handleApplyChanges: vi.fn(),
    handleToggleProjectCollapse: vi.fn(),
    clearError: vi.fn(),
    getTasksForProject: vi.fn(() => []),
  }),
}))

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  test('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Tasks')).toBeInTheDocument()
  })

  test('displays the main interface sections', () => {
    render(<App />)
    expect(screen.getByText('Tasks')).toBeInTheDocument()
    expect(screen.getByText('Add Task')).toBeInTheDocument()
  })

  test('renders empty state when no tasks', () => {
    render(<App />)
    expect(screen.getByText('No tasks found for this project.')).toBeInTheDocument()
    expect(screen.getByText('Click "Add Task" to create your first task.')).toBeInTheDocument()
  })

  test('has add task button disabled when no project selected', () => {
    render(<App />)
    const addTaskButton = screen.getByText('Add Task')
    expect(addTaskButton).toBeDisabled()
  })

  test('renders natural language editor', () => {
    render(<App />)
    expect(screen.getByPlaceholderText(/describe changes to make/i)).toBeInTheDocument()
    expect(screen.getByText('Generate Changes')).toBeInTheDocument()
  })

  test('generate changes button is disabled by default', () => {
    render(<App />)
    const generateButton = screen.getByText('Generate Changes')
    expect(generateButton).toBeDisabled()
  })

  test('renders project sidebar', () => {
    render(<App />)
    // The ProjectSidebar component should be rendered
    // Since we're mocking with empty projects, we should see an empty state
    expect(document.querySelector('.h-screen')).toBeInTheDocument()
  })

  test('does not show loading overlay when projects are not loading', () => {
    render(<App />)
    expect(screen.queryByText('Loading projects...')).not.toBeInTheDocument()
  })

  test('does not show error when no error exists', () => {
    render(<App />)
    expect(screen.queryByRole('alert')).not.toBeInTheDocument()
  })

  test('renders example commands in natural language editor', () => {
    render(<App />)
    expect(screen.getByText('Example Commands:')).toBeInTheDocument()
    expect(screen.getByText('• "Set priority to high and due next Friday"')).toBeInTheDocument()
  })
})