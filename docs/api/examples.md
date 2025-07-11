# API Usage Examples

*Last Updated: 2025-01-11*

## Common Workflows

### 1. Creating a Project with AI Planning

```bash
# Step 1: Generate project plan with AI
curl -X POST "http://localhost:8000/api/planner/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Build a mobile app for habit tracking with social features",
    "config": {
      "provider": "openai",
      "create_milestones": true,
      "max_milestones": 5
    }
  }'

# Response includes project and task patches
{
  "success": true,
  "data": {
    "project_patches": [{
      "op": "add",
      "path": "/projects/-",
      "value": {
        "name": "Habit Tracker Mobile App",
        "description": "A mobile application for tracking daily habits...",
        "status": "planning",
        "priority": "high"
      }
    }],
    "task_patches": [
      {
        "op": "add",
        "path": "/tasks/-",
        "value": {
          "title": "Design UI/UX mockups",
          "description": "Create wireframes and design mockups...",
          "estimated_hours": 20
        }
      }
    ]
  }
}
```

### 2. Complete Project CRUD Lifecycle

```bash
# Create a project
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Q1 Marketing Campaign",
    "description": "Social media marketing campaign for Q1 2025",
    "status": "planning",
    "priority": "high",
    "tags": ["marketing", "q1-2025"],
    "created_by": "john.doe"
  }'

# Response
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Q1 Marketing Campaign",
  "status": "planning",
  "created_at": "2025-01-11T10:00:00Z"
}

# Update the project
curl -X PUT "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "active",
    "description": "Updated: Social media and influencer marketing for Q1"
  }'

# Get project with tasks
curl -X GET "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000"

# Delete (soft delete) the project
curl -X DELETE "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000"
```

### 3. Task Management with Hierarchies

```bash
# Create a parent task
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Develop Backend API",
    "description": "Build RESTful API with FastAPI",
    "status": "todo",
    "priority": "high",
    "estimated_hours": 40,
    "created_by": "john.doe"
  }'

# Response with task ID
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "title": "Develop Backend API",
  "status": "todo"
}

# Create subtasks
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "parent_id": "660e8400-e29b-41d4-a716-446655440001",
    "title": "Design database schema",
    "status": "todo",
    "priority": "high",
    "estimated_hours": 8,
    "created_by": "john.doe"
  }'

# Get task with subtasks
curl -X GET "http://localhost:8000/api/tasks/660e8400-e29b-41d4-a716-446655440001"
```

### 4. Advanced Task Filtering

```bash
# Filter tasks by multiple criteria
curl -X GET "http://localhost:8000/api/tasks?project_id=550e8400-e29b-41d4-a716-446655440000&status=todo&priority=high&assignee=john.doe&sort=created_at:desc"

# Filter by date range
curl -X GET "http://localhost:8000/api/tasks?created_after=2025-01-01T00:00:00Z&created_before=2025-01-31T23:59:59Z"

# Filter by tags
curl -X GET "http://localhost:8000/api/tasks?tags=backend,api,urgent"

# Paginated results
curl -X GET "http://localhost:8000/api/tasks?page=2&per_page=50"
```

### 5. Batch Operations

```bash
# Update multiple tasks
curl -X PATCH "http://localhost:8000/api/tasks/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [
      "660e8400-e29b-41d4-a716-446655440001",
      "660e8400-e29b-41d4-a716-446655440002"
    ],
    "updates": {
      "status": "in_progress",
      "assignee": "jane.doe"
    }
  }'
```

### 6. AI-Powered Task Decomposition

```bash
# Decompose a complex task into subtasks
curl -X POST "http://localhost:8000/api/tasks/660e8400-e29b-41d4-a716-446655440001/decompose" \
  -H "Content-Type: application/json" \
  -d '{
    "num_subtasks": 5,
    "preserve_estimate": true
  }'

# Response with subtask patches
{
  "success": true,
  "data": {
    "patches": [
      {
        "op": "add",
        "path": "/tasks/-",
        "value": {
          "parent_id": "660e8400-e29b-41d4-a716-446655440001",
          "title": "Set up database models",
          "estimated_hours": 8
        }
      }
    ]
  }
}
```

### 7. Natural Language Editing

```bash
# Edit project/tasks using natural language
curl -X POST "http://localhost:8000/api/agent/edit" \
  -H "Content-Type: application/json" \
  -d '{
    "context": {
      "project_id": "550e8400-e29b-41d4-a716-446655440000",
      "task_id": "660e8400-e29b-41d4-a716-446655440001"
    },
    "instruction": "Change the priority to critical and add a due date of next Friday"
  }'
```

### 8. Soft Delete and Restore

```bash
# Soft delete a project (cascades to tasks)
curl -X DELETE "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000"

# View deleted projects
curl -X GET "http://localhost:8000/api/projects/trash"

# Restore a deleted project (restores tasks too)
curl -X POST "http://localhost:8000/api/projects/550e8400-e29b-41d4-a716-446655440000/restore"
```

## Python Client Examples

```python
import requests
import json

class OrchestratorClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json"
        })
    
    def create_project(self, name, description, **kwargs):
        """Create a new project"""
        data = {
            "name": name,
            "description": description,
            "created_by": "api-client",
            **kwargs
        }
        response = self.session.post(
            f"{self.base_url}/api/projects",
            json=data
        )
        response.raise_for_status()
        return response.json()
    
    def list_tasks(self, project_id=None, status=None, **params):
        """List tasks with optional filtering"""
        if project_id:
            params['project_id'] = project_id
        if status:
            params['status'] = status
            
        response = self.session.get(
            f"{self.base_url}/api/tasks",
            params=params
        )
        response.raise_for_status()
        return response.json()
    
    def generate_plan(self, idea, provider="openai"):
        """Generate project plan with AI"""
        data = {
            "idea": idea,
            "config": {
                "provider": provider,
                "create_milestones": True
            }
        }
        response = self.session.post(
            f"{self.base_url}/api/planner/generate",
            json=data
        )
        response.raise_for_status()
        return response.json()

# Usage
client = OrchestratorClient()

# Create a project
project = client.create_project(
    name="New Feature Development",
    description="Implement user authentication",
    priority="high",
    tags=["backend", "security"]
)

# List tasks for the project
tasks = client.list_tasks(
    project_id=project['id'],
    status="todo"
)

# Generate AI plan
plan = client.generate_plan(
    "Build a real-time chat feature with WebSocket support"
)
```

## JavaScript/TypeScript Examples

```typescript
// api-client.ts
interface ProjectCreateRequest {
  name: string;
  description: string;
  status?: 'planning' | 'active' | 'completed';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  tags?: string[];
  created_by: string;
}

class OrchestratorAPI {
  private baseURL: string;

  constructor(baseURL = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async createProject(data: ProjectCreateRequest): Promise<Project> {
    const response = await fetch(`${this.baseURL}/api/projects`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async getTasks(params?: URLSearchParams): Promise<TaskListResponse> {
    const url = new URL(`${this.baseURL}/api/tasks`);
    if (params) {
      url.search = params.toString();
    }

    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }

  async updateTask(taskId: string, updates: Partial<Task>): Promise<Task> {
    const response = await fetch(`${this.baseURL}/api/tasks/${taskId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }

    return response.json();
  }
}

// Usage
const api = new OrchestratorAPI();

// Create project
const project = await api.createProject({
  name: 'Mobile App Development',
  description: 'React Native app for iOS and Android',
  status: 'planning',
  priority: 'high',
  tags: ['mobile', 'react-native'],
  created_by: 'john.doe'
});

// Get filtered tasks
const params = new URLSearchParams({
  project_id: project.id,
  status: 'todo',
  sort: 'priority:desc'
});
const tasks = await api.getTasks(params);

// Update task status
const updatedTask = await api.updateTask(tasks.data[0].id, {
  status: 'in_progress',
  assignee: 'jane.doe'
});
```

## Error Handling Examples

```bash
# Handling validation errors
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Missing required name field"
  }'

# Error response
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "name": "Field required"
    }
  }
}

# Handling not found errors
curl -X GET "http://localhost:8000/api/projects/invalid-uuid"

# Error response
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Project not found",
    "details": {
      "id": "invalid-uuid"
    }
  }
}
```

## Testing API Endpoints

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Interactive API documentation
open "http://localhost:8000/docs"

# Download OpenAPI specification
curl -X GET "http://localhost:8000/openapi.json" > openapi.json
```