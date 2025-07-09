"""Integration tests for PlannerAgent API routes."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.api.models import PlannerConfig, PlannerRequest
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority
from src.agent.base import AgentError, JSONParsingError, ValidationError


class TestPlannerGenerateEndpoint:
    """Test /api/planner/generate endpoint."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    @pytest.fixture
    def mock_planner_agent(self):
        """Mock PlannerAgent for testing."""
        agent = AsyncMock()
        
        # Default successful response
        mock_patch = Patch(
            project_patches=[ProjectPatch(
                op=Op.CREATE,
                name="Test Project",
                description="A test project for the API",
                status=ProjectStatus.PLANNING,
                priority=ProjectPriority.MEDIUM,
                tags=["test", "api"],
                estimated_total_minutes=2400
            )],
            task_patches=[TaskPatch(
                op=Op.CREATE,
                title="Setup Environment",
                description="Configure the development environment",
                status=TaskStatus.TODO,
                priority=TaskPriority.HIGH,
                estimated_minutes=120
            )]
        )
        agent.get_diff.return_value = mock_patch
        return agent
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_success(self, mock_get_agent, app: TestClient, mock_planner_agent):
        """Test successful project plan generation."""
        mock_get_agent.return_value = mock_planner_agent
        
        request_data = {
            "idea": "Build a web application for task management",
            "config": {
                "provider": "openai",
                "create_milestones": True,
                "max_milestones": 3
            }
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["project"] is not None
        assert data["project"]["name"] == "Test Project"
        assert data["project"]["description"] == "A test project for the API"
        assert data["project"]["status"] == "planning"
        assert data["project"]["priority"] == "medium"
        assert data["project"]["tags"] == ["test", "api"]
        assert data["project"]["estimated_total_minutes"] == 2400
        assert data["project"]["estimated_total_hours"] == 40.0
        
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Setup Environment"
        assert data["tasks"][0]["estimated_minutes"] == 120
        assert data["tasks"][0]["estimated_hours"] == 2.0
        
        assert data["raw_patch"] is not None
        assert data["metadata"]["provider_used"] == "openai"
        assert data["metadata"]["milestones_created"] == 1
        assert data["error"] is None
        
        # Verify agent was called correctly
        mock_planner_agent.get_diff.assert_called_once_with(
            "Build a web application for task management", 
            context=None
        )
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_with_context(self, mock_get_agent, app: TestClient, mock_planner_agent):
        """Test project plan generation with context."""
        mock_get_agent.return_value = mock_planner_agent
        
        request_data = {
            "idea": "Create a mobile app",
            "config": {
                "provider": "anthropic",
                "model_name": "claude-3-sonnet-20240229"
            },
            "context": {
                "platform": "iOS",
                "team_size": "2 developers"
            }
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify context was passed to agent
        mock_planner_agent.get_diff.assert_called_once_with(
            "Create a mobile app",
            context={"platform": "iOS", "team_size": "2 developers"}
        )
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_json_parsing_error(self, mock_get_agent, app: TestClient):
        """Test handling of JSON parsing errors."""
        mock_agent = AsyncMock()
        mock_agent.get_diff.side_effect = JSONParsingError("Invalid JSON response")
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "idea": "Build a complex application"
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "invalid JSON" in data["error"]
        assert data["project"] is None
        assert data["tasks"] == []
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_validation_error(self, mock_get_agent, app: TestClient):
        """Test handling of validation errors."""
        mock_agent = AsyncMock()
        mock_agent.get_diff.side_effect = ValidationError("Schema validation failed")
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "idea": "Build an application with invalid data"
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "expected format" in data["error"]
        assert data["project"] is None
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_agent_error(self, mock_get_agent, app: TestClient):
        """Test handling of general agent errors."""
        mock_agent = AsyncMock()
        mock_agent.get_diff.side_effect = AgentError("AI model unavailable")
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "idea": "Build an application"
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is False
        assert "AI agent encountered an error" in data["error"]
    
    def test_generate_project_plan_invalid_request(self, app: TestClient):
        """Test handling of invalid request data."""
        # Test empty idea
        response = app.post("/api/planner/generate", json={"idea": ""})
        assert response.status_code == 422
        
        # Test missing idea
        response = app.post("/api/planner/generate", json={})
        assert response.status_code == 422
        
        # Test invalid provider
        request_data = {
            "idea": "Build an app",
            "config": {"provider": "invalid_provider"}
        }
        response = app.post("/api/planner/generate", json=request_data)
        assert response.status_code == 422
    
    @patch('src.api.planner_routes.get_cached_planner_agent')
    def test_generate_project_plan_no_milestones(self, mock_get_agent, app: TestClient):
        """Test project plan generation without milestones."""
        mock_agent = AsyncMock()
        mock_patch = Patch(
            project_patches=[ProjectPatch(
                op=Op.CREATE,
                name="Simple Project",
                description="A project without milestones",
                status=ProjectStatus.PLANNING,
                priority=ProjectPriority.LOW
            )],
            task_patches=[]  # No tasks
        )
        mock_agent.get_diff.return_value = mock_patch
        mock_get_agent.return_value = mock_agent
        
        request_data = {
            "idea": "Create a simple landing page",
            "config": {"create_milestones": False}
        }
        
        response = app.post("/api/planner/generate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert data["project"]["name"] == "Simple Project"
        assert data["tasks"] == []
        assert data["metadata"]["milestones_created"] == 0


class TestPlannerProvidersEndpoint:
    """Test /api/planner/providers endpoint."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.default_provider = "openai"
        
        # Mock providers config
        provider_config = Mock()
        provider_config.providers = {
            "openai": Mock(
                models=["gpt-4", "gpt-3.5-turbo"],
                default="gpt-4"
            ),
            "anthropic": Mock(
                models=["claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                default="claude-3-sonnet-20240229"
            )
        }
        settings.providers = provider_config
        
        # Mock API key availability
        def get_api_key(provider):
            return "test-key" if provider == "openai" else None
        
        settings.get_api_key = get_api_key
        return settings
    
    def test_get_providers_success(self, mock_settings):
        """Test successful providers retrieval."""
        from src.api.planner_routes import get_settings_dependency
        from src.api.main import create_app
        
        # Create app and override dependency
        test_app = create_app()
        test_app.dependency_overrides[get_settings_dependency] = lambda: mock_settings
        app = TestClient(test_app)
        
        response = app.get("/api/planner/providers")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "providers" in data
        assert "default_provider" in data
        assert data["default_provider"] == "openai"
        
        providers = data["providers"]
        assert len(providers) == 2
        
        # Check OpenAI provider
        openai_provider = next(p for p in providers if p["name"] == "openai")
        assert openai_provider["display_name"] == "OpenAI"
        assert openai_provider["is_available"] is True
        assert openai_provider["is_default"] is True
        assert len(openai_provider["models"]) == 2
        
        # Check model structure
        gpt4_model = next(m for m in openai_provider["models"] if m["name"] == "gpt-4")
        assert gpt4_model["display_name"] == "gpt-4"
        assert gpt4_model["is_default"] is True
        
        # Check Anthropic provider (no API key)
        anthropic_provider = next(p for p in providers if p["name"] == "anthropic")
        assert anthropic_provider["display_name"] == "Anthropic"
        assert anthropic_provider["is_available"] is False
        assert anthropic_provider["is_default"] is False


class TestPlannerConfigEndpoint:
    """Test /api/planner/config endpoint."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.default_provider = "anthropic"
        
        # Mock providers config
        provider_config = Mock()
        provider_config.providers = {
            "anthropic": Mock(
                models=["claude-3-sonnet-20240229"],
                default="claude-3-sonnet-20240229"
            )
        }
        settings.providers = provider_config
        settings.get_api_key = lambda provider: "test-key" if provider == "anthropic" else None
        return settings
    
    @patch('src.api.planner_routes.get_settings_dependency')
    @patch('src.api.planner_routes.get_providers')
    def test_get_config_success(self, mock_get_providers, mock_get_settings, app: TestClient, mock_settings):
        """Test successful config retrieval."""
        mock_get_settings.return_value = mock_settings
        
        # Mock providers response
        mock_providers_response = {
            "providers": [],
            "default_provider": "anthropic"
        }
        mock_get_providers.return_value = mock_providers_response
        
        response = app.get("/api/planner/config")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "default_config" in data
        assert "provider_info" in data
        
        config = data["default_config"]
        assert config["provider"] == "anthropic"
        assert config["model_name"] is None
        assert config["create_milestones"] is True
        assert config["max_milestones"] == 5
        assert config["max_retries"] == 2
        assert config["retry_delay"] == 1.0
        
        assert data["provider_info"] == mock_providers_response


class TestCacheEndpoints:
    """Test cache management endpoints."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    def test_get_cache_stats(self, app: TestClient):
        """Test cache stats endpoint."""
        response = app.get("/api/planner/cache/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "cache_size" in data
        assert "max_cache_size" in data
        assert "hits" in data
        assert "misses" in data
        assert "hit_rate" in data
        
        # Verify data types
        assert isinstance(data["cache_size"], int)
        assert isinstance(data["max_cache_size"], int)
        assert isinstance(data["hits"], int)
        assert isinstance(data["misses"], int)
        assert isinstance(data["hit_rate"], (int, float))
    
    def test_clear_cache(self, app: TestClient):
        """Test cache clear endpoint."""
        response = app.post("/api/planner/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["success"] is True
        assert "message" in data


class TestCORSHeaders:
    """Test CORS headers are properly set."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    @pytest.fixture
    def mock_settings(self):
        """Mock settings for testing."""
        settings = Mock()
        settings.default_provider = "openai"
        settings.providers = Mock()
        settings.providers.providers = {}
        settings.get_api_key = lambda x: None
        return settings
    
    def test_cors_preflight_request(self, mock_settings):
        """Test CORS preflight behavior by checking if CORS middleware is properly configured."""
        from src.api.planner_routes import get_settings_dependency
        from src.api.main import create_app
        
        # Create app and override dependency
        test_app = create_app()
        test_app.dependency_overrides[get_settings_dependency] = lambda: mock_settings
        app = TestClient(test_app)
        
        # Test that CORS is properly configured by checking the middleware
        # Since TestClient doesn't fully simulate preflight requests,
        # we verify that the CORS middleware is present by looking at the app
        cors_middleware_present = any(
            middleware.cls.__name__ == 'CORSMiddleware' 
            for middleware in test_app.user_middleware
        )
        
        assert cors_middleware_present, "CORSMiddleware should be configured"
        
        # Also test that a regular request with Origin header works
        response = app.get("/api/planner/providers", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        
        # Check CORS headers are present
        headers = response.headers
        assert "access-control-allow-origin" in headers
    
    def test_cors_headers_get_request(self, mock_settings):
        """Test CORS headers on actual GET request."""
        from src.api.planner_routes import get_settings_dependency
        from src.api.main import create_app
        
        # Create app and override dependency
        test_app = create_app()
        test_app.dependency_overrides[get_settings_dependency] = lambda: mock_settings
        app = TestClient(test_app)
        
        # Add Origin header to trigger CORS
        response = app.get("/api/planner/providers", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        
        # Check CORS headers are present
        headers = response.headers
        assert "access-control-allow-origin" in headers


class TestErrorHandling:
    """Test API error handling."""
    
    @pytest.fixture
    def app(self) -> TestClient:
        """Create test FastAPI application."""
        return TestClient(create_app())
    
    def test_health_endpoint(self, app: TestClient):
        """Test health check endpoint."""
        response = app.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "healthy"
        assert data["service"] == "databricks-orchestrator-api"
    
    def test_404_error(self, app: TestClient):
        """Test 404 error handling."""
        response = app.get("/api/nonexistent")
        
        assert response.status_code == 404
    
    def test_422_validation_error(self, app: TestClient):
        """Test 422 validation error handling."""
        # Send invalid JSON
        response = app.post("/api/planner/generate", json={"invalid": "data"})
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data