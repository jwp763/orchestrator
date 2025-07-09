"""Project service for business logic and orchestration."""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime

from ..models.project import Project, ProjectCreate, ProjectUpdate, ProjectStatus, ProjectPriority
from ..models.patch import Patch, ProjectPatch, Op
from ..storage.interface import StorageInterface
from ..storage.sql_implementation import SQLStorage

logger = logging.getLogger(__name__)


class ProjectService:
    """Service class for project-related business logic and operations.
    
    Handles project operations with business rule validation, transaction management,
    and coordination between storage and other system components.
    """
    
    def __init__(self, storage: Optional[StorageInterface] = None):
        """Initialize the project service.
        
        Args:
            storage: Storage interface implementation. Defaults to SQLStorage if not provided.
        """
        self.storage = storage or SQLStorage()
    
    def list_projects(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[ProjectStatus] = None,
        priority: Optional[ProjectPriority] = None
    ) -> List[Project]:
        """List projects with optional filtering.
        
        Args:
            skip: Number of projects to skip for pagination
            limit: Maximum number of projects to return  
            status: Filter by project status
            priority: Filter by project priority
            
        Returns:
            List of projects matching the criteria
            
        Raises:
            ValueError: If pagination parameters are invalid
        """
        if skip < 0:
            raise ValueError("Skip parameter must be non-negative")
        if limit <= 0 or limit > 1000:
            raise ValueError("Limit must be between 1 and 1000")
            
        try:
            logger.info(f"Listing projects: skip={skip}, limit={limit}, status={status}, priority={priority}")
            
            # Get all projects from storage
            all_projects = self.storage.get_projects()
            
            # Apply filters
            filtered_projects = all_projects
            if status:
                filtered_projects = [p for p in filtered_projects if p.status == status]
            if priority:
                filtered_projects = [p for p in filtered_projects if p.priority == priority]
            
            # Apply pagination
            projects = filtered_projects[skip:skip + limit]
            
            logger.info(f"Retrieved {len(projects)} projects (filtered from {len(all_projects)} total)")
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            raise
    
    def get_project(self, project_id: str) -> Optional[Project]:
        """Get a project by ID.
        
        Args:
            project_id: The project ID to retrieve
            
        Returns:
            Project if found, None otherwise
        """
        if not project_id or not project_id.strip():
            raise ValueError("Project ID cannot be empty")
            
        try:
            logger.info(f"Retrieving project: {project_id}")
            project = self.storage.get_project(project_id)
            
            if project:
                # Get associated tasks for the project
                tasks = self.storage.get_tasks_by_project(project_id)
                project.tasks = tasks
                logger.info(f"Retrieved project {project_id} with {len(tasks)} tasks")
            else:
                logger.info(f"Project {project_id} not found")
                
            return project
            
        except Exception as e:
            logger.error(f"Error retrieving project {project_id}: {e}")
            raise
    
    def create_project(self, project_create: ProjectCreate, created_by: str) -> Project:
        """Create a new project.
        
        Args:
            project_create: Project creation data
            created_by: ID or name of the user creating the project
            
        Returns:
            The created project
            
        Raises:
            ValueError: If project data is invalid
        """
        if not created_by or not created_by.strip():
            raise ValueError("Created by field cannot be empty")
            
        try:
            logger.info(f"Creating project: {project_create.name}")
            
            # Validate project data
            self._validate_project_data(project_create)
            
            # Create Project instance
            project = Project(
                **project_create.model_dump(),
                created_by=created_by
            )
            
            # Store in database
            created_project = self.storage.create_project(project)
            
            if not created_project:
                raise RuntimeError("Failed to create project in storage")
                
            logger.info(f"Successfully created project: {created_project.id}")
            return created_project
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating project: {e}")
            raise RuntimeError(f"Failed to create project: {str(e)}")
    
    def update_project(self, project_id: str, project_update: ProjectUpdate) -> Optional[Project]:
        """Update an existing project.
        
        Args:
            project_id: ID of the project to update
            project_update: Update data
            
        Returns:
            Updated project if successful, None if project not found
            
        Raises:
            ValueError: If update data is invalid
        """
        if not project_id or not project_id.strip():
            raise ValueError("Project ID cannot be empty")
            
        try:
            logger.info(f"Updating project: {project_id}")
            
            # Get existing project
            existing_project = self.storage.get_project(project_id)
            if not existing_project:
                logger.info(f"Project {project_id} not found for update")
                return None
            
            # Create update data, excluding None values
            update_data = project_update.model_dump(exclude_none=True)
            
            # Validate update data
            self._validate_project_update(update_data)
            
            # Create updated project by merging existing data with updates
            updated_project_data = existing_project.model_dump()
            updated_project_data.update(update_data)
            
            # Create new Project instance with updated data
            updated_project_instance = Project(**updated_project_data)
            
            # Update in storage
            updated_project = self.storage.update_project(project_id, updated_project_instance)
            
            if updated_project:
                logger.info(f"Successfully updated project: {project_id}")
            else:
                logger.error(f"Failed to update project in storage: {project_id}")
                
            return updated_project
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            raise RuntimeError(f"Failed to update project: {str(e)}")
    
    def delete_project(self, project_id: str) -> bool:
        """Delete a project and all associated tasks.
        
        Args:
            project_id: ID of the project to delete
            
        Returns:
            True if deletion was successful, False if project not found
            
        Raises:
            RuntimeError: If deletion fails
        """
        if not project_id or not project_id.strip():
            raise ValueError("Project ID cannot be empty")
            
        try:
            logger.info(f"Deleting project: {project_id}")
            
            # Check if project exists
            existing_project = self.storage.get_project(project_id)
            if not existing_project:
                logger.info(f"Project {project_id} not found for deletion")
                return False
            
            # Get associated tasks for logging
            tasks = self.storage.get_tasks_by_project(project_id)
            task_count = len(tasks)
            
            # Delete project (should cascade to tasks)
            success = self.storage.delete_project(project_id)
            
            if success:
                logger.info(f"Successfully deleted project {project_id} and {task_count} associated tasks")
            else:
                logger.error(f"Failed to delete project in storage: {project_id}")
                raise RuntimeError("Failed to delete project in storage")
                
            return success
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting project {project_id}: {e}")
            raise RuntimeError(f"Failed to delete project: {str(e)}")
    
    def apply_project_patch(self, patch: ProjectPatch) -> Optional[Project]:
        """Apply a project patch operation.
        
        Args:
            patch: Project patch to apply
            
        Returns:
            Result of the patch operation (Project for create/update, None for delete)
            
        Raises:
            ValueError: If patch data is invalid
            RuntimeError: If patch application fails
        """
        try:
            logger.info(f"Applying project patch: {patch.op}")
            
            result = self.storage.apply_project_patch(patch)
            
            if result:
                logger.info(f"Successfully applied project patch: {patch.op}")
            else:
                logger.warning(f"Project patch operation returned None: {patch.op}")
                
            return result
            
        except Exception as e:
            logger.error(f"Error applying project patch: {e}")
            raise RuntimeError(f"Failed to apply project patch: {str(e)}")
    
    def _validate_project_data(self, project_data) -> None:
        """Validate project creation data.
        
        Args:
            project_data: Project data to validate
            
        Raises:
            ValueError: If validation fails
        """
        if not project_data.name or not project_data.name.strip():
            raise ValueError("Project name cannot be empty")
            
        if len(project_data.name) > 255:
            raise ValueError("Project name cannot exceed 255 characters")
            
        if project_data.description and len(project_data.description) > 2000:
            raise ValueError("Project description cannot exceed 2000 characters")
    
    def _validate_project_update(self, update_data: Dict[str, Any]) -> None:
        """Validate project update data.
        
        Args:
            update_data: Update data to validate
            
        Raises:
            ValueError: If validation fails
        """
        if 'name' in update_data:
            name = update_data['name']
            if not name or not str(name).strip():
                raise ValueError("Project name cannot be empty")
            if len(str(name)) > 255:
                raise ValueError("Project name cannot exceed 255 characters")
                
        if 'description' in update_data and update_data['description']:
            description = update_data['description']
            if len(str(description)) > 2000:
                raise ValueError("Project description cannot exceed 2000 characters")