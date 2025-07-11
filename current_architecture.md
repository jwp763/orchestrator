# Current Project Architecture

## Overview

The **Databricks Orchestrator** is an AI-powered project planning and task management system with a modern full-stack architecture. It combines intelligent project breakdown capabilities with comprehensive CRUD operations for projects and tasks, featuring real-time frontend-backend integration.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend Layer                          │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │   React UI      │ │  TypeScript     │ │  Tailwind CSS   │  │
│  │   Components    │ │  Type Safety    │ │  Styling        │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/REST API
┌─────────────────────────────────────────────────────────────────┐
│                        Backend Layer                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │   FastAPI       │ │  Orchestration  │ │   AI Agents     │  │
│  │   REST API      │ │   Services      │ │   Integration   │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │ SQLAlchemy ORM
┌─────────────────────────────────────────────────────────────────┐
│                        Storage Layer                           │
│  ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐  │
│  │   SQLite        │ │   SQL Models    │ │   Databricks    │  │
│  │   Database      │ │   Schema        │ │   Integration   │  │
│  └─────────────────┘ └─────────────────┘ └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Backend Stack
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite with SQLAlchemy ORM 2.0+
- **AI Integration**: Multiple providers (OpenAI, Anthropic, Gemini, xAI)
- **Data Platform**: Databricks SDK integration
- **Validation**: Pydantic 2.0+ for data modeling
- **Development**: Poetry, Black, pytest, mypy

### Frontend Stack
- **Framework**: React 19+ with TypeScript
- **Build Tool**: Vite 7+
- **Styling**: Tailwind CSS 3.4+
- **Icons**: Lucide React
- **Testing**: Vitest, Testing Library
- **Development**: ESLint, Prettier

### Infrastructure
- **Development**: Local SQLite database
- **Deployment**: Databricks workspace integration
- **Version Control**: Git (GitLab)
- **Environment**: Linux-based development environment

## Backend Architecture

### Layer Structure

#### 1. API Layer (`backend/src/api/`)
- **`main.py`**: FastAPI application setup, CORS configuration, routing
- **`project_routes.py`**: Project CRUD endpoints (14KB, 393 lines)
- **`task_routes.py`**: Task CRUD endpoints (16KB, 438 lines) 
- **`planner_routes.py`**: AI planning endpoints (11KB, 318 lines)
- **`models.py`**: Pydantic API models and validation (16KB, 337 lines)

#### 2. Business Logic Layer (`backend/src/orchestration/`)
- **`project_service.py`**: Project business logic (12KB, 317 lines)
- **`task_service.py`**: Task business logic (18KB, 474 lines)
- **`agent_service.py`**: AI agent orchestration (19KB, 429 lines)

#### 3. Data Models Layer (`backend/src/models/`)
- **`project.py`**: Project domain models (4.5KB, 139 lines)
- **`task.py`**: Task domain models (13KB, 406 lines)
- **`agent.py`**: AI agent models (2.8KB, 62 lines)
- **`schemas.py`**: Shared data schemas (5.7KB, 178 lines)
- **`integration.py`**: External platform integrations

#### 4. Storage Layer (`backend/src/storage/`)
- SQLAlchemy ORM models
- Database session management
- Migration support

#### 5. AI Integration (`backend/src/agent/`)
- Multiple AI provider support
- Pluggable agent architecture
- Project planning capabilities

## Frontend Architecture

### Component Structure

#### 1. Core Application (`frontend/src/`)
- **`App.tsx`**: Main application component (4.9KB, 172 lines)
- **`AppRouter.tsx`**: Routing configuration (1.5KB, 57 lines)
- **`main.tsx`**: Application entry point

#### 2. UI Components (`frontend/src/components/`)
- **`ApiTest.tsx`**: API testing interface (5.3KB, 173 lines)
- **`ProjectDetails/`**: Project detail views
- **`TaskDetails/`**: Task detail views
- **`ProjectSidebar/`**: Navigation sidebar
- **`TaskCard/`**: Task display components
- **`NaturalLanguageEditor/`**: AI-powered editing interface

#### 3. Services Layer (`frontend/src/services/`)
- **`api.ts`**: Base API client (5.3KB, 207 lines)
- **`projectService.ts`**: Project API operations (4.8KB, 164 lines)
- **`taskService.ts`**: Task API operations (6.2KB, 216 lines)

#### 4. Type Definitions (`frontend/src/types/`)
- TypeScript interfaces matching backend models
- API response types
- Component prop types

#### 5. Custom Hooks (`frontend/src/hooks/`)
- React hooks for API integration
- State management
- Side effects handling

## Data Flow Architecture

### Request Flow
1. **Frontend**: User interaction triggers API call via service layer
2. **API Gateway**: FastAPI receives HTTP request, validates with Pydantic
3. **Service Layer**: Business logic processes request, coordinates operations
4. **Data Layer**: SQLAlchemy ORM handles database operations
5. **Response**: Data flows back through layers to frontend

### AI Planning Flow
1. **User Input**: Natural language project description
2. **AI Service**: Multiple provider support (OpenAI, Anthropic, etc.)
3. **Planning Logic**: Intelligent breakdown into tasks and milestones
4. **Persistence**: Results stored in database
5. **UI Update**: Frontend displays generated project structure

## Key Features & Capabilities

### Project Management
- Complete CRUD operations for projects and tasks
- Hierarchical task structure with subtasks
- Task dependencies and relationships
- Status tracking and progress monitoring

### AI Integration
- **Multiple Providers**: OpenAI, Anthropic, Gemini, xAI support
- **Intelligent Planning**: Automatic project breakdown
- **Natural Language**: Conversational interface for task creation
- **Configurable**: Provider-specific settings and parameters

### Platform Integrations
- **Databricks**: Workspace integration via SDK
- **External Platforms**: Motion, Linear, Notion, GitLab support
- **Real-time Sync**: Optimistic updates with error handling

### Development Features
- **Type Safety**: Full TypeScript coverage with Pydantic validation
- **API Documentation**: Automatic Swagger/OpenAPI documentation
- **Testing**: Comprehensive test suites for both frontend and backend
- **Code Quality**: Black, ESLint, Prettier, mypy integration

## Configuration & Deployment

### Environment Configuration
- **Backend**: `.env` file for API keys and database URL
- **Frontend**: Vite configuration for development and production builds
- **Databricks**: `databricks.yml` for workspace configuration

### Development Workflow
- **Backend**: FastAPI with auto-reload for development
- **Frontend**: Vite with hot module replacement
- **Database**: SQLite for local development
- **Testing**: pytest for backend, Vitest for frontend

## Security & Quality

### Code Quality
- **Python**: Black formatting, flake8 linting, mypy type checking
- **TypeScript**: ESLint, Prettier, strict TypeScript configuration
- **Testing**: 80%+ code coverage target with pytest and Vitest

### Security Considerations
- **API Keys**: Environment variable configuration
- **Validation**: Pydantic models for request/response validation
- **CORS**: Configured for development environment
- **Type Safety**: Full TypeScript and Python type coverage

## Current Status

### Implemented Features
- ✅ Full-stack application with React frontend and FastAPI backend
- ✅ Complete project and task CRUD operations
- ✅ AI-powered project planning with multiple provider support
- ✅ Real-time frontend-backend integration
- ✅ Comprehensive API documentation
- ✅ Type-safe development with TypeScript and Pydantic

### Architecture Maturity
- **MVP Complete**: Core functionality implemented and tested
- **Production Ready**: Clean architecture with proper separation of concerns
- **Scalable Design**: Modular structure supports future extensions
- **Well Documented**: Comprehensive README and API documentation

This architecture provides a solid foundation for an AI-powered project management system with room for future enhancements and platform integrations.