# System Architecture Overview

*Last Updated: 2025-01-11*

## Executive Summary

The Databricks Orchestrator is a modern, AI-powered project and task management system built with a microservices-inspired architecture. The system combines a FastAPI backend with a React frontend to provide intelligent project planning and orchestration capabilities.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          Client Applications                             │
│  ┌─────────────────┐  ┌──────────────────┐  ┌───────────────────────┐ │
│  │  Web Browser    │  │  Mobile Browser  │  │   API Consumers       │ │
│  │  (React SPA)    │  │  (Responsive)    │  │   (REST Clients)      │ │
│  └────────┬────────┘  └────────┬─────────┘  └──────────┬────────────┘ │
└───────────┼─────────────────────┼────────────────────────┼──────────────┘
            │                     │                         │
            └─────────────────────┴─────────────────────────┘
                                  │
                                  │ HTTPS
                                  │
┌─────────────────────────────────┴─────────────────────────────────────┐
│                          API Gateway Layer                             │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                    FastAPI Application                            │ │
│  │  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐ │ │
│  │  │   CORS      │  │   Auth       │  │   Rate Limiting        │ │ │
│  │  │ Middleware  │  │ Middleware   │  │   Middleware           │ │ │
│  │  └─────────────┘  └──────────────┘  └────────────────────────┘ │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴─────────────────────────────────────┐
│                          Business Logic Layer                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌───────────────────┐  │
│  │  Project Routes  │  │   Task Routes    │  │   Agent Routes    │  │
│  │  /api/projects   │  │   /api/tasks     │  │   /api/planner    │  │
│  └────────┬─────────┘  └────────┬─────────┘  └─────────┬─────────┘  │
│           │                      │                       │            │
│  ┌────────┴──────────────────────┴───────────────────────┴────────┐  │
│  │                    Orchestration Service Layer                  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐ │  │
│  │  │  Project    │  │    Task     │  │      Agent             │ │  │
│  │  │  Service    │  │   Service   │  │     Service            │ │  │
│  │  └─────────────┘  └─────────────┘  └────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴─────────────────────────────────────┐
│                           Data Access Layer                            │
│  ┌──────────────────────────────────────────────────────────────────┐ │
│  │                     Storage Interface (Abstract)                  │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │ │
│  │  │   CRUD      │  │   Patch     │  │    Transaction         │  │ │
│  │  │ Operations  │  │ Operations  │  │    Management          │  │ │
│  │  └─────────────┘  └─────────────┘  └────────────────────────┘  │ │
│  └──────────────────────────┬───────────────────────────────────────┘ │
│                             │                                          │
│  ┌──────────────────────────┴───────────────────────────────────────┐ │
│  │                    SQL Implementation (SQLAlchemy)                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌────────────────────────┐  │ │
│  │  │  Project    │  │    Task     │  │     Session            │  │ │
│  │  │   Models    │  │   Models    │  │    Management          │  │ │
│  │  └─────────────┘  └─────────────┘  └────────────────────────┘  │ │
│  └──────────────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────────────┘
                                  │
┌─────────────────────────────────┴─────────────────────────────────────┐
│                         External Services                              │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  ┌───────────┐ │
│  │   Database   │  │  AI Providers│  │ Integration │  │   Cache   │ │
│  │   (SQLite/   │  │  (OpenAI,    │  │  Platforms  │  │  (Redis)  │ │
│  │  PostgreSQL) │  │  Anthropic)  │  │  (Motion)   │  │  (Future) │ │
│  └──────────────┘  └──────────────┘  └─────────────┘  └───────────┘ │
└────────────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend (React)

```
frontend/src/
├── components/          # React components
│   ├── ProjectSidebar/  # Project navigation
│   ├── TaskCard/        # Task display
│   ├── ProjectDetails/  # Project info
│   └── NaturalLanguageEditor/  # AI interface
├── hooks/              # Custom React hooks
│   ├── useProjectManagement.ts
│   └── useLocalStorage.ts
├── services/           # API client layer
│   ├── projectService.ts
│   └── taskService.ts
└── types/              # TypeScript definitions
```

### Backend (FastAPI)

```
backend/src/
├── api/                # REST endpoints
│   ├── project_routes.py
│   ├── task_routes.py
│   └── planner_routes.py
├── orchestration/      # Business logic
│   ├── project_service.py
│   ├── task_service.py
│   └── agent_service.py
├── storage/            # Data persistence
│   ├── interface.py    # Abstract interface
│   └── sql_implementation.py
├── agent/              # AI agents
│   ├── planner_agent.py
│   ├── decomposer_agent.py
│   └── editor_agent.py
└── models/             # Data models
    ├── project.py
    ├── task.py
    └── schemas.py
```

## Data Flow

### Request Lifecycle

1. **Client Request** → React component initiates API call
2. **API Gateway** → FastAPI validates request, applies middleware
3. **Route Handler** → Endpoint processes request parameters
4. **Service Layer** → Business logic orchestrates operations
5. **Storage Layer** → Database operations via SQLAlchemy
6. **Response** → JSON response returned to client

### AI Agent Integration

```
User Input → NaturalLanguageEditor → API → AgentService
                                              ↓
Response ← API ← PatchApplication ← PlannerAgent
```

## Key Design Patterns

### 1. Repository Pattern
- Abstract storage interface allows swapping implementations
- Currently supports SQL via SQLAlchemy
- Future support for NoSQL, cloud storage

### 2. Service Layer Pattern
- Business logic separated from API routes
- Services coordinate between storage and agents
- Transaction management at service level

### 3. Dependency Injection
- FastAPI's dependency system for request-scoped resources
- Testable components with mock injection
- Database session management

### 4. Event-Driven Updates
- Frontend uses optimistic updates
- Real-time sync with backend state
- Error rollback mechanisms

## Scalability Considerations

### Horizontal Scaling
- Stateless API design enables load balancing
- Database connection pooling
- Session management via external store (future)

### Vertical Scaling
- Async request handling in FastAPI
- Lazy loading in React components
- Query optimization with proper indexes

### Performance Optimizations
- Response caching strategies
- Pagination for large datasets
- Batch operations for bulk updates

## Security Architecture

### API Security
- CORS configuration for frontend origin
- Rate limiting per endpoint
- Input validation via Pydantic

### Data Security
- SQL injection prevention via SQLAlchemy
- XSS protection in React
- Secure credential storage

### Future Enhancements
- JWT authentication
- Role-based access control
- API key management

## Technology Stack

### Backend
- **Language**: Python 3.8+
- **Framework**: FastAPI
- **ORM**: SQLAlchemy
- **Database**: SQLite (dev), PostgreSQL (prod)
- **Testing**: pytest

### Frontend
- **Language**: TypeScript
- **Framework**: React 18
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **Testing**: Vitest + React Testing Library

### Infrastructure
- **Service Coordination**: npm-run-all
- **Environment Management**: Layered configuration files
- **CI/CD**: GitHub Actions
- **Monitoring**: OpenTelemetry (future)

## Deployment Architecture

### Development
- Multi-environment isolation (dev/staging/prod)
- Local SQLite databases per environment
- Hot reload for both frontend and backend
- Mock external services
- Automated setup and validation scripts

### Production
- PostgreSQL database recommended
- npm script coordination
- Environment-specific configurations
- Health monitoring and backup systems

## Integration Points

### Current Integrations
- Multiple AI providers (OpenAI, Anthropic, Gemini, xAI)
- Extensible agent system

### Planned Integrations
- Motion task management
- Linear issue tracking
- Notion documentation
- GitLab project management

## Monitoring & Observability

### Current
- Application logs
- Error tracking
- Basic performance metrics

### Planned
- Distributed tracing
- Custom metrics
- Real-time dashboards
- Alerting system

## Related Documentation

- [Testing Documentation](../testing.md)
- [API Documentation](../api/README.md)
- [Data Models](../reference/data-models.md)
- [Development Setup](../deployment/setup-guide.md)
- [Quick Start Guide](../deployment/quick-start.md)
- [Deployment Guide](../deployment/guide.md)