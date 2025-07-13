# API Endpoints Reference

This document is auto-generated from the codebase. Last updated: $(date)

## Table of Contents

- [Projects API](#projects-api)
- [Tasks API](#tasks-api)
- [Conversations API](#conversations-api)
- [Authentication](#authentication)
- [Health Check](#health-check)

---

## Authentication

Currently, the API does not require authentication for the MVP. Future versions will implement:

- JWT-based authentication
- API key management
- Role-based access control (RBAC)

## Health Check

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Returns service health status |

---

## Error Responses

All endpoints may return the following error responses:

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid input parameters |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

## Rate Limiting

Currently no rate limiting is implemented. Future versions will include:

- Per-IP rate limiting
- Per-user rate limiting
- Endpoint-specific limits

