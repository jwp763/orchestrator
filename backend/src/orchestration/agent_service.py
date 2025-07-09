"""Agent service for coordinating AI agents with data operations."""

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from ..models.project import Project, ProjectCreate
from ..models.task import Task, TaskCreate
from ..models.patch import Patch, ProjectPatch, TaskPatch, Op
from ..agent.planner_agent import PlannerAgent
from ..storage.interface import StorageInterface
from ..storage.sql_implementation import SQLStorage
from .project_service import ProjectService
from .task_service import TaskService

logger = logging.getLogger(__name__)


class AgentService:
    """Service class for coordinating AI agents with data operations.
    
    Handles the orchestration between AI agents and storage operations,
    including patch generation, validation, and application.
    """
    
    def __init__(
        self,
        storage: Optional[StorageInterface] = None,
        project_service: Optional[ProjectService] = None,
        task_service: Optional[TaskService] = None
    ):
        """Initialize the agent service.
        
        Args:
            storage: Storage interface implementation
            project_service: Project service instance
            task_service: Task service instance
        """
        self.storage = storage or SQLStorage()
        self.project_service = project_service or ProjectService(self.storage)
        self.task_service = task_service or TaskService(self.storage)
        
        # Initialize AI agents
        self.planner_agent = PlannerAgent()
    
    def generate_project_from_idea(
        self,
        idea: str,
        context: Optional[Dict[str, Any]] = None,
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Generate a project and tasks from a natural language idea.
        
        Args:
            idea: Natural language description of the project idea
            context: Additional context for the AI agent
            created_by: User who initiated the generation
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating if generation was successful
            - project: Created project data (if successful)
            - tasks: List of created tasks (if successful)
            - patch: The generated patch that was applied
            - error: Error message (if failed)
        """
        try:
            logger.info(f"Generating project from idea: {idea[:100]}...")
            
            # Generate patch using PlannerAgent
            logger.info("Calling PlannerAgent to generate patch")
            generated_patch = self.planner_agent.get_diff(idea, context or {})
            
            if not generated_patch:
                return {
                    "success": False,
                    "error": "Failed to generate patch from idea",
                    "project": None,
                    "tasks": [],
                    "patch": None
                }
            
            logger.info(f"Generated patch with {len(generated_patch.project_patches)} project patches "
                       f"and {len(generated_patch.task_patches)} task patches")
            
            # Apply the generated patch
            result = self.apply_patch(generated_patch, created_by)
            
            if result["success"]:
                logger.info("Successfully generated and applied project from idea")
                return {
                    "success": True,
                    "project": result.get("project"),
                    "tasks": result.get("tasks", []),
                    "patch": generated_patch,
                    "error": None
                }
            else:
                logger.error(f"Failed to apply generated patch: {result.get('error')}")
                return {
                    "success": False,
                    "error": f"Failed to apply patch: {result.get('error')}",
                    "project": None,
                    "tasks": [],
                    "patch": generated_patch
                }
                
        except Exception as e:
            logger.error(f"Error generating project from idea: {e}")
            return {
                "success": False,
                "error": f"Generation failed: {str(e)}",
                "project": None,
                "tasks": [],
                "patch": None
            }
    
    def apply_patch(self, patch: Patch, created_by: str = "system") -> Dict[str, Any]:
        """Apply a patch containing project and/or task operations atomically.
        
        Args:
            patch: Patch containing operations to apply
            created_by: User who initiated the patch application
            
        Returns:
            Dictionary containing:
            - success: Boolean indicating if application was successful
            - project: Applied project data (if any)
            - tasks: List of applied tasks
            - operations_applied: Number of operations successfully applied
            - error: Error message (if failed)
        """
        try:
            logger.info(f"Applying patch with {len(patch.project_patches)} project patches "
                       f"and {len(patch.task_patches)} task patches")
            
            applied_project = None
            applied_tasks = []
            operations_applied = 0
            
            # Begin transaction
            self.storage.begin_transaction()
            
            try:
                # Apply project patches
                for project_patch in patch.project_patches:
                    logger.info(f"Applying project patch: {project_patch.op}")
                    
                    if project_patch.op == Op.CREATE:
                        # Create project using project service
                        project_create = ProjectCreate(
                            name=project_patch.name,
                            description=project_patch.description,
                            status=project_patch.status,
                            priority=project_patch.priority,
                            tags=project_patch.tags or [],
                            due_date=project_patch.due_date,
                            start_date=project_patch.start_date
                        )
                        applied_project = self.project_service.create_project(project_create, created_by)
                        operations_applied += 1
                        
                    elif project_patch.op in [Op.UPDATE, Op.DELETE]:
                        # Use storage layer for direct patch application
                        result = self.storage.apply_project_patch(project_patch)
                        if result:
                            applied_project = result
                            operations_applied += 1
                
                # Apply task patches
                for task_patch in patch.task_patches:
                    logger.info(f"Applying task patch: {task_patch.op}")
                    
                    if task_patch.op == Op.CREATE:
                        # For task creation, we need to ensure project_id is set
                        project_id = task_patch.project_id
                        if not project_id and applied_project:
                            project_id = applied_project.id
                            
                        if not project_id:
                            raise ValueError("Cannot create task without valid project_id")
                        
                        # Create task using task service
                        task_create = TaskCreate(
                            project_id=project_id,
                            title=task_patch.title,
                            description=task_patch.description,
                            status=task_patch.status,
                            priority=task_patch.priority,
                            estimated_minutes=task_patch.estimated_minutes,
                            actual_minutes=task_patch.actual_minutes,
                            due_date=task_patch.due_date,
                            assignee=task_patch.assignee,
                            tags=task_patch.tags or [],
                            labels=task_patch.labels or [],
                            dependencies=task_patch.dependencies or [],
                            metadata=task_patch.metadata or {}
                        )
                        applied_task = self.task_service.create_task(task_create, created_by)
                        applied_tasks.append(applied_task)
                        operations_applied += 1
                        
                    elif task_patch.op in [Op.UPDATE, Op.DELETE]:
                        # Use storage layer for direct patch application
                        result = self.storage.apply_task_patch(task_patch)
                        if result:
                            applied_tasks.append(result)
                            operations_applied += 1
                
                # Commit transaction
                self.storage.commit_transaction()
                
                logger.info(f"Successfully applied patch: {operations_applied} operations")
                return {
                    "success": True,
                    "project": applied_project,
                    "tasks": applied_tasks,
                    "operations_applied": operations_applied,
                    "error": None
                }
                
            except Exception as e:
                # Rollback transaction on error
                logger.error(f"Error applying patch operations: {e}")
                self.storage.rollback_transaction()
                raise
                
        except Exception as e:
            logger.error(f"Error applying patch: {e}")
            return {
                "success": False,
                "project": None,
                "tasks": [],
                "operations_applied": 0,
                "error": str(e)
            }
    
    def validate_patch(self, patch: Patch) -> Dict[str, Any]:
        """Validate a patch without applying it.
        
        Args:
            patch: Patch to validate
            
        Returns:
            Dictionary containing:
            - valid: Boolean indicating if patch is valid
            - errors: List of validation errors
            - warnings: List of validation warnings
        """
        try:
            logger.info("Validating patch")
            
            errors = []
            warnings = []
            
            # Validate project patches
            for i, project_patch in enumerate(patch.project_patches):
                try:
                    if project_patch.op == Op.CREATE:
                        if not project_patch.name:
                            errors.append(f"Project patch {i}: name is required for creation")
                        elif len(project_patch.name) > 255:
                            errors.append(f"Project patch {i}: name exceeds 255 characters")
                            
                        if project_patch.description and len(project_patch.description) > 2000:
                            errors.append(f"Project patch {i}: description exceeds 2000 characters")
                            
                    elif project_patch.op in [Op.UPDATE, Op.DELETE]:
                        if not project_patch.project_id:
                            errors.append(f"Project patch {i}: project_id is required for {project_patch.op}")
                        else:
                            # Check if project exists
                            existing_project = self.storage.get_project(project_patch.project_id)
                            if not existing_project:
                                errors.append(f"Project patch {i}: project {project_patch.project_id} not found")
                                
                except Exception as e:
                    errors.append(f"Project patch {i}: validation error - {str(e)}")
            
            # Validate task patches
            for i, task_patch in enumerate(patch.task_patches):
                try:
                    if task_patch.op == Op.CREATE:
                        if not task_patch.title:
                            errors.append(f"Task patch {i}: title is required for creation")
                        elif len(task_patch.title) > 255:
                            errors.append(f"Task patch {i}: title exceeds 255 characters")
                            
                        if not task_patch.project_id:
                            # Check if there's a project being created in this patch
                            if not any(pp.op == Op.CREATE for pp in patch.project_patches):
                                errors.append(f"Task patch {i}: project_id is required")
                        else:
                            # Check if project exists or is being created
                            existing_project = self.storage.get_project(task_patch.project_id)
                            if not existing_project and not any(
                                pp.op == Op.CREATE for pp in patch.project_patches
                            ):
                                errors.append(f"Task patch {i}: project {task_patch.project_id} not found")
                                
                        if task_patch.description and len(task_patch.description) > 2000:
                            errors.append(f"Task patch {i}: description exceeds 2000 characters")
                            
                    elif task_patch.op in [Op.UPDATE, Op.DELETE]:
                        if not task_patch.task_id:
                            errors.append(f"Task patch {i}: task_id is required for {task_patch.op}")
                        else:
                            # Check if task exists
                            existing_task = self.storage.get_task(task_patch.task_id)
                            if not existing_task:
                                errors.append(f"Task patch {i}: task {task_patch.task_id} not found")
                                
                except Exception as e:
                    errors.append(f"Task patch {i}: validation error - {str(e)}")
            
            # Check for warnings
            if len(patch.project_patches) == 0 and len(patch.task_patches) == 0:
                warnings.append("Patch contains no operations")
                
            if len(patch.task_patches) > 20:
                warnings.append(f"Large number of task operations ({len(patch.task_patches)})")
            
            is_valid = len(errors) == 0
            
            logger.info(f"Patch validation complete: valid={is_valid}, "
                       f"errors={len(errors)}, warnings={len(warnings)}")
            
            return {
                "valid": is_valid,
                "errors": errors,
                "warnings": warnings
            }
            
        except Exception as e:
            logger.error(f"Error validating patch: {e}")
            return {
                "valid": False,
                "errors": [f"Validation failed: {str(e)}"],
                "warnings": []
            }
    
    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Get comprehensive context about a project for AI agents.
        
        Args:
            project_id: ID of the project
            
        Returns:
            Dictionary containing project context information
        """
        try:
            logger.info(f"Getting project context: {project_id}")
            
            project = self.project_service.get_project(project_id)
            if not project:
                return {"error": f"Project {project_id} not found"}
            
            # Get hierarchical task structure
            tasks = self.task_service.get_task_hierarchy(project_id)
            
            # Calculate project statistics
            total_tasks = len(tasks)
            completed_tasks = len([t for t in tasks if t.status == "completed"])
            in_progress_tasks = len([t for t in tasks if t.status == "in_progress"])
            
            total_estimated_minutes = sum(t.estimated_minutes or 0 for t in tasks)
            total_actual_minutes = sum(t.actual_minutes or 0 for t in tasks)
            
            # Organize tasks by hierarchy level
            root_tasks = [t for t in tasks if t.parent_id is None]
            max_depth = max((t.depth for t in tasks), default=0)
            
            context = {
                "project": {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "priority": project.priority,
                    "tags": project.tags,
                    "created_at": project.created_at.isoformat(),
                    "created_by": project.created_by
                },
                "statistics": {
                    "total_tasks": total_tasks,
                    "completed_tasks": completed_tasks,
                    "in_progress_tasks": in_progress_tasks,
                    "completion_percentage": round((completed_tasks / total_tasks * 100) if total_tasks > 0 else 0, 1),
                    "total_estimated_minutes": total_estimated_minutes,
                    "total_actual_minutes": total_actual_minutes,
                    "estimated_hours": round(total_estimated_minutes / 60, 1) if total_estimated_minutes > 0 else 0,
                    "actual_hours": round(total_actual_minutes / 60, 1) if total_actual_minutes > 0 else 0
                },
                "hierarchy": {
                    "root_tasks": len(root_tasks),
                    "max_depth": max_depth,
                    "total_tasks": total_tasks
                },
                "tasks": [
                    {
                        "id": t.id,
                        "title": t.title,
                        "status": t.status,
                        "priority": t.priority,
                        "parent_id": t.parent_id,
                        "depth": t.depth,
                        "estimated_minutes": t.estimated_minutes,
                        "actual_minutes": t.actual_minutes
                    }
                    for t in tasks
                ]
            }
            
            logger.info(f"Generated project context for {project_id}: "
                       f"{total_tasks} tasks, {completed_tasks} completed")
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting project context for {project_id}: {e}")
            return {"error": f"Failed to get project context: {str(e)}"}
    
    def close(self) -> None:
        """Clean up resources."""
        try:
            if hasattr(self.storage, 'close'):
                self.storage.close()
        except Exception as e:
            logger.warning(f"Error closing storage: {e}")