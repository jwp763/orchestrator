# Frontend Testing Guide for Databricks Orchestrator

This guide provides comprehensive instructions for writing, running, and maintaining tests in the Databricks Orchestrator frontend. It covers testing patterns, mocking strategies, component testing, and best practices established in the codebase.

## Table of Contents

- [Overview](#overview)
- [Test Framework & Setup](#test-framework--setup)
- [Test Structure](#test-structure)
- [Component Testing Patterns](#component-testing-patterns)
- [Hook Testing Patterns](#hook-testing-patterns)
- [Mock Strategies](#mock-strategies)
- [Fixtures & Test Data](#fixtures--test-data)
- [Writing New Tests](#writing-new-tests)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The frontend test suite uses **Vitest** with React Testing Library to provide comprehensive component, hook, and integration testing. Tests focus on user behavior and component interactions rather than implementation details.

### Testing Philosophy

- **User-Centric**: Test behavior that users actually experience
- **Integration-Focused**: Test components as they work together
- **Mock External Dependencies**: API calls, localStorage, browser APIs
- **TypeScript-First**: Leverage type safety in tests
- **Fast & Reliable**: Quick feedback with consistent results

## Test Framework & Setup

### Core Technologies

- **Vitest**: Modern test runner with native ESM support
- **React Testing Library**: Component testing utilities
- **@testing-library/jest-dom**: Extended DOM matchers
- **@testing-library/user-event**: Advanced user interaction simulation
- **jsdom**: Browser-like testing environment

### Configuration Files

```typescript
// vite.config.ts - Test configuration
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/test/setup.ts'],
    coverage: {
      reporter: ['text', 'json', 'html']
    }
  }
})
```

```typescript
// src/test/setup.ts - Global test setup
import '@testing-library/jest-dom'
import { beforeEach, vi } from 'vitest'

// Global mocks
beforeEach(() => {
  vi.clearAllMocks()
})

// Mock localStorage and sessionStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', { value: localStorageMock })
```

## Test Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ComponentName/
│   │       ├── ComponentName.tsx
│   │       └── ComponentName.test.tsx    # Component tests
│   ├── hooks/
│   │   ├── useHookName.ts
│   │   └── useHookName.test.ts           # Hook tests
│   ├── utils/
│   │   ├── utilFunction.ts
│   │   └── utilFunction.test.ts          # Utility tests
│   ├── types/
│   │   ├── api.ts
│   │   └── api.test.ts                   # Type validation tests
│   ├── mocks/                            # Mock data and utilities
│   │   ├── projects.ts
│   │   ├── tasks.ts
│   │   └── api.ts
│   └── test/
│       ├── setup.ts                      # Global test setup
│       └── utils.ts                      # Test utilities
├── tests/                                # Additional test files
└── vitest.config.ts                     # Test configuration
```

## Component Testing Patterns

### Basic Component Testing

```typescript
// ComponentName.test.tsx
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, it, expect, vi } from 'vitest'
import ComponentName from './ComponentName'

describe('ComponentName', () => {
  it('renders with required props', () => {
    render(<ComponentName title="Test Title" />)
    
    expect(screen.getByText('Test Title')).toBeInTheDocument()
  })

  it('handles user interactions', async () => {
    const user = userEvent.setup()
    const mockOnClick = vi.fn()
    
    render(<ComponentName onClick={mockOnClick} />)
    
    await user.click(screen.getByRole('button'))
    expect(mockOnClick).toHaveBeenCalledOnce()
  })
})
```

### Advanced Component Testing

```typescript
describe('ProjectDetails', () => {
  const mockProject = {
    id: 'project-1',
    name: 'Test Project',
    status: 'active',
    tasks: [
      { id: 'task-1', title: 'Task 1', status: 'todo' },
      { id: 'task-2', title: 'Task 2', status: 'completed' }
    ]
  }

  it('displays project information correctly', () => {
    render(<ProjectDetails project={mockProject} />)
    
    expect(screen.getByText('Test Project')).toBeInTheDocument()
    expect(screen.getByText('Active')).toBeInTheDocument()
    expect(screen.getAllByTestId('task-item')).toHaveLength(2)
  })

  it('updates project status on interaction', async () => {
    const user = userEvent.setup()
    const mockOnStatusChange = vi.fn()
    
    render(
      <ProjectDetails 
        project={mockProject} 
        onStatusChange={mockOnStatusChange} 
      />
    )
    
    await user.click(screen.getByLabelText('Change status'))
    await user.click(screen.getByText('Completed'))
    
    expect(mockOnStatusChange).toHaveBeenCalledWith('project-1', 'completed')
  })

  it('handles loading and error states', () => {
    render(<ProjectDetails project={mockProject} loading />)
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument()
    
    render(<ProjectDetails project={mockProject} error="Failed to load" />)
    expect(screen.getByText('Failed to load')).toBeInTheDocument()
  })
})
```

### Form Component Testing

```typescript
describe('TaskForm', () => {
  it('validates required fields', async () => {
    const user = userEvent.setup()
    const mockOnSubmit = vi.fn()
    
    render(<TaskForm onSubmit={mockOnSubmit} />)
    
    // Try to submit empty form
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    expect(screen.getByText('Title is required')).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it('submits valid form data', async () => {
    const user = userEvent.setup()
    const mockOnSubmit = vi.fn()
    
    render(<TaskForm onSubmit={mockOnSubmit} />)
    
    await user.type(screen.getByLabelText('Title'), 'New Task')
    await user.type(screen.getByLabelText('Description'), 'Task description')
    await user.selectOptions(screen.getByLabelText('Priority'), 'high')
    await user.click(screen.getByRole('button', { name: /submit/i }))
    
    expect(mockOnSubmit).toHaveBeenCalledWith({
      title: 'New Task',
      description: 'Task description',
      priority: 'high'
    })
  })
})
```

## Hook Testing Patterns

### Basic Hook Testing

```typescript
// useHookName.test.ts
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import useCounter from './useCounter'

describe('useCounter', () => {
  it('initializes with default value', () => {
    const { result } = renderHook(() => useCounter())
    
    expect(result.current.count).toBe(0)
  })

  it('increments count', () => {
    const { result } = renderHook(() => useCounter())
    
    act(() => {
      result.current.increment()
    })
    
    expect(result.current.count).toBe(1)
  })

  it('initializes with custom value', () => {
    const { result } = renderHook(() => useCounter(10))
    
    expect(result.current.count).toBe(10)
  })
})
```

### API Hook Testing

```typescript
describe('usePlannerAPI', () => {
  beforeEach(() => {
    // Reset mocks before each test
    vi.clearAllMocks()
  })

  it('handles successful API calls', async () => {
    const mockResponse = {
      success: true,
      data: { project_patches: [], task_patches: [] }
    }
    
    global.fetch = vi.fn().mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockResponse)
    })

    const { result } = renderHook(() => usePlannerAPI())
    
    await act(async () => {
      await result.current.generatePlan('Create a new project')
    })
    
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBeNull()
    expect(result.current.data).toEqual(mockResponse.data)
  })

  it('handles API errors', async () => {
    global.fetch = vi.fn().mockRejectedValueOnce(new Error('Network error'))

    const { result } = renderHook(() => usePlannerAPI())
    
    await act(async () => {
      try {
        await result.current.generatePlan('Create a new project')
      } catch (error) {
        // Expected to throw
      }
    })
    
    expect(result.current.isLoading).toBe(false)
    expect(result.current.error).toBe('Network error')
  })
})
```

### LocalStorage Hook Testing

```typescript
describe('useLocalStorage', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('returns initial value when localStorage is empty', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'))
    
    expect(result.current[0]).toBe('default')
  })

  it('returns value from localStorage when available', () => {
    localStorage.setItem('test-key', JSON.stringify('stored-value'))
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'default'))
    
    expect(result.current[0]).toBe('stored-value')
  })

  it('updates localStorage when value changes', () => {
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    act(() => {
      result.current[1]('updated-value')
    })
    
    expect(localStorage.setItem).toHaveBeenCalledWith(
      'test-key', 
      JSON.stringify('updated-value')
    )
    expect(result.current[0]).toBe('updated-value')
  })

  it('handles localStorage errors gracefully', () => {
    // Mock localStorage error
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {})
    localStorage.setItem.mockImplementation(() => {
      throw new Error('localStorage quota exceeded')
    })
    
    const { result } = renderHook(() => useLocalStorage('test-key', 'initial'))
    
    act(() => {
      result.current[1]('new-value')
    })
    
    expect(consoleSpy).toHaveBeenCalledWith(
      'Error setting localStorage key "test-key":',
      expect.any(Error)
    )
    
    consoleSpy.mockRestore()
  })
})
```

## Mock Strategies

### API Mocking

```typescript
// Global fetch mock setup
beforeEach(() => {
  global.fetch = vi.fn()
})

// Success response mock
const mockSuccessResponse = (data: any) => {
  global.fetch.mockResolvedValueOnce({
    ok: true,
    status: 200,
    json: () => Promise.resolve(data)
  })
}

// Error response mock
const mockErrorResponse = (status: number, message: string) => {
  global.fetch.mockResolvedValueOnce({
    ok: false,
    status,
    json: () => Promise.resolve({ error: message })
  })
}

// Network error mock
const mockNetworkError = () => {
  global.fetch.mockRejectedValueOnce(new Error('Network error'))
}

// Usage in tests
it('handles successful API response', async () => {
  mockSuccessResponse({ projects: [mockProject] })
  
  // Test component that makes API call
  render(<ProjectList />)
  
  await waitFor(() => {
    expect(screen.getByText('Test Project')).toBeInTheDocument()
  })
})
```

### Storage Mocking

```typescript
// src/test/setup.ts - Global storage mocks
const createMockStorage = () => {
  const store = new Map<string, string>()
  
  return {
    getItem: vi.fn((key: string) => store.get(key) || null),
    setItem: vi.fn((key: string, value: string) => {
      store.set(key, value)
    }),
    removeItem: vi.fn((key: string) => {
      store.delete(key)
    }),
    clear: vi.fn(() => {
      store.clear()
    }),
    length: 0,
    key: vi.fn()
  }
}

Object.defineProperty(window, 'localStorage', {
  value: createMockStorage()
})

Object.defineProperty(window, 'sessionStorage', {
  value: createMockStorage()
})
```

### Module Mocking

```typescript
// Mock entire modules
vi.mock('../services/api', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn(),
    updateProject: vi.fn(),
    deleteProject: vi.fn()
  }
}))

// Partial module mocking
vi.mock('../utils/date', async () => {
  const actual = await vi.importActual('../utils/date')
  return {
    ...actual,
    formatDate: vi.fn(() => '2024-01-01')
  }
})
```

## Fixtures & Test Data

### Mock Data Organization

```typescript
// src/mocks/projects.ts
export const mockProject = {
  id: 'project-1',
  name: 'Test Project',
  description: 'A test project',
  status: 'active' as const,
  priority: 'medium' as const,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  task_count: 5,
  completed_task_count: 2
}

export const mockProjects = [
  mockProject,
  { ...mockProject, id: 'project-2', name: 'Another Project' },
  { ...mockProject, id: 'project-3', name: 'Third Project', status: 'completed' }
]

// src/mocks/tasks.ts
export const mockTask = {
  id: 'task-1',
  project_id: 'project-1',
  title: 'Test Task',
  description: 'A test task',
  status: 'todo' as const,
  priority: 'medium' as const,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z'
}

export const mockTasks = [
  mockTask,
  { ...mockTask, id: 'task-2', title: 'Second Task', status: 'in_progress' },
  { ...mockTask, id: 'task-3', title: 'Third Task', status: 'completed' }
]
```

### Test Utilities

```typescript
// src/test/utils.ts
import { render, RenderOptions } from '@testing-library/react'
import { ReactElement } from 'react'

// Custom render with providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <ThemeProvider theme={defaultTheme}>
      <ErrorBoundary>
        {children}
      </ErrorBoundary>
    </ThemeProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from '@testing-library/react'
export { customRender as render }

// Test data factories
export const createMockProject = (overrides = {}) => ({
  ...mockProject,
  ...overrides
})

export const createMockTask = (overrides = {}) => ({
  ...mockTask,
  ...overrides
})
```

## Writing New Tests

### 1. Component Test Structure

```typescript
import { render, screen } from '@testing-library/react'
import { userEvent } from '@testing-library/user-event'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import YourComponent from './YourComponent'

describe('YourComponent', () => {
  // Setup for each test
  beforeEach(() => {
    vi.clearAllMocks()
  })

  // Test groups
  describe('rendering', () => {
    it('displays required elements', () => {
      render(<YourComponent />)
      expect(screen.getByRole('heading')).toBeInTheDocument()
    })
  })

  describe('user interactions', () => {
    it('handles button clicks', async () => {
      const user = userEvent.setup()
      const mockHandler = vi.fn()
      
      render(<YourComponent onClick={mockHandler} />)
      await user.click(screen.getByRole('button'))
      
      expect(mockHandler).toHaveBeenCalledOnce()
    })
  })

  describe('error handling', () => {
    it('displays error messages', () => {
      render(<YourComponent error="Something went wrong" />)
      expect(screen.getByText('Something went wrong')).toBeInTheDocument()
    })
  })
})
```

### 2. Hook Test Structure

```typescript
import { renderHook, act } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import useYourHook from './useYourHook'

describe('useYourHook', () => {
  it('initializes correctly', () => {
    const { result } = renderHook(() => useYourHook())
    
    expect(result.current).toMatchObject({
      data: null,
      loading: false,
      error: null
    })
  })

  it('handles async operations', async () => {
    const { result } = renderHook(() => useYourHook())
    
    await act(async () => {
      await result.current.fetchData()
    })
    
    expect(result.current.loading).toBe(false)
    expect(result.current.data).toBeDefined()
  })
})
```

### 3. Integration Test Structure

```typescript
describe('Project Management Integration', () => {
  it('completes full project lifecycle', async () => {
    const user = userEvent.setup()
    
    // Mock API responses
    mockSuccessResponse({ projects: [] })
    
    render(<App />)
    
    // Create project
    await user.click(screen.getByText('New Project'))
    await user.type(screen.getByLabelText('Project Name'), 'Test Project')
    await user.click(screen.getByRole('button', { name: /create/i }))
    
    // Verify project appears
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument()
    })
    
    // Continue with other actions...
  })
})
```

## Running Tests

### Command Line Options

```bash
# Run all tests
npm test

# Run tests in watch mode (development)
npm run test:watch

# Run tests with coverage
npm run test:coverage

# Run specific test file
npm test ComponentName.test.tsx

# Run tests matching pattern
npm test -- --reporter=verbose

# Run tests in specific directory
npm test src/components/

# Run tests with UI (Vitest UI)
npm run test:ui
```

### Test Scripts (package.json)

```json
{
  "scripts": {
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:ui": "vitest --ui"
  }
}
```

### Debugging Tests

```bash
# Run tests with debugging output
npm test -- --reporter=verbose

# Run single test with full output
npm test -- --run ComponentName.test.tsx

# Debug specific test
npm test -- --run --reporter=verbose ComponentName.test.tsx -t "test name"
```

## Troubleshooting

### Common Issues

#### Act Warnings

**Symptom**: "Warning: An update to Component was not wrapped in act(...)"

**Solution**: Wrap async operations in `act()`:

```typescript
// ❌ Wrong
const { result } = renderHook(() => useAsyncHook())
await result.current.fetchData() // Missing act()

// ✅ Correct
const { result } = renderHook(() => useAsyncHook())
await act(async () => {
  await result.current.fetchData()
})
```

#### Mock Not Working

**Symptom**: Mocks not being applied or persisting between tests

**Solution**: Ensure proper mock setup and cleanup:

```typescript
// ✅ Correct mock setup
beforeEach(() => {
  vi.clearAllMocks()
  
  global.fetch = vi.fn()
  localStorage.clear()
})
```

#### Component Not Found

**Symptom**: `Unable to find element` errors

**Solution**: Use proper queries and wait for async updates:

```typescript
// ❌ Wrong - element might not be rendered yet
expect(screen.getByText('Loading...')).toBeInTheDocument()

// ✅ Correct - wait for element to appear
await waitFor(() => {
  expect(screen.getByText('Data loaded')).toBeInTheDocument()
})

// Or use findBy queries (automatically wait)
const element = await screen.findByText('Data loaded')
expect(element).toBeInTheDocument()
```

#### TypeScript Errors

**Symptom**: Type errors in test files

**Solution**: Proper type assertions and mocking:

```typescript
// ✅ Correct TypeScript mocking
const mockFunction = vi.fn() as vi.MockedFunction<typeof originalFunction>
mockFunction.mockReturnValue('mocked value')

// ✅ Type assertion for test props
const props: ComponentProps<typeof YourComponent> = {
  title: 'Test',
  onAction: vi.fn()
}
render(<YourComponent {...props} />)
```

### Performance Issues

#### Slow Tests

**Common Causes:**
- Real API calls instead of mocks
- Large DOM trees
- Unnecessary re-renders

**Solutions:**
```typescript
// ✅ Mock expensive operations
vi.mock('../services/api')

// ✅ Use minimal test data
const minimalProps = { id: '1', title: 'Test' }

// ✅ Clean up properly
afterEach(() => {
  cleanup() // React Testing Library cleanup
  vi.clearAllMocks()
})
```

## Best Practices

### Component Testing

1. **Test User Behavior**: Focus on what users see and do
2. **Use Accessible Queries**: Prefer `getByRole`, `getByLabelText`
3. **Test Error States**: Include loading, error, and empty states
4. **Mock External Dependencies**: APIs, localStorage, complex utilities

### Hook Testing

1. **Test Hook Logic**: Focus on state changes and side effects
2. **Use renderHook**: Avoid testing hooks through components
3. **Test Edge Cases**: Error handling, async operations, cleanup
4. **Mock Dependencies**: External services, timers, DOM APIs

### Assertions

1. **Be Specific**: Use precise assertions over generic ones
2. **Test Behavior**: Focus on user-visible behavior changes
3. **Use waitFor**: For async updates and state changes
4. **Verify Mocks**: Ensure functions are called with correct arguments

### Code Organization

1. **Group Related Tests**: Use `describe` blocks for logical grouping
2. **Descriptive Names**: Test names should explain the behavior
3. **Reuse Test Data**: Create fixtures for common test scenarios
4. **Clean Setup**: Use `beforeEach` for consistent test environment

### Performance

1. **Fast Execution**: Keep tests under 100ms each
2. **Proper Cleanup**: Clear mocks and state between tests
3. **Minimal Rendering**: Only render what's necessary for the test
4. **Efficient Mocks**: Use targeted mocks, not global overrides

---

## Contributing to Frontend Tests

When adding new tests or modifying existing ones:

1. **Follow Existing Patterns**: Use the same structure and utilities
2. **Update This Guide**: Document new patterns or techniques
3. **Test Your Tests**: Ensure tests fail when code is broken
4. **Consider Accessibility**: Include accessibility testing where relevant
5. **Review Coverage**: Aim for comprehensive coverage of new functionality

This testing guide is a living document. As new patterns emerge or existing ones evolve, please update this documentation to help future developers understand and maintain the frontend test suite effectively.