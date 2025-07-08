"""Tests for API models."""

import pytest
from pydantic import ValidationError

from src.api.models import (
    ConfigResponse,
    ErrorResponse,
    PlannerConfig,
    PlannerRequest,
    PlannerResponse,
    ProjectMetadata,
    ProviderInfo,
    ProviderModel,
    ProvidersResponse,
    TaskMetadata,
)
from src.models.project import ProjectPriority, ProjectStatus
from src.models.task import TaskPriority, TaskStatus


class TestPlannerConfig:
    """Test PlannerConfig model validation."""

    def test_valid_config(self) -> None:
        """Test PlannerConfig with valid values."""
        config = PlannerConfig(
            provider="openai",
            model_name="gpt-4",
            create_milestones=True,
            max_milestones=3,
            max_retries=2,
            retry_delay=1.5,
        )

        assert config.provider == "openai"
        assert config.model_name == "gpt-4"
        assert config.create_milestones is True
        assert config.max_milestones == 3
        assert config.max_retries == 2
        assert config.retry_delay == 1.5

    def test_default_values(self) -> None:
        """Test PlannerConfig with default values."""
        config = PlannerConfig()

        assert config.provider == "openai"
        assert config.model_name is None
        assert config.create_milestones is True
        assert config.max_milestones == 5
        assert config.max_retries == 2
        assert config.retry_delay == 1.0

    def test_invalid_provider(self) -> None:
        """Test PlannerConfig with invalid provider."""
        with pytest.raises(ValidationError) as exc_info:
            PlannerConfig(provider="invalid_provider")

        assert "Provider must be one of" in str(exc_info.value)

    def test_max_milestones_bounds(self) -> None:
        """Test PlannerConfig max_milestones bounds validation."""
        # Test lower bound
        with pytest.raises(ValidationError):
            PlannerConfig(max_milestones=-1)

        # Test upper bound
        with pytest.raises(ValidationError):
            PlannerConfig(max_milestones=9)

        # Test valid bounds
        config = PlannerConfig(max_milestones=0)
        assert config.max_milestones == 0

        config = PlannerConfig(max_milestones=8)
        assert config.max_milestones == 8

    def test_max_retries_bounds(self) -> None:
        """Test PlannerConfig max_retries bounds validation."""
        with pytest.raises(ValidationError):
            PlannerConfig(max_retries=-1)

        with pytest.raises(ValidationError):
            PlannerConfig(max_retries=6)

        config = PlannerConfig(max_retries=0)
        assert config.max_retries == 0

        config = PlannerConfig(max_retries=5)
        assert config.max_retries == 5

    def test_retry_delay_bounds(self) -> None:
        """Test PlannerConfig retry_delay bounds validation."""
        with pytest.raises(ValidationError):
            PlannerConfig(retry_delay=0.05)

        with pytest.raises(ValidationError):
            PlannerConfig(retry_delay=11.0)

        config = PlannerConfig(retry_delay=0.1)
        assert config.retry_delay == 0.1

        config = PlannerConfig(retry_delay=10.0)
        assert config.retry_delay == 10.0


class TestPlannerRequest:
    """Test PlannerRequest model validation."""

    def test_valid_request(self) -> None:
        """Test PlannerRequest with valid values."""
        request = PlannerRequest(
            idea="Build a web application for task management",
            config=PlannerConfig(provider="anthropic"),
            context={"team_size": "3 developers"},
        )

        assert request.idea == "Build a web application for task management"
        assert request.config.provider == "anthropic"
        assert request.context == {"team_size": "3 developers"}

    def test_default_config(self) -> None:
        """Test PlannerRequest with default config."""
        request = PlannerRequest(idea="Build a simple website")

        assert request.idea == "Build a simple website"
        assert isinstance(request.config, PlannerConfig)
        assert request.context is None

    def test_idea_validation(self) -> None:
        """Test idea field validation."""
        # Test empty idea
        with pytest.raises(ValidationError):
            PlannerRequest(idea="")

        # Test whitespace-only idea
        with pytest.raises(ValidationError):
            PlannerRequest(idea="   ")

        # Test too short idea
        with pytest.raises(ValidationError):
            PlannerRequest(idea="short")

        # Test too long idea
        with pytest.raises(ValidationError):
            PlannerRequest(idea="x" * 5001)

        # Test valid idea gets trimmed
        request = PlannerRequest(idea="  Build a web app  ")
        assert request.idea == "Build a web app"


class TestProjectMetadata:
    """Test ProjectMetadata model."""

    def test_valid_project_metadata(self) -> None:
        """Test ProjectMetadata with valid values."""
        project = ProjectMetadata(
            name="Task Management App",
            description="A web application for managing tasks",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["web", "productivity"],
            estimated_total_minutes=4830,
        )

        assert project.name == "Task Management App"
        assert project.description == "A web application for managing tasks"
        assert project.status == ProjectStatus.PLANNING
        assert project.priority == ProjectPriority.HIGH
        assert project.tags == ["web", "productivity"]
        assert project.estimated_total_minutes == 4830

    def test_default_values(self) -> None:
        """Test ProjectMetadata with default values."""
        project = ProjectMetadata(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
        )

        assert project.tags == []
        assert project.estimated_total_minutes is None


class TestTaskMetadata:
    """Test TaskMetadata model."""

    def test_valid_task_metadata(self) -> None:
        """Test TaskMetadata with valid values."""
        task = TaskMetadata(
            title="Setup Database",
            description="Configure the database schema",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            estimated_minutes=120,
        )

        assert task.title == "Setup Database"
        assert task.description == "Configure the database schema"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.HIGH
        assert task.estimated_minutes == 120

    def test_estimated_hours_property(self) -> None:
        """Test estimated_hours property calculation."""
        task = TaskMetadata(
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            estimated_minutes=90,
        )

        assert task.estimated_hours == 1.5

        # Test with None
        task_no_estimate = TaskMetadata(
            title="Test Task", description="Test description", status=TaskStatus.TODO, priority=TaskPriority.MEDIUM
        )

        assert task_no_estimate.estimated_hours is None


class TestPlannerResponse:
    """Test PlannerResponse model."""

    def test_successful_response(self) -> None:
        """Test PlannerResponse for successful request."""
        project = ProjectMetadata(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
        )

        task = TaskMetadata(
            title="Test Task",
            description="Test task description",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            estimated_minutes=60,
        )

        response = PlannerResponse(
            success=True,
            project=project,
            tasks=[task],
            raw_patch={"project_patches": [], "task_patches": []},
            metadata={"provider_used": "openai"},
        )

        assert response.success is True
        assert response.project == project
        assert response.tasks == [task]
        assert response.raw_patch == {"project_patches": [], "task_patches": []}
        assert response.metadata == {"provider_used": "openai"}
        assert response.error is None

    def test_error_response(self) -> None:
        """Test PlannerResponse for error case."""
        response = PlannerResponse(success=False, error="API key not configured")

        assert response.success is False
        assert response.error == "API key not configured"
        assert response.project is None
        assert response.tasks == []
        assert response.raw_patch is None
        assert response.metadata == {}


class TestProviderModels:
    """Test provider-related models."""

    def test_provider_model(self) -> None:
        """Test ProviderModel."""
        model = ProviderModel(
            name="gpt-4", display_name="GPT-4", description="Advanced language model", is_default=True
        )

        assert model.name == "gpt-4"
        assert model.display_name == "GPT-4"
        assert model.description == "Advanced language model"
        assert model.is_default is True

    def test_provider_info(self) -> None:
        """Test ProviderInfo."""
        models = [
            ProviderModel(name="gpt-4", display_name="GPT-4", is_default=True),
            ProviderModel(name="gpt-3.5-turbo", display_name="GPT-3.5 Turbo"),
        ]

        provider = ProviderInfo(name="openai", display_name="OpenAI", models=models, is_available=True, is_default=True)

        assert provider.name == "openai"
        assert provider.display_name == "OpenAI"
        assert provider.models == models
        assert provider.is_available is True
        assert provider.is_default is True

    def test_providers_response(self) -> None:
        """Test ProvidersResponse."""
        provider = ProviderInfo(name="openai", display_name="OpenAI", models=[], is_available=True)

        response = ProvidersResponse(providers=[provider], default_provider="openai")

        assert response.providers == [provider]
        assert response.default_provider == "openai"

    def test_config_response(self) -> None:
        """Test ConfigResponse."""
        config = PlannerConfig()
        providers = ProvidersResponse(providers=[], default_provider="openai")

        response = ConfigResponse(default_config=config, provider_info=providers)

        assert response.default_config == config
        assert response.provider_info == providers


class TestErrorResponse:
    """Test ErrorResponse model."""

    def test_error_response(self) -> None:
        """Test ErrorResponse model."""
        response = ErrorResponse(
            error="Invalid request", details={"field": "provider", "value": "invalid"}, code="VALIDATION_ERROR"
        )

        assert response.error == "Invalid request"
        assert response.details == {"field": "provider", "value": "invalid"}
        assert response.code == "VALIDATION_ERROR"

    def test_error_response_minimal(self) -> None:
        """Test ErrorResponse with minimal fields."""
        response = ErrorResponse(error="Something went wrong")

        assert response.error == "Something went wrong"
        assert response.details is None
        assert response.code is None


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_planner_config_serialization(self) -> None:
        """Test PlannerConfig serialization."""
        config = PlannerConfig(
            provider="anthropic", model_name="claude-3-sonnet-20240229", create_milestones=False, max_milestones=3
        )

        # Test JSON serialization
        json_str = config.model_dump_json()
        assert "anthropic" in json_str
        assert "claude-3-sonnet-20240229" in json_str
        assert "false" in json_str.lower()

        # Test deserialization
        restored = PlannerConfig.model_validate_json(json_str)
        assert restored.provider == config.provider
        assert restored.model_name == config.model_name
        assert restored.create_milestones == config.create_milestones
        assert restored.max_milestones == config.max_milestones

    def test_planner_request_serialization(self) -> None:
        """Test PlannerRequest serialization."""
        request = PlannerRequest(
            idea="Build a mobile app", config=PlannerConfig(provider="openai"), context={"platform": "iOS"}
        )

        # Test dict serialization
        data = request.model_dump()
        assert data["idea"] == "Build a mobile app"
        assert data["config"]["provider"] == "openai"
        assert data["context"] == {"platform": "iOS"}

        # Test deserialization
        restored = PlannerRequest.model_validate(data)
        assert restored.idea == request.idea
        assert restored.config.provider == request.config.provider
        assert restored.context == request.context
