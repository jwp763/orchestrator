"""Task management API routes."""

import logging
from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.responses import JSONResponse

from .models import (
    TaskResponse, TaskWithSubtasksResponse, TaskListResponse,
    TaskCreateRequest, TaskUpdateRequest, ErrorResponse
)
from ..models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
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


def task_to_response(task: Task) -> TaskResponse:
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


def task_with_subtasks_to_response(task: Task, subtasks: List[Task]) -> TaskWithSubtasksResponse:
    """Convert Task with subtasks to TaskWithSubtasksResponse."""
    return TaskWithSubtasksResponse(
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
        gitlab_issue_id=task.gitlab_issue_id,
        subtasks=[task_to_response(subtask) for subtask in subtasks]
    )


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    skip: int = Query(0, ge=0, description="Number of tasks to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tasks to return"),
    project_id: Optional[str] = Query(None, description="Filter by project ID"),
    parent_id: Optional[str] = Query(None, description="Filter by parent task ID"),
    task_status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    status_alias: Optional[TaskStatus] = Query(None, alias="status", description="Filter by task status (alias for task_status)"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by task priority"),
    assignee: Optional[str] = Query(None, description="Filter by assignee"),
    search: Optional[str] = Query(None, description="Search in task title and description"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    created_after: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    created_before: Optional[str] = Query(None, description="Filter by creation date (ISO format)"),
    sort_by: str = Query("created_at", description="Sort by field (created_at, updated_at, title, priority)"),
    sort_order: str = Query("desc", description="Sort order (asc, desc)"),
    storage: StorageInterface = Depends(get_storage)
):
    """
    List all tasks with advanced filtering, searching, and pagination.
    
    Returns a paginated list of tasks with comprehensive filtering and sorting options.
    """
    try:
        logger.info(f"Listing tasks with skip={skip}, limit={limit}, project_id={project_id}, search='{search}'")
        
        # Parse tags if provided
        tag_list = None
        if tags:
            tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
        
        # Parse date filters if provided
        created_after_dt = None
        created_before_dt = None
        if created_after:
            try:
                created_after_dt = datetime.fromisoformat(created_after.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid created_after date format: {created_after}"
                )
        if created_before:
            try:
                created_before_dt = datetime.fromisoformat(created_before.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Invalid created_before date format: {created_before}"
                )
        
        # Validate sort parameters
        valid_sort_fields = ["created_at", "updated_at", "title", "priority", "status"]
        if sort_by not in valid_sort_fields:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid sort_by field. Must be one of: {', '.join(valid_sort_fields)}"
            )
        
        if sort_order.lower() not in ["asc", "desc"]:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid sort_order. Must be 'asc' or 'desc'"
            )
        
        # Use the new enhanced list_tasks method
        # Use status_alias parameter if provided, otherwise use task_status
        status_filter = status_alias or task_status
        result = storage.list_tasks(
            skip=skip,
            limit=limit,
            project_id=project_id,
            status=status_filter.value if status_filter else None,
            priority=priority.value if priority else None,
            assignee=assignee,
            parent_id=parent_id,
            search=search,
            tags=tag_list,
            created_after=created_after_dt,
            created_before=created_before_dt,
            sort_by=sort_by,
            sort_order=sort_order
        )
        
        return TaskListResponse(
            tasks=[task_to_response(t) for t in result["tasks"]],
            total=result["total"],
            page=result["page"],
            per_page=result["per_page"],
            has_next=result["has_next"],
            has_prev=result["has_prev"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tasks: {str(e)}"
        )


@router.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_request: TaskCreateRequest,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Create a new task.
    
    Creates a new task with the provided data and returns the created task.
    """
    try:
        logger.info(f"Creating task: {task_request.title}")
        
        # Verify project exists
        project = storage.get_project(task_request.project_id)
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project with ID {task_request.project_id} not found"
            )
        
        # Verify parent task exists if provided
        if task_request.parent_id:
            parent_task = storage.get_task(task_request.parent_id)
            if not parent_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent task with ID {task_request.parent_id} not found"
                )
            if parent_task.project_id != task_request.project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent task must be in the same project"
                )
        
        # Convert request to TaskCreate model
        task_create = TaskCreate(
            project_id=task_request.project_id,
            parent_id=task_request.parent_id,
            title=task_request.title,
            description=task_request.description,
            status=task_request.status,
            priority=task_request.priority,
            tags=task_request.tags,
            estimated_minutes=task_request.estimated_minutes,
            due_date=datetime.fromisoformat(task_request.due_date).date() if task_request.due_date else None,
            assignee=task_request.assignee,
            dependencies=task_request.dependencies,
            metadata=task_request.metadata,
            motion_task_id=task_request.motion_task_id,
            linear_issue_id=task_request.linear_issue_id,
            notion_task_id=task_request.notion_task_id,
            gitlab_issue_id=task_request.gitlab_issue_id
        )
        
        # Create Task instance
        task = Task(
            **task_create.model_dump(),
            created_by=task_request.created_by
        )
        
        # Store in database
        created_task = storage.create_task(task)
        
        if not created_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task"
            )
        
        logger.info(f"Successfully created task: {created_task.id}")
        return task_to_response(created_task)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskWithSubtasksResponse)
async def get_task(
    task_id: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Get a task by ID with its subtasks.
    
    Returns the task details including all subtasks.
    """
    try:
        logger.info(f"Getting task: {task_id}")
        
        task = storage.get_task(task_id)
        if not task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Get subtasks (tasks where parent_id = task_id)
        all_project_tasks = storage.get_tasks_by_project(task.project_id)
        subtasks = [t for t in all_project_tasks if t.parent_id == task_id]
        
        return task_with_subtasks_to_response(task, subtasks)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task: {str(e)}"
        )


@router.put("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_update: TaskUpdateRequest,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Update an existing task.
    
    Updates the task with the provided data. Only provided fields are updated.
    """
    try:
        logger.info(f"Updating task: {task_id}")
        
        # Get existing task
        existing_task = storage.get_task(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Create update data, excluding None values
        update_data = task_update.model_dump(exclude_none=True)
        
        # Verify parent task exists if provided
        if 'parent_id' in update_data and update_data['parent_id']:
            parent_task = storage.get_task(update_data['parent_id'])
            if not parent_task:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent task with ID {update_data['parent_id']} not found"
                )
            if parent_task.project_id != existing_task.project_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent task must be in the same project"
                )
        
        # Convert date strings to date objects
        if 'due_date' in update_data and update_data['due_date']:
            update_data['due_date'] = datetime.fromisoformat(update_data['due_date']).date()
        
        # Create updated task by merging existing data with updates
        updated_task_data = existing_task.model_dump()
        updated_task_data.update(update_data)
        
        # Create new Task instance with updated data
        updated_task_instance = Task(**updated_task_data)
        
        # Update task
        updated_task = storage.update_task(task_id, updated_task_instance)
        
        if not updated_task:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task"
            )
        
        logger.info(f"Successfully updated task: {task_id}")
        return task_to_response(updated_task)
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error updating task: {e}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid date format: {str(e)}"
        )
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task: {str(e)}"
        )


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: str,
    storage: StorageInterface = Depends(get_storage)
):
    """
    Delete a task by ID.
    
    Deletes the task and all subtasks. This operation cannot be undone.
    """
    try:
        logger.info(f"Deleting task: {task_id}")
        
        # Check if task exists
        existing_task = storage.get_task(task_id)
        if not existing_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task with ID {task_id} not found"
            )
        
        # Delete task (should cascade to subtasks)
        success = storage.delete_task(task_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete task"
            )
        
        logger.info(f"Successfully deleted task: {task_id}")
        return None
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task: {str(e)}"
        )