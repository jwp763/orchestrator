import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import App from './App'

describe('App', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Clear localStorage mock
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    })
  })

  test('renders without crashing', () => {
    render(<App />)
    expect(screen.getByText('Orchestrator')).toBeInTheDocument()
  })

  test('displays the correct title and subtitle', () => {
    render(<App />)
    expect(screen.getByText('Orchestrator')).toBeInTheDocument()
    expect(screen.getByText('AI-Powered Project Planning & Task Management')).toBeInTheDocument()
  })

  test('renders project idea form', () => {
    render(<App />)
    expect(screen.getByLabelText('Project Idea')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('Describe your project idea here...')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Generate Project Plan' })).toBeInTheDocument()
  })

  test('displays default provider and model', () => {
    render(<App />)
    expect(screen.getByText('Using openai - o3')).toBeInTheDocument()
  })

  test('updates project idea when user types', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const textarea = screen.getByLabelText('Project Idea')
    await user.type(textarea, 'Build a todo app')
    
    expect(textarea).toHaveValue('Build a todo app')
  })

  test('prevents form submission when project idea is empty', async () => {
    const user = userEvent.setup()
    render(<App />)
    
    const submitButton = screen.getByRole('button', { name: 'Generate Project Plan' })
    await user.click(submitButton)
    
    // The form should not submit due to required attribute
    const textarea = screen.getByLabelText('Project Idea')
    expect(textarea).toBeInvalid()
  })

  test('handles form submission with valid input', async () => {
    const user = userEvent.setup()
    const consoleSpy = vi.spyOn(console, 'log').mockImplementation(() => {})
    
    render(<App />)
    
    const textarea = screen.getByLabelText('Project Idea')
    const submitButton = screen.getByRole('button', { name: 'Generate Project Plan' })
    
    await user.type(textarea, 'Build a todo app')
    await user.click(submitButton)
    
    expect(consoleSpy).toHaveBeenCalledWith('Generating project for:', 'Build a todo app')
    
    consoleSpy.mockRestore()
  })

  test('persists user preferences in localStorage', () => {
    const mockLocalStorage = {
      getItem: vi.fn(),
      setItem: vi.fn(),
    }
    
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    })
    
    render(<App />)
    
    expect(mockLocalStorage.getItem).toHaveBeenCalledWith('orchestrator-preferences')
  })

  test('loads preferences from localStorage when available', () => {
    const mockPreferences = {
      lastConfig: {
        provider: 'anthropic',
        model: 'claude-3-sonnet',
        max_retries: 3,
        create_milestones: false,
        max_milestones: 8,
        temperature: 0.5,
        max_tokens: 1000,
      },
      theme: 'dark',
      autoSave: false,
    }
    
    const mockLocalStorage = {
      getItem: vi.fn().mockReturnValue(JSON.stringify(mockPreferences)),
      setItem: vi.fn(),
    }
    
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    })
    
    render(<App />)
    
    expect(screen.getByText('Using anthropic - claude-3-sonnet')).toBeInTheDocument()
  })

  test('handles localStorage errors gracefully', () => {
    const mockLocalStorage = {
      getItem: vi.fn().mockImplementation(() => {
        throw new Error('Storage error')
      }),
      setItem: vi.fn(),
    }
    
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true,
    })
    
    const consoleSpy = vi.spyOn(console, 'warn').mockImplementation(() => {})
    
    render(<App />)
    
    // Should still render with default values
    expect(screen.getByText('Using openai - o3')).toBeInTheDocument()
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error reading localStorage key "orchestrator-preferences":',
      expect.any(Error)
    )
    
    consoleSpy.mockRestore()
  })

  test('has proper accessibility attributes', () => {
    render(<App />)
    
    const textarea = screen.getByLabelText('Project Idea')
    const submitButton = screen.getByRole('button', { name: 'Generate Project Plan' })
    
    expect(textarea).toHaveAttribute('id', 'project-idea')
    expect(textarea).toHaveAttribute('required')
    expect(submitButton).toHaveAttribute('type', 'submit')
  })

  test('has proper form structure', () => {
    render(<App />)
    
    const form = screen.getByRole('main').querySelector('form')
    const textarea = screen.getByLabelText('Project Idea')
    const submitButton = screen.getByRole('button', { name: 'Generate Project Plan' })
    
    expect(form).toContainElement(textarea)
    expect(form).toContainElement(submitButton)
  })
})