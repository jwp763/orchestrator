from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from src.models.project import Project
from src.models.task import Task


class BaseStorageRepository(ABC):
    """Abstract base class for storage repositories."""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> None:
        """Initialize the repository with the given configuration."""
        pass

    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Project]:
        """Retrieve a project by its ID."""
        pass

    @abstractmethod
    def create_project(self, project: Project) -> Project:
        """Create a new project."""
        pass

    @abstractmethod
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        """Update an existing project."""
        pass

    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]:
        """Retrieve a task by its ID."""
        pass

    @abstractmethod
    def create_task(self, task: Task) -> Task:
        """Create a new task."""
        pass

    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update an existing task."""
        pass

    @abstractmethod
    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        """Retrieve all tasks for a given project."""
        pass
