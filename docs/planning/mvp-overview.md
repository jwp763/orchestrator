# MVP Overview

*Last Updated: 2025-01-11*

## Project Vision

The Databricks Orchestrator is an intelligent project management tool that uses conversational AI to help users define, structure, and refine projects and their associated tasks. The system follows a "diff-first" approach where all changes are explicit, reviewable, and auditable.

## Core User Experience

### 1. Project Scaffolding
Users initiate new projects with high-level goals (e.g., "Build a new user authentication flow"). The AI agent proposes an initial breakdown into manageable high-level tasks, presented as a diff.

### 2. Iterative Refinement
Users converse with the agent to refine plans ("Combine the first two tasks," "Add a task for documentation"). Each instruction results in a new diff applied to the proposal.

### 3. Approval & Task Decomposition
Once satisfied, users accept the high-level structure. They can select individual tasks and break them down into smaller sub-tasks through focused conversations. This process is recursive.

### 4. Visualization
The GUI provides clear, text-based, hierarchical visualization of projects, allowing users to expand and collapse sections to see the current state.

## Key Architectural Principles

### Diff-First Interaction
- AI agent **never** outputs full project/task objects after initial creation
- **Always** outputs `Patch` objects describing `create`, `update`, or `delete` operations
- First plan is simply a `Patch` against an empty project
- Simplifies validation, makes changes explicit, provides natural audit trail

### Separation of Concerns
Two distinct AI agent modes:

**Project Mode**
- Initial project scaffolding
- High-level planning focus
- Breaking large visions into coherent top-level tasks
- 1-2 week milestone horizon
- Reasoning about dependencies and structure

**Task Mode**
- Decomposing existing tasks into sub-tasks
- Granular detail focus
- Technical sequencing
- Clear acceptance criteria
- Project context as constraint, but focused on single task

### Storage Abstraction
- Application logic decoupled from physical storage
- All database operations through defined interface (repository pattern)
- Allows swapping SQL for Delta Lake or other backends
- Future-proof architecture

## Core Concepts

### Project
- Top-level container for work
- Has title, summary, and collection of root-level tasks
- Status tracking (planning, active, completed, etc.)
- Priority levels and tagging support

### Task
- Unit of work within a project
- Can be nested to create hierarchy (sub-tasks)
- Attributes: title, description, status, sub-tasks
- Time tracking and dependency management
- Integration references for external systems

### Patch
- Pydantic object representing changes
- Contains operation (`create`, `update`, `delete`)
- Target ID and body of changes
- Atomic, auditable units of change

## Technology Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (dev), PostgreSQL (prod ready)
- **AI Providers**: OpenAI, Anthropic, Gemini, xAI

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: React hooks + Context

### Infrastructure
- **Testing**: pytest (backend), Vitest (frontend)
- **Type Checking**: mypy (Python), TypeScript
- **Code Quality**: Black, Ruff, ESLint
- **Documentation**: Markdown with architectural diagrams

## Success Metrics

1. **Usability**: Users can go from idea to structured project in < 5 minutes
2. **Reliability**: 99%+ test coverage on critical paths
3. **Performance**: < 2 second response time for AI operations
4. **Flexibility**: Easy to add new AI providers or storage backends
5. **Maintainability**: Clear architecture allowing team scaling

## Future Vision

While the MVP focuses on core project/task management with AI assistance, the architecture supports:
- Real-time collaboration
- Advanced workflow automation
- Multi-platform integrations
- Enterprise security features
- Analytics and reporting
- Mobile applications

## Related Documentation

- [Implementation Status](implementation-status.md)
- [Phase 1: Core Schemas](phase-1-schemas.md)
- [Phase 2: AI Agents](phase-2-agents.md)
- [Phase 3: API Layer](phase-3-api.md)
- [Phase 4: Frontend](phase-4-frontend.md)
- [Future Phases](future-phases.md)