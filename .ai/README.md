# AI Assistant Documentation

This directory contains configuration and context for AI assistants working with the Databricks Orchestrator project.

## Quick Links to AI-Specific Documentation

### Primary Resources

1. **[CLAUDE.md](../CLAUDE.md)** - Main AI assistant instructions and project context
   - Project overview and goals
   - Development standards
   - Workflow commands
   - Current tasks and priorities
   - Critical troubleshooting guide

2. **[PROJECT.md](../PROJECT.md)** - Current sprint focus and technical details
   - Active development tasks
   - Test troubleshooting guide
   - Architecture patterns
   - Known issues and solutions

### Testing Documentation

3. **[Backend Testing Guide](../backend/tests/README.md)** - Comprehensive backend testing patterns
   - Database isolation techniques
   - Mock configuration
   - Common error patterns
   - Testing best practices

4. **[Frontend Testing Guide](../frontend/tests/README.md)** - Frontend testing patterns
   - React Testing Library usage
   - Component testing strategies
   - Hook testing patterns
   - Mocking strategies

5. **[Testing Troubleshooting](../TESTING_TROUBLESHOOTING.md)** - Quick fixes for common test issues
   - Session management errors
   - Mock configuration problems
   - Import path issues
   - Database isolation failures

### Architecture & Planning

6. **[MVP Overview](../docs/planning/mvp-overview.md)** - Project vision and core concepts
   - User experience flow
   - Architectural principles
   - Technology stack

7. **[Implementation Status](../docs/planning/implementation-status.md)** - Current progress
   - Component completion status
   - Test coverage metrics
   - Next steps

8. **[System Architecture](../docs/architecture/overview.md)** - Technical architecture
   - Component structure
   - Data flow
   - Design patterns

### Reference Documentation

9. **[Data Models](../docs/reference/data-models.md)** - Complete data model reference
   - Core models (Project, Task)
   - Patch models
   - Validation rules

10. **[API Reference](../docs/api/README.md)** - API documentation
    - Endpoint reference
    - Request/response formats
    - Error codes

11. **[Commands Reference](../docs/reference/commands.md)** - Development commands
    - Testing commands
    - Build commands
    - Deployment commands

## AI Development Workflow

### 1. Starting a Task
```bash
# Always start from the project root
cd /Users/johnpope/databricks_orchestrator

# Check current branch
git status

# Read relevant documentation
cat CLAUDE.md  # For project context
cat PROJECT.md # For current sprint
```

### 2. Running Tests
```bash
# CRITICAL: Always run tests from the correct directory
cd backend && pytest  # Backend tests
cd frontend && npm test  # Frontend tests
```

### 3. Common Issues

#### Backend Test Failures
- Check `backend/tests/README.md` for database isolation patterns
- Review `TESTING_TROUBLESHOOTING.md` for specific error fixes
- Always use `isolated_client` fixture for API tests

#### Frontend Test Failures
- Check `frontend/tests/README.md` for mocking patterns
- Ensure test matches current component implementation
- Update tests when changing UI components

### 4. Documentation Updates
When adding new patterns or fixing issues:
1. Update the relevant testing README
2. Add troubleshooting steps to TESTING_TROUBLESHOOTING.md
3. Update CLAUDE.md if it's a recurring issue

## Task Management

### Current Tasks Location
- **Structured Tasks**: `.ai/tasks/current.yaml`
- **MVP Plan**: `docs/planning/mvp-overview.md`
- **Sprint Focus**: See `PROJECT.md` header

### Task Completion Protocol
1. Mark todo as completed in TodoWrite tool
2. Update task status in `.ai/tasks/current.yaml`
3. Update relevant documentation if needed

## Key Principles for AI Assistants

1. **Test-First Development**: Always run tests before and after changes
2. **Documentation Currency**: Keep testing guides updated with new patterns
3. **Error Pattern Recognition**: Document recurring issues in troubleshooting guides
4. **Minimal File Creation**: Prefer editing existing files over creating new ones
5. **Context Awareness**: Read CLAUDE.md and PROJECT.md before starting work

## Recent Achievements

- Test reliability improved from 478 to 499 passing tests (backend)
- Frontend tests achieving 100% success rate
- Comprehensive testing documentation established
- Professional-grade architecture patterns implemented

## Support

For questions or issues:
- Create an issue at: https://github.com/anthropics/claude-code/issues
- Check existing documentation first
- Update docs when finding solutions to new problems