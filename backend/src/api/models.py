"""Pydantic models for API requests and responses."""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, computed_field

from ..models.patch import Patch
from ..models.project import Project, ProjectCreate, ProjectUpdate, ProjectPriority, ProjectStatus
from ..models.task import Task, TaskCreate, TaskUpdate, TaskPriority, TaskStatus


class PlannerConfig(BaseModel):
    """Configuration for the PlannerAgent."""
    
    provider: str = Field(default="openai", description="AI provider to use")
    model_name: Optional[str] = Field(default=None, description="Specific model name (uses provider default if None)")
    create_milestones: bool = Field(default=True, description="Whether to create milestone tasks")
    max_milestones: int = Field(default=5, ge=0, le=8, description="Maximum number of milestone tasks")
    max_retries: int = Field(default=2, ge=0, le=5, description="Maximum retry attempts")
    retry_delay: float = Field(default=1.0, ge=0.1, le=10.0, description="Delay between retries in seconds")
    
    @field_validator('provider')
    @classmethod
    def validate_provider(cls, v):
        """Validate provider is supported."""
        supported_providers = ['openai', 'anthropic', 'gemini', 'xai']
        if v not in supported_providers:
            raise ValueError(f"Provider must be one of {supported_providers}")
        return v


class PlannerRequest(BaseModel):
    """Request model for the planner endpoint."""
    
    idea: str = Field(..., min_length=10, max_length=5000, description="Project idea description")
    config: PlannerConfig = Field(default_factory=PlannerConfig, description="Agent configuration")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context for planning")
    
    @field_validator('idea')
    @classmethod
    def validate_idea(cls, v):
        """Validate project idea is meaningful."""
        if not v.strip():
            raise ValueError("Project idea cannot be empty")
        return v.strip()


class ProjectMetadata(BaseModel):
    """Project metadata from the generated patch."""
    
    name: str = Field(..., description="Generated project name")
    description: str = Field(..., description="Project description")
    status: ProjectStatus = Field(..., description="Project status")
    priority: ProjectPriority = Field(..., description="Project priority")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    estimated_total_minutes: Optional[int] = Field(default=None, description="Estimated total minutes")
    
    @computed_field
    @property
    def estimated_total_hours(self) -> Optional[float]:
        """Convert estimated total minutes to hours."""
        return self.estimated_total_minutes / 60.0 if self.estimated_total_minutes else None


class TaskMetadata(BaseModel):
    """Task metadata from the generated patch."""
    
    title: str = Field(..., description="Task title")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(..., description="Task status")
    priority: TaskPriority = Field(..., description="Task priority")
    estimated_minutes: Optional[int] = Field(default=None, description="Estimated minutes")
    
    @computed_field
    @property
    def estimated_hours(self) -> Optional[float]:
        """Convert estimated minutes to hours."""
        return self.estimated_minutes / 60.0 if self.estimated_minutes else None


class PlannerResponse(BaseModel):
    """Response model for the planner endpoint."""
    
    success: bool = Field(..., description="Whether the request was successful")
    project: Optional[ProjectMetadata] = Field(default=None, description="Generated project metadata")
    tasks: List[TaskMetadata] = Field(default_factory=list, description="Generated milestone tasks")
    raw_patch: Optional[Dict[str, Any]] = Field(default=None, description="Raw patch data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Response metadata")
    error: Optional[str] = Field(default=None, description="Error message if request failed")


class ProviderModel(BaseModel):
    """Model information for a provider."""
    
    name: str = Field(..., description="Model name")
    display_name: str = Field(..., description="Human-readable model name")
    description: Optional[str] = Field(default=None, description="Model description")
    is_default: bool = Field(default=False, description="Whether this is the default model")


class ProviderInfo(BaseModel):
    """Provider information."""
    
    name: str = Field(..., description="Provider name")
    display_name: str = Field(..., description="Human-readable provider name")
    models: List[ProviderModel] = Field(..., description="Available models")
    is_available: bool = Field(..., description="Whether provider is available (has API key)")
    is_default: bool = Field(default=False, description="Whether this is the default provider")


class ProvidersResponse(BaseModel):
    """Response model for the providers endpoint."""
    
    providers: List[ProviderInfo] = Field(..., description="Available providers")
    default_provider: str = Field(..., description="Default provider name")


class ConfigResponse(BaseModel):
    """Response model for the config endpoint."""
    
    default_config: PlannerConfig = Field(..., description="Default configuration")
    provider_info: ProvidersResponse = Field(..., description="Provider information")


class ErrorResponse(BaseModel):
    """Error response model."""
    
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default=None, description="Additional error details")
    code: Optional[str] = Field(default=None, description="Error code")


# CRUD API Models

class ProjectResponse(BaseModel):
    """Response model for project operations."""
    
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(..., description="Current project status")
    priority: ProjectPriority = Field(..., description="Project priority level")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    due_date: Optional[str] = Field(None, description="Project due date (ISO format)")
    start_date: Optional[str] = Field(None, description="Project start date (ISO format)")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    created_by: str = Field(..., description="Creator ID or name")
    task_count: int = Field(0, description="Total number of tasks")
    completed_task_count: int = Field(0, description="Number of completed tasks")
    
    # Integration references
    motion_project_id: Optional[str] = Field(None, description="Motion project ID")
    linear_project_id: Optional[str] = Field(None, description="Linear project ID")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID")
    gitlab_project_id: Optional[str] = Field(None, description="GitLab project ID")


class ProjectWithTasksResponse(ProjectResponse):
    """Response model for project with tasks."""
    
    tasks: List['TaskResponse'] = Field(default_factory=list, description="Project tasks")


class TaskResponse(BaseModel):
    """Response model for task operations."""
    
    id: str = Field(..., description="Task ID")
    project_id: str = Field(..., description="Project ID")
    parent_id: Optional[str] = Field(None, description="Parent task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    status: TaskStatus = Field(..., description="Current task status")
    priority: TaskPriority = Field(..., description="Task priority level")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    
    # Time tracking
    estimated_minutes: Optional[int] = Field(None, description="Estimated time in minutes")
    actual_minutes: int = Field(0, description="Actual time spent in minutes")
    
    # Scheduling
    due_date: Optional[str] = Field(None, description="Task due date (ISO format)")
    
    # Assignment and hierarchy
    assignee: Optional[str] = Field(None, description="Task assignee")
    depth: int = Field(0, description="Task depth in hierarchy")
    sort_order: int = Field(0, description="Sort order within parent")
    
    # Progress and metadata
    completion_percentage: int = Field(0, description="Completion percentage (0-100)")
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    attachments: List[Dict[str, Any]] = Field(default_factory=list, description="Task attachments")
    notes: Optional[str] = Field(None, description="Task notes")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    # Timestamps
    created_at: str = Field(..., description="Creation timestamp (ISO format)")
    updated_at: str = Field(..., description="Last update timestamp (ISO format)")
    created_by: str = Field(..., description="Creator ID or name")
    
    # Integration references
    motion_task_id: Optional[str] = Field(None, description="Motion task ID")
    linear_issue_id: Optional[str] = Field(None, description="Linear issue ID")
    notion_task_id: Optional[str] = Field(None, description="Notion task ID")
    gitlab_issue_id: Optional[str] = Field(None, description="GitLab issue ID")


class TaskWithSubtasksResponse(TaskResponse):
    """Response model for task with subtasks."""
    
    subtasks: List['TaskResponse'] = Field(default_factory=list, description="Subtasks")


class ProjectListResponse(BaseModel):
    """Response model for project list operations."""
    
    projects: List[ProjectResponse] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(100, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_prev: bool = Field(False, description="Whether there are previous pages")


class TaskListResponse(BaseModel):
    """Response model for task list operations."""
    
    tasks: List[TaskResponse] = Field(..., description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
    page: int = Field(1, description="Current page number")
    per_page: int = Field(100, description="Items per page")
    has_next: bool = Field(False, description="Whether there are more pages")
    has_prev: bool = Field(False, description="Whether there are previous pages")


class ProjectCreateRequest(BaseModel):
    """Request model for creating projects."""
    
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Project status")
    priority: ProjectPriority = Field(ProjectPriority.MEDIUM, description="Project priority")
    tags: List[str] = Field(default_factory=list, description="Project tags")
    due_date: Optional[str] = Field(None, description="Project due date (ISO format)")
    start_date: Optional[str] = Field(None, description="Project start date (ISO format)")
    created_by: str = Field(..., description="Creator ID or name")
    
    # Integration references
    motion_project_id: Optional[str] = Field(None, description="Motion project ID")
    linear_project_id: Optional[str] = Field(None, description="Linear project ID")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID")
    gitlab_project_id: Optional[str] = Field(None, description="GitLab project ID")


class ProjectUpdateRequest(BaseModel):
    """Request model for updating projects."""
    
    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Project description")
    status: Optional[ProjectStatus] = Field(None, description="Project status")
    priority: Optional[ProjectPriority] = Field(None, description="Project priority")
    tags: Optional[List[str]] = Field(None, description="Project tags")
    due_date: Optional[str] = Field(None, description="Project due date (ISO format)")
    start_date: Optional[str] = Field(None, description="Project start date (ISO format)")
    
    # Integration references
    motion_project_id: Optional[str] = Field(None, description="Motion project ID")
    linear_project_id: Optional[str] = Field(None, description="Linear project ID")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID")
    gitlab_project_id: Optional[str] = Field(None, description="GitLab project ID")


class TaskCreateRequest(BaseModel):
    """Request model for creating tasks."""
    
    project_id: str = Field(..., description="Project ID")
    parent_id: Optional[str] = Field(None, description="Parent task ID")
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: TaskStatus = Field(TaskStatus.TODO, description="Task status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    
    # Time tracking
    estimated_minutes: Optional[int] = Field(None, ge=0, description="Estimated time in minutes")
    
    # Scheduling
    due_date: Optional[str] = Field(None, description="Task due date (ISO format)")
    
    # Assignment and hierarchy
    assignee: Optional[str] = Field(None, description="Task assignee")
    
    # Progress and metadata
    dependencies: List[str] = Field(default_factory=list, description="Task dependencies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_by: str = Field(..., description="Creator ID or name")
    
    # Integration references
    motion_task_id: Optional[str] = Field(None, description="Motion task ID")
    linear_issue_id: Optional[str] = Field(None, description="Linear issue ID")
    notion_task_id: Optional[str] = Field(None, description="Notion task ID")
    gitlab_issue_id: Optional[str] = Field(None, description="GitLab issue ID")


class TaskUpdateRequest(BaseModel):
    """Request model for updating tasks."""
    
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=2000, description="Task description")
    status: Optional[TaskStatus] = Field(None, description="Task status")
    priority: Optional[TaskPriority] = Field(None, description="Task priority")
    tags: Optional[List[str]] = Field(None, description="Task tags")
    
    # Time tracking
    estimated_minutes: Optional[int] = Field(None, ge=0, description="Estimated time in minutes")
    actual_minutes: Optional[int] = Field(None, ge=0, description="Actual time spent in minutes")
    
    # Scheduling
    due_date: Optional[str] = Field(None, description="Task due date (ISO format)")
    
    # Assignment and hierarchy
    assignee: Optional[str] = Field(None, description="Task assignee")
    parent_id: Optional[str] = Field(None, description="Parent task ID")
    
    # Progress and metadata
    dependencies: Optional[List[str]] = Field(None, description="Task dependencies")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    
    # Integration references
    motion_task_id: Optional[str] = Field(None, description="Motion task ID")
    linear_issue_id: Optional[str] = Field(None, description="Linear issue ID")
    notion_task_id: Optional[str] = Field(None, description="Notion task ID")
    gitlab_issue_id: Optional[str] = Field(None, description="GitLab issue ID")


# Fix forward reference for TaskWithSubtasksResponse
TaskWithSubtasksResponse.model_rebuild()
ProjectWithTasksResponse.model_rebuild()