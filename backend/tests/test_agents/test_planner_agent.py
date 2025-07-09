"""Comprehensive tests for PlannerAgent."""

import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest

from src.agent.base import AgentError, JSONParsingError, ValidationError
from src.agent.planner_agent import PlannerAgent, create_planner_agent
from src.models.patch import Op, Patch, ProjectPatch, TaskPatch
from src.models.project import ProjectPriority, ProjectStatus
from src.models.task import TaskPriority, TaskStatus


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    settings = MagicMock()
    settings.default_provider = "anthropic"
    settings.get_api_key.return_value = "test-key"

    # Mock provider config
    mock_provider_config = MagicMock()
    mock_provider_config.default = "claude-3-haiku-20240307"

    mock_providers = MagicMock()
    mock_providers.providers = {"anthropic": mock_provider_config}

    settings.providers = mock_providers
    return settings


class TestPlannerAgentInitialization:
    """Test PlannerAgent initialization and configuration."""

    def test_default_initialization(self, mock_settings):
        """Test PlannerAgent with default configuration."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

            assert agent.create_milestones is True
            assert agent.max_milestones == 5
            assert agent.max_retries == 2
            assert agent.retry_delay == 1.0

    def test_custom_initialization(self, mock_settings):
        """Test PlannerAgent with custom configuration."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(
                create_milestones=False, max_milestones=3, max_retries=5, retry_delay=2.0, provider="openai"
            )

            assert agent.create_milestones is False
            assert agent.max_milestones == 3
            assert agent.max_retries == 5
            assert agent.retry_delay == 2.0
            assert agent.provider == "openai"

    def test_factory_function(self, mock_settings):
        """Test create_planner_agent factory function."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = create_planner_agent(provider="anthropic", create_milestones=True, max_milestones=4)

            assert isinstance(agent, PlannerAgent)
            assert agent.provider == "anthropic"
            assert agent.create_milestones is True
            assert agent.max_milestones == 4


class TestPlannerAgentSystemPrompt:
    """Test system prompt generation for PlannerAgent."""

    def test_system_prompt_without_milestones(self, mock_settings):
        """Test system prompt when milestones are disabled."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=False)
            prompt = agent._build_system_prompt(include_milestones=False)

            assert "You are a PlannerAgent" in prompt
            assert "CREATE operations" in prompt
            assert "MILESTONE CREATION" not in prompt
            assert "project_patches" in prompt
            assert "task_patches" in prompt

    def test_system_prompt_with_milestones(self, mock_settings):
        """Test system prompt when milestones are enabled."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=3)
            prompt = agent._build_system_prompt(include_milestones=True)

            assert "You are a PlannerAgent" in prompt
            assert "MILESTONE CREATION" in prompt
            assert "3 or fewer logical phases" in prompt
            assert "Example milestone task" in prompt

    def test_system_prompt_includes_required_elements(self, mock_settings):
        """Test that system prompt includes all required elements."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()
            prompt = agent._build_system_prompt()

            # Check for critical instructions
            assert "ONLY valid JSON" in prompt
            assert "CREATE operations" in prompt
            assert "RESPONSE FORMAT" in prompt
            assert "VALID VALUES" in prompt
            assert "EFFORT ESTIMATION GUIDELINES" in prompt

            # Check for valid enum values
            assert "planning" in prompt
            assert "medium" in prompt
            assert "todo" in prompt


class TestPlannerAgentValidation:
    """Test validation and enhancement logic."""

    def test_validate_empty_project_patches_raises_error(self, mock_settings):
        """Test that missing project patches raises an error."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()
            # Since Pydantic validation prevents creating empty patches,
            # we need to test the internal validation logic differently
            project_patch = ProjectPatch(op=Op.CREATE, name="Test")
            patch_obj = Patch(project_patches=[project_patch])

            # Clear the patches after creation to test our validation
            patch_obj.project_patches = []

            with pytest.raises(ValueError, match="must generate at least one project patch"):
                agent._validate_and_enhance_result(patch_obj, "test input")

    def test_validate_enhances_minimal_project_patch(self, mock_settings):
        """Test that minimal project patch gets enhanced with defaults."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

            # Create minimal project patch
            project_patch = ProjectPatch(op=Op.CREATE)
            patch_obj = Patch(project_patches=[project_patch])

            agent._validate_and_enhance_result(patch_obj, "Build a website for my business")

            # Check enhancements
            enhanced_project = patch_obj.project_patches[0]
            assert enhanced_project.name is not None
            assert len(enhanced_project.name) >= 3
            assert enhanced_project.description is not None
            assert enhanced_project.status == ProjectStatus.PLANNING
            assert enhanced_project.priority == ProjectPriority.MEDIUM
            assert "planning" in enhanced_project.tags
            assert "new-project" in enhanced_project.tags

    def test_validate_preserves_existing_values(self, mock_settings):
        """Test that existing values are preserved during validation."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        project_patch = ProjectPatch(
            op=Op.CREATE,
            name="Custom Project Name",
            description="Custom description",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["custom", "tag"],
        )
        patch_obj = Patch(project_patches=[project_patch])

        agent._validate_and_enhance_result(patch_obj, "test input")

        # Check values are preserved
        enhanced_project = patch_obj.project_patches[0]
        assert enhanced_project.name == "Custom Project Name"
        assert enhanced_project.description == "Custom description"
        assert enhanced_project.status == ProjectStatus.ACTIVE
        assert enhanced_project.priority == ProjectPriority.HIGH
        assert enhanced_project.tags == ["custom", "tag"]

    def test_validate_enhances_task_patches(self, mock_settings):
        """Test that task patches get enhanced with defaults."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        project_patch = ProjectPatch(op=Op.CREATE, name="Test Project")
        # Create task patch with CREATE operation initially, then modify it
        task_patch = TaskPatch(op=Op.CREATE, title="Test Task")
        patch_obj = Patch(project_patches=[project_patch], task_patches=[task_patch])

        # Manually change operation after creation to test validation
        task_patch.op = Op.UPDATE

        agent._validate_and_enhance_result(patch_obj, "test input")

        # Check task enhancements
        enhanced_task = patch_obj.task_patches[0]
        assert enhanced_task.op == Op.CREATE  # Should be corrected
        assert enhanced_task.status == TaskStatus.TODO
        assert enhanced_task.priority == TaskPriority.MEDIUM
        assert enhanced_task.title == "Test Task"  # Should preserve existing title

    def test_validate_preserves_task_values(self, mock_settings):
        """Test that existing task values are preserved."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        project_patch = ProjectPatch(op=Op.CREATE, name="Test Project")
        task_patch = TaskPatch(op=Op.CREATE, title="Custom Task", status=TaskStatus.TODO, priority=TaskPriority.HIGH)
        patch_obj = Patch(project_patches=[project_patch], task_patches=[task_patch])

        agent._validate_and_enhance_result(patch_obj, "test input")

        # Check task values are preserved
        enhanced_task = patch_obj.task_patches[0]
        assert enhanced_task.title == "Custom Task"
        assert enhanced_task.status == TaskStatus.TODO
        assert enhanced_task.priority == TaskPriority.HIGH


class TestPlannerAgentGetDiff:
    """Test the main get_diff method."""

    @pytest.mark.asyncio
    async def test_get_diff_successful_response(self, mock_settings):
        """Test successful project creation from user input."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        # Mock the LLM response
        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "E-commerce Website",
                    "description": "Build a modern e-commerce platform",
                    "status": "planning",
                    "priority": "high",
                    "tags": ["ecommerce", "web"],
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Setup Development Environment",
                    "description": "Configure dev tools and frameworks",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 480,
                }
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await agent.get_diff("Create an e-commerce website for selling handmade crafts")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 1

            project = result.project_patches[0]
            assert project.name == "E-commerce Website"
            assert project.status == ProjectStatus.PLANNING
            assert project.priority == ProjectPriority.HIGH

            task = result.task_patches[0]
            assert task.title == "Setup Development Environment"
            assert task.status == TaskStatus.TODO

    @pytest.mark.asyncio
    async def test_get_diff_without_milestones(self, mock_settings):
        """Test project creation without milestone tasks."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=False)

        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Simple Project",
                    "description": "A basic project",
                    "status": "planning",
                    "priority": "medium",
                }
            ],
            "task_patches": [],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await agent.get_diff("Create a simple project")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 0

    @pytest.mark.asyncio
    async def test_get_diff_with_context_override(self, mock_settings):
        """Test that context can override milestone creation setting."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True)

        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Context Project",
                    "description": "Project influenced by context",
                    "status": "planning",
                    "priority": "medium",
                }
            ],
            "task_patches": [],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            # Test with context override
            context = {"create_milestones": False}
            result = await agent.get_diff("Create a project", context=context)

            # Verify the system prompt was built without milestones
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args
            system_prompt = call_args.kwargs["system_prompt"]
            assert "MILESTONE CREATION" not in system_prompt

    @pytest.mark.asyncio
    async def test_get_diff_handles_llm_errors(self, mock_settings):
        """Test that LLM errors are properly handled."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.side_effect = JSONParsingError("Invalid JSON from LLM")

            with pytest.raises(JSONParsingError):
                await agent.get_diff("Create a project")

    @pytest.mark.asyncio
    async def test_get_diff_validates_result(self, mock_settings):
        """Test that invalid results are caught and enhanced."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        # Mock response with missing required fields
        mock_response = {
            "project_patches": [
                {
                    "op": "create"
                    # Missing name, description, etc.
                }
            ],
            "task_patches": [],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await agent.get_diff("Build something awesome")

            # Check that validation enhanced the result
            project = result.project_patches[0]
            assert project.name is not None
            assert len(project.name) >= 3
            assert project.description is not None
            assert project.status == ProjectStatus.PLANNING

    def test_get_diff_sync_wrapper(self, mock_settings):
        """Test the synchronous wrapper method."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Sync Project",
                    "description": "Test sync method",
                    "status": "planning",
                    "priority": "medium",
                }
            ],
            "task_patches": [],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = agent.get_diff_sync("Create a sync project")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert result.project_patches[0].name == "Sync Project"


class TestPlannerAgentPromptBuilding:
    """Test prompt building and LLM interaction."""

    @pytest.mark.asyncio
    async def test_prompt_includes_user_input(self, mock_settings):
        """Test that user input is properly included in the prompt."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        mock_response = {"project_patches": [{"op": "create", "name": "Test"}], "task_patches": []}

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            user_input = "Build a revolutionary AI-powered social platform"
            await agent.get_diff(user_input)

            # Check that the user input was included in the prompt
            call_args = mock_llm.call_args
            prompt = call_args.kwargs["prompt"]
            assert user_input in prompt
            assert "Project Idea:" in prompt

    @pytest.mark.asyncio
    async def test_system_prompt_varies_with_milestone_setting(self, mock_settings):
        """Test that system prompt changes based on milestone setting."""
        # Test with milestones enabled
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent_with_milestones = PlannerAgent(create_milestones=True)

        mock_response = {"project_patches": [{"op": "create", "name": "Test"}], "task_patches": []}

        with patch.object(agent_with_milestones, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            await agent_with_milestones.get_diff("Test project")

            call_args = mock_llm.call_args
            system_prompt = call_args.kwargs["system_prompt"]
            assert "MILESTONE CREATION" in system_prompt

        # Test with milestones disabled
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent_without_milestones = PlannerAgent(create_milestones=False)

        with patch.object(agent_without_milestones, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            await agent_without_milestones.get_diff("Test project")

            call_args = mock_llm.call_args
            system_prompt = call_args.kwargs["system_prompt"]
            assert "MILESTONE CREATION" not in system_prompt


class TestPlannerAgentEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.mark.asyncio
    async def test_empty_user_input(self, mock_settings):
        """Test handling of empty user input."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        mock_response = {"project_patches": [{"op": "create", "name": "Default Project"}], "task_patches": []}

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            # Should not raise an error
            result = await agent.get_diff("")
            assert isinstance(result, Patch)

    @pytest.mark.asyncio
    async def test_very_long_user_input(self, mock_settings):
        """Test handling of very long user input."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        mock_response = {"project_patches": [{"op": "create", "name": "Long Project"}], "task_patches": []}

        # Create a very long input
        long_input = "Build a project " * 1000

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await agent.get_diff(long_input)
            assert isinstance(result, Patch)

    @pytest.mark.asyncio
    async def test_special_characters_in_input(self, mock_settings):
        """Test handling of special characters in user input."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        mock_response = {"project_patches": [{"op": "create", "name": "Special Project"}], "task_patches": []}

        special_input = "Create a project with émojis 🚀 and symbols @#$%^&*()"

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await agent.get_diff(special_input)
            assert isinstance(result, Patch)

    @pytest.mark.asyncio
    async def test_fallback_name_generation(self, mock_settings):
        """Test fallback name generation from user input."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent()

        # Create response with no name
        mock_response = {"project_patches": [{"op": "create"}], "task_patches": []}

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            user_input = "Build An Amazing Revolutionary Platform For Everyone"
            result = await agent.get_diff(user_input)

            # Check that a name was generated from the input
            project = result.project_patches[0]
            assert project.name is not None
            assert len(project.name) >= 3
            # Should contain some words from the input
            assert any(
                word.lower() in project.name.lower() for word in ["Build", "Amazing", "Revolutionary", "Platform"]
            )


class TestPlannerAgentIntegration:
    """Integration tests with realistic scenarios."""

    @pytest.mark.asyncio
    async def test_realistic_web_project(self, mock_settings):
        """Test with a realistic web development project."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=4)

        realistic_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Personal Portfolio Website",
                    "description": "Modern responsive portfolio website showcasing design and development skills",
                    "status": "planning",
                    "priority": "medium",
                    "tags": ["web", "portfolio", "frontend"],
                    "estimated_total_minutes": 2400,
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Design and Wireframing",
                    "description": "Create wireframes and visual design mockups",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 600,
                },
                {
                    "op": "create",
                    "title": "Frontend Development",
                    "description": "Implement responsive HTML/CSS/JS",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 1200,
                },
                {
                    "op": "create",
                    "title": "Content Creation",
                    "description": "Write and optimize content for all pages",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 480,
                },
                {
                    "op": "create",
                    "title": "Testing and Deployment",
                    "description": "Test across devices and deploy to hosting",
                    "status": "todo",
                    "priority": "medium",
                    "estimated_minutes": 120,
                },
            ],
        }

        with patch.object(agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(realistic_response)

            result = await agent.get_diff(
                "I want to create a personal portfolio website to showcase my work as a designer and developer"
            )

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 4

            project = result.project_patches[0]
            assert "Portfolio" in project.name
            assert "design" in project.description.lower()
            assert project.status == ProjectStatus.PLANNING

            # Verify all tasks are properly configured
            for task in result.task_patches:
                assert task.op == Op.CREATE
                assert task.status == TaskStatus.TODO
                assert task.priority in [TaskPriority.HIGH, TaskPriority.MEDIUM]
                assert task.estimated_minutes is not None
                assert task.estimated_minutes > 0
