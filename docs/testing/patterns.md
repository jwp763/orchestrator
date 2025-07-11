# Common Testing Patterns

*Last Updated: 2025-01-11*

## Overview

This document describes testing patterns used across both backend (Python/pytest) and frontend (TypeScript/Vitest) codebases. These patterns ensure consistent, maintainable, and reliable tests.

## Universal Testing Principles

### 1. Arrange-Act-Assert (AAA)

All tests follow the AAA pattern:

**Python Example:**
```python
def test_project_creation(isolated_client):
    # Arrange
    project_data = {
        "name": "Test Project",
        "created_by": "test_user"
    }
    
    # Act
    response = isolated_client.post("/api/projects", json=project_data)
    
    # Assert
    assert response.status_code == 201
    assert response.json()["name"] == "Test Project"
```

**TypeScript Example:**
```typescript
it('creates a new task', async () => {
  // Arrange
  const taskData = {
    title: 'Test Task',
    project_id: 'test-project'
  };
  
  // Act
  const result = await taskService.createTask(taskData);
  
  // Assert
  expect(result.title).toBe('Test Task');
  expect(result.id).toBeDefined();
});
```

### 2. Test Isolation

Each test runs independently without side effects:

**Backend Pattern - Database Isolation:**
```python
class TestFeature(TestDatabaseIsolation):
    """Inherits database isolation for each test"""
    
    def test_isolated_operation(self, isolated_client):
        # Each test gets a fresh database
        # No cleanup needed - automatic rollback
```

**Frontend Pattern - Mock Reset:**
```typescript
beforeEach(() => {
  vi.clearAllMocks();
  localStorage.clear();
});
```

### 3. Descriptive Test Names

Test names clearly describe what is being tested:

**Python:**
```python
def test_delete_project_with_tasks_cascades_soft_delete():
    """Test name describes exact behavior"""
    pass

def test_api_returns_404_when_project_not_found():
    """Include expected outcome in name"""
    pass
```

**TypeScript:**
```typescript
describe('ProjectService', () => {
  it('should return paginated results when requesting project list', () => {});
  it('should throw error when project creation fails', () => {});
});
```

## Mock Patterns

### Backend Mocking

**1. Service Layer Mocking:**
```python
@patch('src.storage.sql_implementation.SQLStorage')
def test_with_mocked_storage(mock_storage):
    # Configure mock return value
    mock_storage.list_projects.return_value = {
        "projects": [mock_project],
        "total": 1,
        "page": 1
    }
    
    # Test uses mock instead of real database
    result = project_service.get_projects()
    assert len(result["projects"]) == 1
```

**2. External API Mocking:**
```python
@patch('src.agent.base.get_llm_client')
def test_ai_agent(mock_llm):
    mock_llm.return_value.generate.return_value = {
        "content": '{"patches": []}'
    }
    
    agent = PlannerAgent()
    result = agent.get_diff("Test idea")
    assert result.patches == []
```

### Frontend Mocking

**1. API Service Mocking:**
```typescript
vi.mock('../services/projectService', () => ({
  projectService: {
    getProjects: vi.fn(),
    createProject: vi.fn(),
  }
}));

beforeEach(() => {
  vi.mocked(projectService.getProjects).mockResolvedValue({
    success: true,
    data: { projects: [mockProject] }
  });
});
```

**2. Hook Mocking:**
```typescript
vi.mock('./hooks/useProjectManagement', () => ({
  useProjectManagement: () => ({
    projects: [mockProject],
    isLoading: false,
    error: null,
    handleProjectSelect: vi.fn()
  })
}));
```

## Fixture Patterns

### Backend Fixtures

**1. Reusable Test Data:**
```python
@pytest.fixture
def sample_project(isolated_client):
    """Create a project for use in multiple tests"""
    project_data = {
        "name": "Test Project",
        "created_by": "fixture_user"
    }
    response = isolated_client.post("/api/projects", json=project_data)
    return response.json()

def test_update_project(isolated_client, sample_project):
    # Use the fixture
    response = isolated_client.put(
        f"/api/projects/{sample_project['id']}",
        json={"name": "Updated Name"}
    )
    assert response.status_code == 200
```

**2. Fixture Composition:**
```python
@pytest.fixture
def project_with_tasks(isolated_client, sample_project):
    """Compose fixtures for complex scenarios"""
    # Create tasks for the project
    for i in range(3):
        isolated_client.post("/api/tasks", json={
            "project_id": sample_project["id"],
            "title": f"Task {i}",
            "created_by": "fixture_user"
        })
    return sample_project
```

### Frontend Fixtures

**1. Mock Data Factories:**
```typescript
// Factory functions for test data
export const createMockProject = (overrides = {}): Project => ({
  id: 'test-id',
  name: 'Test Project',
  status: 'active',
  created_at: '2025-01-11T00:00:00Z',
  ...overrides
});

export const createMockTask = (overrides = {}): Task => ({
  id: 'task-id',
  title: 'Test Task',
  status: 'todo',
  project_id: 'test-id',
  ...overrides
});
```

**2. Test Utilities:**
```typescript
// Custom render with providers
export const renderWithProviders = (ui: ReactElement) => {
  return render(
    <QueryClient>
      <ThemeProvider>
        {ui}
      </ThemeProvider>
    </QueryClient>
  );
};
```

## Integration Test Patterns

### Backend Integration

**1. Complete Workflow Testing:**
```python
class TestProjectLifecycle(TestDatabaseIsolation):
    def test_complete_project_workflow(self, isolated_client):
        # 1. Create project
        create_response = isolated_client.post("/api/projects", json={
            "name": "Workflow Test",
            "created_by": "test"
        })
        project_id = create_response.json()["id"]
        
        # 2. Add tasks
        task_response = isolated_client.post("/api/tasks", json={
            "project_id": project_id,
            "title": "Task 1",
            "created_by": "test"
        })
        
        # 3. Update project
        update_response = isolated_client.put(
            f"/api/projects/{project_id}",
            json={"status": "active"}
        )
        
        # 4. Verify final state
        get_response = isolated_client.get(f"/api/projects/{project_id}")
        project = get_response.json()
        assert project["status"] == "active"
        assert len(project["tasks"]) == 1
```

### Frontend Integration

**1. User Interaction Testing:**
```typescript
describe('Project Management Flow', () => {
  it('completes full project creation flow', async () => {
    const user = userEvent.setup();
    
    render(<App />);
    
    // Click create button
    await user.click(screen.getByText('New Project'));
    
    // Fill form
    await user.type(screen.getByLabelText('Project Name'), 'Test Project');
    await user.selectOptions(screen.getByLabelText('Priority'), 'high');
    
    // Submit
    await user.click(screen.getByText('Create'));
    
    // Verify result
    await waitFor(() => {
      expect(screen.getByText('Test Project')).toBeInTheDocument();
    });
  });
});
```

## Error Testing Patterns

### Backend Error Testing

```python
def test_handles_database_error(isolated_client, monkeypatch):
    # Simulate database error
    def mock_create(*args, **kwargs):
        raise Exception("Database connection lost")
    
    monkeypatch.setattr(
        "src.storage.sql_implementation.SQLStorage.create_project",
        mock_create
    )
    
    response = isolated_client.post("/api/projects", json={
        "name": "Test",
        "created_by": "test"
    })
    
    assert response.status_code == 500
    assert "error" in response.json()
```

### Frontend Error Testing

```typescript
it('displays error message on API failure', async () => {
  // Mock API error
  vi.mocked(projectService.createProject).mockRejectedValue(
    new Error('Network error')
  );
  
  render(<ProjectForm />);
  
  const user = userEvent.setup();
  await user.click(screen.getByText('Submit'));
  
  await waitFor(() => {
    expect(screen.getByText('Network error')).toBeInTheDocument();
  });
});
```

## Performance Testing Patterns

### Backend Performance

```python
def test_api_response_time(isolated_client, sample_projects):
    """Test that API responds within acceptable time"""
    import time
    
    start_time = time.time()
    response = isolated_client.get("/api/projects?per_page=100")
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 1.0  # Less than 1 second
```

### Frontend Performance

```typescript
it('renders large lists efficiently', async () => {
  const largeProjectList = Array.from({ length: 1000 }, (_, i) => 
    createMockProject({ id: `project-${i}`, name: `Project ${i}` })
  );
  
  const startTime = performance.now();
  render(<ProjectList projects={largeProjectList} />);
  const endTime = performance.now();
  
  expect(endTime - startTime).toBeLessThan(100); // Under 100ms
  expect(screen.getByText('Project 0')).toBeInTheDocument();
});
```

## Async Testing Patterns

### Backend Async

```python
@pytest.mark.asyncio
async def test_async_operation():
    """Test async functions properly"""
    result = await async_service.process_data()
    assert result is not None
```

### Frontend Async

```typescript
it('handles async operations', async () => {
  render(<AsyncComponent />);
  
  // Wait for async operation
  await waitFor(() => {
    expect(screen.getByText('Data loaded')).toBeInTheDocument();
  });
  
  // Alternative: use findBy (auto-waits)
  const element = await screen.findByText('Data loaded');
  expect(element).toBeInTheDocument();
});
```

## Data-Driven Testing

### Backend Parametrized Tests

```python
@pytest.mark.parametrize("status,expected_count", [
    ("active", 5),
    ("completed", 3),
    ("archived", 2),
])
def test_filter_by_status(isolated_client, status, expected_count):
    # Create projects with different statuses
    # ... setup code ...
    
    response = isolated_client.get(f"/api/projects?status={status}")
    assert len(response.json()["projects"]) == expected_count
```

### Frontend Test.each

```typescript
describe.each([
  ['active', 'bg-green-500'],
  ['completed', 'bg-gray-500'],
  ['blocked', 'bg-red-500'],
])('StatusBadge with %s status', (status, expectedClass) => {
  it(`renders with ${expectedClass} class`, () => {
    render(<StatusBadge status={status} />);
    const badge = screen.getByText(status);
    expect(badge).toHaveClass(expectedClass);
  });
});
```

## Test Organization Patterns

### Backend Organization

```python
# tests/test_api/test_project_routes.py
class TestProjectCreation:
    """Group related tests in classes"""
    
    def test_creates_with_valid_data(self):
        pass
    
    def test_rejects_invalid_data(self):
        pass
    
    def test_handles_duplicate_names(self):
        pass

class TestProjectUpdate:
    """Separate concerns into different classes"""
    
    def test_updates_allowed_fields(self):
        pass
    
    def test_prevents_invalid_updates(self):
        pass
```

### Frontend Organization

```typescript
// ProjectCard.test.tsx
describe('ProjectCard', () => {
  describe('rendering', () => {
    it('displays project information', () => {});
    it('shows correct status badge', () => {});
  });
  
  describe('interactions', () => {
    it('handles click events', () => {});
    it('shows menu on right click', () => {});
  });
  
  describe('edge cases', () => {
    it('handles missing data gracefully', () => {});
    it('truncates long descriptions', () => {});
  });
});
```

## Best Practices

1. **Keep Tests Simple**: Each test should verify one behavior
2. **Use Descriptive Names**: Test names should explain what and why
3. **Avoid Test Interdependence**: Tests must run in any order
4. **Mock External Dependencies**: Don't make real API calls
5. **Test Edge Cases**: Include error scenarios and boundaries
6. **Maintain Test Performance**: Keep individual tests under 100ms
7. **Document Complex Tests**: Add comments for non-obvious logic
8. **Refactor Test Code**: Apply same quality standards as production code

## Related Documentation

- [Backend Testing Guide](backend-guide.md)
- [Frontend Testing Guide](frontend-guide.md)
- [Testing Overview](../testing.md)
- [Troubleshooting](troubleshooting.md)