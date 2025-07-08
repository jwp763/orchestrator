from datetime import datetime, date
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class TaskStatus(str, Enum):
    """
    Enumeration of possible task status values.
    
    Represents the current state of a task in its lifecycle from
    creation to completion or cancellation.
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, Enum):
    """
    Enumeration of task priority levels.
    
    Used to indicate the relative importance and urgency of tasks
    for scheduling and resource allocation decisions.
    """
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    BACKLOG = "backlog"


class TaskBase(BaseModel):
    """
    Base model for task data with hierarchical support.
    
    Provides the core fields and validation for task management including
    hierarchical parent-child relationships, time tracking, dependencies,
    and integration with external task management systems.
    
    Features:
    - Hierarchical task structure with parent-child relationships
    - Time estimation and tracking in minutes
    - Dependency management for task ordering
    - Integration IDs for external systems (Motion, Linear, GitLab, Notion)
    - Flexible metadata and labeling system
    
    Validation:
    - Estimated/actual minutes must be positive/non-negative
    - Task depth limited to 5 levels maximum
    - Dependencies must be valid task ID strings
    """
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Detailed task description")
    project_id: str = Field(..., description="Parent project ID")
    status: TaskStatus = Field(TaskStatus.TODO, description="Current task status")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority")
    
    # Hierarchical fields
    parent_id: Optional[str] = Field(None, description="References parent task ID")
    estimated_minutes: Optional[int] = Field(None, description="Time estimate in minutes")
    actual_minutes: Optional[int] = Field(None, description="Actual time spent in minutes")
    depth: int = Field(0, description="Tree depth (0 = root task)")
    dependencies: List[str] = Field(default_factory=list, description="Task IDs that must complete first")
    
    # Scheduling
    due_date: Optional[date] = Field(None, description="Task due date")
    
    # Assignment
    assignee: Optional[str] = Field(None, description="Assigned to")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    labels: List[str] = Field(default_factory=list, description="Task labels")
    
    # Integration references
    motion_task_id: Optional[str] = Field(None, description="Motion task ID")
    linear_issue_id: Optional[str] = Field(None, description="Linear issue ID")
    notion_task_id: Optional[str] = Field(None, description="Notion task ID")
    gitlab_issue_id: Optional[str] = Field(None, description="GitLab issue ID")
    
    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('estimated_minutes')
    def validate_estimated_minutes(cls, v):
        """
        Validate that estimated_minutes is positive when provided.
        
        Args:
            v: The estimated_minutes value to validate
            
        Returns:
            int: The validated value
            
        Raises:
            ValueError: If estimated_minutes is not positive
        """
        if v is not None and v <= 0:
            raise ValueError('estimated_minutes must be positive')
        return v
    
    @validator('actual_minutes')
    def validate_actual_minutes(cls, v):
        """
        Validate that actual_minutes is non-negative when provided.
        
        Args:
            v: The actual_minutes value to validate
            
        Returns:
            int: The validated value
            
        Raises:
            ValueError: If actual_minutes is negative
        """
        if v is not None and v < 0:
            raise ValueError('actual_minutes cannot be negative')
        return v
    
    @validator('depth')
    def validate_depth(cls, v):
        """
        Validate that task depth is within allowed range (0-5).
        
        Args:
            v: The depth value to validate
            
        Returns:
            int: The validated depth value
            
        Raises:
            ValueError: If depth is negative or exceeds 5 levels
        """
        if v < 0:
            raise ValueError('depth cannot be negative')
        if v > 5:
            raise ValueError('depth cannot exceed 5 levels')
        return v
    
    @validator('dependencies')
    def validate_dependencies(cls, v):
        """
        Validate that dependency IDs are valid non-empty strings.
        
        Args:
            v: List of dependency task IDs to validate
            
        Returns:
            List[str]: The validated dependency list
            
        Raises:
            ValueError: If any dependency ID is empty or not a string
        """
        if v:
            for dep_id in v:
                if not isinstance(dep_id, str) or not dep_id.strip():
                    raise ValueError('dependency IDs must be non-empty strings')
        return v
    
    @property
    def estimated_hours(self) -> Optional[float]:
        """
        Convert estimated_minutes to hours for display purposes.
        
        Returns:
            Optional[float]: Estimated time in hours (minutes / 60), 
                           or None if estimated_minutes is not set
                           
        Example:
            >>> task.estimated_minutes = 90
            >>> task.estimated_hours
            1.5
        """
        if self.estimated_minutes is not None:
            return self.estimated_minutes / 60.0
        return None
    
    @property
    def actual_hours(self) -> Optional[float]:
        """
        Convert actual_minutes to hours for display purposes.
        
        Returns:
            Optional[float]: Actual time spent in hours (minutes / 60),
                           or None if actual_minutes is not set
                           
        Example:
            >>> task.actual_minutes = 120
            >>> task.actual_hours
            2.0
        """
        if self.actual_minutes is not None:
            return self.actual_minutes / 60.0
        return None


class TaskCreate(TaskBase):
    """
    Model for creating new tasks.
    
    Inherits all fields from TaskBase without requiring ID or timestamps,
    which are generated automatically by the storage layer.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Model for updating existing tasks.
    
    All fields are optional to allow partial updates. Includes the same
    validation as TaskBase for fields that are provided.
    """
    title: Optional[str] = None
    description: Optional[str] = None
    project_id: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    
    # Hierarchical fields
    parent_id: Optional[str] = None
    estimated_minutes: Optional[int] = None
    actual_minutes: Optional[int] = None
    depth: Optional[int] = None
    dependencies: Optional[List[str]] = None
    
    # Scheduling
    due_date: Optional[date] = None
    
    # Assignment
    assignee: Optional[str] = None
    tags: Optional[List[str]] = None
    labels: Optional[List[str]] = None
    
    # Integration references
    motion_task_id: Optional[str] = None
    linear_issue_id: Optional[str] = None
    notion_task_id: Optional[str] = None
    gitlab_issue_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    @validator('estimated_minutes')
    def validate_estimated_minutes(cls, v):
        if v is not None and v <= 0:
            raise ValueError('estimated_minutes must be positive')
        return v
    
    @validator('actual_minutes')
    def validate_actual_minutes(cls, v):
        if v is not None and v < 0:
            raise ValueError('actual_minutes cannot be negative')
        return v
    
    @validator('depth')
    def validate_depth(cls, v):
        if v is not None and (v < 0 or v > 5):
            raise ValueError('depth must be between 0 and 5')
        return v


class Task(TaskBase):
    """
    Complete task model with database fields and validation methods.
    
    Extends TaskBase with database-specific fields like ID, timestamps,
    and computed fields. Includes methods for validating hierarchical
    relationships and preventing circular dependencies.
    
    Additional Fields:
    - id: Unique identifier generated by storage layer
    - created_at/updated_at: Automatic timestamp management
    - completed_at: Set when task status changes to completed
    - created_by: User who created the task
    - is_overdue/days_until_due: Computed scheduling fields
    """
    id: str = Field(..., description="Unique task ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_by: str = Field(..., description="Creator ID or name")
    
    
    # Computed fields
    is_overdue: bool = Field(False, description="Whether task is overdue")
    days_until_due: Optional[int] = Field(None, description="Days until due date")
    
    def validate_parent_not_self(self):
        """
        Validate that a task is not set as its own parent.
        
        Raises:
            ValueError: If parent_id equals the task's own ID
        """
        if self.parent_id == self.id:
            raise ValueError("Task cannot be its own parent")
    
    def validate_no_circular_dependencies(self, all_tasks: List['Task']):
        """
        Validate that task dependencies don't create circular references.
        
        Performs a depth-first search through the dependency graph to detect
        cycles that would prevent proper task scheduling.
        
        Args:
            all_tasks (List[Task]): Complete list of tasks to check against
            
        Raises:
            ValueError: If a circular dependency is detected
            
        Example:
            >>> tasks = [task1, task2, task3]  # task1 depends on task2, task2 on task3
            >>> task1.validate_no_circular_dependencies(tasks)  # OK
            >>> task3.dependencies = [task1.id]  # Creates cycle
            >>> task1.validate_no_circular_dependencies(tasks)  # Raises ValueError
        """
        if not self.dependencies:
            return
        
        visited = set()
        stack = list(self.dependencies)
        
        while stack:
            dep_id = stack.pop()
            if dep_id == self.id:
                raise ValueError(f"Circular dependency detected: task depends on itself")
            if dep_id in visited:
                continue
            visited.add(dep_id)
            
            # Find the dependency task and check its dependencies
            dep_task = next((t for t in all_tasks if t.id == dep_id), None)
            if dep_task and dep_task.dependencies:
                stack.extend(dep_task.dependencies)
    
    @property
    def is_parent(self) -> bool:
        """
        Check if this task has child tasks.
        
        Note: This is a placeholder property. The actual implementation
        requires a database query to check for tasks with this task's ID
        as their parent_id.
        
        Returns:
            bool: True if task has children, False otherwise
            
        Todo:
            Implement database query: SELECT COUNT(*) FROM tasks WHERE parent_id = self.id
        """
        # This is a placeholder - actual implementation would require database query
        return False
    
    @property
    def total_estimated_minutes(self) -> Optional[int]:
        """
        Calculate total estimated time including all descendants.
        
        Note: This is a placeholder property. The actual implementation
        requires a recursive database query to sum estimated_minutes
        for this task and all its descendants.
        
        Returns:
            Optional[int]: Total estimated minutes for task tree,
                         or None if no estimate available
                         
        Todo:
            Implement recursive calculation of self + all descendant estimates
        """
        # This is a placeholder - actual implementation would require recursive database query
        return self.estimated_minutes
    
    class Config:
        from_attributes = True