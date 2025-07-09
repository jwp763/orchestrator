"""Task service for business logic and hierarchical operations."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from ..models.patch import Patch, TaskPatch, Op
from ..storage.interface import StorageInterface
from ..storage.sql_implementation import SQLStorage

logger = logging.getLogger(__name__)


class TaskService:
    """Service class for task-related business logic and hierarchical operations.
    
    Handles task operations with business rule validation, hierarchical relationship
    management, and coordination between storage and other system components.
    """
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        """Initialize the task service.
        
        Args:
            storage: Storage interface implementation. Defaults to SQLStorage if not provided.
        """
        self.storage = storage or SQLStorage()
    
    def list_tasks(
        self,
        skip: int = 0,
        limit: int = 100,
        project_id: Optional[str] = None,
        parent_id: Optional[str] = None,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        assignee: Optional[str] = None
    ) -> List[Task]:
        """List tasks with optional filtering.
        
        Args:
            skip: Number of tasks to skip for pagination
            limit: Maximum number of tasks to return
            project_id: Filter by project ID
            parent_id: Filter by parent task ID
            status: Filter by task status
            priority: Filter by task priority
            assignee: Filter by assignee
            
        Returns:
            List of tasks matching the criteria
            
        Raises:
            ValueError: If pagination parameters are invalid
        """
        if skip < 0:
            raise ValueError("Skip parameter must be non-negative")
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
            
        try:
            logger.info(f"Listing tasks: skip={skip}, limit={limit}, project_id={project_id}, "
                       f"parent_id={parent_id}, status={status}, priority={priority}, assignee={assignee}")
            
            # Get tasks based on filters
            if project_id:
                all_tasks = self.storage.get_tasks_by_project(project_id)
            else:
                # Get all tasks from all projects
                all_projects = self.storage.get_projects()
                all_tasks = []
                for project in all_projects:
                    all_tasks.extend(self.storage.get_tasks_by_project(project.id))
            
            # Apply additional filters
            filtered_tasks = all_tasks
            if parent_id:
                filtered_tasks = [t for t in filtered_tasks if t.parent_id == parent_id]
            if status:
                filtered_tasks = [t for t in filtered_tasks if t.status == status]
            if priority:
                filtered_tasks = [t for t in filtered_tasks if t.priority == priority]
            if assignee:
                filtered_tasks = [t for t in filtered_tasks if t.assignee == assignee]
            
            # Apply pagination
            tasks = filtered_tasks[skip:skip + limit]
            
            logger.info(f"Retrieved {len(tasks)} tasks (filtered from {len(all_tasks)} total)")
            return tasks
            
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise
    
    def get_task(self, task_id: str, include_subtasks: bool = True) -> Optional[Task]:
        """Get a task by ID, optionally including subtasks.
        
        Args:
            task_id: The task ID to retrieve
            include_subtasks: Whether to include subtasks in the response
            
        Returns:
            Task if found, None otherwise
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")
            
        try:
            logger.info(f"Retrieving task: {task_id}")
            task = self.storage.get_task(task_id)
            
            if task and include_subtasks:
                # Get subtasks (tasks where parent_id = task_id)
                all_project_tasks = self.storage.get_tasks_by_project(task.project_id)
                subtasks = [t for t in all_project_tasks if t.parent_id == task_id]
                logger.info(f"Retrieved task {task_id} with {len(subtasks)} subtasks")
                # Return task and subtasks as a tuple for service layer use
                return task, subtasks
            else:
                logger.info(f"Task {task_id} {'not found' if not task else 'found'}")
                
            return task
            
        except Exception as e:
            logger.error(f"Error retrieving task {task_id}: {e}")
            raise
    
    def create_task(self, task_create: TaskCreate, created_by: str) -> Task:
        """Create a new task with validation and hierarchy management.
        
        Args:
            task_create: Task creation data
            created_by: ID or name of the user creating the task
            
        Returns:
            The created task
            
        Raises:
            ValueError: If task data is invalid
        """
        if not created_by or not created_by.strip():
            raise ValueError("Created by field cannot be empty")
            
        try:
            logger.info(f"Creating task: {task_create.title}")
            
            # Validate task data and hierarchy
            self._validate_task_creation(task_create)
            
            # Create Task instance
            task = Task(
                **task_create.model_dump(),
                created_by=created_by
            )
            
            # Store in database
            created_task = self.storage.create_task(task)
            
            if not created_task:
                raise RuntimeError("Failed to create task in storage")
                
            logger.info(f"Successfully created task: {created_task.id}")
            return created_task
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise RuntimeError(f"Failed to create task: {str(e)}")
    
    def _validate_task_creation(self, task_create: TaskCreate) -> None:
        """Validate task creation data and hierarchy.
        
        Args:
            task_create: Task data to validate
            
        Raises:
            ValueError: If validation fails
        """
        # Basic validation
        if not task_create.title or not task_create.title.strip():
            raise ValueError("Task title cannot be empty")
            
        if len(task_create.title) > 255:
            raise ValueError("Task title cannot exceed 255 characters")
            
        if task_create.description and len(task_create.description) > 2000:
            raise ValueError("Task description cannot exceed 2000 characters")
        
        # Verify project exists
        project = self.storage.get_project(task_create.project_id)
        if not project:
            raise ValueError(f"Project with ID {task_create.project_id} not found")
        
        # Verify parent task exists if provided
        if task_create.parent_id:
            parent_task = self.storage.get_task(task_create.parent_id)
            if not parent_task:
                raise ValueError(f"Parent task with ID {task_create.parent_id} not found")
            if parent_task.project_id != task_create.project_id:
                raise ValueError("Parent task must be in the same project")
            
            # Check depth limit (prevent deeply nested hierarchies)
            if parent_task.depth >= 4:  # Allow up to 5 levels (0-4)
                raise ValueError("Task hierarchy cannot exceed 5 levels")
    
    def update_task(self, task_id: str, task_update: TaskUpdate) -> Optional[Task]:
        """Update an existing task with hierarchy validation.
        
        Args:
            task_id: ID of the task to update
            task_update: Update data
            
        Returns:
            Updated task if successful, None if task not found
            
        Raises:
            ValueError: If update data is invalid
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")
            
        try:
            logger.info(f"Updating task: {task_id}")
            
            # Get existing task
            existing_task = self.storage.get_task(task_id)
            if not existing_task:
                logger.info(f"Task {task_id} not found for update")
                return None
            
            # Create update data, excluding None values
            update_data = task_update.model_dump(exclude_none=True)
            
            # Validate update data and hierarchy
            self._validate_task_update(task_id, existing_task, update_data)
            
            # Create updated task by merging existing data with updates
            updated_task_data = existing_task.model_dump()
            updated_task_data.update(update_data)
            
            # Create new Task instance with updated data
            updated_task_instance = Task(**updated_task_data)
            
            # Update in storage
            updated_task = self.storage.update_task(task_id, updated_task_instance)
            
            if updated_task:
                logger.info(f"Successfully updated task: {task_id}")
            else:
                logger.error(f"Failed to update task in storage: {task_id}")
                
            return updated_task
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}")
            raise RuntimeError(f"Failed to update task: {str(e)}")
    
    def _validate_task_update(self, task_id: str, existing_task: Task, update_data: Dict[str, Any]) -> None:
        """Validate task update data and hierarchy.
        
        Args:
            task_id: ID of the task being updated
            existing_task: Current task data
            update_data: Update data to validate
            
        Raises:
            ValueError: If validation fails
        """
        if 'title' in update_data:
            title = update_data['title']
            if not title or not str(title).strip():
                raise ValueError("Task title cannot be empty")
            if len(str(title)) > 255:
                raise ValueError("Task title cannot exceed 255 characters")
                
        if 'description' in update_data and update_data['description']:
            description = update_data['description']
            if len(str(description)) > 2000:
                raise ValueError("Task description cannot exceed 2000 characters")
        
        # Verify parent task exists if being updated
        if 'parent_id' in update_data and update_data['parent_id']:
            parent_id = update_data['parent_id']
            parent_task = self.storage.get_task(parent_id)
            if not parent_task:
                raise ValueError(f"Parent task with ID {parent_id} not found")
            if parent_task.project_id != existing_task.project_id:
                raise ValueError("Parent task must be in the same project")
            
            # Prevent circular references
            if parent_id == task_id:
                raise ValueError("Task cannot be its own parent")
            
            # Check if the new parent would create a cycle
            if self._would_create_cycle(task_id, parent_id):
                raise ValueError("Parent assignment would create a circular dependency")
            
            # Check depth limit
            if parent_task.depth >= 4:
                raise ValueError("Task hierarchy cannot exceed 5 levels")
    
    def _would_create_cycle(self, task_id: str, new_parent_id: str) -> bool:
        """Check if assigning a new parent would create a circular dependency.
        
        Args:
            task_id: ID of the task being updated
            new_parent_id: ID of the proposed new parent
            
        Returns:
            True if a cycle would be created, False otherwise
        """
        # Walk up the hierarchy from the new parent to see if we encounter the task being updated
        current_id = new_parent_id
        visited = set()
        
        while current_id:
            if current_id == task_id:
                return True  # Cycle detected
            if current_id in visited:
                break  # Avoid infinite loop
            visited.add(current_id)
            
            current_task = self.storage.get_task(current_id)
            if not current_task:
                break
            current_id = current_task.parent_id
            
        return False
    
    def delete_task(self, task_id: str, cascade_subtasks: bool = True) -> bool:
        """Delete a task and optionally its subtasks.
        
        Args:
            task_id: ID of the task to delete
            cascade_subtasks: Whether to delete subtasks (default: True)
            
        Returns:
            True if deletion was successful, False if task not found
            
        Raises:
            RuntimeError: If deletion fails
        """
        if not task_id or not task_id.strip():
            raise ValueError("Task ID cannot be empty")
            
        try:
            logger.info(f"Deleting task: {task_id} (cascade_subtasks={cascade_subtasks})")
            
            # Check if task exists
            existing_task = self.storage.get_task(task_id)
            if not existing_task:
                logger.info(f"Task {task_id} not found for deletion")
                return False
            
            if cascade_subtasks:
                # Get and delete subtasks first
                subtasks = self._get_all_subtasks(task_id, existing_task.project_id)
                for subtask in subtasks:
                    self.storage.delete_task(subtask.id)
                logger.info(f"Deleted {len(subtasks)} subtasks of task {task_id}")
            
            # Delete the main task
            success = self.storage.delete_task(task_id)
            
            if success:
                logger.info(f"Successfully deleted task {task_id}")
            else:
                logger.error(f"Failed to delete task in storage: {task_id}")
                raise RuntimeError("Failed to delete task in storage")
                
            return success
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}")
            raise RuntimeError(f"Failed to delete task: {str(e)}")
    
    def _get_all_subtasks(self, task_id: str, project_id: str) -> List[Task]:
        """Recursively get all subtasks of a given task.
        
        Args:
            task_id: ID of the parent task
            project_id: ID of the project
            
        Returns:
            List of all subtasks (recursive)
        """
        all_project_tasks = self.storage.get_tasks_by_project(project_id)
        direct_subtasks = [t for t in all_project_tasks if t.parent_id == task_id]
        
        all_subtasks = []
        for subtask in direct_subtasks:
            all_subtasks.append(subtask)
            # Recursively get subtasks of this subtask
            all_subtasks.extend(self._get_all_subtasks(subtask.id, project_id))
            
        return all_subtasks
    
    def get_task_hierarchy(self, project_id: str) -> List[Task]:
        """Get all tasks for a project organized in hierarchical order.
        
        Args:
            project_id: ID of the project
            
        Returns:
            List of tasks ordered by hierarchy (parents before children)
        """
        try:
            logger.info(f"Getting task hierarchy for project: {project_id}")
            
            all_tasks = self.storage.get_tasks_by_project(project_id)
            
            # Organize tasks by hierarchy level
            root_tasks = [t for t in all_tasks if t.parent_id is None]
            ordered_tasks = []
            
            def add_task_and_children(task: Task, level: int = 0):
                """Recursively add task and its children to the ordered list."""
                task.depth = level  # Update depth for display
                ordered_tasks.append(task)
                
                # Find and add children
                children = [t for t in all_tasks if t.parent_id == task.id]
                children.sort(key=lambda x: x.created_at)  # Sort by creation time
                
                for child in children:
                    add_task_and_children(child, level + 1)
            
            # Add all root tasks and their hierarchies
            root_tasks.sort(key=lambda x: x.created_at)
            for root_task in root_tasks:
                add_task_and_children(root_task)
            
            logger.info(f"Retrieved hierarchical task list: {len(ordered_tasks)} tasks")
            return ordered_tasks
            
        except Exception as e:
            logger.error(f"Error getting task hierarchy for project {project_id}: {e}")
            raise
    
    def apply_task_patch(self, patch: TaskPatch) -> Optional[Task]:
        """Apply a task patch operation.
        
        Args:
            patch: Task patch to apply
            
        Returns:
            Result of the patch operation (Task for create/update, None for delete)
            
        Raises:
            ValueError: If patch data is invalid
            RuntimeError: If patch application fails
        """
        try:
            logger.info(f"Applying task patch: {patch.op}")
            
            result = self.storage.apply_task_patch(patch)
            
            if result:
                logger.info(f"Successfully applied task patch: {patch.op}")
            else:
                logger.warning(f"Task patch operation returned None: {patch.op}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error applying task patch: {e}")
            raise RuntimeError(f"Failed to apply task patch: {str(e)}")