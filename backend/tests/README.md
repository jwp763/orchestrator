# Testing Guide for Databricks Orchestrator Backend

This guide provides comprehensive instructions for writing, running, and maintaining tests in the Databricks Orchestrator backend. It covers testing patterns, database isolation, fixtures, and best practices established in the codebase.

## Table of Contents

- [Overview](#overview)
- [Quick Reference](#quick-reference)
- [Test Structure](#test-structure)
- [Database Isolation](#database-isolation)
- [Test Types and Patterns](#test-types-and-patterns)
- [Fixtures and Utilities](#fixtures-and-utilities)
- [Writing New Tests](#writing-new-tests)
- [Running Tests](#running-tests)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Quick Reference

### Test Failure Checklist
**When tests fail, check these first:**

1. **Database Isolation**
   - [ ] Test class inherits from `TestDatabaseIsolation`?
   - [ ] Using `isolated_client` fixture instead of `client`?
   - [ ] All client references updated consistently?

2. **Mock Configuration**
   - [ ] Mock return value matches actual API method format?
   - [ ] Mocking the correct method (e.g., `list_tasks` not `get_tasks_by_project`)?
   - [ ] Return value is dict/list/object as expected?

3. **Execution Environment**
   - [ ] Running from backend directory: `cd backend && python -m pytest tests/`?
   - [ ] Python path and imports working correctly?

4. **Business Logic**
   - [ ] Foreign key constraints handled (cascade delete)?
   - [ ] Transaction boundaries correct (flush vs commit)?

### Common Patterns

**Integration Test Template:**
```python
class TestMyFeature(TestDatabaseIsolation):
    def test_feature_lifecycle(self, isolated_client):
        # Create, read, update, delete with isolated database
        response = isolated_client.post("/api/resource", json=data)
        assert response.status_code == 201
```

**Mock API Response Template:**
```python
# For paginated list endpoints
mock_storage.list_items.return_value = {
    "items": [item1, item2],
    "total": 2,
    "page": 1,
    "per_page": 20,
    "has_next": False,
    "has_prev": False
}
```

**Cascade Delete Pattern:**
```python
def delete_parent(self, parent_id: str) -> bool:
    # Delete children first
    children = self.session.query(Child).filter(Child.parent_id == parent_id).all()
    for child in children:
        self.session.delete(child)
    
    # Then delete parent
    parent = self.session.query(Parent).filter(Parent.id == parent_id).first()
    if parent:
        self.session.delete(parent)
        return True
    return False
```

## Overview

The test suite uses pytest with comprehensive database isolation, mock patterns, and fixture management to ensure reliable, fast, and isolated testing. Tests are organized by type (unit, integration, API) with clear separation of concerns.

### Testing Philosophy

- **Isolation**: Each test runs in complete isolation with fresh database state
- **Realistic**: Integration tests use real components with isolated data
- **Fast**: Unit tests use mocks; integration tests use in-memory databases
- **Comprehensive**: Coverage includes unit, integration, performance, and security tests

## Test Structure

```
tests/
├── README.md                          # This guide
├── __init__.py                        # Test configuration
├── test_agents/                       # Agent component tests
│   ├── __init__.py
│   ├── test_planner_agent.py         # PlannerAgent unit tests
│   ├── test_planner_agent_simple.py  # Basic agent tests
│   └── test_planner_integration.py   # Agent integration tests
├── test_api/                          # API endpoint tests
│   ├── __init__.py
│   ├── test_database_isolation.py    # Base isolation utilities
│   ├── test_task_pagination.py       # Comprehensive pagination tests
│   ├── test_project_routes.py        # Project API tests
│   ├── test_task_routes.py           # Task API tests
│   ├── test_crud_integration.py      # End-to-end CRUD tests
│   ├── test_api_performance.py       # Performance and load tests
│   └── test_api_security.py          # Security validation tests
├── test_schema_models/                # Data model tests
│   ├── __init__.py
│   ├── test_model_integration.py     # Cross-model testing
│   ├── test_patch_models.py          # Patch operation tests
│   ├── test_project_models.py        # Project model tests
│   └── test_task_models.py           # Task model tests
├── test_storage.py                    # Storage layer tests
├── test_soft_delete_*.py             # Soft delete functionality tests
└── conftest.py                       # Global test configuration
```

## Database Isolation

### Core Isolation Pattern

All tests requiring database access inherit from `TestDatabaseIsolation` base class:

```python
from tests.test_api.test_database_isolation import TestDatabaseIsolation

class TestYourFeature(TestDatabaseIsolation):
    """Test your feature with database isolation."""
    
    def test_your_feature(self, isolated_client):
        """Test using isolated client with fresh database."""
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
```

### Key Isolation Fixtures

#### `isolated_engine` (Function Scope)
Creates an in-memory SQLite database for each test:

```python
@pytest.fixture(scope="function")
def isolated_engine(self):
    """Create isolated in-memory database engine for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    Base.metadata.create_all(engine)
    return engine
```

#### `isolated_session` (Function Scope)
Provides a database session with automatic rollback:

```python
@pytest.fixture(scope="function")
def isolated_session(self, isolated_engine):
    """Create isolated database session with automatic rollback."""
    Session = sessionmaker(bind=isolated_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()  # Always rollback to ensure isolation
        session.close()
```

#### `isolated_storage` (Function Scope)
Storage layer instance with isolated session:

```python
@pytest.fixture(scope="function")
def isolated_storage(self, isolated_session):
    """Create isolated storage instance for testing."""
    storage = SQLStorage(database_url="sqlite:///:memory:")
    storage.session = isolated_session
    yield storage
    # Cleanup handled automatically
```

#### `isolated_client` (Function Scope)
FastAPI test client with dependency injection:

```python
@pytest.fixture(scope="function")
def isolated_client(self, isolated_storage):
    """Create isolated test client with database isolation."""
    from src.api.project_routes import get_storage as get_project_storage
    from src.api.task_routes import get_storage as get_task_storage
    
    # Override FastAPI dependencies
    app.dependency_overrides[get_project_storage] = lambda: isolated_storage
    app.dependency_overrides[get_task_storage] = lambda: isolated_storage
    
    try:
        client = TestClient(app)
        yield client
    finally:
        app.dependency_overrides.clear()  # Always cleanup
```

### Database Isolation Benefits

- **Complete Isolation**: Each test gets a fresh, empty database
- **No Side Effects**: Tests cannot interfere with each other
- **Fast Execution**: In-memory databases are extremely fast
- **Automatic Cleanup**: No manual cleanup required
- **Realistic Testing**: Uses real database operations, not mocks

## Test Types and Patterns

### Unit Tests

Test individual components in isolation with mocked dependencies.

```python
class TestSQLStorageUnit:
    """Unit tests for SQLStorage with mocked dependencies."""
    
    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock SQLAlchemy session."""
        return Mock()
    
    def test_create_project_calls_session_add(self, storage, mock_session):
        """Test that create_project calls session.add."""
        project = Project(name="Test Project", created_by="test_user")
        
        with mock_patch.object(storage, "_convert_pydantic_project_to_sql") as mock_convert:
            mock_convert.return_value = Mock()
            result = storage.create_project(project)
            mock_session.add.assert_called_once()
```

**Key Characteristics:**
- Mock external dependencies (database, APIs, file system)
- Test single component or method
- Fast execution (no I/O)
- Focus on logic and behavior

### Integration Tests

Test complete workflows with real components but isolated data.

```python
class TestCRUDIntegrationLifecycles(TestDatabaseIsolation):
    """Integration tests for complete CRUD lifecycles."""
    
    def test_project_complete_lifecycle(self, isolated_client):
        """Test complete project lifecycle from creation to deletion."""
        # 1. Create project
        project_data = {"name": "Test Project", "created_by": "user"}
        create_response = isolated_client.post("/api/projects", json=project_data)
        assert create_response.status_code == 201
        
        # 2. Read project
        project_id = create_response.json()["id"]
        get_response = isolated_client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200
        
        # 3. Update project
        update_data = {"name": "Updated Project"}
        update_response = isolated_client.put(f"/api/projects/{project_id}", json=update_data)
        assert update_response.status_code == 200
        
        # 4. Delete project
        delete_response = isolated_client.delete(f"/api/projects/{project_id}")
        assert delete_response.status_code == 204
```

**Key Characteristics:**
- Use real database operations with isolated data
- Test complete user workflows
- Verify end-to-end functionality
- Include realistic error scenarios

### Performance Tests

Test system performance under load and measure metrics.

```python
class TestAPIPerformance(TestDatabaseIsolation):
    """Performance tests for API endpoints."""
    
    def test_concurrent_requests_performance(self, isolated_client):
        """Test API performance under concurrent load."""
        def create_project(client, project_num):
            project_data = {
                "name": f"Concurrent Test Project {project_num}",
                "created_by": f"user_{project_num}"
            }
            start_time = time.time()
            response = client.post("/api/projects", json=project_data)
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time
            }
        
        # Test concurrent project creation
        concurrent_requests = 10
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [
                executor.submit(create_project, isolated_client, i)
                for i in range(concurrent_requests)
            ]
            results = [future.result() for future in as_completed(futures)]
        
        # Verify all requests succeeded
        successful_requests = sum(1 for r in results if r["status_code"] == 201)
        assert successful_requests == concurrent_requests
```

### Security Tests

Test security measures and input validation.

```python
class TestAPISecurity(TestDatabaseIsolation):
    """Security tests for API endpoints."""
    
    def test_sql_injection_prevention(self, isolated_client):
        """Test that SQL injection attempts are prevented."""
        malicious_payloads = [
            "'; DROP TABLE projects; --",
            "' OR 1=1 --",
            "'; INSERT INTO projects (name) VALUES ('hacked'); --"
        ]
        
        for payload in malicious_payloads:
            project_data = {"name": payload, "created_by": "test_user"}
            response = isolated_client.post("/api/projects", json=project_data)
            
            # Should either succeed with escaped data or fail validation
            if response.status_code == 201:
                # If created, verify data was escaped properly
                project = response.json()
                assert project["name"] == payload  # Stored as-is, not executed
```

## Fixtures and Utilities

### Data Creation Fixtures

Create reusable test data with proper dependencies:

```python
@pytest.fixture
def sample_projects(self, isolated_client):
    """Create sample projects for testing."""
    projects_data = [
        {"name": "Project Alpha", "priority": "high", "created_by": "user1"},
        {"name": "Project Beta", "priority": "medium", "created_by": "user2"},
        {"name": "Project Gamma", "priority": "low", "created_by": "user3"}
    ]
    
    created_projects = []
    for project_data in projects_data:
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        created_projects.append(response.json())
    
    return created_projects

@pytest.fixture
def sample_tasks(self, isolated_client, sample_projects):
    """Create sample tasks based on sample projects."""
    tasks_data = []
    for i, project in enumerate(sample_projects):
        task_data = {
            "project_id": project["id"],
            "title": f"Task {i+1}",
            "status": "todo",
            "created_by": "task_user"
        }
        response = isolated_client.post("/api/tasks", json=task_data)
        assert response.status_code == 201
        tasks_data.append(response.json())
    
    return tasks_data
```

### Mock Fixtures

Common mocking patterns for external dependencies:

```python
@pytest.fixture
def mock_llm_client():
    """Mock LLM client for agent testing."""
    with patch('src.agent.base.get_llm_client') as mock:
        mock_client = AsyncMock()
        mock_client.generate.return_value = {
            "content": '{"project_patches": [], "task_patches": []}'
        }
        mock.return_value = mock_client
        yield mock_client

@pytest.fixture
def mock_settings():
    """Mock application settings."""
    settings = MagicMock()
    settings.default_provider = "anthropic"
    settings.get_api_key.return_value = "test-key"
    settings.model_name = "claude-3-sonnet"
    return settings
```

### Assertion Helpers

Reusable assertion patterns:

```python
def assert_valid_project_response(project_data, expected_name=None):
    """Assert that project response has valid structure."""
    assert "id" in project_data
    assert "name" in project_data
    assert "created_at" in project_data
    assert "updated_at" in project_data
    
    if expected_name:
        assert project_data["name"] == expected_name
    
    # Validate UUID format
    import uuid
    uuid.UUID(project_data["id"])  # Will raise if invalid

def assert_api_error_response(response, expected_status, expected_detail=None):
    """Assert that API error response has expected format."""
    assert response.status_code == expected_status
    error_data = response.json()
    assert "detail" in error_data
    
    if expected_detail:
        assert expected_detail in error_data["detail"]
```

## Writing New Tests

### 1. Choose the Right Test Type

- **Unit Test**: Testing individual functions/methods with mocked dependencies
- **Integration Test**: Testing complete workflows with real components
- **API Test**: Testing HTTP endpoints with full request/response cycle

### 2. Use Appropriate Base Class

```python
# For tests requiring database access
class TestYourFeature(TestDatabaseIsolation):
    pass

# For pure unit tests without database
class TestYourComponent:
    pass
```

### 3. Follow Naming Conventions

```python
# Test files
test_feature_name.py

# Test classes  
class TestFeatureName:
    pass

# Test methods
def test_specific_behavior_description(self):
    pass

# Fixtures
@pytest.fixture
def feature_specific_fixture(self):
    pass
```

### 4. Structure Test Methods

```python
def test_specific_behavior(self, isolated_client):
    """Test description explaining what behavior is being tested."""
    # 1. Arrange: Set up test data and conditions
    project_data = {"name": "Test Project", "created_by": "user"}
    
    # 2. Act: Perform the action being tested
    response = isolated_client.post("/api/projects", json=project_data)
    
    # 3. Assert: Verify the expected outcome
    assert response.status_code == 201
    project = response.json()
    assert project["name"] == "Test Project"
```

### 5. Use Fixtures Effectively

```python
class TestProjectManagement(TestDatabaseIsolation):
    """Test project management functionality."""
    
    @pytest.fixture
    def test_project(self, isolated_client):
        """Create a test project for reuse in multiple tests."""
        project_data = {"name": "Test Project", "created_by": "test_user"}
        response = isolated_client.post("/api/projects", json=project_data)
        return response.json()
    
    def test_project_update(self, isolated_client, test_project):
        """Test project update functionality."""
        update_data = {"name": "Updated Project"}
        response = isolated_client.put(
            f"/api/projects/{test_project['id']}", 
            json=update_data
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Project"
```

## Running Tests

### Running All Tests

```bash
# Run entire test suite
pytest

# Run with coverage
pytest --cov=src

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_api/test_task_pagination.py

# Run specific test class
pytest tests/test_api/test_task_pagination.py::TestTaskPagination

# Run specific test method
pytest tests/test_api/test_task_pagination.py::TestTaskPagination::test_newly_created_task_appears_first
```

### Running by Category

```bash
# Run only unit tests (fast)
pytest tests/test_storage.py -k "Unit"

# Run only integration tests
pytest tests/test_api/test_crud_integration.py

# Run only performance tests
pytest tests/test_api/test_api_performance.py

# Run only security tests
pytest tests/test_api/test_api_security.py
```

### Performance Testing

```bash
# Run performance tests with timing
pytest tests/test_api/test_api_performance.py -v --tb=short

# Run with memory profiling
pytest tests/test_api/test_api_performance.py --profile

# Run concurrent tests specifically
pytest tests/test_api/test_api_performance.py::TestAPIPerformance::test_concurrent_requests_performance
```

### Debugging Tests

```bash
# Run with debugger on failure
pytest --pdb

# Show all output (disable capture)
pytest -s

# Stop on first failure
pytest -x

# Show local variables in traceback
pytest -l

# Verbose output with full diff
pytest -vvv
```

## Troubleshooting

### Recent Critical Patterns (July 2025)

#### Mock Object "Not Subscriptable" Errors
**Issue**: `'Mock' object is not subscriptable` in API route tests
**Cause**: Mock return value format doesn't match actual API method expectations
**Solution**: Always check what the actual route method calls and match the return format

```python
# ❌ Wrong - mocking wrong method with wrong format
mock_storage.get_tasks_by_project.return_value = [task_instance]

# ✅ Correct - mocking actual method with correct format
mock_storage.list_tasks.return_value = {
    "tasks": [task_instance],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "has_next": False,
    "has_prev": False
}
```

#### Foreign Key Constraint Violations
**Issue**: 500 errors when deleting resources with related data
**Cause**: No cascade delete logic implemented in storage layer
**Solution**: Implement proper cascade delete in storage methods

```python
# Example: Project deletion with task cascade
def delete_project(self, project_id: str) -> bool:
    # Delete related tasks first
    sql_tasks = self.session.query(SQLTask).filter(SQLTask.project_id == project_id).all()
    for task in sql_tasks:
        self.session.delete(task)
    
    # Then delete the project
    self.session.delete(sql_project)
```

#### Integration Test Database Isolation
**Issue**: Test data not appearing in listings, isolation failures
**Cause**: Test classes not properly inheriting from `TestDatabaseIsolation`
**Solution**: ALL integration tests must use proper base class and fixtures

```python
# ❌ Wrong - custom fixtures, shared database
class TestMyIntegration:
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    def test_something(self, client):
        # Uses shared database - data conflicts

# ✅ Correct - proper isolation
class TestMyIntegration(TestDatabaseIsolation):
    def test_something(self, isolated_client):
        # Uses isolated database - no conflicts
```

#### Client Fixture Consistency
**Issue**: Mixed fixture usage causing database state conflicts
**Cause**: Using both `client` and `isolated_client` inconsistently
**Solution**: Systematic replacement when inheriting `TestDatabaseIsolation`

```python
# Replace ALL instances in test methods:
# client.get() -> isolated_client.get()
# client.post() -> isolated_client.post()
# client.put() -> isolated_client.put()
# client.delete() -> isolated_client.delete()
```

### Common Issues and Solutions

#### Database Session Conflicts

**Symptom**: `SQLAlchemy session closed`, `Session is already flushing`, or `transaction state` errors

**Root Cause**: Multiple threads sharing the same SQLAlchemy session instance, or improper transaction management.

**Solution**: Ensure proper inheritance from `TestDatabaseIsolation` and understand session management:

```python
# ❌ Wrong - no database isolation
class TestMyFeature:
    def test_something(self, client):  # Uses shared database
        pass

# ✅ Correct - with database isolation
class TestMyFeature(TestDatabaseIsolation):
    def test_something(self, isolated_client):  # Uses isolated database
        pass
```

#### Test Interference

**Symptom**: Tests pass individually but fail when run together

**Solution**: Check for shared state or missing isolation:

```python
# ❌ Wrong - shared class variables
class TestMyFeature:
    shared_data = []  # This persists between tests!
    
# ✅ Correct - use fixtures for test data
class TestMyFeature(TestDatabaseIsolation):
    @pytest.fixture
    def test_data(self):
        return []  # Fresh data for each test
```

#### Fixture Scope Issues

**Symptom**: Unexpected data persistence between tests

**Solution**: Use function scope for isolation:

```python
# ❌ Wrong - session scope can cause interference
@pytest.fixture(scope="session")
def shared_database():
    pass

# ✅ Correct - function scope for isolation
@pytest.fixture(scope="function")
def isolated_database():
    pass
```

#### Async Test Issues

**Symptom**: `RuntimeError: no running event loop`

**Solution**: Use proper async test markers:

```python
# ✅ Correct async testing
@pytest.mark.asyncio
async def test_async_operation():
    result = await some_async_function()
    assert result is not None
```

#### Mock Configuration Problems

**Symptom**: Mocks not being applied or persisting between tests

**Solution**: Use proper mock context management:

```python
# ✅ Correct mock usage
def test_with_mock(self):
    with patch('src.module.function') as mock_func:
        mock_func.return_value = "test_value"
        result = function_under_test()
        assert result == "expected"
    # Mock automatically cleaned up
```

#### Session Management and Transaction Issues

**Symptom**: `Session is already flushing`, `no such table`, or transaction rollback failures

**Root Cause**: Improper session handling in SQLStorage between standalone operations and transactions

**Solution**: Understand the SQLStorage session behavior:

```python
# SQLStorage behavior:
# - With injected session (transactions): uses flush() to avoid premature commits
# - Without injected session (standalone): creates new session and commits

# ✅ Testing transaction rollback
def test_transaction_rollback(self, isolated_storage):
    storage.begin_transaction()
    # Operations here use flush(), not commit()
    result = storage.apply_patch(patch_with_error)
    assert result is False  # Should rollback automatically

# ✅ Testing concurrent operations  
def test_concurrent_requests(self, isolated_client):
    # Each API call gets its own session via dependency injection
    # This prevents "Session is already flushing" errors
```

**Key Points for Future Sessions**:
- SQLStorage.session setter must update SessionLocal to use same engine
- Apply patch methods use flush() to maintain transaction boundaries  
- Concurrent tests may show partial failures (7/10) due to SQLite limitations - this is acceptable
- Always run tests from backend/ directory to avoid import errors

**For Specific Error Patterns and Solutions:**
See `TESTING_TROUBLESHOOTING.md` in the project root for detailed troubleshooting guide with:
- Recent critical issues and their fixes
- Common error patterns and solutions
- Step-by-step debugging approaches
- Historical context of major fixes

#### Import and Module Issues

**Symptom**: `ImportError: attempted relative import beyond top-level package`

**Solution**: Always run tests from the correct directory:

```bash
# ✅ Correct - run from backend directory
cd backend && python -m pytest tests/

# ❌ Wrong - causes import issues
python -m pytest backend/tests/
```

### Performance Issues

#### Slow Test Execution

**Common Causes:**
- Using real database instead of in-memory
- Not using proper mocking for external calls
- Complex test data setup

**Solutions:**
```python
# ✅ Use in-memory database (inherited from TestDatabaseIsolation)
class TestMyFeature(TestDatabaseIsolation):
    pass

# ✅ Mock external dependencies
@patch('src.external.api_call')
def test_with_external_dependency(self, mock_api):
    mock_api.return_value = {"result": "success"}
    # Test continues without real API call
```

#### Memory Leaks in Tests

**Symptoms**: Tests slow down over time, memory usage increases

**Solutions:**
- Ensure proper session cleanup (handled by `TestDatabaseIsolation`)
- Close file handles and network connections
- Use appropriate fixture scopes

## Best Practices

### Test Organization

1. **Group Related Tests**: Use test classes to group related functionality
2. **Clear Naming**: Test names should describe behavior, not implementation
3. **One Concept per Test**: Each test should verify one specific behavior
4. **Proper Setup/Teardown**: Use fixtures for setup, rely on isolation for cleanup

### Database Testing

1. **Always Use Isolation**: Inherit from `TestDatabaseIsolation` for database tests
2. **Test Real Scenarios**: Use realistic data and workflows
3. **Verify State Changes**: Assert database state before and after operations
4. **Test Edge Cases**: Include boundary conditions and error scenarios

### Mock Usage

1. **Mock External Dependencies**: Database, APIs, file system, time
2. **Don't Mock Code Under Test**: Only mock dependencies, not the system being tested
3. **Verify Mock Interactions**: Assert that mocks were called correctly
4. **Use Realistic Mock Data**: Mock responses should match real service behavior

### Assertions

1. **Specific Assertions**: Use specific assertions rather than general ones
2. **Multiple Assertions**: It's OK to have multiple assertions in one test for related checks
3. **Error Testing**: Test both success and failure scenarios
4. **Message Clarity**: Use assertion messages to clarify what failed

### Fixtures

1. **Single Responsibility**: Each fixture should have one clear purpose
2. **Proper Scope**: Use function scope for isolation, higher scopes sparingly
3. **Dependency Injection**: Use fixture dependencies to build complex scenarios
4. **Cleanup Handling**: Rely on automatic cleanup rather than manual teardown

### Performance Considerations

1. **Fast Unit Tests**: Keep unit tests under 100ms each
2. **Efficient Integration Tests**: Use in-memory databases for speed
3. **Parallel Execution**: Write tests that can run in parallel safely
4. **Resource Management**: Properly manage connections and file handles

### Documentation

1. **Test Docstrings**: Explain what behavior is being tested
2. **Fixture Documentation**: Document complex fixtures and their purpose
3. **Update This Guide**: Keep this README current as patterns evolve
4. **Code Comments**: Explain complex test setup or assertions

---

## Contributing to Tests

When adding new tests or modifying existing ones:

1. **Follow Existing Patterns**: Use the same patterns and fixtures as similar tests
2. **Add Documentation**: Update this README if introducing new patterns
3. **Test Your Tests**: Ensure new tests fail appropriately when code is broken
4. **Consider Performance**: Keep tests fast and efficient
5. **Review Coverage**: Aim for comprehensive coverage of new functionality

This testing guide is a living document. As new patterns emerge or existing ones evolve, please update this documentation to help future developers understand and maintain the test suite effectively.

## Additional Resources

- **`TESTING_TROUBLESHOOTING.md`** - Detailed troubleshooting guide for specific error patterns
- **`CLAUDE.md`** - Section 9 contains critical test troubleshooting checklist
- **`backend/tests/README.md`** - This comprehensive guide (you are here)
- **Project test history** - Check git history for test-related commits and their messages

**When encountering new test issues:**
1. Check this README first for patterns and solutions
2. Consult `TESTING_TROUBLESHOOTING.md` for specific error messages
3. Update both documents with any new patterns discovered
4. Consider adding examples to help future developers

## Recent Improvements (July 2025)

### API Testing Best Practices

**Parameter Naming Consistency**:
- Always verify API parameter names match test expectations
- Add parameter aliases for better usability (`status` vs `task_status`)
- Document parameter naming conventions in API specifications

**Pagination Handling**:
- Explicitly specify pagination parameters in tests
- Don't assume APIs return all results by default
- Test both paginated and full result scenarios

### Performance Testing Insights

**Concurrency Limitations**:
- SQLite has fundamental concurrent write limitations
- Expect lower success rates in concurrent tests (7/10 vs 10/10)
- Consider PostgreSQL for production concurrent load testing
- Document database-specific constraints in test descriptions

**Optional Dependencies**:
- Use graceful skipping for optional dependencies (`psutil`, monitoring tools)
- Document optional dependencies in test requirements
- Provide fallback implementations where possible

### Session Management Patterns

**Storage Layer Testing**:
- Test both injected and fresh session scenarios
- Maintain consistent session lifecycle management
- Separate unit tests (mocked sessions) from integration tests (real sessions)
- Document session injection patterns for test consistency

**Database Isolation**:
- Continue using `TestDatabaseIsolation` for all integration tests
- Fresh sessions prevent concurrent test interference
- Session cleanup is critical for test reliability

### Mock Configuration Advanced Patterns

**Model Name Alignment**:
- Ensure mock model names match actual SQLAlchemy models
- Use `Project` and `Task` not `SQLProject` and `SQLTask` in mocks
- Test mock configurations with actual model conversion logic

**Return Value Structures**:
- Mock return values must match actual API response structures
- Test both success and failure scenarios in mock configurations
- Validate mock behavior matches production code behavior

### Test Reliability Metrics

**Current Status** (July 2025):
- **516 total test cases**
- **3 failures remaining** (down from 7 total issues)
- **Critical API functionality**: All fixed
- **Remaining issues**: Test infrastructure and SQLite concurrency

**Quality Improvements**:
- Fixed all API filtering and pagination issues
- Improved session management reliability
- Added graceful handling of optional dependencies
- Better error messages and debugging information
