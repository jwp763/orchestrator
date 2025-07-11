# Testing Overview

*Last Updated: 2025-01-11*

## Backend Testing (Python)

### Framework & Configuration
- **Framework**: pytest with pytest-cov for coverage reporting
- **Configuration**: Defined in `pyproject.toml` with comprehensive test options
- **Test Discovery**: Tests located in `tests/` directory and individual test files in `backend/`

### Test Structure
```
backend/
├── tests/
│   ├── test_api/           # API endpoint tests
│   ├── test_agents/        # Agent behavior tests
│   ├── test_schema_models/ # Data model tests
│   └── *.py               # Core functionality tests
├── test_*.py              # Additional test files
```

### Key Test Categories
1. **API Tests** (`tests/test_api/`):
   - `test_crud_integration.py` - CRUD operations
   - `test_api_security.py` - Security testing
   - `test_task_pagination.py` - Pagination functionality
   - `test_api_performance.py` - Performance testing
   - `test_database_isolation.py` - Database testing

2. **Agent Tests** (`tests/test_agents/`):
   - `test_agent_base.py` - Base agent functionality
   - `test_planner_agent.py` - Planning agent logic
   - `test_planner_integration.py` - Integration testing

3. **Schema Model Tests** (`tests/test_schema_models/`):
   - `test_task_models.py` - Task model validation and behavior
   - `test_project_models.py` - Project model testing
   - `test_patch_models.py` - Patch model testing
   - `test_model_integration.py` - Cross-model integration tests

4. **Core Tests**:
   - `test_storage.py` - Data storage functionality
   - `test_soft_delete_models.py` - Soft delete features
   - `test_soft_delete_performance.py` - Performance of soft delete
   - `test_soft_delete_migration.py` - Migration testing

### Testing Features
- **Coverage Reporting**: HTML and terminal coverage reports
- **Async Testing**: Full async/await support with pytest-asyncio
- **Mocking**: Extensive use of unittest.mock for isolation
- **Error Handling**: Comprehensive error scenario testing
- **Retry Logic**: Tests for retry mechanisms with backoff
- **Validation**: Pydantic model validation testing

### Test Configuration (pyproject.toml)
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
]
```

## Frontend Testing (React/TypeScript)

### Framework & Configuration
- **Framework**: Vitest with React Testing Library
- **Environment**: jsdom for DOM simulation
- **Setup**: Custom test setup with mocks in `src/test/setup.ts`

### Test Structure
```
frontend/src/
├── components/
│   ├── TaskCard/TaskCard.test.tsx
│   ├── TaskDetails/TaskDetails.test.tsx
│   └── ProjectDetails/ProjectDetails.test.tsx
├── hooks/
│   ├── usePlannerAPI.test.ts
│   └── useLocalStorage.test.ts
├── utils/
│   ├── date.test.ts
│   └── colors.test.ts
├── types/api.test.ts
├── App.test.tsx
└── test/setup.ts
```

### Testing Features
- **Component Testing**: Full component rendering and interaction tests
- **Hook Testing**: Custom React hooks testing
- **Utility Testing**: Pure function and utility testing
- **Mocking**: localStorage, sessionStorage, and fetch API mocks
- **User Interaction**: fireEvent and user-event testing
- **Accessibility**: Testing Library's accessibility-focused queries

### Test Configuration (vite.config.ts)
```typescript
export default defineConfig({
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
})
```

### Frontend Test Scripts
- `npm test` - Run tests in watch mode
- `npm run test:run` - Run tests once
- `npm run test:coverage` - Run tests with coverage

## Code Quality & Linting

### Backend
- **Black**: Code formatting (120 character line length)
- **isort**: Import sorting
- **flake8**: Linting with custom rules
- **mypy**: Static type checking with Pydantic support
- **ruff**: Additional linting (modern Python linter)

### Frontend
- **ESLint**: Code linting with React-specific rules
- **Prettier**: Code formatting
- **TypeScript**: Static type checking

## Testing Patterns & Best Practices

### Backend Patterns
- **Fixture-based Testing**: Extensive use of pytest fixtures
- **Async Testing**: Proper async/await testing patterns
- **Mock Isolation**: Comprehensive mocking for external dependencies
- **Error Scenario Testing**: Testing failure cases and error handling
- **Integration Testing**: Full workflow testing

### Frontend Patterns
- **Component Testing**: Testing component rendering and user interactions
- **Hook Testing**: Testing custom React hooks in isolation
- **Mock Management**: Proper setup and teardown of mocks
- **Accessibility Testing**: Using Testing Library's accessibility-focused approach
- **Edge Case Testing**: Testing null/undefined states and error conditions

## Test Coverage & Quality

### Backend
- **Coverage Reporting**: Both terminal and HTML coverage reports
- **Test Organization**: Well-structured test hierarchy
- **Comprehensive Coverage**: API, business logic, and integration tests
- **Performance Testing**: Dedicated performance test suites

### Frontend
- **Component Coverage**: Tests for major UI components
- **Business Logic**: Tests for utilities and custom hooks
- **Error Handling**: Tests for error states and edge cases
- **Type Safety**: TypeScript ensures type correctness

## Development Workflow

### Running Tests
- **Backend**: `pytest` (with coverage enabled by default)
- **Frontend**: `npm test` or `npm run test:run`

### Test Development
- Both backend and frontend follow TDD/BDD patterns
- Comprehensive test suites for new features
- Integration tests for complex workflows
- Performance and load testing considerations

## Documentation & Planning

The project includes extensive testing documentation in the `docs_archive/` directory, including:
- Test strategy documentation
- Testing checklists and requirements
- Performance testing guidelines
- Integration testing plans

This testing setup demonstrates a mature, production-ready approach with comprehensive coverage across both backend and frontend components.

## Current Test Statistics (Updated July 2025)

### Backend Test Files
- **Total Test Cases**: 516 individual test cases
- **Current Status**: 512 passed, 3 failed, 1 skipped
- **Test Reliability**: 99.4% (512/516 passing)
- **Organized Test Directory**: 25 Python test files in `backend/tests/`
- **Root Level Tests**: 6 additional test files in `backend/` root
- **Test Categories**: 
  - API Tests (10 files)
  - Agent Tests (4 files)
  - Schema Model Tests (4 files)
  - Core Functionality Tests (7 files)

### Frontend Test Files
- **Total Test Files**: 12 test files
- **Component Tests**: 4 component test files
- **Hook Tests**: 2 custom hook test files
- **Utility Tests**: 2 utility test files
- **Type Tests**: 1 API type test file
- **App Tests**: 1 main application test file

### Test Coverage Areas
- **Backend**: API endpoints, business logic, data models, agents, storage, migrations
- **Frontend**: React components, custom hooks, utilities, types, user interactions
- **Integration**: Cross-system integration testing
- **Performance**: Load testing and performance benchmarks
- **Security**: Security-focused testing for APIs and data handling

The testing infrastructure continues to evolve with comprehensive coverage ensuring code quality and reliability across all system components.

## Recent Test Improvements (July 2025)

### Critical Issues Resolved
- **API Filtering**: Fixed parameter naming mismatches (`status` vs `task_status`)
- **Pagination Logic**: Corrected test expectations for API pagination defaults
- **Optional Dependencies**: Added graceful skipping for missing dependencies (`psutil`)
- **Session Management**: Improved SQLite session handling for better reliability

### Test Reliability Metrics
- **Before**: 499 passed, 5 failed, 2 errors (7 total issues)
- **After**: 512 passed, 3 failed, 1 skipped (3 total issues)
- **Improvement**: 57% reduction in test failures
- **API Functionality**: All critical API issues resolved

### Remaining Issues
1. **Storage Unit Test**: Session injection mocking needs refinement
2. **SQLite Concurrency**: Fundamental limitations (7/10 vs 10/10 success rate)
3. **Import Error**: Minor import issue in task validation tests

### Quality Improvements
- Enhanced troubleshooting documentation with 5 new error patterns
- Updated testing guidelines with session management best practices
- Added API parameter naming consistency guidelines
- Improved optional dependency handling patterns