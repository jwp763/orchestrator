# Testing Documentation

*Last Updated: 2025-01-11*

## Table of Contents

- [Overview](#overview)
- [Testing Architecture](#testing-architecture)
- [Backend Testing Guide](#backend-testing-guide)
- [Frontend Testing Guide](#frontend-testing-guide)
- [Common Testing Patterns](#common-testing-patterns)
- [Troubleshooting Guide](#troubleshooting-guide)
- [Performance Metrics](#performance-metrics)

---

## Overview

The Databricks Orchestrator project has achieved comprehensive test coverage across both backend and frontend components, with robust testing infrastructure supporting reliable development workflows.

### Current Test Status (July 2025)

| Component | Total Tests | Success Rate | Coverage | Notes |
|-----------|-------------|--------------|----------|-------|
| Backend | 516 | 99.4% | 88% | 3 acceptable SQLite-related failures |
| Frontend | 156 | 100% | 100% | Full component coverage |
| **Total** | **672** | **99.6%** | **94%** | Production-ready quality |

### Quick Start

```bash
# Backend testing (ALWAYS run from backend directory)
cd backend && pytest                    # Run all tests
cd backend && pytest -v                # Verbose output
cd backend && pytest --cov=src         # With coverage

# Frontend testing
cd frontend && npm test                # Run all tests
cd frontend && npm run test:watch      # Watch mode
cd frontend && npm run test:coverage   # With coverage

# Full stack testing (from root)
npm run test:all                       # Run all backend + frontend tests
```

---

## Testing Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Testing Architecture                        │
├─────────────────────────────────────────────────────────────────┤
│  Backend Testing (Python/FastAPI)   │  Frontend Testing (React) │
│  ├─ Unit Tests                      │  ├─ Component Tests        │
│  ├─ Integration Tests               │  ├─ Hook Tests             │
│  ├─ API Tests                       │  ├─ Utility Tests          │
│  ├─ Performance Tests               │  └─ Integration Tests      │
│  └─ Security Tests                  │                            │
├─────────────────────────────────────────────────────────────────┤
│                   Test Infrastructure                           │
│  ├─ Database Isolation (SQLite in-memory)                      │
│  ├─ Mock Services & API Layers                                 │
│  ├─ Fixture Management                                          │
│  ├─ Multi-Environment Support (dev/staging/prod)               │
│  └─ Continuous Integration                                      │
└─────────────────────────────────────────────────────────────────┘
```

### Key Technologies

| Layer | Backend | Frontend |
|-------|---------|----------|
| Framework | pytest | Vitest |
| Database | SQLAlchemy + SQLite | N/A |
| API Testing | FastAPI TestClient | Mock Service Worker |
| Mocking | unittest.mock | vi.mock |
| Coverage | pytest-cov | @vitest/coverage-v8 |

---

## Backend Testing Guide

### Test Structure

```
backend/
├── tests/
│   ├── test_api/           # API endpoint tests
│   ├── test_agents/        # AI agent tests
│   ├── test_schema_models/ # Data model tests
│   └── *.py               # Core functionality tests
└── test_*.py              # Additional test files
```

### Database Isolation Pattern

**CRITICAL**: All integration tests must inherit from `TestDatabaseIsolation`:

```python
from tests.fixtures import TestDatabaseIsolation

class TestProjectAPI(TestDatabaseIsolation):
    def test_create_project(self, isolated_client):
        # Each test gets fresh database
        response = isolated_client.post("/api/projects", json={...})
        assert response.status_code == 201
```

**Note**: Tests use in-memory SQLite databases, completely isolated from the development (`orchestrator_dev.db`), staging (`orchestrator_staging.db`), and production (`orchestrator_prod.db`) databases.

### Key Test Categories

#### 1. Unit Tests
- **Scope**: Individual components with mocked dependencies
- **Speed**: <100ms per test
- **Example**: Model validation, utility functions

#### 2. Integration Tests
- **Scope**: Complete workflows with real components
- **Database**: Isolated in-memory SQLite
- **Example**: API endpoints, service layers

#### 3. Performance Tests
- **Scope**: Load testing, concurrency, resource usage
- **Metrics**: Response times, throughput
- **Note**: SQLite has concurrency limitations (70% success acceptable)

#### 4. Security Tests
- **Scope**: Input validation, SQL injection prevention
- **Coverage**: API security, data sanitization

### Mock Patterns

```python
# Correct mock return format
mock_storage.list_tasks.return_value = {
    "tasks": [task_instance],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "has_next": False,
    "has_prev": False
}

# AI agent mocking
@patch('src.agent.base.get_llm_client')
def test_ai_agent(mock_llm):
    mock_llm.return_value.generate.return_value = {
        "content": '{"patches": []}'
    }
```

### Testing Commands

```bash
# Run specific test file
cd backend && pytest tests/test_storage.py

# Run with markers
cd backend && pytest -m "unit"
cd backend && pytest -m "integration"

# Debug failing test
cd backend && pytest tests/test_api/test_task_routes.py::test_list_tasks -vv

# Stop on first failure
cd backend && pytest -x --tb=short

# Run tests in different environments
# Note: Tests always use in-memory DB, but you can test with env vars:
export $(cat .env.staging | grep -v '^#' | xargs) && cd backend && pytest
```

---

## Frontend Testing Guide

### Test Structure

```
frontend/src/
├── components/
│   └── ComponentName/
│       ├── ComponentName.tsx
│       └── ComponentName.test.tsx
├── hooks/
│   └── useHookName.test.ts
├── utils/
│   └── utilName.test.ts
└── test/setup.ts          # Global test setup
```

### Testing Philosophy

Follow user-centric testing principles:

```typescript
// ✅ Test what users see and do
expect(screen.getByText('Create Project')).toBeInTheDocument()
await userEvent.click(screen.getByRole('button', { name: /submit/i }))

// ❌ Avoid implementation details
expect(component.state.isLoading).toBe(true)
```

### Component Testing Pattern

```typescript
describe('ProjectCard', () => {
  const mockProject = {
    id: '123',
    name: 'Test Project',
    status: 'active'
  };

  it('displays project information', () => {
    render(<ProjectCard project={mockProject} />);
    
    expect(screen.getByText('Test Project')).toBeInTheDocument();
    expect(screen.getByText('active')).toBeInTheDocument();
  });

  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<ProjectCard project={mockProject} onClick={handleClick} />);
    
    await userEvent.click(screen.getByRole('article'));
    expect(handleClick).toHaveBeenCalledWith('123');
  });
});
```

### Hook Testing Pattern

```typescript
import { renderHook, waitFor } from '@testing-library/react';

describe('useProjectManagement', () => {
  it('fetches projects on mount', async () => {
    const { result } = renderHook(() => useProjectManagement());
    
    await waitFor(() => {
      expect(result.current.projects).toHaveLength(2);
    });
  });
});
```

### Mocking API Calls

```typescript
// Mock entire module
vi.mock('../services/projectService', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn()
  }
}));

// Configure mock behavior
beforeEach(() => {
  vi.mocked(projectService.getProjects).mockResolvedValue({
    data: [mockProject],
    total: 1
  });
});
```

---

## Common Testing Patterns

### 1. Arrange-Act-Assert (AAA)

All tests follow the AAA pattern for clarity:

| Language | Example |
|----------|---------|
| Python | ```python<br>def test_project_creation(isolated_client):<br>    # Arrange<br>    project_data = {"name": "Test"}<br>    <br>    # Act<br>    response = isolated_client.post("/api/projects", json=project_data)<br>    <br>    # Assert<br>    assert response.status_code == 201<br>``` |
| TypeScript | ```typescript<br>it('creates a task', async () => {<br>  // Arrange<br>  const taskData = { title: 'Test' };<br>  <br>  // Act<br>  const result = await createTask(taskData);<br>  <br>  // Assert<br>  expect(result.title).toBe('Test');<br>});<br>``` |

### 2. Test Isolation

Each test runs independently without side effects:

| Backend | Frontend |
|---------|----------|
| Database isolation via `TestDatabaseIsolation` | Mock reset in `beforeEach` |
| Fresh session per test | LocalStorage cleared |
| Automatic rollback | No global state mutation |

### 3. Fixture Patterns

#### Backend Fixtures
```python
@pytest.fixture
def sample_project(isolated_client):
    """Reusable project for tests"""
    response = isolated_client.post("/api/projects", json={
        "name": "Test Project",
        "created_by": "test_user"
    })
    return response.json()
```

#### Frontend Factories
```typescript
export const createMockProject = (overrides = {}): Project => ({
  id: 'test-id',
  name: 'Test Project',
  status: 'active',
  ...overrides
});
```

### 4. Error Testing

| Scenario | Backend Example | Frontend Example |
|----------|-----------------|------------------|
| API Error | ```python<br>response = client.post("/api/projects", json={})<br>assert response.status_code == 422<br>``` | ```typescript<br>vi.mocked(api.create).mockRejectedValue(new Error());<br>``` |
| Validation | ```python<br>with pytest.raises(ValidationError):<br>    Task(title="", project_id=None)<br>``` | ```typescript<br>expect(() => validateTask({})).toThrow();<br>``` |

---

## Troubleshooting Guide

### Critical Issues and Solutions

| Symptom | Cause | Solution | Prevention |
|---------|-------|----------|------------|
| `'Mock' object is not subscriptable` | Mock returns wrong type | Match mock return to API contract | Use TypedDict for mock data |
| `Session is already flushing` | Database isolation missing | Inherit from `TestDatabaseIsolation` | Always use `isolated_client` |
| `ImportError: attempted relative import` | Wrong directory | Run from backend: `cd backend && pytest` | Add to documentation |
| Foreign key constraint error | No cascade delete | Implement cascade in storage layer | Test deletion scenarios |
| Test data not appearing | Using wrong client fixture | Replace `client` with `isolated_client` | Consistent fixture usage |

### Common Backend Issues

#### 1. Session Management
```python
# Problem: Session conflicts
# Solution: Use flush() in transactions, commit() in standalone
def apply_patch(self, patch):
    if self._session:  # Injected session
        self.session.flush()  # Don't commit
    else:  # Fresh session
        self.session.commit()  # OK to commit
```

#### 2. Mock Configuration
```python
# ❌ Wrong - returns list
mock_storage.list_tasks.return_value = [task1, task2]

# ✅ Correct - returns dict with pagination
mock_storage.list_tasks.return_value = {
    "tasks": [task1, task2],
    "total": 2,
    "page": 1
}
```

#### 3. SQLite Limitations
- Concurrent writes: 70% success rate acceptable
- Use PostgreSQL for production concurrency testing
- Document known limitations

### Common Frontend Issues

#### 1. Act Warnings
```typescript
// Problem: State update not wrapped
// Solution: Use waitFor or act
await waitFor(() => {
  expect(screen.getByText('Updated')).toBeInTheDocument();
});
```

#### 2. Hook Dependencies
```typescript
// Problem: Infinite re-renders
// Solution: Stable dependencies
const stableCallback = useCallback(() => {
  // implementation
}, [necessaryDep]); // Only required deps
```

#### 3. Async Testing
```typescript
// Use findBy for async elements
const element = await screen.findByText('Loaded');

// Or waitFor with expect
await waitFor(() => {
  expect(mockFn).toHaveBeenCalled();
});
```

### Quick Fix Checklist

- [ ] Running tests from correct directory?
- [ ] Using `TestDatabaseIsolation` for integration tests?
- [ ] Mock return values match API contracts?
- [ ] All async operations properly awaited?
- [ ] Test data uses correct fixtures?

---

## Performance Metrics

### Backend Performance Benchmarks

| Test Type | Target | Actual | Status |
|-----------|--------|--------|--------|
| Unit tests | <100ms | ~50ms | ✅ Excellent |
| Integration tests | <500ms | ~200ms | ✅ Good |
| API response time | <200ms | ~150ms | ✅ Good |
| Concurrent requests (10) | 70% success | 70% | ✅ Acceptable (SQLite) |

### Frontend Performance Targets

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Component render | <16ms | ~10ms | ✅ Excellent |
| Test execution | <100ms | ~80ms | ✅ Good |
| Bundle size | <500KB | 420KB | ✅ Good |

### Coverage Goals

| Component | Target | Current | Trend |
|-----------|--------|---------|-------|
| Backend Core | 90% | 88% | ↗️ Improving |
| Backend API | 95% | 92% | ↗️ Improving |
| Frontend Components | 90% | 100% | ✅ Exceeded |
| Frontend Hooks | 90% | 100% | ✅ Exceeded |

---

## Related Documentation

- [Architecture Overview](architecture/overview.md)
- [API Reference](api/README.md)
- [Development Setup](deployment/setup-guide.md)