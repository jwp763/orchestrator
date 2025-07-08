"""Core Pydantic schemas for the Orchestrator application."""

from datetime import datetime, date
from enum import Enum
from typing import List, Optional, Dict, Any
try:
    from typing import Self  # Python 3.11+
except ImportError:
    from typing_extensions import Self  # Python < 3.11
from pydantic import BaseModel, Field, model_validator
from uuid import uuid4


class TaskStatus(str, Enum):
    """Task status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ProjectStatus(str, Enum):
    """Project status enumeration."""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class Priority(str, Enum):
    """Priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Op(str, Enum):
    """Operation type for patches."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class Task(BaseModel):
    """Task model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    project_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority = Priority.MEDIUM
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    labels: List[str] = Field(default_factory=list)
    depends_on: List[str] = Field(default_factory=list)
    blocks: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    created_by: str

    @model_validator(mode='before')
    @classmethod
    def set_timestamps(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        # Always update the updated_at timestamp
        values['updated_at'] = datetime.now()
        
        # Handle completed_at based on status
        if isinstance(values, dict):
            status = values.get('status')
            if (status == TaskStatus.COMPLETED and 
                not values.get('completed_at')):
                values['completed_at'] = datetime.now()
            elif status != TaskStatus.COMPLETED:
                values['completed_at'] = None
        return values


class Project(BaseModel):
    """Project model."""
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.ACTIVE
    priority: int = Field(default=3, ge=1, le=5)
    tags: List[str] = Field(default_factory=list)
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    created_by: str
    tasks: List[Task] = Field(default_factory=list)

    @model_validator(mode='before')
    @classmethod
    def set_updated_at(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(values, dict):
            values['updated_at'] = datetime.now()
        return values

    @property
    def task_count(self) -> int:
        return len(self.tasks)

    @property
    def completed_task_count(self) -> int:
        return len([task for task in self.tasks 
                   if task.status == TaskStatus.COMPLETED])


class TaskPatch(BaseModel):
    """Task patch model for updates."""
    op: Op
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[date] = None
    estimated_hours: Optional[float] = None
    actual_hours: Optional[float] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    depends_on: Optional[List[str]] = None
    blocks: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    @model_validator(mode='after')
    def validate_task_id_for_operation(self) -> Self:
        if (self.op in [Op.UPDATE, Op.DELETE] and not self.task_id):
            raise ValueError(f"task_id is required for {self.op} operation")
        return self


class ProjectPatch(BaseModel):
    """Project patch model for updates."""
    op: Op
    project_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    tasks: Optional[List[TaskPatch]] = None

    @model_validator(mode='after')
    def validate_project_id_for_operation(self) -> Self:
        if (self.op in [Op.UPDATE, Op.DELETE] and not self.project_id):
            raise ValueError(f"project_id is required for {self.op} operation")
        return self


class Patch(BaseModel):
    """Combined patch model for both projects and tasks."""
    project_patches: List[ProjectPatch] = Field(default_factory=list)
    task_patches: List[TaskPatch] = Field(default_factory=list)

    @model_validator(mode='after')
    def validate_patches_not_empty(self) -> Self:
        # At least one patch must be provided
        if not self.project_patches and not self.task_patches:
            raise ValueError("At least one patch must be provided")
        return self