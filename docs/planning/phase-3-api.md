# Phase 3: API Layer & Backend Routes

*Last Updated: 2025-01-11*

**Status**: 🚧 Not Started  
**Estimated Time**: 5-6 hours  
**Priority**: High - Required for MVP

## Goal

Build a RESTful API using FastAPI that exposes the storage and agent capabilities to the frontend, enabling the full conversational project management experience.

## Planned Architecture

### API Structure
```
backend/src/
├── main.py                 # FastAPI application entry
├── api/
│   ├── __init__.py
│   ├── project_routes.py   # Project CRUD endpoints
│   ├── task_routes.py      # Task CRUD endpoints
│   ├── planner_routes.py   # AI planning endpoints
│   ├── agent_routes.py     # Conversational AI endpoints
│   └── middleware.py       # CORS, auth, logging
├── orchestration/
│   ├── project_service.py  # Project business logic
│   ├── task_service.py     # Task business logic
│   └── agent_service.py    # Agent orchestration
└── schemas/
    ├── requests.py         # API request models
    └── responses.py        # API response models
```

## Task Breakdown

### Task 3.1: FastAPI Application Setup

**File**: `src/main.py`

**Implementation**:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api import project_routes, task_routes, planner_routes

app = FastAPI(
    title="Databricks Orchestrator API",
    version="1.0.0",
    description="AI-powered project management"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Route registration
app.include_router(project_routes.router, prefix="/api/projects")
app.include_router(task_routes.router, prefix="/api/tasks")
app.include_router(planner_routes.router, prefix="/api/planner")

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
```

### Task 3.2: Project Management Endpoints

**File**: `src/api/project_routes.py`

**Endpoints**:
```python
# GET /api/projects
# List all projects with pagination and filtering
@router.get("/", response_model=ProjectListResponse)
async def list_projects(
    page: int = 1,
    per_page: int = 20,
    status: Optional[ProjectStatus] = None,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# POST /api/projects
# Create a new project
@router.post("/", response_model=Project)
async def create_project(
    project: ProjectCreate,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# GET /api/projects/{project_id}
# Get project details with tasks
@router.get("/{project_id}", response_model=ProjectDetail)
async def get_project(
    project_id: str,
    include_tasks: bool = True,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# PUT /api/projects/{project_id}
# Update project
@router.put("/{project_id}", response_model=Project)
async def update_project(
    project_id: str,
    updates: ProjectUpdate,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# DELETE /api/projects/{project_id}
# Soft delete project
@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    cascade: bool = True,
    storage: StorageInterface = Depends(get_storage)
):
    pass
```

### Task 3.3: Task Management Endpoints

**File**: `src/api/task_routes.py`

**Endpoints**:
```python
# GET /api/tasks
# List tasks with filtering
@router.get("/", response_model=TaskListResponse)
async def list_tasks(
    project_id: Optional[str] = None,
    parent_id: Optional[str] = None,
    status: Optional[TaskStatus] = None,
    assignee: Optional[str] = None,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# POST /api/tasks
# Create a new task
@router.post("/", response_model=Task)
async def create_task(
    task: TaskCreate,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# GET /api/tasks/{task_id}
# Get task with subtasks
@router.get("/{task_id}", response_model=TaskDetail)
async def get_task(
    task_id: str,
    include_subtasks: bool = True,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# PUT /api/tasks/{task_id}
# Update task
@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: str,
    updates: TaskUpdate,
    storage: StorageInterface = Depends(get_storage)
):
    pass

# POST /api/tasks/{task_id}/decompose
# AI-powered task decomposition
@router.post("/{task_id}/decompose", response_model=PatchSet)
async def decompose_task(
    task_id: str,
    request: DecomposeRequest,
    storage: StorageInterface = Depends(get_storage),
    agent: DecomposerAgent = Depends(get_decomposer_agent)
):
    pass
```

### Task 3.4: AI Planning Endpoints

**File**: `src/api/planner_routes.py`

**Endpoints**:
```python
# POST /api/planner/generate
# Generate project plan from idea
@router.post("/generate", response_model=PlannerResponse)
async def generate_plan(
    request: PlannerRequest,
    agent: PlannerAgent = Depends(get_planner_agent)
):
    """
    Generate a complete project plan from a natural language description.
    Returns patches to create the project and initial tasks.
    """
    pass

# POST /api/planner/refine
# Refine existing plan
@router.post("/refine", response_model=PatchSet)
async def refine_plan(
    request: RefineRequest,
    storage: StorageInterface = Depends(get_storage),
    agent: EditorAgent = Depends(get_editor_agent)
):
    """
    Refine an existing project plan based on user feedback.
    Returns patches to modify the project structure.
    """
    pass

# POST /api/planner/apply
# Apply patches to project
@router.post("/apply", response_model=ApplyResponse)
async def apply_patches(
    patch_set: PatchSet,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Apply a set of patches to modify project/task structure.
    Used after user approves AI-generated changes.
    """
    pass
```

### Task 3.5: Conversational Agent Endpoints

**File**: `src/api/agent_routes.py`

**Endpoints**:
```python
# POST /api/agent/chat
# Main conversational interface
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    storage: StorageInterface = Depends(get_storage),
    agent: OrchestratorAgent = Depends(get_orchestrator_agent)
):
    """
    Process natural language requests and return appropriate patches.
    Maintains conversation context and routes to appropriate sub-agents.
    """
    pass

# GET /api/agent/capabilities
# List agent capabilities
@router.get("/capabilities", response_model=CapabilitiesResponse)
async def get_capabilities():
    """
    Return list of available agent actions and tools.
    Helps frontend provide better UX guidance.
    """
    pass

# POST /api/agent/validate
# Validate patches before applying
@router.post("/validate", response_model=ValidationResponse)
async def validate_patches(
    patch_set: PatchSet,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Pre-validate patches to catch errors before applying.
    Returns detailed validation results.
    """
    pass
```

### Task 3.6: Service Layer Implementation

**File**: `src/orchestration/project_service.py`

**Key Methods**:
```python
class ProjectService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage
    
    async def create_with_tasks(
        self, 
        project: ProjectCreate,
        tasks: List[TaskCreate]
    ) -> ProjectDetail:
        """Create project and initial tasks atomically"""
        
    async def get_project_hierarchy(
        self, 
        project_id: str
    ) -> ProjectHierarchy:
        """Get complete project with task tree"""
        
    async def apply_ai_patches(
        self,
        patch_set: PatchSet
    ) -> PatchResult:
        """Apply AI-generated patches with validation"""
```

## API Design Principles

### 1. RESTful Conventions
- Proper HTTP methods (GET, POST, PUT, DELETE)
- Meaningful status codes
- Resource-based URLs
- Stateless operations

### 2. Consistent Response Format
```python
class APIResponse(BaseModel):
    success: bool
    data: Optional[Any]
    error: Optional[ErrorDetail]
    metadata: ResponseMetadata
```

### 3. Error Handling
```python
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(exc),
                "details": exc.errors()
            }
        }
    )
```

### 4. Authentication (Future)
```python
# Prepared for JWT authentication
async def get_current_user(
    token: str = Depends(oauth2_scheme)
) -> User:
    # Decode and validate JWT
    pass
```

## Dependencies Management

### Dependency Injection
```python
# Storage dependency
async def get_storage() -> StorageInterface:
    return SQLStorage(settings.database_url)

# Agent dependencies
async def get_planner_agent() -> PlannerAgent:
    return PlannerAgent(
        provider=settings.ai_provider,
        api_key=settings.ai_api_key
    )
```

### Request Context
```python
# Request ID tracking
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response
```

## Testing Strategy

### Unit Tests
- Test each endpoint in isolation
- Mock storage and agent dependencies
- Validate request/response schemas

### Integration Tests
- Test complete workflows
- Use test database
- Verify transaction handling

### Load Tests
- Concurrent request handling
- Database connection pooling
- Response time benchmarks

## Performance Considerations

### 1. Async Operations
- All endpoints async for better concurrency
- Non-blocking database operations
- Parallel agent calls where possible

### 2. Caching
```python
from fastapi_cache import FastAPICache
from fastapi_cache.decorator import cache

@router.get("/projects/{project_id}")
@cache(expire=60)  # Cache for 1 minute
async def get_project(project_id: str):
    pass
```

### 3. Pagination
- Default page size: 20
- Maximum page size: 100
- Cursor-based for large datasets

## Security Considerations

### 1. Input Validation
- Pydantic models for all inputs
- SQL injection prevention via ORM
- XSS prevention in responses

### 2. Rate Limiting
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/planner/generate")
@limiter.limit("10/minute")
async def generate_plan():
    pass
```

### 3. CORS Configuration
- Restrict origins in production
- Validate preflight requests
- Secure cookie handling

## Documentation

### OpenAPI/Swagger
- Auto-generated from FastAPI
- Available at `/docs`
- Includes request/response examples

### API Versioning
- URL-based versioning (`/api/v1/`)
- Backward compatibility
- Deprecation notices

## Deployment Preparation

### Environment Variables
```bash
DATABASE_URL=sqlite:///./orchestrator.db
AI_PROVIDER=openai
AI_API_KEY=sk-...
CORS_ORIGINS=http://localhost:3000
LOG_LEVEL=INFO
```

### Docker Support
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0"]
```

## Next Phase

With the API layer complete, Phase 4 focuses on building the frontend interface that consumes these endpoints.

## Related Documentation

- [Phase 4: Frontend](phase-4-frontend.md)
- [API Reference](../api/README.md)
- [OpenAPI Specification](../api/openapi.json)