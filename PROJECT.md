# AI-Assisted Project Plan & Context

## Table of Contents

- [Current Sprint Focus](#current-sprint-focus)
- [1. Project Goal](#1-project-goal)
- [2. Tech Stack](#2-tech-stack)
- [3. Project Structure](#3-project-structure)
- [4. Development Standards](#4-development-standards)
- [5. Workflow Commands](#5-workflow-commands)
- [6. Current Tasks](#6-current-tasks)
- [7. Architecture & Design](#7-architecture--design)
- [8. Agent-Hints & Constraints](#8-agent-hints--constraints)
- [9. Critical Test Troubleshooting](#9-critical-test-troubleshooting)
- [10. Task Completion Protocol](#10-task-completion-protocol)
- [11. Documentation Maintenance](#11-documentation-maintenance)
- [12. AI Assistant Instructions](#12-ai-assistant-instructions)

---

## Current Sprint Focus

### 🎯 Active Development Tasks

**Priority:** Backend-Frontend Integration & Testing

1. **TEST-API-002** - Test Suite: Orchestration Service Layer (Pending - High Priority)
   - Unit tests for ProjectService, TaskService, and AgentService
   - Integration tests with real storage and agents
   - Transaction handling across multiple operations

2. **TEST-UI-007** - Test Suite: Frontend-Backend Integration (Pending - High Priority)
   - Frontend API service tests with mocked responses
   - Hook tests with proper service mocking
   - E2E tests for complete user workflows


### 📊 Recent Achievements (July 2025)

- ✅ **Testing Infrastructure**: 672 total tests (Backend: 516, Frontend: 156)
- ✅ **Backend**: 99.4% test success rate (3 acceptable failures)
- ✅ **Frontend**: 100% test success rate (fixed all 16 critical failures)
- ✅ **Documentation**: Comprehensive testing architecture and troubleshooting guides
- ✅ **Multi-Environment Setup**: Complete dev/staging/prod isolation with automated scripts
- ✅ **Soft Delete Implementation**: Complete cascading soft delete with 14 comprehensive tests passing
- ✅ **Deployment Documentation**: Complete deployment guide overhaul with npm script workflow

### 📋 Task Summary

- **Completed**: 11 tasks (MVP-001, MVP-002, MVP-003a/b, UI-001, UI-002, API-001, API-002, TEST-API-001, FIX-001, UI-007, DEL-001, DEL-002, DEL-008)
- **In Progress**: 0 tasks
- **Pending**: 14 tasks (prioritized by dependencies and business value)

---

## 1. Project Goal

This project, the Orchestrator, is a personal project and task management system that uses AI agents to intelligently orchestrate work across multiple platforms. The MVP focuses on a conversational interface for project and task management, where the AI agent assists the user in breaking down goals into actionable tasks.

## 2. Tech Stack

- **Language:** Python 3.8+ (Backend), TypeScript (Frontend)
- **Backend:** FastAPI, SQLAlchemy, Pydantic
- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite
- **Database:** SQLite with multi-environment support
  - Development: `orchestrator_dev.db`
  - Staging: `orchestrator_staging.db`
  - Production: `orchestrator_prod.db`
- **Testing:** pytest (Backend), Vitest + React Testing Library (Frontend)
- **AI Integration:** Multi-provider support (OpenAI, Anthropic, Gemini, XAI)
- **Version Control:** Git with GitHub

## 3. Project Structure

```
databricks_orchestrator/
├── backend/           # FastAPI backend application
│   ├── src/          # Core application code
│   │   ├── agent/    # AI agents (Planner, Decomposer, Editor)
│   │   ├── api/      # REST API endpoints
│   │   ├── config/   # Settings and configuration
│   │   ├── models/   # Pydantic data models
│   │   ├── orchestration/  # Service layer
│   │   └── storage/  # Database abstraction
│   └── tests/        # Comprehensive test suite
├── frontend/         # React frontend application
│   ├── src/         # React components and hooks
│   └── tests/       # Frontend test suite
├── scripts/         # Environment and utility scripts
│   ├── start-dev.sh     # Start development environment
│   ├── start-staging.sh # Start staging environment
│   ├── start-prod.sh    # Start production environment
│   ├── backup-prod.sh   # Backup production database
│   ├── copy-prod-to-staging.sh  # Copy prod to staging
│   └── reset-dev.sh     # Reset development database
├── docs/            # Project documentation
├── notebooks/       # Databricks notebooks
├── .ai/            # AI tool configurations
├── .env.dev        # Development environment config
├── .env.staging    # Staging environment config
├── .env.prod       # Production environment config
└── package.json    # Root-level npm scripts
```

## 4. Development Standards

### Code Style

- **Python**: PEP 8 with Black formatting, type hints for all functions
- **TypeScript**: ESLint + Prettier, strict type checking
- **Documentation**: Clear docstrings for public methods, inline comments for complex logic

### Testing Requirements

- **Coverage**: Minimum 80% code coverage
- **Patterns**: Follow established patterns in `backend/tests/README.md` and `frontend/tests/README.md`
- **Isolation**: Use `TestDatabaseIsolation` for backend integration tests
- **Frontend**: React Testing Library with user-centric testing approach

## 5. Workflow Commands

### Environment Management

```bash
# Start environments (from project root)
npm run start:dev                      # Development environment
npm run start:staging                  # Staging environment
npm run start:prod                     # Production environment

# Direct script usage
./scripts/start-dev.sh                 # Development on ports 8000/5174
./scripts/start-staging.sh             # Staging on ports 8001/5175
./scripts/start-prod.sh                # Production on ports 8002/5176

# Database management
npm run db:backup                      # Backup production database
npm run db:copy-prod-to-staging        # Copy prod data to staging
npm run db:reset-dev                   # Reset development database
```

### Backend Development

```bash
# Testing (ALWAYS run from backend directory)
cd backend && pytest                    # Run all tests
cd backend && pytest -v                 # Verbose output
cd backend && pytest --cov=src         # With coverage
cd backend && pytest tests/test_api/   # Specific directory

# Code Quality
black .                                # Format code
mypy .                                 # Type checking
```

### Frontend Development

```bash
# Development
npm run dev                           # Start dev server (port 5174)
npm run dev:staging                   # Dev server on staging port (5175)
npm run dev:prod                      # Dev server on prod port (5176)
npm run build                         # Production build

# Testing
npm test                              # Run tests
npm run test:watch                    # Watch mode
npm run test:coverage                 # With coverage
npm run test:ui                       # Vitest UI
```

### Quick Commands (from root)

```bash
# Full stack operations
npm run test:all                      # Run all tests (backend + frontend)
npm run lint:all                      # Lint all code
npm run install:all                   # Install all dependencies
```

### Documentation References

- **Testing Overview**: `docs/testing.md`
- **Backend Testing**: `docs/testing/backend-guide.md`
- **Frontend Testing**: `docs/testing/frontend-guide.md`
- **Troubleshooting**: `docs/testing/troubleshooting.md`
- **Development Setup**: `docs/development/setup.md`

## 6. Current Tasks

- **Active Sprint**: See [Current Sprint Focus](#current-sprint-focus)
- **Full Task List**: `.ai/tasks/current.yaml` (with automatic datetime tracking using system time)
- **Task Template**: `.ai/templates/task-template.yaml` (ALWAYS use `date -Iseconds` for timestamps, includes test requirements)
- **MVP Overview**: `docs/planning/mvp-overview.md`

## 7. Architecture & Design

- **Architecture Overview**: `docs/architecture/overview.md`
- **Architecture Decision Records**: `docs/decisions/`
- **MVP Planning**: `docs/planning/`

## 8. Agent-Hints & Constraints

- **Production Safety**: Do not modify production configurations or secrets
- **Idempotency**: Ensure all data operations are idempotent where possible
- **Transactions**: Use proper transaction boundaries for multi-system operations
- **Test Execution**: Always run tests from backend directory: `cd backend && pytest`
- **Session Management**: SQLStorage uses flush() for transactions, commit() for standalone
- **Date/Time**: CRITICAL - AI assistants' internal date perception is often WRONG. ALWAYS use `date -Iseconds` command to get system datetime for task timestamps
- **Multi-Environment**: Separate databases and ports for dev/staging/prod isolation
- **Environment Variables**: Use .env.dev, .env.staging, or .env.prod for configuration

<details>
<summary><strong>9. Critical Test Troubleshooting</strong> (Click to expand)</summary>

### Common Test Issues and Solutions

#### 1. Database Isolation Problems
- **Symptom**: "Session is already flushing", "database is locked", "session closed"
- **Solution**: Ensure test classes inherit from `TestDatabaseIsolation` and use `isolated_client`
- **Example**: `class TestMyFeature(TestDatabaseIsolation): def test_something(self, isolated_client):`

#### 2. Mock Object Errors
- **Symptom**: "'Mock' object is not subscriptable" or has no attribute
- **Solution**: Check mock return value matches expected data structure
- **Example**: `mock_storage.list_tasks.return_value = {"tasks": [...], "total": 1, "page": 1}`

#### 3. Foreign Key Constraint Errors
- **Symptom**: 500 errors when deleting projects with tasks
- **Solution**: Implement cascade delete in storage layer
- **Location**: `src/storage/sql_implementation.py` delete_project method

#### 4. Import Path Issues
- **Symptom**: `ImportError: attempted relative import beyond top-level package`
- **Solution**: ALWAYS run tests from backend directory: `cd backend && python -m pytest tests/`

#### 5. Test Data Not Appearing
- **Symptom**: Created objects don't appear in listings
- **Solution**: Check if test is using `isolated_client` instead of `client`

### Quick Fix Checklist
- [ ] Test class inherits from `TestDatabaseIsolation`?
- [ ] Using `isolated_client` fixture instead of `client`?
- [ ] Running tests from backend directory?
- [ ] Mocks return correct data structure?
- [ ] Check `docs/testing/troubleshooting.md` for specific patterns

**Detailed Guides**:
- Backend: `docs/testing/backend-guide.md`
- Frontend: `docs/testing/frontend-guide.md`
- Troubleshooting: `docs/testing/troubleshooting.md`

</details>

## 10. Task Completion Protocol

**CRITICAL: Update both tracking systems when completing tasks:**

1. **TodoWrite Tool**: Mark internal todo as "completed"
2. **Task File**: Update status in `.ai/tasks/current.yaml` from "pending" to "completed"

```
1. Start task → Update TodoWrite (status: "in_progress")
                AND set start_date in current.yaml using `date -Iseconds` command
2. Work on task → Keep TodoWrite updated
                  AND implement all test requirements from task specification
3. Finish task → Update TodoWrite (status: "completed")
                 AND update .ai/tasks/current.yaml (status: "completed")
                 AND set completion_date using `date -Iseconds` command
                 AND verify all tests are passing (unit, integration, performance, security)
```

## 11. Documentation Maintenance

**Keep Documentation Current:**

- **Testing Guides**: Update when adding new patterns or fixtures
  - Backend: `docs/testing/backend-guide.md`
  - Frontend: `docs/testing/frontend-guide.md`
- **Architecture**: Update `docs/architecture/overview.md` for structural changes
- **API Changes**: Update documentation when modifying endpoints
- **Decision Records**: Create ADRs in `docs/decisions/` for significant decisions

## 12. AI Assistant Instructions

For AI assistants working on this project:

- **Detailed Instructions**: See `.ai/ai-instructions.md`
- **Quick Reference**: See `.ai/ai-quick-reference.md`
- **Note**: This project is built with AI coding assistants (Claude, Codex, Gemini, etc.)
