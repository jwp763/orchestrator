# Error Codes Reference

*Last Updated: 2025-01-11*

## Overview

This document provides a comprehensive reference for all error codes used in the Databricks Orchestrator API. Each error includes a unique code, HTTP status, description, and example scenarios.

## Error Response Format

All API errors follow this consistent format:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context",
      "suggestion": "How to fix"
    },
    "request_id": "uuid-for-tracking"
  },
  "metadata": {
    "timestamp": "2025-01-11T12:00:00Z",
    "version": "1.0.0"
  }
}
```

## Error Categories

### 1. Validation Errors (400)

#### VALIDATION_ERROR
**HTTP Status**: 400 Bad Request  
**Description**: Request data failed validation

```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid request parameters",
  "details": {
    "name": "Field required",
    "estimated_minutes": "Must be between 0 and 10080"
  }
}
```

**Common Causes**:
- Missing required fields
- Invalid data types
- Values outside allowed ranges
- Invalid enum values

#### INVALID_PATCH
**HTTP Status**: 400 Bad Request  
**Description**: Patch operation is invalid

```json
{
  "code": "INVALID_PATCH",
  "message": "Cannot update non-existent resource",
  "details": {
    "op": "update",
    "task_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### INVALID_HIERARCHY
**HTTP Status**: 400 Bad Request  
**Description**: Task hierarchy constraints violated

```json
{
  "code": "INVALID_HIERARCHY",
  "message": "Maximum task depth exceeded",
  "details": {
    "current_depth": 5,
    "max_depth": 5,
    "parent_id": "task-id"
  }
}
```

### 2. Authentication Errors (401)

#### UNAUTHORIZED
**HTTP Status**: 401 Unauthorized  
**Description**: Missing or invalid authentication

```json
{
  "code": "UNAUTHORIZED",
  "message": "Authentication required",
  "details": {
    "suggestion": "Include valid API key or JWT token"
  }
}
```

#### TOKEN_EXPIRED
**HTTP Status**: 401 Unauthorized  
**Description**: Authentication token has expired

```json
{
  "code": "TOKEN_EXPIRED",
  "message": "Authentication token expired",
  "details": {
    "expired_at": "2025-01-11T11:00:00Z",
    "suggestion": "Refresh your token"
  }
}
```

### 3. Authorization Errors (403)

#### FORBIDDEN
**HTTP Status**: 403 Forbidden  
**Description**: User lacks required permissions

```json
{
  "code": "FORBIDDEN",
  "message": "Insufficient permissions",
  "details": {
    "required_permission": "project.delete",
    "user_role": "viewer"
  }
}
```

#### RESOURCE_LOCKED
**HTTP Status**: 403 Forbidden  
**Description**: Resource is locked for editing

```json
{
  "code": "RESOURCE_LOCKED",
  "message": "Project is locked by another user",
  "details": {
    "locked_by": "user@example.com",
    "locked_until": "2025-01-11T12:30:00Z"
  }
}
```

### 4. Not Found Errors (404)

#### NOT_FOUND
**HTTP Status**: 404 Not Found  
**Description**: Requested resource doesn't exist

```json
{
  "code": "NOT_FOUND",
  "message": "Project not found",
  "details": {
    "resource_type": "project",
    "id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

#### DELETED_RESOURCE
**HTTP Status**: 404 Not Found  
**Description**: Resource has been soft deleted

```json
{
  "code": "DELETED_RESOURCE",
  "message": "Task has been deleted",
  "details": {
    "deleted_at": "2025-01-10T15:30:00Z",
    "suggestion": "Use restore endpoint to recover"
  }
}
```

### 5. Conflict Errors (409)

#### DUPLICATE_RESOURCE
**HTTP Status**: 409 Conflict  
**Description**: Resource already exists

```json
{
  "code": "DUPLICATE_RESOURCE",
  "message": "Project with this name already exists",
  "details": {
    "field": "name",
    "value": "Q1 Marketing Campaign",
    "existing_id": "project-id"
  }
}
```

#### CONCURRENT_UPDATE
**HTTP Status**: 409 Conflict  
**Description**: Resource modified by another request

```json
{
  "code": "CONCURRENT_UPDATE",
  "message": "Resource was modified by another request",
  "details": {
    "suggestion": "Retry with latest version"
  }
}
```

### 6. AI/Agent Errors (422)

#### AI_GENERATION_FAILED
**HTTP Status**: 422 Unprocessable Entity  
**Description**: AI failed to generate valid response

```json
{
  "code": "AI_GENERATION_FAILED",
  "message": "Could not generate project plan",
  "details": {
    "provider": "openai",
    "model": "gpt-4",
    "reason": "Invalid response format"
  }
}
```

#### INVALID_AI_REQUEST
**HTTP Status**: 422 Unprocessable Entity  
**Description**: AI request parameters invalid

```json
{
  "code": "INVALID_AI_REQUEST",
  "message": "Request too vague for planning",
  "details": {
    "suggestion": "Provide more specific project details",
    "min_length": 20
  }
}
```

### 7. Rate Limiting Errors (429)

#### RATE_LIMIT_EXCEEDED
**HTTP Status**: 429 Too Many Requests  
**Description**: API rate limit exceeded

```json
{
  "code": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded",
  "details": {
    "limit": 100,
    "window": "1 minute",
    "retry_after": 45
  }
}
```

#### AI_QUOTA_EXCEEDED
**HTTP Status**: 429 Too Many Requests  
**Description**: AI API quota exceeded

```json
{
  "code": "AI_QUOTA_EXCEEDED",
  "message": "AI generation quota exceeded",
  "details": {
    "quota": 1000,
    "used": 1000,
    "resets_at": "2025-01-12T00:00:00Z"
  }
}
```

### 8. Server Errors (500)

#### INTERNAL_ERROR
**HTTP Status**: 500 Internal Server Error  
**Description**: Unexpected server error

```json
{
  "code": "INTERNAL_ERROR",
  "message": "An unexpected error occurred",
  "details": {
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "suggestion": "Please try again or contact support"
  }
}
```

#### DATABASE_ERROR
**HTTP Status**: 500 Internal Server Error  
**Description**: Database operation failed

```json
{
  "code": "DATABASE_ERROR",
  "message": "Database operation failed",
  "details": {
    "operation": "insert",
    "suggestion": "Retry the request"
  }
}
```

### 9. Service Unavailable (503)

#### SERVICE_UNAVAILABLE
**HTTP Status**: 503 Service Unavailable  
**Description**: Service temporarily unavailable

```json
{
  "code": "SERVICE_UNAVAILABLE",
  "message": "Service undergoing maintenance",
  "details": {
    "retry_after": 300,
    "maintenance_until": "2025-01-11T13:00:00Z"
  }
}
```

#### AI_PROVIDER_UNAVAILABLE
**HTTP Status**: 503 Service Unavailable  
**Description**: AI provider is unavailable

```json
{
  "code": "AI_PROVIDER_UNAVAILABLE",
  "message": "AI provider is currently unavailable",
  "details": {
    "provider": "openai",
    "fallback_available": true,
    "suggestion": "Request will use fallback provider"
  }
}
```

## Error Handling Best Practices

### Client-Side Handling

```typescript
try {
  const response = await api.createProject(data);
  return response;
} catch (error) {
  if (error.code === 'VALIDATION_ERROR') {
    // Show field-specific errors
    showValidationErrors(error.details);
  } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
    // Implement exponential backoff
    await delay(error.details.retry_after * 1000);
    return retry();
  } else if (error.code === 'UNAUTHORIZED') {
    // Redirect to login
    redirectToLogin();
  } else {
    // Generic error handling
    showErrorMessage(error.message);
  }
}
```

### Retry Logic

```python
def retry_with_backoff(func, max_retries=3):
    retryable_codes = [
        'INTERNAL_ERROR',
        'DATABASE_ERROR',
        'SERVICE_UNAVAILABLE',
        'AI_PROVIDER_UNAVAILABLE'
    ]
    
    for attempt in range(max_retries):
        try:
            return func()
        except APIError as e:
            if e.code not in retryable_codes:
                raise
            
            if attempt == max_retries - 1:
                raise
            
            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
```

## Webhook Error Events

When using webhooks, errors are communicated via webhook events:

```json
{
  "event_type": "task.create.failed",
  "timestamp": "2025-01-11T12:00:00Z",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid task data",
    "details": {
      "field": "project_id",
      "message": "Project not found"
    }
  },
  "context": {
    "webhook_id": "webhook-id",
    "attempt": 1
  }
}
```

## Monitoring & Alerting

### Error Metrics

Track these key metrics:

1. **Error Rate by Code**
   - `VALIDATION_ERROR`: User input issues
   - `INTERNAL_ERROR`: System health
   - `DATABASE_ERROR`: Storage issues
   - `AI_GENERATION_FAILED`: AI reliability

2. **Response Time by Error**
   - Fast errors (< 100ms): Validation
   - Slow errors (> 1s): Database, AI

3. **Error Patterns**
   - Spike detection
   - Trend analysis
   - User impact assessment

### Alert Thresholds

```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    duration: 5 minutes
    severity: critical
    
  - name: database_errors
    condition: error_code == 'DATABASE_ERROR' && count > 10
    duration: 1 minute
    severity: high
    
  - name: ai_failures
    condition: error_code == 'AI_GENERATION_FAILED' && rate > 20%
    duration: 10 minutes
    severity: medium
```

## Related Documentation

- [API Reference](../api/README.md)
- [Testing Error Scenarios](../testing/error-testing.md)
- [Monitoring Guide](../monitoring/guide.md)