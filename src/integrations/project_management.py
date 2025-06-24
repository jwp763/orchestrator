"""Base classes for integrations providing project and task management."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime

from .base import BaseIntegration
from ..models import Project, Task


class ProjectManagementIntegration(BaseIntegration, ABC):
    """Base class for integrations that manage projects and tasks."""

    # Project operations
    @abstractmethod
    def create_project(self, project: Project) -> Dict[str, Any]:
        """Create a project in the external service"""
        pass

    @abstractmethod
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a project in the external service"""
        pass

    @abstractmethod
    def get_project(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get a project from the external service"""
        pass

    @abstractmethod
    def list_projects(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List projects from the external service"""
        pass

    # Task operations
    @abstractmethod
    def create_task(self, task: Task) -> Dict[str, Any]:
        """Create a task in the external service"""
        pass

    @abstractmethod
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a task in the external service"""
        pass

    @abstractmethod
    def get_task(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get a task from the external service"""
        pass

    @abstractmethod
    def list_tasks(self, project_id: Optional[str] = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List tasks from the external service"""
        pass

    # Sync operations
    def sync_projects(self, direction: str = "bidirectional") -> Dict[str, Any]:
        """Sync projects between local and external service"""
        sync_stats = {
            "projects_created_local": 0,
            "projects_updated_local": 0,
            "projects_created_external": 0,
            "projects_updated_external": 0,
            "errors": [],
        }

        try:
            if direction in ["pull", "bidirectional"]:
                # Pull from external to local
                external_projects = self.list_projects()
                for ext_project in external_projects:
                    try:
                        local_project = self._find_local_project_by_external_id(ext_project["id"])
                        if local_project:
                            # Update existing
                            updates = self._map_external_project_to_updates(ext_project)
                            self.delta.update_project(local_project["id"], updates)
                            sync_stats["projects_updated_local"] += 1
                        else:
                            # Create new
                            project_data = self._map_external_project_to_local(ext_project)
                            self.delta.create_project(project_data, "sync_user")
                            sync_stats["projects_created_local"] += 1
                    except Exception as e:
                        self.logger.error(f"Error syncing project {ext_project.get('id')}: {e}")
                        sync_stats["errors"].append(str(e))

            if direction in ["push", "bidirectional"]:
                # Push from local to external
                local_projects = self.delta.get_projects()
                for local_project in local_projects:
                    try:
                        ext_id = self._get_external_project_id(local_project)
                        if ext_id:
                            # Update existing
                            updates = self._map_local_project_to_external_updates(local_project)
                            self.update_project(ext_id, updates)
                            sync_stats["projects_updated_external"] += 1
                        else:
                            # Create new
                            ext_data = self.create_project(Project(**local_project))
                            # Update local with external ID
                            self.delta.update_project(
                                local_project["id"], {f"{self.integration_type}_project_id": ext_data["id"]}
                            )
                            sync_stats["projects_created_external"] += 1
                    except Exception as e:
                        self.logger.error(f"Error pushing project {local_project.get('id')}: {e}")
                        sync_stats["errors"].append(str(e))

        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            sync_stats["errors"].append(f"Sync failed: {str(e)}")

        return sync_stats

    def sync_tasks(self, project_id: Optional[str] = None, direction: str = "bidirectional") -> Dict[str, Any]:
        """Sync tasks between local and external service"""
        # Similar implementation to sync_projects
        sync_stats = {
            "tasks_created_local": 0,
            "tasks_updated_local": 0,
            "tasks_created_external": 0,
            "tasks_updated_external": 0,
            "errors": [],
        }

        # Implementation would follow similar pattern to sync_projects
        return sync_stats

    # Helper methods used during sync
    @abstractmethod
    def _map_external_project_to_local(self, external_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map external project data to local format"""
        pass

    @abstractmethod
    def _map_external_project_to_updates(self, external_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map external project data to update fields"""
        pass

    @abstractmethod
    def _map_local_project_to_external_updates(self, local_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map local project data to external update format"""
        pass

    def _find_local_project_by_external_id(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Find a local project by its external ID"""
        projects = self.delta.get_projects({f"{self.integration_type}_project_id": external_id})
        return projects[0] if projects else None

    def _get_external_project_id(self, local_project: Dict[str, Any]) -> Optional[str]:
        """Get the external ID for a local project"""
        return local_project.get(f"{self.integration_type}_project_id")
