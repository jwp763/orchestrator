"""Project management API routes."""

import logging
from typing import List, Optional
from datetime import datetime, date

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse

from .models import (
    ProjectResponse, ProjectWithTasksResponse, ProjectListResponse,
    ProjectCreateRequest, ProjectUpdateRequest, TaskResponse, ErrorResponse
)
from ..models.project import Project, ProjectCreate, ProjectUpdate, ProjectStatus, ProjectPriority
from ..storage.interface import StorageInterface
from ..storage.sql_implementation import SQLStorage

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Dependency to get storage instance
def get_storage() -> StorageInterface:
    """Get storage instance."""
    return SQLStorage()


def project_to_response(project: Project) -> ProjectResponse:
    """Convert Project model to ProjectResponse."""
    return ProjectResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        priority=project.priority,
        tags=project.tags,
        due_date=project.due_date.isoformat() if project.due_date else None,
        start_date=project.start_date.isoformat() if project.start_date else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        created_by=project.created_by,
        task_count=project.task_count,
        completed_task_count=project.completed_task_count,
        motion_project_id=project.motion_project_id,
        linear_project_id=project.linear_project_id,
        notion_page_id=project.notion_page_id,
        gitlab_project_id=project.gitlab_project_id
    )


def task_to_response(task) -> TaskResponse:
    """Convert Task model to TaskResponse."""
    return TaskResponse(
        id=task.id,
        project_id=task.project_id,
        parent_id=task.parent_id,
        title=task.title,
        description=task.description,
        status=task.status,
        priority=task.priority,
        tags=task.tags,
        estimated_minutes=task.estimated_minutes,
        actual_minutes=task.actual_minutes or 0,
        due_date=task.due_date.isoformat() if task.due_date else None,
        assignee=task.assignee,
        depth=task.depth,
        sort_order=0,
        completion_percentage=0,
        dependencies=task.dependencies,
        attachments=[],
        notes=None,
        metadata=task.metadata,
        created_at=task.created_at.isoformat(),
        updated_at=task.updated_at.isoformat(),
        created_by=task.created_by,
        motion_task_id=task.motion_task_id,
        linear_issue_id=task.linear_issue_id,
        notion_task_id=task.notion_task_id,
        gitlab_issue_id=task.gitlab_issue_id
    )


def project_with_tasks_to_response(project: Project) -> ProjectWithTasksResponse:
    """Convert Project with tasks to ProjectWithTasksResponse."""
    return ProjectWithTasksResponse(
        id=project.id,
        name=project.name,
        description=project.description,
        status=project.status,
        priority=project.priority,
        tags=project.tags,
        due_date=project.due_date.isoformat() if project.due_date else None,
        start_date=project.start_date.isoformat() if project.start_date else None,
        created_at=project.created_at.isoformat(),
        updated_at=project.updated_at.isoformat(),
        created_by=project.created_by,
        task_count=project.task_count,
        completed_task_count=project.completed_task_count,
        motion_project_id=project.motion_project_id,
        linear_project_id=project.linear_project_id,
        notion_page_id=project.notion_page_id,
        gitlab_project_id=project.gitlab_project_id,
        tasks=[task_to_response(task) for task in project.tasks]
    )


@router.get("/projects", response_model=ProjectListResponse)
async def list_projects(
    skip: int = Query(0, ge=0, description="Number of projects to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of projects to return"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    priority: Optional[ProjectPriority] = Query(None, description="Filter by project priority"),
    storage: StorageInterface = Depends(get_storage)
):
    """
    List all projects with optional filtering and pagination.
    
    Returns a paginated list of projects with optional filtering by status and priority.
    """
    try:
        logger.info(f"Listing projects with skip={skip}, limit={limit}, status={status}, priority={priority}")
        
        # Get all projects from storage
        all_projects = storage.get_projects()
        
        # Apply filters
        filtered_projects = all_projects
        if status:
            filtered_projects = [p for p in filtered_projects if p.status == status]
        if priority:
            filtered_projects = [p for p in filtered_projects if p.priority == priority]
        
        # Apply pagination
        total = len(filtered_projects)
        projects = filtered_projects[skip:skip + limit]
        
        # Calculate pagination info
        page = (skip // limit) + 1
        has_next = skip + limit < total
        has_prev = skip > 0
        
        return ProjectListResponse(
            projects=[project_to_response(p) for p in projects],
            total=total,
            page=page,
            per_page=limit,
            has_next=has_next,
            has_prev=has_prev
        )
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_request: ProjectCreateRequest,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Create a new project.
    
    Creates a new project with the provided data and returns the created project.
    """
    try:
        logger.info(f"Creating project: {project_request.name}")
        
        # Convert request to ProjectCreate model
        project_create = ProjectCreate(
            name=project_request.name,
            description=project_request.description,
            status=project_request.status,
            priority=project_request.priority,
            tags=project_request.tags,
            due_date=datetime.fromisoformat(project_request.due_date).date() if project_request.due_date else None,
            start_date=datetime.fromisoformat(project_request.start_date).date() if project_request.start_date else None,
            motion_project_id=project_request.motion_project_id,
            linear_project_id=project_request.linear_project_id,
            notion_page_id=project_request.notion_page_id,
            gitlab_project_id=project_request.gitlab_project_id
        )
        
        # Create Project instance
        project = Project(
            **project_create.model_dump(),
            created_by=project_request.created_by
        )
        
        # Store in database
        created_project = storage.create_project(project)
        
        if not created_project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project"
            )
        
        logger.info(f"Successfully created project: {created_project.id}")
        return project_to_response(created_project)
        
    except ValueError as e:
        logger.error(f"Validation error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/projects/{project_id}", response_model=ProjectWithTasksResponse)
async def get_project(
    project_id: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Get a project by ID with its tasks.
    
    Returns the project details including all associated tasks.
    """
    try:
        logger.info(f"Getting project: {project_id}")
        
        project = storage.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get tasks for this project
        tasks = storage.get_tasks_by_project(project_id)
        project.tasks = tasks
        
        return project_with_tasks_to_response(project)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put("/projects/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_update: ProjectUpdateRequest,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Update an existing project.
    
    Updates the project with the provided data. Only provided fields are updated.
    """
    try:
        logger.info(f"Updating project: {project_id}")
        
        # Get existing project
        existing_project = storage.get_project(project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Create update data, excluding None values
        update_data = project_update.model_dump(exclude_none=True)
        
        # Convert date strings to date objects
        if 'due_date' in update_data and update_data['due_date']:
            update_data['due_date'] = datetime.fromisoformat(update_data['due_date']).date()
        if 'start_date' in update_data and update_data['start_date']:
            update_data['start_date'] = datetime.fromisoformat(update_data['start_date']).date()
        
        # Create updated project by merging existing data with updates
        updated_project_data = existing_project.model_dump()
        updated_project_data.update(update_data)
        
        # Create new Project instance with updated data
        updated_project_instance = Project(**updated_project_data)
        
        # Update project
        updated_project = storage.update_project(project_id, updated_project_instance)
        
        if not updated_project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project"
            )
        
        logger.info(f"Successfully updated project: {project_id}")
        return project_to_response(updated_project)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating project: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Delete a project by ID.
    
    Deletes the project and all associated tasks. This operation cannot be undone.
    """
    try:
        logger.info(f"Deleting project: {project_id}")
        
        # Check if project exists
        existing_project = storage.get_project(project_id)
        if not existing_project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Delete project (should cascade to tasks)
        success = storage.delete_project(project_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete project"
            )
        
        logger.info(f"Successfully deleted project: {project_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def get_project_tasks(
    project_id: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Get all tasks for a project.
    
    Returns all tasks associated with the specified project.
    """
    try:
        logger.info(f"Getting tasks for project: {project_id}")
        
        # Check if project exists
        project = storage.get_project(project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {project_id} not found"
            )
        
        # Get tasks
        tasks = storage.get_tasks_by_project(project_id)
        
        return [task_to_response(task) for task in tasks]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting tasks for project {project_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project tasks: {str(e)}"
        )