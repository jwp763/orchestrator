from datetime import date, datetime
from enum import Enum
from typing import Any, List, Optional, TYPE_CHECKING
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

if TYPE_CHECKING:
    from .task import Task, TaskStatus


class ProjectStatus(str, Enum):
    """
    Enumeration of possible project status values.

    Represents the lifecycle stages of a project from initial planning
    through completion and archival.
    """

    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectPriority(str, Enum):
    """
    Enumeration of project priority levels.

    Used to indicate the relative importance and urgency of projects
    for resource allocation and scheduling decisions.
    """

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKLOG = "backlog"


class ProjectBase(BaseModel):
    """
    Base model for project data with core fields and validation.

    Provides the foundation for project management including status tracking,
    priority management, scheduling, and integration with external systems.
    Supports tagging and metadata for flexible organization.
    """

    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Current project status")
    priority: ProjectPriority = Field(ProjectPriority.MEDIUM, description="Project priority level")
    tags: List[str] = Field(default_factory=list, description="Project tags")

    # Scheduling
    due_date: Optional[date] = Field(None, description="Project due date")
    start_date: Optional[date] = Field(None, description="Project start date")

    # Integration references
    motion_project_id: Optional[str] = Field(None, description="Motion project ID")
    linear_project_id: Optional[str] = Field(None, description="Linear project ID")
    notion_page_id: Optional[str] = Field(None, description="Notion page ID")
    gitlab_project_id: Optional[str] = Field(None, description="GitLab project ID")


class ProjectCreate(ProjectBase):
    """
    Model for creating new projects.

    Inherits all fields from ProjectBase without requiring ID or timestamps,
    which are generated automatically by the storage layer.
    """

    pass


class ProjectUpdate(BaseModel):
    """
    Model for updating existing projects.

    All fields are optional to allow partial updates. Maintains the same
    validation rules as ProjectBase for fields that are provided.
    """

    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    motion_project_id: Optional[str] = None
    linear_project_id: Optional[str] = None
    notion_page_id: Optional[str] = None
    gitlab_project_id: Optional[str] = None


class Project(ProjectBase):
    """
    Complete project model with database fields and metadata.

    Extends ProjectBase with database-specific fields like ID, timestamps,
    and creator information. Used for project instances retrieved from
    or stored in the database.
    """

    id: str = Field(default_factory=lambda: str(uuid4()), description="Unique project ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    created_by: str = Field(..., description="Creator ID or name")

    # Related tasks (populated by storage layer)
    tasks: List["Task"] = Field(default_factory=list, description="Project tasks")

    @model_validator(mode="before")
    @classmethod
    def set_updated_at(cls, values: Any) -> Any:
        """Set updated_at timestamp."""
        if isinstance(values, dict):
            values["updated_at"] = datetime.now()
        return values

    @property
    def task_count(self) -> int:
        """Get the total number of tasks in this project."""
        return len(self.tasks)

    @property
    def completed_task_count(self) -> int:
        """Get the number of completed tasks in this project."""
        # Import here to avoid circular imports
        from .task import TaskStatus
        return len([task for task in self.tasks if task.status == TaskStatus.COMPLETED])

    model_config = ConfigDict(from_attributes=True)
