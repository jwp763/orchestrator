# Data Models Reference

This document is auto-generated from the Pydantic models. Last updated: $(date)

## Table of Contents

- [Project Models](#project-models)
- [Task Models](#task-models)
- [Conversation Models](#conversation-models)
- [Agent Models](#agent-models)

---

## Project Models

### ProjectBase

Base model for project data with core fields and validation.

Provides the foundation for project management including status tracking,
priority management, scheduling, and integration with external systems.
Supports tagging and metadata for flexible organization.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | `str` | No | - |
| description | `Optional[str]` | No | - |
| status | `ProjectStatus` | No | - |
| priority | `ProjectPriority` | No | - |
| tags | `List[str]` | No | - |
| due_date | `Optional[date]` | No | - |
| start_date | `Optional[date]` | No | - |
| motion_project_id | `Optional[str]` | No | - |
| linear_project_id | `Optional[str]` | No | - |
| notion_page_id | `Optional[str]` | No | - |
| gitlab_project_id | `Optional[str]` | No | - |

### ProjectCreate

Model for creating new projects.

Inherits all fields from ProjectBase without requiring ID or timestamps,
which are generated automatically by the storage layer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|

### ProjectUpdate

Model for updating existing projects.

All fields are optional to allow partial updates. Maintains the same
validation rules as ProjectBase for fields that are provided.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | `Optional[str]` | No | - |
| description | `Optional[str]` | No | - |
| status | `Optional[ProjectStatus]` | No | - |
| priority | `Optional[ProjectPriority]` | No | - |
| tags | `Optional[List[str]]` | No | - |
| due_date | `Optional[date]` | No | - |
| start_date | `Optional[date]` | No | - |
| motion_project_id | `Optional[str]` | No | - |
| linear_project_id | `Optional[str]` | No | - |
| notion_page_id | `Optional[str]` | No | - |
| gitlab_project_id | `Optional[str]` | No | - |

### Project

Complete project model with database fields and metadata.

Extends ProjectBase with database-specific fields like ID, timestamps,
and creator information. Used for project instances retrieved from
or stored in the database.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | `str` | No | - |
| created_at | `datetime` | No | - |
| updated_at | `datetime` | No | - |
| created_by | `str` | No | - |
| tasks | `List['Task']` | No | - |

## Task Models

### TaskBase

Base model for task data with hierarchical support.

Provides the core fields and validation for task management including
hierarchical parent-child relationships, time tracking, dependencies,
and integration with external task management systems.

Features:
- Hierarchical task structure with parent-child relationships
- Time estimation and tracking in minutes
- Dependency management for task ordering
- Integration IDs for external systems (Motion, Linear, GitLab, Notion)
- Flexible metadata and labeling system

Validation:
- Estimated/actual minutes must be positive/non-negative
- Task depth limited to 5 levels maximum
- Dependencies must be valid task ID strings

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | `str` | No | - |
| description | `Optional[str]` | No | - |
| project_id | `str` | No | - |
| status | `TaskStatus` | No | - |
| priority | `TaskPriority` | No | - |
| parent_id | `Optional[str]` | No | - |
| estimated_minutes | `Optional[int]` | No | - |
| actual_minutes | `Optional[int]` | No | - |
| depth | `int` | No | - |
| dependencies | `List[str]` | No | - |
| due_date | `Optional[date]` | No | - |
| assignee | `Optional[str]` | No | - |
| tags | `List[str]` | No | - |
| labels | `List[str]` | No | - |
| motion_task_id | `Optional[str]` | No | - |
| linear_issue_id | `Optional[str]` | No | - |
| notion_task_id | `Optional[str]` | No | - |
| gitlab_issue_id | `Optional[str]` | No | - |
| metadata | `Dict[str, Any]` | No | - |

### TaskCreate

Model for creating new tasks.

Inherits all fields from TaskBase without requiring ID or timestamps,
which are generated automatically by the storage layer.

| Field | Type | Required | Description |
|-------|------|----------|-------------|

### TaskUpdate

Model for updating existing tasks.

All fields are optional to allow partial updates. Includes the same
validation as TaskBase for fields that are provided.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| title | `Optional[str]` | No | - |
| description | `Optional[str]` | No | - |
| project_id | `Optional[str]` | No | - |
| status | `Optional[TaskStatus]` | No | - |
| priority | `Optional[TaskPriority]` | No | - |
| parent_id | `Optional[str]` | No | - |
| estimated_minutes | `Optional[int]` | No | - |
| actual_minutes | `Optional[int]` | No | - |
| depth | `Optional[int]` | No | - |
| dependencies | `Optional[List[str]]` | No | - |
| due_date | `Optional[date]` | No | - |
| assignee | `Optional[str]` | No | - |
| tags | `Optional[List[str]]` | No | - |
| labels | `Optional[List[str]]` | No | - |
| motion_task_id | `Optional[str]` | No | - |
| linear_issue_id | `Optional[str]` | No | - |
| notion_task_id | `Optional[str]` | No | - |
| gitlab_issue_id | `Optional[str]` | No | - |
| metadata | `Optional[Dict[str, Any]]` | No | - |

### Task

Complete task model with database fields and validation methods.

Extends TaskBase with database-specific fields like ID, timestamps,
and computed fields. Includes methods for validating hierarchical
relationships and preventing circular dependencies.

Additional Fields:
- id: Unique identifier generated by storage layer
- created_at/updated_at: Automatic timestamp management
- completed_at: Set when task status changes to completed
- created_by: User who created the task
- is_overdue/days_until_due: Computed scheduling fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | `str` | No | - |
| created_at | `datetime` | No | - |
| updated_at | `datetime` | No | - |
| completed_at | `Optional[datetime]` | No | - |
| created_by | `str` | No | - |
| is_overdue | `bool` | No | - |
| days_until_due | `Optional[int]` | No | - |

