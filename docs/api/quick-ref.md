# API Quick Reference

*Last Updated: 2025-01-11*

## All Endpoints at a Glance

### Project Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/projects` | List all projects | - | Project list with pagination |
| POST | `/api/projects` | Create new project | `ProjectCreateRequest` | Created project |
| GET | `/api/projects/{id}` | Get project details | - | Project with tasks |
| PUT | `/api/projects/{id}` | Update project | `ProjectUpdateRequest` | Updated project |
| DELETE | `/api/projects/{id}` | Soft delete project | - | 204 No Content |
| POST | `/api/projects/{id}/restore` | Restore deleted project | - | Restored project |
| GET | `/api/projects/trash` | List deleted projects | - | Deleted project list |

### Task Management

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/tasks` | List all tasks | - | Task list with pagination |
| POST | `/api/tasks` | Create new task | `TaskCreateRequest` | Created task |
| GET | `/api/tasks/{id}` | Get task details | - | Task with subtasks |
| PUT | `/api/tasks/{id}` | Update task | `TaskUpdateRequest` | Updated task |
| DELETE | `/api/tasks/{id}` | Soft delete task | - | 204 No Content |
| POST | `/api/tasks/{id}/restore` | Restore deleted task | - | Restored task |
| GET | `/api/tasks/trash` | List deleted tasks | - | Deleted task list |
| GET | `/api/projects/{id}/tasks` | Get project tasks | - | Task list for project |

### AI Planning

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| POST | `/api/planner/generate` | Generate project plan | `PlannerRequest` | AI-generated patches |
| GET | `/api/planner/providers` | List AI providers | - | Available providers |
| GET | `/api/planner/config` | Get default config | - | Planner configuration |
| POST | `/api/tasks/{id}/decompose` | Decompose task | `DecomposeRequest` | Subtask patches |
| POST | `/api/agent/edit` | Edit with AI | `EditRequest` | Edit patches |

### System

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/health` | Health check | - | System status |
| GET | `/api/version` | API version | - | Version info |
| GET | `/api/docs` | Interactive docs | - | Swagger UI |
| GET | `/openapi.json` | OpenAPI spec | - | API specification |

## Query Parameters

### Pagination
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 20, max: 100)

### Filtering
- `status`: Filter by status (active, completed, archived)
- `priority`: Filter by priority (low, medium, high, critical)
- `created_after`: Filter by creation date
- `created_before`: Filter by creation date
- `assignee`: Filter by assignee
- `tags`: Filter by tags (comma-separated)

### Sorting
- `sort`: Sort field and order (e.g., `created_at:desc`, `priority:asc`)

## Common Request Bodies

### ProjectCreateRequest
```json
{
  "name": "string",
  "description": "string",
  "status": "planning|active|on_hold|completed|archived",
  "priority": "low|medium|high|critical",
  "tags": ["string"],
  "created_by": "string"
}
```

### TaskCreateRequest
```json
{
  "project_id": "uuid",
  "title": "string",
  "description": "string",
  "status": "todo|in_progress|blocked|completed|cancelled",
  "priority": "low|medium|high|critical",
  "parent_id": "uuid (optional)",
  "assignee": "string (optional)",
  "due_date": "datetime (optional)",
  "tags": ["string"],
  "created_by": "string"
}
```

### PlannerRequest
```json
{
  "idea": "string",
  "config": {
    "provider": "openai|anthropic|gemini|xai",
    "model": "string",
    "create_milestones": true,
    "max_milestones": 5
  }
}
```

## Common Response Formats

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "metadata": {
    "timestamp": "2025-01-11T12:00:00Z"
  }
}
```

### Error Response
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable message",
    "details": { ... }
  }
}
```

### Paginated Response
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## HTTP Headers

### Request Headers
- `Content-Type: application/json`
- `Accept: application/json`
- `Authorization: Bearer {token}` (future)

### Response Headers
- `Content-Type: application/json`
- `X-Request-ID: uuid`
- `X-RateLimit-*: rate limit info`

## Status Enums

### Project Status
- `planning`
- `active`
- `on_hold`
- `completed`
- `archived`

### Task Status
- `todo`
- `in_progress`
- `blocked`
- `completed`
- `cancelled`

### Priority Levels
- `low`
- `medium`
- `high`
- `critical`