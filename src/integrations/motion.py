"""Motion API integration"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import logging

from .base import IntegrationError
from .project_management import ProjectManagementIntegration
from ..models import Project, Task, ProjectStatus, TaskStatus, TaskPriority


logger = logging.getLogger(__name__)


class MotionIntegration(ProjectManagementIntegration):
    """Integration with Motion task management"""

    BASE_URL = "https://api.usemotion.com/v1"

    @property
    def integration_type(self) -> str:
        return "motion"

    def _get_headers(self) -> Dict[str, str]:
        """Get API headers"""
        api_key = self.config.api_key.get_secret_value() if self.config.api_key else None
        if not api_key:
            raise IntegrationError("Motion API key not configured")

        return {"X-API-Key": api_key, "Accept": "application/json", "Content-Type": "application/json"}

    def validate_config(self) -> bool:
        """Validate Motion configuration"""
        if not self.config.api_key:
            raise IntegrationError("Motion API key is required")
        return True

    def test_connection(self) -> bool:
        """Test Motion API connection"""
        try:
            response = requests.get(f"{self.BASE_URL}/users/me", headers=self._get_headers(), timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Motion connection test failed: {e}")
            return False

    # User operations
    def get_current_user(self) -> Dict[str, Any]:
        """Get current Motion user"""
        response = requests.get(f"{self.BASE_URL}/users/me", headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_users(self) -> List[Dict[str, Any]]:
        """List Motion workspace users"""
        response = requests.get(f"{self.BASE_URL}/users", headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("users", [])

    # Project operations
    def create_project(self, project: Project) -> Dict[str, Any]:
        """Create a project in Motion"""
        data = {
            "name": project.name,
            "description": project.description,
            "dueDate": project.due_date.isoformat() if project.due_date else None,
            "status": self._map_project_status_to_motion(project.status),
            "workspaceId": self.config.workspace_id,
        }

        response = requests.post(f"{self.BASE_URL}/projects", json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Motion project"""
        motion_updates = {}

        if "name" in updates:
            motion_updates["name"] = updates["name"]
        if "description" in updates:
            motion_updates["description"] = updates["description"]
        if "due_date" in updates:
            motion_updates["dueDate"] = updates["due_date"].isoformat() if updates["due_date"] else None
        if "status" in updates:
            motion_updates["status"] = self._map_project_status_to_motion(updates["status"])

        response = requests.patch(
            f"{self.BASE_URL}/projects/{project_id}", json=motion_updates, headers=self._get_headers()
        )
        response.raise_for_status()
        return response.json()

    def get_project(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get a Motion project"""
        try:
            response = requests.get(f"{self.BASE_URL}/projects/{external_id}", headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def list_projects(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List Motion projects"""
        params = {}
        if filters:
            if "status" in filters:
                params["status"] = filters["status"]

        response = requests.get(f"{self.BASE_URL}/projects", params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("projects", [])

    # Task operations
    def create_task(self, task: Task) -> Dict[str, Any]:
        """Create a task in Motion"""
        # Get Motion project ID
        project = self.delta.get_project(task.project_id)
        if not project or not project.get("motion_project_id"):
            raise IntegrationError(f"Project {task.project_id} not synced with Motion")

        data = {
            "name": task.title,
            "description": task.description,
            "projectId": project["motion_project_id"],
            "dueDate": task.due_date.isoformat() if task.due_date else None,
            "duration": int(task.estimated_hours * 60) if task.estimated_hours else None,  # Motion uses minutes
            "priority": self._map_task_priority_to_motion(task.priority),
            "status": self._map_task_status_to_motion(task.status),
            "assigneeId": self._get_motion_user_id(task.assignee) if task.assignee else None,
            "labels": task.labels,
        }

        # Remove None values
        data = {k: v for k, v in data.items() if v is not None}

        response = requests.post(f"{self.BASE_URL}/tasks", json=data, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update a Motion task"""
        motion_updates = {}

        if "title" in updates:
            motion_updates["name"] = updates["title"]
        if "description" in updates:
            motion_updates["description"] = updates["description"]
        if "due_date" in updates:
            motion_updates["dueDate"] = updates["due_date"].isoformat() if updates["due_date"] else None
        if "estimated_hours" in updates:
            motion_updates["duration"] = int(updates["estimated_hours"] * 60) if updates["estimated_hours"] else None
        if "priority" in updates:
            motion_updates["priority"] = self._map_task_priority_to_motion(updates["priority"])
        if "status" in updates:
            motion_updates["status"] = self._map_task_status_to_motion(updates["status"])
        if "assignee" in updates:
            motion_updates["assigneeId"] = (
                self._get_motion_user_id(updates["assignee"]) if updates["assignee"] else None
            )

        response = requests.patch(f"{self.BASE_URL}/tasks/{task_id}", json=motion_updates, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_task(self, external_id: str) -> Optional[Dict[str, Any]]:
        """Get a Motion task"""
        try:
            response = requests.get(f"{self.BASE_URL}/tasks/{external_id}", headers=self._get_headers())
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise

    def list_tasks(self, project_id: Optional[str] = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """List Motion tasks"""
        params = {}

        if project_id:
            # Get Motion project ID
            project = self.delta.get_project(project_id)
            if project and project.get("motion_project_id"):
                params["projectId"] = project["motion_project_id"]

        if filters:
            if "status" in filters:
                params["status"] = filters["status"]
            if "assignee" in filters:
                params["assigneeId"] = self._get_motion_user_id(filters["assignee"])

        response = requests.get(f"{self.BASE_URL}/tasks", params=params, headers=self._get_headers())
        response.raise_for_status()
        return response.json().get("tasks", [])

    # Mapping methods
    def _map_project_status_to_motion(self, status: ProjectStatus) -> str:
        """Map internal project status to Motion status"""
        mapping = {
            ProjectStatus.PLANNING: "PLANNING",
            ProjectStatus.ACTIVE: "IN_PROGRESS",
            ProjectStatus.ON_HOLD: "ON_HOLD",
            ProjectStatus.COMPLETED: "COMPLETED",
            ProjectStatus.ARCHIVED: "ARCHIVED",
        }
        return mapping.get(status, "PLANNING")

    def _map_motion_project_status(self, motion_status: str) -> ProjectStatus:
        """Map Motion project status to internal status"""
        mapping = {
            "PLANNING": ProjectStatus.PLANNING,
            "IN_PROGRESS": ProjectStatus.ACTIVE,
            "ON_HOLD": ProjectStatus.ON_HOLD,
            "COMPLETED": ProjectStatus.COMPLETED,
            "ARCHIVED": ProjectStatus.ARCHIVED,
        }
        return mapping.get(motion_status, ProjectStatus.PLANNING)

    def _map_task_status_to_motion(self, status: TaskStatus) -> str:
        """Map internal task status to Motion status"""
        mapping = {
            TaskStatus.TODO: "TODO",
            TaskStatus.IN_PROGRESS: "IN_PROGRESS",
            TaskStatus.BLOCKED: "BLOCKED",
            TaskStatus.IN_REVIEW: "IN_REVIEW",
            TaskStatus.COMPLETED: "COMPLETED",
            TaskStatus.CANCELLED: "CANCELLED",
        }
        return mapping.get(status, "TODO")

    def _map_motion_task_status(self, motion_status: str) -> TaskStatus:
        """Map Motion task status to internal status"""
        mapping = {
            "TODO": TaskStatus.TODO,
            "IN_PROGRESS": TaskStatus.IN_PROGRESS,
            "BLOCKED": TaskStatus.BLOCKED,
            "IN_REVIEW": TaskStatus.IN_REVIEW,
            "COMPLETED": TaskStatus.COMPLETED,
            "CANCELLED": TaskStatus.CANCELLED,
        }
        return mapping.get(motion_status, TaskStatus.TODO)

    def _map_task_priority_to_motion(self, priority: TaskPriority) -> str:
        """Map internal priority to Motion priority"""
        mapping = {
            TaskPriority.CRITICAL: "ASAP",
            TaskPriority.HIGH: "HIGH",
            TaskPriority.MEDIUM: "MEDIUM",
            TaskPriority.LOW: "LOW",
            TaskPriority.BACKLOG: "LOW",
        }
        return mapping.get(priority, "MEDIUM")

    def _map_motion_task_priority(self, motion_priority: str) -> TaskPriority:
        """Map Motion priority to internal priority"""
        mapping = {
            "ASAP": TaskPriority.CRITICAL,
            "HIGH": TaskPriority.HIGH,
            "MEDIUM": TaskPriority.MEDIUM,
            "LOW": TaskPriority.LOW,
        }
        return mapping.get(motion_priority, TaskPriority.MEDIUM)

    def _get_motion_user_id(self, user_ref: str) -> Optional[str]:
        """Get Motion user ID from local user reference"""
        if not user_ref:
            return None

        # Try to find user by ID or name
        user = self.delta.get_user(user_ref)
        if user and user.get("motion_user_id"):
            return user["motion_user_id"]

        # Fallback: search by name in Motion users
        motion_users = self.list_users()
        for m_user in motion_users:
            if m_user.get("name") == user_ref or m_user.get("email") == user_ref:
                return m_user["id"]

        return None

    def _map_external_project_to_local(self, external_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map Motion project to local format"""
        return {
            "name": external_project["name"],
            "description": external_project.get("description"),
            "status": self._map_motion_project_status(external_project.get("status", "PLANNING")),
            "priority": 3,  # Default priority
            "due_date": (
                datetime.fromisoformat(external_project["dueDate"].replace("Z", "+00:00")).date()
                if external_project.get("dueDate")
                else None
            ),
            "motion_project_id": external_project["id"],
            "tags": external_project.get("labels", []),
        }

    def _map_external_project_to_updates(self, external_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map Motion project to update fields"""
        updates = {
            "name": external_project["name"],
            "description": external_project.get("description"),
            "status": self._map_motion_project_status(external_project.get("status", "PLANNING")),
        }

        if external_project.get("dueDate"):
            updates["due_date"] = datetime.fromisoformat(external_project["dueDate"].replace("Z", "+00:00")).date()

        return updates

    def _map_local_project_to_external_updates(self, local_project: Dict[str, Any]) -> Dict[str, Any]:
        """Map local project to Motion update format"""
        updates = {
            "name": local_project["name"],
            "description": local_project.get("description"),
            "status": self._map_project_status_to_motion(ProjectStatus(local_project["status"])),
        }

        if local_project.get("due_date"):
            updates["dueDate"] = (
                local_project["due_date"].isoformat()
                if isinstance(local_project["due_date"], date)
                else local_project["due_date"]
            )

        return updates
