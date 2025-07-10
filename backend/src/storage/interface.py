"""Storage interface for the Orchestrator application."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from src.models import Project, Task
from src.models.patch import Patch, ProjectPatch, TaskPatch


class StorageInterface(ABC):
    """Abstract interface for storage operations."""

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by ID."""
        pass

    @abstractmethod
    def get_projects(self) -> List[Project]:
        """Retrieve all projects."""
        pass

    @abstractmethod
    def create_project(self, project: Project) -> Project:
        """Create a new project."""
        pass

    @abstractmethod
    def update_project(self, project_id: str, project: Project) -> Optional[Project]:
        """Update an existing project."""
        pass

    @abstractmethod
    def delete_project(self, project_id: str) -> bool:
        """Delete a project by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by ID."""
        pass

    @abstractmethod
    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Retrieve all tasks for a project."""
        pass

    @abstractmethod
    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 20,
        project_id: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        assignee: Optional[str] = None,
        parent_id: Optional[str] = None,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        created_after: Optional[datetime] = None,
        created_before: Optional[datetime] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """List tasks with filtering, pagination, and sorting.
        
        Returns a dictionary with:
        - tasks: List of tasks
        - total: Total count of tasks matching filters
        - page: Current page number
        - per_page: Items per page
        - has_next: Whether there's a next page
        - has_prev: Whether there's a previous page
        """
        pass

    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        pass

    @abstractmethod
    def update_task(self, task_id: str, task: Task) -> Optional[Task]:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete_task(self, task_id: str) -> bool:
        """Delete a task by ID. Returns True if deleted, False if not found."""
        pass

    @abstractmethod
    def apply_patch(self, patch: Patch) -> bool:
        """Apply a patch containing project and/or task operations.

        Returns True if successful, False otherwise.
        All operations in the patch should be applied atomically.
        """
        pass

    @abstractmethod
    def apply_project_patch(self, patch: ProjectPatch) -> Optional[Project]:
        """Apply a single project patch operation.

        Returns the affected project or None if operation failed.
        """
        pass

    @abstractmethod
    def apply_task_patch(self, patch: TaskPatch) -> Optional[Task]:
        """Apply a single task patch operation.

        Returns the affected task or None if operation failed.
        """
        pass

    @abstractmethod
    def begin_transaction(self) -> None:
        """Begin a database transaction."""
        pass

    @abstractmethod
    def commit_transaction(self) -> None:
        """Commit the current transaction."""
        pass

    @abstractmethod
    def rollback_transaction(self) -> None:
        """Rollback the current transaction."""
        pass
