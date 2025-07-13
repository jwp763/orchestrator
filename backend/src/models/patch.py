"""Patch models for project and task operations."""

from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from .project import ProjectPriority, ProjectStatus
from .task import TaskPriority, TaskStatus


class Op(str, Enum):
    """Operation type for patches."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"


class JsonPatchOp(BaseModel):
    """JSON Patch operation model for fine-grained updates."""
    
    op: str  # "add", "remove", "replace", "move", "copy", "test"
    path: str  # JSON Pointer path like "/title" or "/tags/0"
    value: Optional[Any] = None  # Value for add/replace operations
    from_path: Optional[str] = None  # Source path for move/copy operations


class TaskPatch(BaseModel):
    """Task patch model for updates."""

    op: Op
    task_id: Optional[str] = None
    project_id: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None

    # Integration references
    motion_task_id: Optional[str] = None
    linear_issue_id: Optional[str] = None
    notion_task_id: Optional[str] = None
    gitlab_issue_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_task_id_for_operation(self) -> Self:
        if self.op in [Op.UPDATE, Op.DELETE] and not self.task_id:
            raise ValueError(f"task_id is required for {self.op.value} operation")
        return self


class ProjectPatch(BaseModel):
    """Project patch model for updates."""

    op: Op
    project_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    tags: Optional[List[str]] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    estimated_total_minutes: Optional[int] = None

    # Integration references
    motion_project_id: Optional[str] = None
    linear_project_id: Optional[str] = None
    notion_page_id: Optional[str] = None
    gitlab_project_id: Optional[str] = None

    @model_validator(mode="after")
    def validate_project_id_for_operation(self) -> Self:
        if self.op in [Op.UPDATE, Op.DELETE] and not self.project_id:
            raise ValueError(f"project_id is required for {self.op.value} operation")
        return self


class Patch(BaseModel):
    """Combined patch model for both projects and tasks."""

    project_patches: List[ProjectPatch] = []
    task_patches: List[TaskPatch] = []

    @model_validator(mode="after")
    def validate_patches_not_empty(self) -> Self:
        # At least one patch must be provided
        if not self.project_patches and not self.task_patches:
            raise ValueError("At least one patch must be provided")
        return self
