"""Tools available to the orchestrator agent"""

from typing import Dict, Any, List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

from ..models import ProjectCreate, TaskCreate, ProjectUpdate, TaskUpdate, ProjectStatus, TaskStatus, TaskPriority


class CreateProjectTool(BaseModel):
    """
    Tool for creating a new project through the AI agent.

    Provides structured parameters for project creation with validation
    and integration support. Used by the agent to translate natural
    language requests into database operations.
    """

    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    due_date: Optional[date] = Field(None, description="Project due date")
    start_date: Optional[date] = Field(None, description="Project start date")
    priority: int = Field(3, ge=1, le=5, description="Priority (1=highest, 5=lowest)")
    status: ProjectStatus = Field(ProjectStatus.PLANNING)
    tags: List[str] = Field(default_factory=list)
    integration: Optional[str] = Field(None, description="Primary integration (motion/linear/notion/gitlab)")


class CreateTaskTool(BaseModel):
    """
    Tool for creating a new task through the AI agent.

    Supports hierarchical task creation with time estimation,
    assignment, and integration synchronization. Maps natural
    language task descriptions to structured data.
    """

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
    """
    Tool for updating existing projects through the AI agent.

    Enables partial updates to project fields with flexible
    parameter structure for any valid project attribute.
    """

    project_id: str = Field(..., description="Project ID or name to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class UpdateTaskTool(BaseModel):
    """
    Tool for updating existing tasks through the AI agent.

    Supports partial updates including status changes, time tracking,
    assignment modifications, and hierarchical restructuring.
    """

    task_id: str = Field(..., description="Task ID or title to update")
    updates: Dict[str, Any] = Field(..., description="Fields to update")


class QueryTool(BaseModel):
    """
    Tool for querying projects and tasks through the AI agent.

    Enables natural language queries to be translated into database
    lookups with filtering and integration-specific searches.
    """

    query_type: str = Field(..., description="Type: 'projects', 'tasks', 'overview'")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filter criteria")
    integration: Optional[str] = Field(None, description="Specific integration to query")


class SyncTool(BaseModel):
    """
    Tool for synchronizing with external integrations.

    Handles bidirectional sync operations between the orchestrator
    and external task management systems like Motion, Linear, etc.
    """

    integration: str = Field(..., description="Integration to sync: motion/linear/gitlab/notion")
    sync_type: str = Field("bidirectional", description="Sync type: pull/push/bidirectional")
    project_ids: Optional[List[str]] = Field(None, description="Specific projects to sync")


class AgentTools:
    """
    Collection of all available tools for the orchestrator agent.

    Provides a registry of tool classes and parsing utilities for
    converting agent tool calls into validated tool instances.
    """

    @staticmethod
    def get_all_tools():
        """
        Get dictionary of all available tool classes.

        Returns:
            Dict[str, BaseModel]: Mapping of tool names to tool classes
        """
        return {
            "create_project": CreateProjectTool,
            "create_task": CreateTaskTool,
            "update_project": UpdateProjectTool,
            "update_task": UpdateTaskTool,
            "query": QueryTool,
            "sync": SyncTool,
        }

    @staticmethod
    def parse_tool_call(tool_name: str, parameters: Dict[str, Any]):
        """
        Parse and validate a tool call from the AI agent.

        Converts raw tool call parameters into validated tool instances
        with proper type checking and validation.

        Args:
            tool_name (str): Name of the tool to invoke
            parameters (Dict[str, Any]): Raw parameters from agent

        Returns:
            BaseModel: Validated tool instance

        Raises:
            ValueError: If tool name is unknown
            ValidationError: If parameters are invalid for the tool

        Example:
            >>> tool = AgentTools.parse_tool_call("create_project", {
            ...     "name": "New Project",
            ...     "description": "A test project"
            ... })
            >>> isinstance(tool, CreateProjectTool)
            True
        """
        tools = AgentTools.get_all_tools()
        if tool_name not in tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool_class = tools[tool_name]
        return tool_class(**parameters)
