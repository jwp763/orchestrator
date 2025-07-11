# API Documentation

*Last Updated: 2025-01-11*

## Overview

The Orchestrator API is a RESTful service built with FastAPI that provides comprehensive project and task management capabilities with AI-powered planning features.

## Base URL

```
Development: http://localhost:8000
Production: https://api.orchestrator.example.com
```

## Authentication

Currently, the API operates without authentication for development purposes. Future versions will implement:
- JWT-based authentication
- API key authentication for service-to-service communication
- OAuth2 for third-party integrations

## API Conventions

### Request Format
- **Content-Type**: `application/json`
- **Accept**: `application/json`
- **Encoding**: UTF-8

### Response Format
All responses follow a consistent structure:

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "metadata": {
    "timestamp": "2025-01-11T12:00:00Z",
    "version": "1.0.0"
  }
}
```

Error responses:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": { ... }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request format |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 500 | Internal Server Error | Server error |

### Pagination

List endpoints support pagination:

```
GET /api/projects?page=1&per_page=20
```

Response includes pagination metadata:
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

### Filtering and Sorting

```
GET /api/tasks?status=active&priority=high&sort=created_at:desc
```

## API Endpoints

### Projects
- [Project Endpoints](endpoints/projects.md) - CRUD operations for projects
- [Project Soft Delete](endpoints/projects-delete.md) - Soft delete and restore

### Tasks
- [Task Endpoints](endpoints/tasks.md) - CRUD operations for tasks
- [Task Hierarchies](endpoints/tasks-hierarchy.md) - Subtask management
- [Task Filtering](endpoints/tasks-filtering.md) - Advanced filtering

### AI Planning
- [Planner Endpoints](endpoints/planner.md) - AI-powered project planning
- [Agent Configuration](endpoints/agents.md) - AI agent settings

### System
- [Health Check](endpoints/health.md) - System status
- [Version Info](endpoints/version.md) - API version information

## Quick Reference

See [API Quick Reference](quick-ref.md) for a complete table of all endpoints.

## Examples

See [API Examples](examples.md) for practical usage examples and common workflows.

## Rate Limiting

The API implements rate limiting to ensure fair usage:

- **Default**: 100 requests per minute per IP
- **Authenticated**: 1000 requests per minute per user
- **Bulk Operations**: 10 requests per minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1641900000
```

## Versioning

The API uses URL versioning:
```
/api/v1/projects  (current)
/api/v2/projects  (future)
```

## Error Handling

See [Error Codes Reference](../reference/error-codes.md) for a complete list of error codes and their meanings.

## SDK and Client Libraries

### Official SDKs
- Python SDK (planned)
- JavaScript/TypeScript SDK (planned)

### Community SDKs
- None yet - contributions welcome!

## OpenAPI Specification

The complete OpenAPI specification is available at:
- Development: http://localhost:8000/openapi.json
- Interactive Docs: http://localhost:8000/docs

## Webhooks (Future)

Planned webhook support for:
- Project status changes
- Task completion
- AI planning completion

## Related Documentation

- [Development Setup](../development/setup.md)
- [Testing Guide](../testing/overview.md)
- [Architecture Overview](../architecture/overview.md)