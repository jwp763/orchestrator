"""PlannerAgent implementation for processing project ideas into project structures."""

import json
from typing import Any, Dict, List, Optional, Union

from .base import AgentBase
from ..models.patch import Patch, ProjectPatch, TaskPatch, Op
from ..models.project import ProjectStatus, ProjectPriority
from ..models.task import TaskStatus, TaskPriority


class PlannerAgent(AgentBase):
    """
    Agent that transforms high-level project ideas into structured project metadata.

    The PlannerAgent analyzes user input describing a project idea and returns
    a ProjectPatch (and optionally TaskPatches for milestones) that creates
    the project structure with appropriate metadata including:
    - Project name and description
    - Estimated effort and timeline
    - Priority and status settings
    - Optional high-level milestone tasks

    This agent is typically used for the initial project creation from
    natural language descriptions.
    """

    def __init__(self, create_milestones: bool = True, max_milestones: int = 5, **kwargs):
        """
        Initialize the PlannerAgent.

        Args:
            create_milestones: Whether to create initial milestone tasks
            max_milestones: Maximum number of milestone tasks to create
            **kwargs: Additional arguments passed to AgentBase
        """
        super().__init__(**kwargs)
        self.create_milestones = create_milestones
        self.max_milestones = max_milestones

    def _build_system_prompt(self, include_milestones: bool = True) -> str:
        """
        Build the system prompt for the PlannerAgent.

        Args:
            include_milestones: Whether to include milestone creation instructions

        Returns:
            System prompt string
        """
        base_prompt = """You are a PlannerAgent that transforms project ideas into structured project metadata.

Your task is to analyze a user's project idea and return a JSON patch that creates a well-structured project with appropriate metadata.

CRITICAL REQUIREMENTS:
1. Return ONLY valid JSON - no markdown formatting, no explanations, no extra text
2. Use CREATE operations for new projects and tasks
3. Generate realistic effort estimates in hours (converted to minutes)
4. Set appropriate priority and status values
5. Create meaningful project names and descriptions

RESPONSE FORMAT:
You must return a JSON object with this exact structure:
{
  "project_patches": [
    {
      "op": "create",
      "name": "Clear, descriptive project name",
      "description": "Detailed description of the project scope and goals",
      "status": "planning",
      "priority": "medium",
      "tags": ["relevant", "tags"],
      "estimated_total_hours": 40
    }
  ],
  "task_patches": [
    // Optional milestone tasks (if requested)
  ]
}

VALID VALUES:
- status: "planning", "active", "on_hold", "completed", "archived"
- priority: "critical", "high", "medium", "low", "backlog"
- task_status: "todo", "in_progress", "blocked", "in_review", "completed", "cancelled"
- task_priority: "critical", "high", "medium", "low", "backlog"

EFFORT ESTIMATION GUIDELINES:
- Small projects: 8-40 hours
- Medium projects: 40-200 hours  
- Large projects: 200-1000+ hours
- Always provide realistic estimates based on project complexity"""

        if include_milestones:
            milestone_prompt = f"""

MILESTONE CREATION:
When creating milestone tasks:
1. Break the project into {self.max_milestones} or fewer logical phases
2. Each milestone should represent a significant deliverable
3. Distribute effort roughly equally across milestones
4. Set all milestone tasks to "todo" status and appropriate priority
5. Include clear titles and descriptions for each milestone

Example milestone task:
{{
  "op": "create",
  "title": "Phase 1: Requirements Analysis",
  "description": "Gather and document detailed requirements",
  "status": "todo",
  "priority": "high",
  "estimated_minutes": 1200
}}"""
            return base_prompt + milestone_prompt

        return base_prompt

    async def get_diff(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Union[Patch, ProjectPatch]:
        """
        Generate a project structure from a user's project idea.

        Args:
            user_input: Natural language description of the project idea
            context: Optional context (not typically used for planning)

        Returns:
            Patch object containing project creation patches and optional milestone tasks

        Raises:
            AgentError: If the agent fails to generate a valid project structure
        """
        # Determine if we should create milestones
        should_create_milestones = self.create_milestones
        if context and "create_milestones" in context:
            should_create_milestones = context["create_milestones"]

        # Build the prompt
        prompt = f"""Project Idea: {user_input.strip()}

Please create a structured project from this idea. Include appropriate metadata and, if suitable, break it down into milestone tasks."""

        # Get system prompt
        system_prompt = self._build_system_prompt(include_milestones=should_create_milestones)

        # Call LLM with retry logic
        result = await self._call_llm_with_retry(prompt=prompt, system_prompt=system_prompt, response_type=Patch)

        # Post-process the result to ensure it meets our requirements
        self._validate_and_enhance_result(result, user_input)

        return result

    def _validate_and_enhance_result(self, patch: Patch, original_input: str) -> None:
        """
        Validate and enhance the generated patch to ensure quality.

        Args:
            patch: The generated patch object
            original_input: Original user input for fallback enhancements
        """
        # Ensure we have at least one project patch
        if not patch.project_patches:
            raise ValueError("PlannerAgent must generate at least one project patch")

        # Validate the first (main) project patch
        main_project = patch.project_patches[0]

        # Ensure we have a name
        if not main_project.name or len(main_project.name.strip()) < 3:
            # Extract a reasonable name from the input as fallback
            words = original_input.split()[:4]  # Take first 4 words
            main_project.name = " ".join(words).title()

        # Ensure we have a description
        if not main_project.description:
            main_project.description = f"Project: {original_input[:200]}"

        # Set defaults if not provided
        if not main_project.status:
            main_project.status = ProjectStatus.PLANNING

        if not main_project.priority:
            main_project.priority = ProjectPriority.MEDIUM

        if not main_project.tags:
            main_project.tags = ["planning", "new-project"]

        # Validate task patches if they exist
        if patch.task_patches:
            for task_patch in patch.task_patches:
                # Ensure tasks have proper CREATE operation
                if task_patch.op != Op.CREATE:
                    task_patch.op = Op.CREATE

                # Set default status and priority if not provided
                if not task_patch.status:
                    task_patch.status = TaskStatus.TODO

                if not task_patch.priority:
                    task_patch.priority = TaskPriority.MEDIUM

                # Ensure task has a title
                if not task_patch.title:
                    task_patch.title = "Milestone Task"

    def get_diff_sync(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Union[Patch, ProjectPatch]:
        """
        Synchronous wrapper for get_diff method.

        Args:
            user_input: Natural language description of the project idea
            context: Optional context information

        Returns:
            Patch object containing project creation patches
        """
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(self.get_diff(user_input, context))
        finally:
            loop.close()


def create_planner_agent(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    create_milestones: bool = True,
    max_milestones: int = 5,
    **kwargs,
) -> PlannerAgent:
    """
    Factory function to create a PlannerAgent instance.

    Args:
        provider: AI provider name
        model_name: Specific model name
        create_milestones: Whether to create milestone tasks
        max_milestones: Maximum number of milestone tasks
        **kwargs: Additional arguments passed to the agent

    Returns:
        Configured PlannerAgent instance
    """
    return PlannerAgent(
        provider=provider,
        model_name=model_name,
        create_milestones=create_milestones,
        max_milestones=max_milestones,
        **kwargs,
    )
