# Data Models Reference

*Last Updated: 2025-01-11*

## Overview

This document provides a comprehensive reference for all data models used in the Databricks Orchestrator system. Models are implemented using Pydantic for validation and SQLAlchemy for persistence.

## Core Models

### Project

**Location**: `src/models/project.py`

```python
class Project(BaseModel):
    id: UUID
    name: str                          # Project title (required)
    description: Optional[str]         # Detailed description
    status: ProjectStatus              # Current status
    priority: Priority                 # Priority level
    tags: List[str] = []              # Flexible categorization
    metadata: Dict[str, Any] = {}     # Custom fields
    integration_ids: Dict[str, str] = {} # External system IDs
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]    # Soft delete
    created_by: str                   # User identifier
    
    # Relationships
    tasks: List[Task] = []           # Root-level tasks
```

**Status Values**:
- `planning` - Initial planning phase
- `active` - In progress
- `on_hold` - Temporarily paused
- `completed` - Successfully finished
- `archived` - Long-term storage

**Priority Values**:
- `low` - Can be deferred
- `medium` - Normal priority
- `high` - Needs attention
- `critical` - Urgent/blocking

### Task

**Location**: `src/models/task.py`

```python
class Task(BaseModel):
    id: UUID
    project_id: UUID                   # Parent project
    parent_id: Optional[UUID]          # Parent task (hierarchical)
    
    # Core fields
    title: str                         # Task title (required)
    description: Optional[str]         # Detailed description
    status: TaskStatus                 # Current status
    priority: Priority                 # Priority level
    
    # Assignment & scheduling
    assignee: Optional[str]            # Assigned user
    due_date: Optional[datetime]       # Due date
    
    # Time tracking (in minutes)
    estimated_minutes: Optional[int]   # Estimated effort
    actual_minutes: Optional[int]      # Actual effort spent
    
    # Metadata
    tags: List[str] = []              # Flexible categorization
    metadata: Dict[str, Any] = {}     # Custom fields
    integration_ids: Dict[str, str] = {} # External system IDs
    dependencies: List[UUID] = []      # Task dependencies
    
    # Hierarchy
    depth: int = 0                    # Nesting level (0-5)
    subtasks: List[Task] = []        # Child tasks
    
    # Audit fields
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]    # Soft delete
    created_by: str                   # User identifier
    
    # Computed properties
    @property
    def estimated_hours(self) -> Optional[float]:
        return self.estimated_minutes / 60 if self.estimated_minutes else None
```

**Status Values**:
- `todo` - Not started
- `in_progress` - Being worked on
- `blocked` - Waiting on dependency
- `completed` - Finished
- `cancelled` - Won't be done

**Depth Constraints**:
- Maximum depth: 5 levels
- Root tasks: depth = 0
- Each subtask: parent.depth + 1

## Patch Models

### PatchSet

**Location**: `src/models/patch.py`

```python
class PatchSet(BaseModel):
    """Container for multiple patch operations"""
    project_patches: List[ProjectPatch] = []
    task_patches: List[TaskPatch] = []
    
    def is_empty(self) -> bool:
        return not (self.project_patches or self.task_patches)
```

### ProjectPatch

```python
class ProjectPatch(BaseModel):
    op: Op                            # Operation type
    project_id: Optional[UUID]        # Target project (update/delete)
    body: Optional[ProjectUpdate]     # Update payload
    
    @validator('body')
    def validate_body(cls, v, values):
        if values.get('op') in [Op.CREATE, Op.UPDATE] and not v:
            raise ValueError(f"body required for {values.get('op')}")
        return v
```

### TaskPatch

```python
class TaskPatch(BaseModel):
    op: Op                           # Operation type
    task_id: Optional[UUID]          # Target task (update/delete)
    parent_id: Optional[UUID]        # Parent for new tasks
    body: Optional[TaskUpdate]       # Update payload
```

### Operation Types

```python
class Op(str, Enum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
```

## Agent Models

### AgentRequest

**Location**: `src/models/agent.py`

```python
class AgentRequest(BaseModel):
    """Request to an AI agent"""
    message: str                     # User message
    context: Dict[str, Any]          # Conversation context
    mode: AgentMode                  # Agent operation mode
    provider: Optional[str]          # AI provider override
    model: Optional[str]             # Model override
    temperature: float = 0.7         # Creativity level
    max_tokens: Optional[int]        # Response limit
```

### AgentResponse

```python
class AgentResponse(BaseModel):
    """Response from an AI agent"""
    message: str                     # AI response text
    patches: Optional[PatchSet]      # Proposed changes
    confidence: float                # Confidence score (0-1)
    tokens_used: int                # Token consumption
    model_used: str                 # Actual model used
    provider_used: str              # Actual provider used
```

### AgentMode

```python
class AgentMode(str, Enum):
    PROJECT_PLANNING = "project_planning"
    TASK_DECOMPOSITION = "task_decomposition"
    NATURAL_EDIT = "natural_edit"
    CONVERSATION = "conversation"
```

## Integration Models

### IntegrationConfig

**Location**: `src/models/integration.py`

```python
class IntegrationConfig(BaseModel):
    """Configuration for external integrations"""
    provider: IntegrationProvider
    api_key: Optional[str]           # API key (encrypted)
    workspace_id: Optional[str]      # Workspace/org ID
    settings: Dict[str, Any] = {}    # Provider-specific settings
    
    # Sync settings
    sync_enabled: bool = False
    sync_direction: SyncDirection = SyncDirection.BIDIRECTIONAL
    sync_frequency: int = 3600       # Seconds between syncs
    
    # Field mappings
    field_mappings: Dict[str, str] = {}  # Internal -> External
```

### IntegrationProvider

```python
class IntegrationProvider(str, Enum):
    MOTION = "motion"
    LINEAR = "linear"
    GITLAB = "gitlab"
    NOTION = "notion"
    JIRA = "jira"
    ASANA = "asana"
```

## User Models

### User

**Location**: `src/models/user.py`

```python
class User(BaseModel):
    id: UUID
    email: str
    name: str
    role: UserRole
    
    # Preferences
    preferences: Dict[str, Any] = {}
    default_ai_provider: Optional[str]
    default_ai_model: Optional[str]
    
    # Integration accounts
    integration_accounts: Dict[str, IntegrationAccount] = {}
    
    # Audit
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool = True
```

### UserRole

```python
class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
```

## Request/Response Models

### ProjectCreate

```python
class ProjectCreate(BaseModel):
    name: str
    description: Optional[str]
    status: ProjectStatus = ProjectStatus.PLANNING
    priority: Priority = Priority.MEDIUM
    tags: List[str] = []
    created_by: str
```

### TaskCreate

```python
class TaskCreate(BaseModel):
    project_id: UUID
    parent_id: Optional[UUID]
    title: str
    description: Optional[str]
    status: TaskStatus = TaskStatus.TODO
    priority: Priority = Priority.MEDIUM
    assignee: Optional[str]
    due_date: Optional[datetime]
    estimated_minutes: Optional[int]
    tags: List[str] = []
    created_by: str
```

### ListResponse

```python
class ListResponse(BaseModel, Generic[T]):
    """Generic paginated response"""
    items: List[T]
    total: int
    page: int
    per_page: int
    has_next: bool
    has_prev: bool
```

## SQL Models

### SQLAlchemy Table Definitions

**Location**: `src/storage/sql_models.py`

```python
class ProjectTable(Base):
    __tablename__ = "projects"
    
    id = Column(UUID, primary_key=True, default=uuid4)
    name = Column(String, nullable=False, index=True)
    description = Column(Text)
    status = Column(Enum(ProjectStatus), nullable=False)
    priority = Column(Enum(Priority), nullable=False)
    tags = Column(JSON, default=list)
    metadata = Column(JSON, default=dict)
    integration_ids = Column(JSON, default=dict)
    
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True, index=True)
    created_by = Column(String, nullable=False)
    
    # Relationships
    tasks = relationship("TaskTable", back_populates="project")
```

## Validation Rules

### Field Constraints

1. **String Fields**:
   - `name`/`title`: 1-255 characters
   - `description`: 0-5000 characters
   - `tags`: Max 20 tags, each 1-50 characters

2. **Time Constraints**:
   - `estimated_minutes`: 0-10080 (1 week)
   - `actual_minutes`: 0-10080
   - `due_date`: Must be future date

3. **Hierarchy Constraints**:
   - `depth`: 0-5 levels
   - Circular dependencies prevented
   - Parent must exist

### Business Rules

1. **Status Transitions**:
   ```python
   VALID_TRANSITIONS = {
       TaskStatus.TODO: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
       TaskStatus.IN_PROGRESS: [TaskStatus.BLOCKED, TaskStatus.COMPLETED],
       TaskStatus.BLOCKED: [TaskStatus.IN_PROGRESS, TaskStatus.CANCELLED],
       TaskStatus.COMPLETED: [],  # Terminal state
       TaskStatus.CANCELLED: []   # Terminal state
   }
   ```

2. **Cascade Rules**:
   - Delete project → Soft delete all tasks
   - Delete parent task → Soft delete subtasks
   - Complete parent → Warning if subtasks incomplete

## Performance Indexes

### Database Indexes

```sql
-- Frequently queried fields
CREATE INDEX idx_projects_status ON projects(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_tasks_project_id ON tasks(project_id) WHERE deleted_at IS NULL;
CREATE INDEX idx_tasks_parent_id ON tasks(parent_id);
CREATE INDEX idx_tasks_assignee ON tasks(assignee);

-- Composite indexes for common queries
CREATE INDEX idx_tasks_project_status ON tasks(project_id, status);
CREATE INDEX idx_tasks_assignee_status ON tasks(assignee, status);
```

## Migration Considerations

### Adding Fields

1. Always provide defaults for new fields
2. Use nullable for optional fields
3. Run migrations in transaction
4. Update validation schemas

### Schema Evolution

```python
# Example migration
def upgrade():
    op.add_column('tasks',
        sa.Column('priority', 
                  sa.Enum(Priority),
                  nullable=False,
                  server_default='medium')
    )
```

## Related Documentation

- [API Reference](../api/README.md)
- [Storage Architecture](../architecture/storage.md)
- [Database Schema](../database/schema.sql)