"""Tools available to the orchestrator agent"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from ..models import (
    ProjectCreate, TaskCreate, 
    ProjectUpdate, TaskUpdate,
    ProjectStatus, TaskStatus, TaskPriority
)


class CreateProjectTool(BaseModel):
    """Tool for creating a new project"""
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    due_date: Optional[date] = Field(None, description="Project due date")
    start_date: Optional[date] = Field(None, description="Project start date")
    priority: int = Field(3, ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    status: ProjectStatus = Field(ProjectStatus.PLANNING)
    tags: List[str] = Field(default_factory=list)
    integration: Optional[str] = Field(None, description="Primary integration (motion/linear/notion/gitlab)")


class CreateTaskTool(BaseModel):
    """Tool for creating a new task"""
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    project_id: str = Field(..., description="Project ID or name")
    due_date: Optional[date] = Field(None, description="Task due date")
    estimated_hours: Optional[float] = Field(None, description="Estimated hours")
    priority: TaskPriority = Field(TaskPriority.MEDIUM)
    status: TaskStatus = Field(TaskStatus.TODO)
    assignee: Optional[str] = Field(None, description="Assignee name or ID")
    tags: List[str] = Field(default_factory=list)
    integration: Optional[str] = Field(None, description="Primary integration")


class UpdateProjectTool(BaseModel):
    """Tool for updating an existing project"""
    project_id: str = Field(..., description="Project ID or name to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class UpdateTaskTool(BaseModel):
    """Tool for updating an existing task"""
    task_id: str = Field(..., description="Task ID or title to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class QueryTool(BaseModel):
    """Tool for querying projects and tasks"""
    query_type: str = Field(..., description="Type: 'projects', 'tasks', 'overview'")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")
    integration: Optional[str] = Field(None, description="Specific integration to query")


class SyncTool(BaseModel):
    """Tool for syncing with external integrations"""
    integration: str = Field(..., description="Integration to sync: motion/linear/gitlab/notion")
    sync_type: str = Field("bidirectional", description="Sync type: pull/push/bidirectional")
    project_ids: Optional[List[str]] = Field(None, description="Specific projects to sync")


class AgentTools:
    """Collection of all available tools"""
    
    @staticmethod
    def get_all_tools():
        return {
            "create_project": CreateProjectTool,
            "create_task": CreateTaskTool,
            "update_project": UpdateProjectTool,
            "update_task": UpdateTaskTool,
            "query": QueryTool,
            "sync": SyncTool
        }
    
    @staticmethod
    def parse_tool_call(tool_name: str, parameters: Dict[str, Any]):
        """Parse and validate a tool call"""
        tools = AgentTools.get_all_tools()
        if tool_name not in tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        tool_class = tools[tool_name]
        return tool_class(**parameters)