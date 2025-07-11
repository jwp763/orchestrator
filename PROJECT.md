# AI-Assisted Project Plan & Context

## 1. Project Goal

This project, the Orchestrator, is a personal project and task management system that uses AI agents to intelligently orchestrate work across multiple platforms. The MVP focuses on a conversational interface for project and task management, where the AI agent assists the user in breaking down goals into actionable tasks.

**Recent Achievement (July 2025)**: Successfully improved test suite reliability from 478 to 499 passing tests by implementing proper database isolation patterns, fixing cascade delete logic, and resolving mock configuration issues. Test failure rate reduced from 8 to 5 critical issues.

## 2. Tech Stack

- **Language:** Python 3.8+
- **Platform:** Local Development (FastAPI, SQLite)
- **Core Libraries:** pydantic, sqlalchemy, fastapi
- **IDE:** Cursor with AI assistance
- **Version Control:** GitLab

## 3. Project Structure

- `src/`: Core application code, including the AI agent, data models, and integrations.
- `notebooks/`: Databricks notebooks for interactive development and setup.
- `tests/`: Unit and integration tests.
- `configs/`: Environment-specific configurations.
- `.ai/`: AI tool configurations, detailed tasks, and context.
- `docs/`: Human-readable documentation, including architecture and decision records.

## 4. Development Standards

### Code Style

- Follow PEP 8 with Black formatting.
- Use type hints for all functions.
- Write clear, structured docstrings for all public methods.

### Testing

- Use pytest for all testing.
- Aim for a minimum of 80% code coverage.
- All new features must be accompanied by tests, as detailed in the MVP plan.
- **CRITICAL**: Follow the testing patterns and guidelines in `backend/tests/README.md` for backend tests
- **CRITICAL**: Follow the testing patterns and guidelines in `frontend/tests/README.md` for frontend tests
- **CRITICAL**: When introducing new testing techniques or patterns, update the respective README files to document them
- **Backend**: Use database isolation for all API and integration tests (inherit from `TestDatabaseIsolation`)
- **Frontend**: Use React Testing Library with Vitest for component and hook testing
- Write unit tests with proper mocking for fast execution
- Include performance and security tests for critical features

## 5. Workflow Commands

### Backend Testing

**CRITICAL**: Always run from backend directory to avoid import errors:

- `cd backend && pytest`: Run the backend test suite.
- `cd backend && pytest -v`: Run tests with verbose output.
- `cd backend && pytest --cov=src`: Run tests with coverage reporting.
- `cd backend && pytest tests/test_api/test_task_pagination.py`: Run specific test file.
- `cd backend && pytest tests/ -x --tb=short`: Stop on first failure with short traceback.

### Frontend Testing

- `cd frontend && npm test`: Run the frontend test suite.
- `cd frontend && npm run test:watch`: Run tests in watch mode.
- `cd frontend && npm run test:coverage`: Run tests with coverage.
- `cd frontend && npm run test:ui`: Run tests with Vitest UI.

### Code Quality

- `black .`: Format the code.
- `mypy .`: Run static type checking.

**Testing Documentation:**

- **Testing Overview**: See `testing_overview.md` for comprehensive testing strategy, frameworks, and current test statistics
- **Backend**: See `backend/tests/README.md` for comprehensive backend testing guidelines
- **Frontend**: See `frontend/tests/README.md` for comprehensive frontend testing guidelines
- **Troubleshooting**: See `TESTING_TROUBLESHOOTING.md` for specific error patterns and solutions

## 6. Current Tasks

For the current development sprint, please refer to the detailed MVP plan, which includes detailed descriptions, implementation details, and tests for each task.

- **Active Plan:** [MVP Project Plan](docs/MVP_PLAN.md)

For a machine-readable list of tasks, see:

- **Structured Tasks:** `.ai/tasks/current.yaml`

## 7. Architecture & Design

For a deeper understanding of the system architecture and key design decisions, please refer to:

- **Architecture Overview:** `docs/architecture.md`
- **Architecture Decision Records (ADRs):** `docs/decisions/`

## 8. Agent-Hints & Constraints

- **Do Not Modify:** Production configurations or secrets without explicit approval.
- **Idempotency:** Ensure that all data operations are idempotent where possible.
- **Transactions:** When performing operations that span multiple systems (e.g., database and an external API), ensure they are handled within a transaction or have a clear rollback strategy.
- **Test Execution**: Always run tests from the backend/ directory: `cd backend && python -m pytest tests/`
- **Session Management**: SQLStorage uses flush() for transactions, commit() for standalone operations

## 9. Critical Test Troubleshooting - MUST READ FIRST

**WHEN TESTS FAIL, CHECK THIS SECTION FIRST:**

### Common Test Issues and Solutions

1. **Database Isolation Problems**
   - **Symptom**: Tests fail with "Session is already flushing", "database is locked", or "session closed"
   - **Solution**: Ensure test classes inherit from `TestDatabaseIsolation` and use `isolated_client` fixture
   - **Example**: `class TestMyFeature(TestDatabaseIsolation): def test_something(self, isolated_client):`
   - **Details**: See `backend/tests/README.md` section "Database Isolation"

2. **Mock Object Errors**
   - **Symptom**: "'Mock' object is not subscriptable" or "'Mock' object has no attribute"
   - **Solution**: Check that mocks return the expected data structure (dict vs list vs object)
   - **Example**: `mock_storage.list_tasks.return_value = {"tasks": [...], "total": 1, "page": 1}`
   - **Details**: See `backend/tests/README.md` section "Mock Configuration Problems"

3. **Foreign Key Constraint Errors**
   - **Symptom**: 500 errors when deleting projects with tasks
   - **Solution**: Check if cascade delete is implemented in storage layer
   - **Location**: `src/storage/sql_implementation.py` delete_project method
   - **Details**: See `backend/tests/TESTING_TROUBLESHOOTING.md`

4. **Import Path Issues**
   - **Symptom**: `ImportError: attempted relative import beyond top-level package`
   - **Solution**: ALWAYS run tests from backend directory: `cd backend && python -m pytest tests/`
   - **Details**: See `backend/tests/TESTING_TROUBLESHOOTING.md`

5. **Test Data Not Appearing**
   - **Symptom**: Created objects don't appear in listings, `assert our_project is not None` fails
   - **Solution**: Check if test is using `isolated_client` instead of `client`
   - **Common Fix**: Replace `client` parameter with `isolated_client` in test methods

**QUICK FIX CHECKLIST:**
- [ ] Test class inherits from `TestDatabaseIsolation`?
- [ ] Using `isolated_client` fixture instead of `client`?
- [ ] Running tests from backend directory?
- [ ] Mocks return correct data structure?
- [ ] Check `backend/tests/TESTING_TROUBLESHOOTING.md` for specific error patterns

**For detailed troubleshooting, see:**
- `backend/tests/README.md` - Comprehensive testing guide
- `backend/tests/TESTING_TROUBLESHOOTING.md` - Specific error patterns and solutions

## 10. Task Completion Protocol

**CRITICAL: When completing any task, you MUST update both tracking systems:**

1. **TodoWrite Tool:** Mark internal todo as "completed"
2. **Task File:** Update the task status in `.ai/tasks/current.yaml` from "pending" to "completed"

**Example workflow:**

```
1. Start task → Update TodoWrite (status: "in_progress")
2. Work on task → Keep TodoWrite updated
3. Finish task → Update TodoWrite (status: "completed") AND update .ai/tasks/current.yaml (status: "completed")
```

**Never forget step 3** - both systems must be updated or the task is not truly complete.

## 11. Documentation Maintenance

**CRITICAL: Keep Documentation Current**

- **Testing Guides**: When adding new testing patterns, fixtures, or techniques, immediately update the appropriate testing README:

  - **Backend (`backend/tests/README.md`)**: Database isolation techniques, fixture patterns, API testing, performance testing
  - **Frontend (`frontend/tests/README.md`)**: Component testing patterns, hook testing, mocking strategies, user interaction testing
  - Include new fixture patterns and their usage
  - Document new testing utilities or helpers
  - Update best practices or troubleshooting steps
  - Provide examples of the new patterns in action

- **Architecture Changes**: Update `docs/architecture.md` when making significant structural changes
- **API Changes**: Update API documentation when modifying endpoints or data models
- **Decision Records**: Create ADRs in `docs/decisions/` for significant technical decisions

**The testing READMEs are living documents** - they should be the single source of truth for how to write, run, and maintain tests in both the backend and frontend codebases. Keeping them current ensures consistent testing practices across the team and reduces onboarding time for new contributors.

- **Backend testing**: Database isolation, API integration, performance, and security testing
- **Frontend testing**: Component behavior, user interactions, hooks, and mocking strategies

## 12. AI Assistant Instructions

For AI assistants working on this project:

- **Detailed Instructions:** See `.ai/ai-instructions.md` for comprehensive guidance tailored to the developer's experience level and learning goals
- **Quick Reference:** See `.ai/ai-quick-reference.md` for a condensed reference guide
- **Note:** This project is built with assistance from AI coding agents (Claude, GPT-4, Gemini, etc.) - the instructions apply to all AI assistants
