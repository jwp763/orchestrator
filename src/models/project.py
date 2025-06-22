from datetime import datetime, date
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field


class ProjectStatus(str, Enum):
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectBase(BaseModel):
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    status: ProjectStatus = Field(ProjectStatus.PLANNING, description="Current project status")
    priority: int = Field(3, ge=1, le=5, description="Priority from 1 (highest) to 5 (lowest)")
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
    pass


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    motion_project_id: Optional[str] = None
    linear_project_id: Optional[str] = None
    notion_page_id: Optional[str] = None
    gitlab_project_id: Optional[str] = None


class Project(ProjectBase):
    id: str = Field(..., description="Unique project ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    created_by: str = Field(..., description="Creator ID or name")
    
    # Computed fields
    task_count: int = Field(0, description="Number of tasks in project")
    completed_task_count: int = Field(0, description="Number of completed tasks")
    
    class Config:
        from_attributes = True