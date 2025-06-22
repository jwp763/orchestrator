from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKLOG = "backlog"


class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    project_id: str = Field(..., description="Parent project ID")
    status: TaskStatus = Field(TaskStatus.TODO, description="Current task status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    
    # Scheduling
    due_date: Optional[date] = Field(None, description="Task due date")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours to complete")
    actual_hours: Optional[float] = Field(None, description="Actual hours spent")
    
    # Assignment
    assignee: Optional[str] = Field(None, description="Assigned to")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    labels: List[str] = Field(default_factory=list, description="Task labels")
    
    # Integration references
    motion_task_id: Optional[str] = Field(None, description="Motion task ID")
    linear_issue_id: Optional[str] = Field(None, description="Linear issue ID")
    notion_task_id: Optional[str] = Field(None, description="Notion task ID")
    gitlab_issue_id: Optional[str] = Field(None, description="GitLab issue ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TaskCreate(TaskBase):
    pass


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    motion_task_id: Optional[str] = None
    linear_issue_id: Optional[str] = None
    notion_task_id: Optional[str] = None
    gitlab_issue_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Task(TaskBase):
    id: str = Field(..., description="Unique task ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_by: str = Field(..., description="Creator ID or name")
    
    # Dependencies
    depends_on: List[str] = Field(default_factory=list, description="Task IDs this depends on")
    blocks: List[str] = Field(default_factory=list, description="Task IDs this blocks")
    
    # Computed fields
    is_overdue: bool = Field(False, description="Whether task is overdue")
    days_until_due: Optional[int] = Field(None, description="Days until due date")
    
    class Config:
        from_attributes = True