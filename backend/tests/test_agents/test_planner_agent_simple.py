"""Simplified tests for PlannerAgent functionality."""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from src.agent.planner_agent import PlannerAgent, create_planner_agent
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority


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


@pytest.fixture
def planner_agent(mock_settings):
    """Create a PlannerAgent for testing."""
    with patch("src.agent.base.get_settings", return_value=mock_settings):
        return PlannerAgent(create_milestones=True, max_milestones=3)


class TestPlannerAgentBasic:
    """Basic functionality tests for PlannerAgent."""

    def test_initialization(self, mock_settings):
        """Test PlannerAgent initialization."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = PlannerAgent(create_milestones=True, max_milestones=5)

            assert agent.create_milestones is True
            assert agent.max_milestones == 5
            assert agent.max_retries == 2

    def test_system_prompt_generation(self, planner_agent):
        """Test system prompt generation."""
        prompt = planner_agent._build_system_prompt(include_milestones=True)

        assert "You are a PlannerAgent" in prompt
        assert "CREATE operations" in prompt
        assert "MILESTONE CREATION" in prompt
        assert "project_patches" in prompt
        assert "task_patches" in prompt

    def test_system_prompt_without_milestones(self, planner_agent):
        """Test system prompt without milestones."""
        prompt = planner_agent._build_system_prompt(include_milestones=False)

        assert "You are a PlannerAgent" in prompt
        assert "MILESTONE CREATION" not in prompt

    def test_validation_enhances_minimal_patch(self, planner_agent):
        """Test that validation enhances minimal project patches."""
        # Create minimal project patch
        project_patch = ProjectPatch(op=Op.CREATE)
        patch = Patch(project_patches=[project_patch])

        planner_agent._validate_and_enhance_result(patch, "Build a website")

        # Check enhancements
        enhanced_project = patch.project_patches[0]
        assert enhanced_project.name is not None
        assert len(enhanced_project.name) >= 3
        assert enhanced_project.description is not None
        assert enhanced_project.status == ProjectStatus.PLANNING
        assert enhanced_project.priority == ProjectPriority.MEDIUM
        assert "planning" in enhanced_project.tags

    def test_validation_preserves_existing_values(self, planner_agent):
        """Test that existing values are preserved during validation."""
        project_patch = ProjectPatch(
            op=Op.CREATE,
            name="Custom Project",
            description="Custom description",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["custom"],
        )
        patch = Patch(project_patches=[project_patch])

        planner_agent._validate_and_enhance_result(patch, "test input")

        # Check values are preserved
        enhanced_project = patch.project_patches[0]
        assert enhanced_project.name == "Custom Project"
        assert enhanced_project.description == "Custom description"
        assert enhanced_project.status == ProjectStatus.ACTIVE
        assert enhanced_project.priority == ProjectPriority.HIGH
        assert enhanced_project.tags == ["custom"]

    def test_validation_empty_patches_raises_error(self, planner_agent):
        """Test that empty patches raise an error."""
        # Since Pydantic validation prevents creating empty patches,
        # we need to test the internal validation logic differently
        project_patch = ProjectPatch(op=Op.CREATE, name="Test")
        patch = Patch(project_patches=[project_patch])

        # Clear the patches after creation to test our validation
        patch.project_patches = []

        with pytest.raises(ValueError, match="must generate at least one project patch"):
            planner_agent._validate_and_enhance_result(patch, "test input")

    @pytest.mark.asyncio
    async def test_get_diff_successful_response(self, planner_agent):
        """Test successful project creation from user input."""
        # Mock the LLM response
        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Test Project",
                    "description": "A test project",
                    "status": "planning",
                    "priority": "medium",
                    "tags": ["test"],
                }
            ],
            "task_patches": [],
        }

        with patch.object(planner_agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await planner_agent.get_diff("Create a test project")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1

            project = result.project_patches[0]
            assert project.name == "Test Project"
            assert project.status == ProjectStatus.PLANNING

    @pytest.mark.asyncio
    async def test_get_diff_with_milestones(self, planner_agent):
        """Test project creation with milestone tasks."""
        mock_response = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "Web Project",
                    "description": "A web development project",
                    "status": "planning",
                    "priority": "high",
                }
            ],
            "task_patches": [
                {
                    "op": "create",
                    "title": "Setup Phase",
                    "description": "Initial setup",
                    "status": "todo",
                    "priority": "high",
                    "estimated_minutes": 120,
                }
            ],
        }

        with patch.object(planner_agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = await planner_agent.get_diff("Create a web project with milestones")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert len(result.task_patches) == 1

            task = result.task_patches[0]
            assert task.title == "Setup Phase"
            assert task.status == TaskStatus.TODO

    def test_get_diff_sync_wrapper(self, planner_agent):
        """Test the synchronous wrapper method."""
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

        with patch.object(planner_agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            result = planner_agent.get_diff_sync("Create a sync project")

            assert isinstance(result, Patch)
            assert len(result.project_patches) == 1
            assert result.project_patches[0].name == "Sync Project"


class TestPlannerAgentFactory:
    """Test the factory function."""

    def test_factory_function(self, mock_settings):
        """Test create_planner_agent factory function."""
        with patch("src.agent.base.get_settings", return_value=mock_settings):
            agent = create_planner_agent(provider="anthropic", create_milestones=True, max_milestones=4)

            assert isinstance(agent, PlannerAgent)
            assert agent.provider == "anthropic"
            assert agent.create_milestones is True
            assert agent.max_milestones == 4


class TestPlannerAgentValidation:
    """Test validation and enhancement of task patches."""

    def test_task_patch_validation(self, planner_agent):
        """Test task patch validation and enhancement."""
        project_patch = ProjectPatch(op=Op.CREATE, name="Test Project")
        # Create task patch with CREATE operation (valid)
        task_patch = TaskPatch(op=Op.CREATE, title="Original Task")
        patch = Patch(project_patches=[project_patch], task_patches=[task_patch])

        # Manually change operation after creation to test validation
        task_patch.op = Op.UPDATE

        planner_agent._validate_and_enhance_result(patch, "test input")

        # Check task enhancements
        enhanced_task = patch.task_patches[0]
        assert enhanced_task.op == Op.CREATE  # Should be corrected
        assert enhanced_task.status == TaskStatus.TODO
        assert enhanced_task.priority == TaskPriority.MEDIUM
        assert enhanced_task.title == "Original Task"  # Should preserve existing title

    def test_name_generation_from_input(self, planner_agent):
        """Test fallback name generation from user input."""
        project_patch = ProjectPatch(op=Op.CREATE)  # No name
        patch = Patch(project_patches=[project_patch])

        planner_agent._validate_and_enhance_result(patch, "Build An Amazing Website")

        # Check that a name was generated
        enhanced_project = patch.project_patches[0]
        assert enhanced_project.name is not None
        assert len(enhanced_project.name) >= 3
        # Should contain some words from input
        name_lower = enhanced_project.name.lower()
        assert any(word.lower() in name_lower for word in ["Build", "Amazing", "Website"])


class TestPlannerAgentContextHandling:
    """Test context handling functionality."""

    @pytest.mark.asyncio
    async def test_context_overrides_milestone_setting(self, planner_agent):
        """Test that context can override milestone creation."""
        mock_response = {"project_patches": [{"op": "create", "name": "Context Project"}], "task_patches": []}

        with patch.object(planner_agent, "_call_llm_with_retry", new_callable=AsyncMock) as mock_llm:
            mock_llm.return_value = Patch.model_validate(mock_response)

            # Test with context override
            context = {"create_milestones": False}
            await planner_agent.get_diff("Create a project", context=context)

            # Verify the system prompt was built without milestones
            mock_llm.assert_called_once()
            call_args = mock_llm.call_args
            system_prompt = call_args.kwargs["system_prompt"]
            assert "MILESTONE CREATION" not in system_prompt
