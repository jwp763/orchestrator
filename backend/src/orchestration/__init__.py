"""Orchestration service layer for coordinating business logic, AI agents, and storage.

This package provides service classes that encapsulate business logic and coordinate
between different components of the system:

- ProjectService: Handles project-related business logic and operations
- TaskService: Manages task operations including hierarchical relationships  
- AgentService: Coordinates AI agent interactions with data operations

The service layer provides:
- Business logic validation and processing
- Transaction management across multiple operations
- Dependency injection for storage and agent components
- Error handling and transformation
- Patch application logic for atomic updates
"""

from .project_service import ProjectService
from .task_service import TaskService
from .agent_service import AgentService

__all__ = [
    "ProjectService",
    "TaskService", 
    "AgentService",
]