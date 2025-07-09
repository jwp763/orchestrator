"""
Unit and integration tests for project CRUD API endpoints.

Tests API-001 acceptance criteria:
- Unit tests for all project route handlers with valid and invalid request data
- Unit tests for request/response model validation and serialization
- Unit tests for error handling for non-existent resources and validation errors
- Integration tests for full CRUD lifecycle for projects using TestClient
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.project_routes import router
from src.api.models import (
    ProjectCreateRequest, ProjectUpdateRequest, ProjectResponse,
    ProjectListResponse, ErrorResponse
)
from src.storage.sql_models import Base, Project
from src.storage.sql_implementation import SQLStorage
from src.orchestration.project_service import ProjectService
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority


class TestProjectRouteHandlers:
    """Unit tests for project route handlers."""

    @pytest.fixture
    def mock_project_service(self):
        """Mock project service for unit tests."""
        return Mock(spec=ProjectService)

    @pytest.fixture
    def mock_project_data(self):
        """Mock project data for testing."""
        return {
            "id": "test-project-1",
            "name": "Test Project",
            "description": "A test project",
            "status": "planning",
            "priority": "high",
            "tags": ["test", "example"],
            "created_by": "test_user",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "task_count": 0,
            "completed_task_count": 0
        }

    @pytest.fixture
    def client_with_mock_service(self, mock_project_service):
        """Create test client with mocked service."""
        from src.api.project_routes import get_project_service
        
        def mock_get_service():
            return mock_project_service
        
        app.dependency_overrides[get_project_service] = mock_get_service
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_list_projects_success(self, client_with_mock_service, mock_project_service, mock_project_data):
        """Test GET /api/projects returns list of projects."""
        from src.models.project import Project
        
        project_instance = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_project_service.list_projects.return_value = [project_instance]
        
        response = client_with_mock_service.get("/api/projects")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["projects"]) == 1
        assert data["projects"][0]["name"] == "Test Project"
        # The API calls list_projects twice - once for filtered results and once for count
        assert mock_project_service.list_projects.call_count == 2
        first_call, second_call = mock_project_service.list_projects.call_args_list
        assert first_call == ((), {"skip": 0, "limit": 100, "status": None, "priority": None})
        assert second_call == ((), {"skip": 0, "limit": 1000})

    def test_list_projects_with_filters(self, client_with_mock_service, mock_project_service, mock_project_data):
        """Test GET /api/projects with query filters."""
        from src.models.project import Project
        
        project_instance = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_project_service.list_projects.return_value = [project_instance]
        
        response = client_with_mock_service.get("/api/projects?status=planning&priority=high")
        
        assert response.status_code == 200
        # The API calls list_projects twice - once for filtered results and once for count
        assert mock_project_service.list_projects.call_count == 2
        first_call, second_call = mock_project_service.list_projects.call_args_list
        assert first_call == ((), {"skip": 0, "limit": 100, "status": ProjectStatus.PLANNING, "priority": ProjectPriority.HIGH})
        assert second_call == ((), {"skip": 0, "limit": 1000})

    def test_create_project_success(self, client_with_mock_service, mock_project_service, mock_project_data):
        """Test POST /api/projects creates new project."""
        from src.models.project import Project
        
        created_project = Project(
            id="new-project-1",
            name="New Project",
            description="A new project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["new", "test"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_project_service.create_project.return_value = created_project
        
        project_data = {
            "name": "New Project",
            "description": "A new project",
            "status": "planning",
            "priority": "high",
            "tags": ["new", "test"],
            "created_by": "test_user"
        }
        
        response = client_with_mock_service.post("/api/projects", json=project_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Project"
        mock_project_service.create_project.assert_called_once()

    def test_create_project_invalid_data(self, client_with_mock_service, mock_project_service):
        """Test POST /api/projects with invalid data returns 422."""
        invalid_data = {
            "name": "",  # Empty name should fail validation
            "status": "INVALID_STATUS",
            "priority": "INVALID_PRIORITY"
        }
        
        response = client_with_mock_service.post("/api/projects", json=invalid_data)
        
        assert response.status_code == 422
        mock_project_service.create_project.assert_not_called()

    def test_get_project_success(self, client_with_mock_service, mock_project_service, mock_project_data):
        """Test GET /api/projects/{id} returns project details."""
        from src.models.project import Project
        
        project_instance = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0,
            tasks=[]
        )
        mock_project_service.get_project.return_value = project_instance
        
        response = client_with_mock_service.get("/api/projects/test-project-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-project-1"
        assert data["name"] == "Test Project"
        mock_project_service.get_project.assert_called_once_with("test-project-1")

    def test_get_project_not_found(self, client_with_mock_service, mock_project_service):
        """Test GET /api/projects/{id} with non-existent project returns 404."""
        mock_project_service.get_project.return_value = None
        
        response = client_with_mock_service.get("/api/projects/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_project_success(self, client_with_mock_service, mock_project_service, mock_project_data):
        """Test PUT /api/projects/{id} updates project."""
        # Mock both get_project_service and get_storage for the update route
        from src.api.project_routes import get_storage
        from src.models.project import Project
        
        mock_storage = Mock()
        project_instance = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_storage.get_project.return_value = project_instance
        
        updated_project = Project(
            id="test-project-1",
            name="Updated Project",
            description="Updated description",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_storage.update_project.return_value = updated_project
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        update_data = {
            "name": "Updated Project",
            "description": "Updated description"
        }
        
        response = client_with_mock_service.put("/api/projects/test-project-1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Project"
        mock_storage.update_project.assert_called_once()

    def test_update_project_not_found(self, client_with_mock_service, mock_project_service):
        """Test PUT /api/projects/{id} with non-existent project returns 404."""
        from src.api.project_routes import get_storage
        
        mock_storage = Mock()
        mock_storage.get_project.return_value = None
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        update_data = {"name": "Updated Project"}
        
        response = client_with_mock_service.put("/api/projects/nonexistent", json=update_data)
        
        assert response.status_code == 404

    def test_delete_project_success(self, client_with_mock_service, mock_project_service):
        """Test DELETE /api/projects/{id} deletes project."""
        from src.api.project_routes import get_storage
        
        mock_storage = Mock()
        mock_storage.get_project.return_value = {"id": "test-project-1"}
        mock_storage.delete_project.return_value = True
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = client_with_mock_service.delete("/api/projects/test-project-1")
        
        assert response.status_code == 204
        mock_storage.delete_project.assert_called_once_with("test-project-1")

    def test_delete_project_not_found(self, client_with_mock_service, mock_project_service):
        """Test DELETE /api/projects/{id} with non-existent project returns 404."""
        from src.api.project_routes import get_storage
        
        mock_storage = Mock()
        mock_storage.get_project.return_value = None
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = client_with_mock_service.delete("/api/projects/nonexistent")
        
        assert response.status_code == 404

    def test_get_project_tasks_success(self, client_with_mock_service, mock_project_service):
        """Test GET /api/projects/{id}/tasks returns project tasks."""
        from src.api.project_routes import get_storage
        from src.models.project import Project
        from src.models.task import Task, TaskStatus, TaskPriority
        
        mock_storage = Mock()
        project_instance = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            task_count=0,
            completed_task_count=0
        )
        mock_storage.get_project.return_value = project_instance
        
        mock_task = Task(
            id="task-1",
            project_id="test-project-1",
            title="Task 1",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            depth=0,
            dependencies=[],
            tags=[],
            metadata={}
        )
        mock_storage.get_tasks_by_project.return_value = [mock_task]
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        response = client_with_mock_service.get("/api/projects/test-project-1/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Task 1"


class TestProjectRequestResponseModels:
    """Unit tests for project request/response model validation."""

    def test_project_create_request_valid(self):
        """Test ProjectCreateRequest with valid data."""
        data = {
            "name": "Test Project",
            "description": "A test project",
            "status": "planning",
            "priority": "high",
            "tags": ["test"],
            "created_by": "test_user"
        }
        
        request = ProjectCreateRequest(**data)
        assert request.name == "Test Project"
        assert request.status == ProjectStatus.PLANNING
        assert request.priority == ProjectPriority.HIGH

    def test_project_create_request_missing_name(self):
        """Test ProjectCreateRequest fails with missing name."""
        data = {
            "description": "A test project",
            "status": "PLANNING",
            "priority": "HIGH",
            "created_by": "test_user"
        }
        
        with pytest.raises(ValueError):
            ProjectCreateRequest(**data)

    def test_project_create_request_invalid_status(self):
        """Test ProjectCreateRequest fails with invalid status."""
        data = {
            "name": "Test Project",
            "status": "INVALID_STATUS",
            "priority": "high",
            "created_by": "test_user"
        }
        
        with pytest.raises(ValueError):
            ProjectCreateRequest(**data)

    def test_project_update_request_partial(self):
        """Test ProjectUpdateRequest with partial data."""
        data = {
            "name": "Updated Project",
            "tags": ["updated"]
        }
        
        request = ProjectUpdateRequest(**data)
        assert request.name == "Updated Project"
        assert request.description is None  # Optional field
        assert request.tags == ["updated"]

    def test_project_response_serialization(self):
        """Test ProjectResponse serialization."""
        now = datetime.now()
        data = {
            "id": "test-project-1",
            "name": "Test Project",
            "description": "A test project",
            "status": "planning",
            "priority": "high",
            "tags": ["test"],
            "created_by": "test_user",
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "task_count": 5,
            "completed_task_count": 2,
            "due_date": None,
            "start_date": None,
            "motion_project_id": None,
            "linear_project_id": None,
            "notion_page_id": None,
            "gitlab_project_id": None
        }
        
        response = ProjectResponse(**data)
        json_data = response.model_dump()
        
        assert json_data["id"] == "test-project-1"
        assert json_data["name"] == "Test Project"
        assert json_data["status"] == "planning"
        assert json_data["priority"] == "high"
        assert json_data["task_count"] == 5
        assert json_data["completed_task_count"] == 2


class TestProjectRoutesIntegration:
    """Integration tests for project routes with real database."""

    @pytest.fixture
    def test_engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def test_session(self, test_engine):
        """Create test database session."""
        Session = sessionmaker(bind=test_engine)
        session = Session()
        yield session
        session.close()

    @pytest.fixture
    def storage(self, test_session):
        """Create storage instance for testing."""
        return SQLStorage()

    @pytest.fixture
    def client(self):
        """Create test client with real storage."""
        return TestClient(app)

    def test_project_crud_lifecycle(self, client):
        """Test complete project CRUD lifecycle."""
        # Create project
        project_data = {
            "name": "Integration Test Project",
            "description": "Testing full lifecycle",
            "status": "planning",
            "priority": "high",
            "tags": ["integration", "test"],
            "created_by": "integration_user"
        }
        
        create_response = client.post("/api/projects", json=project_data)
        assert create_response.status_code == 201
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # Read project
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200
        retrieved_project = get_response.json()
        assert retrieved_project["name"] == "Integration Test Project"
        
        # Update project
        update_data = {
            "name": "Updated Integration Project",
            "description": "Updated description",
            "status": "active"
        }
        
        update_response = client.put(f"/api/projects/{project_id}", json=update_data)
        assert update_response.status_code == 200
        updated_project = update_response.json()
        assert updated_project["name"] == "Updated Integration Project"
        assert updated_project["status"] == "active"
        
        # List projects
        list_response = client.get("/api/projects")
        assert list_response.status_code == 200
        projects_list = list_response.json()
        assert len(projects_list["projects"]) >= 1
        # Find our created project in the list
        our_project = next((p for p in projects_list["projects"] if p["id"] == project_id), None)
        assert our_project is not None
        assert our_project["name"] == "Updated Integration Project"
        
        # Delete project
        delete_response = client.delete(f"/api/projects/{project_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_deleted_response = client.get(f"/api/projects/{project_id}")
        assert get_deleted_response.status_code == 404

    def test_project_list_filtering(self, client):
        """Test project list filtering functionality."""
        # Create multiple projects
        projects_data = [
            {
                "name": "High Priority Project",
                "status": "planning",
                "priority": "high",
                "tags": ["important"],
                "created_by": "user1"
            },
            {
                "name": "Low Priority Project",
                "status": "active",
                "priority": "low",
                "tags": ["optional"],
                "created_by": "user2"
            }
        ]
        
        for project_data in projects_data:
            create_response = client.post("/api/projects", json=project_data)
            assert create_response.status_code == 201
        
        # Test filtering by status
        response = client.get("/api/projects?status=planning")
        assert response.status_code == 200
        filtered_projects = response.json()
        planning_projects = [p for p in filtered_projects["projects"] if p["status"] == "planning"]
        assert len(planning_projects) >= 1
        assert any(p["name"] == "High Priority Project" for p in planning_projects)
        
        # Test filtering by priority
        response = client.get("/api/projects?priority=low")
        assert response.status_code == 200
        filtered_projects = response.json()
        low_priority_projects = [p for p in filtered_projects["projects"] if p["priority"] == "low"]
        assert len(low_priority_projects) >= 1
        assert any(p["name"] == "Low Priority Project" for p in low_priority_projects)

    def test_project_validation_errors(self, client):
        """Test validation errors are properly handled."""
        # Test missing required fields
        invalid_data = {
            "description": "Missing name and created_by"
        }
        
        response = client.post("/api/projects", json=invalid_data)
        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail
        
        # Test invalid enum values
        invalid_data = {
            "name": "Test Project",
            "status": "INVALID_STATUS",
            "priority": "INVALID_PRIORITY",
            "created_by": "test_user"
        }
        
        response = client.post("/api/projects", json=invalid_data)
        assert response.status_code == 422

    def test_project_not_found_errors(self, client):
        """Test 404 errors for non-existent projects."""
        # Test get non-existent project
        response = client.get("/api/projects/nonexistent-id")
        assert response.status_code == 404
        
        # Test update non-existent project
        update_data = {"name": "Updated Name"}
        response = client.put("/api/projects/nonexistent-id", json=update_data)
        assert response.status_code == 404
        
        # Test delete non-existent project
        response = client.delete("/api/projects/nonexistent-id")
        assert response.status_code == 404
        
        # Test get tasks for non-existent project
        response = client.get("/api/projects/nonexistent-id/tasks")
        assert response.status_code == 404


class TestProjectRoutesErrorHandling:
    """Test error handling in project routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_service_error_handling(self, client):
        """Test proper error handling when service raises exceptions."""
        from src.api.project_routes import get_project_service
        
        mock_service = Mock()
        mock_service.create_project.side_effect = Exception("Database error")
        
        app.dependency_overrides[get_project_service] = lambda: mock_service
        
        project_data = {
            "name": "Test Project",
            "created_by": "test_user"
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        
        app.dependency_overrides.clear()

    def test_validation_error_handling(self, client):
        """Test validation error handling."""
        # Test malformed JSON
        response = client.post("/api/projects", content="invalid json")
        assert response.status_code == 422
        
        # Test wrong content type
        response = client.post("/api/projects", data="not json")
        assert response.status_code == 422