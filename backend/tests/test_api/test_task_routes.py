"""
Unit and integration tests for task CRUD API endpoints.

Tests API-001 acceptance criteria:
- Unit tests for all task route handlers with valid and invalid request data
- Unit tests for request/response model validation and serialization
- Unit tests for error handling for non-existent resources and validation errors
- Integration tests for full CRUD lifecycle for tasks using TestClient
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.api.main import app
from src.api.task_routes import router
from src.api.models import (
    TaskCreateRequest, TaskUpdateRequest, TaskResponse,
    TaskListResponse, TaskWithSubtasksResponse, ErrorResponse
)
from src.storage.sql_models import Base, Task
from src.storage.sql_implementation import SQLStorage
from src.models.task import TaskStatus, TaskPriority
from src.models.project import ProjectStatus, ProjectPriority


class TestTaskRouteHandlers:
    """Unit tests for task route handlers."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage for unit tests."""
        return Mock(spec=SQLStorage)

    @pytest.fixture
    def mock_task_data(self):
        """Mock task data for testing."""
        return {
            "id": "test-task-1",
            "project_id": "test-project-1",
            "parent_id": None,
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": "medium",
            "tags": ["test", "example"],
            "estimated_minutes": 60,
            "actual_minutes": 0,
            "due_date": None,
            "assignee": "test_user",
            "depth": 0,
            "sort_order": 0,
            "completion_percentage": 0,
            "dependencies": [],
            "attachments": [],
            "notes": None,
            "metadata": {},
            "created_by": "test_user",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "motion_task_id": None,
            "linear_issue_id": None,
            "notion_task_id": None,
            "gitlab_issue_id": None
        }

    @pytest.fixture
    def mock_project_data(self):
        """Mock project data for testing."""
        from src.models.project import Project
        return Project(
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

    @pytest.fixture
    def client_with_mock_storage(self, mock_storage):
        """Create test client with mocked storage."""
        from src.api.task_routes import get_storage
        
        def mock_get_storage():
            return mock_storage
        
        app.dependency_overrides[get_storage] = mock_get_storage
        client = TestClient(app)
        yield client
        app.dependency_overrides.clear()

    def test_list_tasks_success(self, client_with_mock_storage, mock_storage, mock_task_data, mock_project_data):
        """Test GET /api/tasks returns list of tasks."""
        from src.models.task import Task
        
        task_instance = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=["test", "example"],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock the list_tasks method to return the expected dictionary format
        mock_storage.list_tasks.return_value = {
            "tasks": [task_instance],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "has_next": False,
            "has_prev": False
        }
        
        response = client_with_mock_storage.get("/api/tasks")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["title"] == "Test Task"

    def test_list_tasks_with_filters(self, client_with_mock_storage, mock_storage, mock_project_data):
        """Test GET /api/tasks with query filters."""
        from src.models.task import Task
        
        task_instance = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            tags=["test"],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Mock the list_tasks method to return the expected dictionary format
        mock_storage.list_tasks.return_value = {
            "tasks": [task_instance],
            "total": 1,
            "page": 1,
            "per_page": 20,
            "has_next": False,
            "has_prev": False
        }
        
        response = client_with_mock_storage.get("/api/tasks?project_id=test-project-1&status=todo&priority=high")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["status"] == "todo"
        assert data["tasks"][0]["priority"] == "high"

    def test_create_task_success(self, client_with_mock_storage, mock_storage, mock_project_data):
        """Test POST /api/tasks creates new task."""
        from src.models.task import Task
        
        # Mock project exists
        mock_storage.get_project.return_value = mock_project_data
        
        created_task = Task(
            id="new-task-1",
            project_id="test-project-1",
            title="New Task",
            description="A new task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=["new", "test"],
            estimated_minutes=30,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_storage.create_task.return_value = created_task
        
        task_data = {
            "project_id": "test-project-1",
            "title": "New Task",
            "description": "A new task",
            "status": "todo",
            "priority": "medium",
            "tags": ["new", "test"],
            "estimated_minutes": 30,
            "assignee": "test_user",
            "created_by": "test_user"
        }
        
        response = client_with_mock_storage.post("/api/tasks", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Task"
        assert data["project_id"] == "test-project-1"
        mock_storage.create_task.assert_called_once()

    def test_create_task_project_not_found(self, client_with_mock_storage, mock_storage):
        """Test POST /api/tasks with non-existent project returns 404."""
        mock_storage.get_project.return_value = None
        
        task_data = {
            "project_id": "nonexistent-project",
            "title": "New Task",
            "created_by": "test_user"
        }
        
        response = client_with_mock_storage.post("/api/tasks", json=task_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_create_task_invalid_data(self, client_with_mock_storage, mock_storage):
        """Test POST /api/tasks with invalid data returns 422."""
        invalid_data = {
            "project_id": "test-project-1",
            "title": "",  # Empty title should fail validation
            "status": "INVALID_STATUS",
            "priority": "INVALID_PRIORITY"
        }
        
        response = client_with_mock_storage.post("/api/tasks", json=invalid_data)
        
        assert response.status_code == 422
        mock_storage.create_task.assert_not_called()

    def test_create_task_with_parent_success(self, client_with_mock_storage, mock_storage, mock_project_data):
        """Test POST /api/tasks with parent task creates subtask."""
        from src.models.task import Task
        
        # Mock project exists
        mock_storage.get_project.return_value = mock_project_data
        
        # Mock parent task exists
        parent_task = Task(
            id="parent-task-1",
            project_id="test-project-1",
            title="Parent Task",
            description="A parent task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=[],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_storage.get_task.return_value = parent_task
        
        created_task = Task(
            id="subtask-1",
            project_id="test-project-1",
            parent_id="parent-task-1",
            title="Subtask",
            description="A subtask",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=[],
            estimated_minutes=30,
            actual_minutes=0,
            assignee="test_user",
            depth=1,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_storage.create_task.return_value = created_task
        
        task_data = {
            "project_id": "test-project-1",
            "parent_id": "parent-task-1",
            "title": "Subtask",
            "description": "A subtask",
            "created_by": "test_user"
        }
        
        response = client_with_mock_storage.post("/api/tasks", json=task_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Subtask"
        assert data["parent_id"] == "parent-task-1"

    def test_create_task_parent_not_found(self, client_with_mock_storage, mock_storage, mock_project_data):
        """Test POST /api/tasks with non-existent parent returns 404."""
        mock_storage.get_project.return_value = mock_project_data
        mock_storage.get_task.return_value = None
        
        task_data = {
            "project_id": "test-project-1",
            "parent_id": "nonexistent-parent",
            "title": "Subtask",
            "created_by": "test_user"
        }
        
        response = client_with_mock_storage.post("/api/tasks", json=task_data)
        
        assert response.status_code == 404
        data = response.json()
        assert "parent task" in data["detail"].lower()

    def test_get_task_success(self, client_with_mock_storage, mock_storage):
        """Test GET /api/tasks/{id} returns task details."""
        from src.models.task import Task
        
        task_instance = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=["test"],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        subtask = Task(
            id="subtask-1",
            project_id="test-project-1",
            parent_id="test-task-1",
            title="Subtask",
            description="A subtask",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            tags=[],
            estimated_minutes=30,
            actual_minutes=0,
            assignee="test_user",
            depth=1,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_storage.get_task.return_value = task_instance
        mock_storage.get_tasks_by_project.return_value = [task_instance, subtask]
        
        response = client_with_mock_storage.get("/api/tasks/test-task-1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-task-1"
        assert data["title"] == "Test Task"
        assert len(data["subtasks"]) == 1
        assert data["subtasks"][0]["title"] == "Subtask"

    def test_get_task_not_found(self, client_with_mock_storage, mock_storage):
        """Test GET /api/tasks/{id} with non-existent task returns 404."""
        mock_storage.get_task.return_value = None
        
        response = client_with_mock_storage.get("/api/tasks/nonexistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"].lower()

    def test_update_task_success(self, client_with_mock_storage, mock_storage):
        """Test PUT /api/tasks/{id} updates task."""
        from src.models.task import Task
        
        existing_task = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=["test"],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        updated_task = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Updated Task",
            description="Updated description",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            tags=["test", "updated"],
            estimated_minutes=90,
            actual_minutes=30,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_storage.get_task.return_value = existing_task
        mock_storage.update_task.return_value = updated_task
        
        update_data = {
            "title": "Updated Task",
            "description": "Updated description",
            "status": "in_progress",
            "priority": "high",
            "estimated_minutes": 90,
            "actual_minutes": 30
        }
        
        response = client_with_mock_storage.put("/api/tasks/test-task-1", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Task"
        assert data["status"] == "in_progress"
        assert data["priority"] == "high"
        mock_storage.update_task.assert_called_once()

    def test_update_task_not_found(self, client_with_mock_storage, mock_storage):
        """Test PUT /api/tasks/{id} with non-existent task returns 404."""
        mock_storage.get_task.return_value = None
        
        update_data = {"title": "Updated Task"}
        
        response = client_with_mock_storage.put("/api/tasks/nonexistent", json=update_data)
        
        assert response.status_code == 404

    def test_delete_task_success(self, client_with_mock_storage, mock_storage):
        """Test DELETE /api/tasks/{id} deletes task."""
        from src.models.task import Task
        
        task_instance = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            tags=["test"],
            estimated_minutes=60,
            actual_minutes=0,
            assignee="test_user",
            depth=0,
            dependencies=[],
            metadata={},
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_storage.get_task.return_value = task_instance
        mock_storage.delete_task.return_value = True
        
        response = client_with_mock_storage.delete("/api/tasks/test-task-1")
        
        assert response.status_code == 204
        mock_storage.delete_task.assert_called_once_with("test-task-1")

    def test_delete_task_not_found(self, client_with_mock_storage, mock_storage):
        """Test DELETE /api/tasks/{id} with non-existent task returns 404."""
        mock_storage.get_task.return_value = None
        
        response = client_with_mock_storage.delete("/api/tasks/nonexistent")
        
        assert response.status_code == 404


class TestTaskRequestResponseModels:
    """Unit tests for task request/response model validation."""

    def test_task_create_request_valid(self):
        """Test TaskCreateRequest with valid data."""
        data = {
            "project_id": "test-project-1",
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": "medium",
            "tags": ["test"],
            "estimated_minutes": 60,
            "assignee": "test_user",
            "created_by": "test_user"
        }
        
        request = TaskCreateRequest(**data)
        assert request.title == "Test Task"
        assert request.project_id == "test-project-1"
        assert request.status == TaskStatus.TODO
        assert request.priority == TaskPriority.MEDIUM

    def test_task_create_request_missing_title(self):
        """Test TaskCreateRequest fails with missing title."""
        data = {
            "project_id": "test-project-1",
            "description": "A test task",
            "status": "todo",
            "priority": "medium",
            "created_by": "test_user"
        }
        
        with pytest.raises(ValueError):
            TaskCreateRequest(**data)

    def test_task_create_request_invalid_status(self):
        """Test TaskCreateRequest fails with invalid status."""
        data = {
            "project_id": "test-project-1",
            "title": "Test Task",
            "status": "INVALID_STATUS",
            "priority": "medium",
            "created_by": "test_user"
        }
        
        with pytest.raises(ValueError):
            TaskCreateRequest(**data)

    def test_task_update_request_partial(self):
        """Test TaskUpdateRequest with partial data."""
        data = {
            "title": "Updated Task",
            "status": "in_progress",
            "tags": ["updated"]
        }
        
        request = TaskUpdateRequest(**data)
        assert request.title == "Updated Task"
        assert request.status == TaskStatus.IN_PROGRESS
        assert request.description is None  # Optional field
        assert request.tags == ["updated"]

    def test_task_response_serialization(self):
        """Test TaskResponse serialization."""
        now = datetime.now()
        data = {
            "id": "test-task-1",
            "project_id": "test-project-1",
            "parent_id": None,
            "title": "Test Task",
            "description": "A test task",
            "status": "todo",
            "priority": "medium",
            "tags": ["test"],
            "estimated_minutes": 60,
            "actual_minutes": 30,
            "due_date": None,
            "assignee": "test_user",
            "depth": 0,
            "sort_order": 0,
            "completion_percentage": 50,
            "dependencies": [],
            "attachments": [],
            "notes": None,
            "metadata": {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "created_by": "test_user",
            "motion_task_id": None,
            "linear_issue_id": None,
            "notion_task_id": None,
            "gitlab_issue_id": None
        }
        
        response = TaskResponse(**data)
        json_data = response.model_dump()
        
        assert json_data["id"] == "test-task-1"
        assert json_data["title"] == "Test Task"
        assert json_data["status"] == "todo"
        assert json_data["priority"] == "medium"
        assert json_data["estimated_minutes"] == 60
        assert json_data["actual_minutes"] == 30


class TestTaskRoutesIntegration:
    """Integration tests for task routes with real database."""

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

    @pytest.fixture
    def test_project(self, client):
        """Create a test project for task testing."""
        project_data = {
            "name": "Test Project for Tasks",
            "description": "A project for testing tasks",
            "status": "planning",
            "priority": "high",
            "created_by": "test_user"
        }
        
        response = client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        return response.json()

    def test_task_crud_lifecycle(self, client, test_project):
        """Test complete task CRUD lifecycle."""
        project_id = test_project["id"]
        
        # Create task
        task_data = {
            "project_id": project_id,
            "title": "Integration Test Task",
            "description": "Testing full lifecycle",
            "status": "todo",
            "priority": "medium",
            "tags": ["integration", "test"],
            "estimated_minutes": 120,
            "assignee": "integration_user",
            "created_by": "integration_user"
        }
        
        create_response = client.post("/api/tasks", json=task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        task_id = created_task["id"]
        
        # Read task
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 200
        retrieved_task = get_response.json()
        assert retrieved_task["title"] == "Integration Test Task"
        assert retrieved_task["project_id"] == project_id
        
        # Update task
        update_data = {
            "title": "Updated Integration Task",
            "description": "Updated description",
            "status": "in_progress",
            "priority": "high",
            "actual_minutes": 60
        }
        
        update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
        assert update_response.status_code == 200
        updated_task = update_response.json()
        assert updated_task["title"] == "Updated Integration Task"
        assert updated_task["status"] == "in_progress"
        assert updated_task["priority"] == "high"
        
        # List tasks
        list_response = client.get("/api/tasks")
        assert list_response.status_code == 200
        tasks_list = list_response.json()
        assert len(tasks_list["tasks"]) >= 1
        # Find our created task in the list
        our_task = next((t for t in tasks_list["tasks"] if t["id"] == task_id), None)
        assert our_task is not None
        assert our_task["title"] == "Updated Integration Task"
        
        # Delete task
        delete_response = client.delete(f"/api/tasks/{task_id}")
        assert delete_response.status_code == 204
        
        # Verify deletion
        get_deleted_response = client.get(f"/api/tasks/{task_id}")
        assert get_deleted_response.status_code == 404

    def test_task_hierarchical_relationships(self, client, test_project):
        """Test parent-child task relationships."""
        project_id = test_project["id"]
        
        # Create parent task
        parent_data = {
            "project_id": project_id,
            "title": "Parent Task",
            "description": "A parent task",
            "status": "todo",
            "priority": "high",
            "created_by": "test_user"
        }
        
        parent_response = client.post("/api/tasks", json=parent_data)
        assert parent_response.status_code == 201
        parent_task = parent_response.json()
        parent_id = parent_task["id"]
        
        # Create subtask
        subtask_data = {
            "project_id": project_id,
            "parent_id": parent_id,
            "title": "Subtask",
            "description": "A subtask",
            "status": "todo",
            "priority": "medium",
            "created_by": "test_user"
        }
        
        subtask_response = client.post("/api/tasks", json=subtask_data)
        assert subtask_response.status_code == 201
        subtask = subtask_response.json()
        assert subtask["parent_id"] == parent_id
        
        # Get parent task with subtasks
        get_parent_response = client.get(f"/api/tasks/{parent_id}")
        assert get_parent_response.status_code == 200
        parent_with_subtasks = get_parent_response.json()
        assert len(parent_with_subtasks["subtasks"]) == 1
        assert parent_with_subtasks["subtasks"][0]["title"] == "Subtask"
        
        # Test filtering by parent_id
        list_response = client.get(f"/api/tasks?parent_id={parent_id}")
        assert list_response.status_code == 200
        filtered_tasks = list_response.json()
        assert len(filtered_tasks["tasks"]) == 1
        assert filtered_tasks["tasks"][0]["title"] == "Subtask"

    def test_task_filtering_and_pagination(self, client, test_project):
        """Test task filtering and pagination functionality."""
        project_id = test_project["id"]
        
        # Create multiple tasks with different attributes
        tasks_data = [
            {
                "project_id": project_id,
                "title": "High Priority Task",
                "status": "todo",
                "priority": "high",
                "assignee": "user1",
                "created_by": "user1"
            },
            {
                "project_id": project_id,
                "title": "In Progress Task",
                "status": "in_progress",
                "priority": "medium",
                "assignee": "user2",
                "created_by": "user2"
            },
            {
                "project_id": project_id,
                "title": "Low Priority Task",
                "status": "todo",
                "priority": "low",
                "assignee": "user1",
                "created_by": "user1"
            }
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            create_response = client.post("/api/tasks", json=task_data)
            assert create_response.status_code == 201
            created_tasks.append(create_response.json())
        
        # Test filtering by project_id
        response = client.get(f"/api/tasks?project_id={project_id}")
        assert response.status_code == 200
        project_tasks = response.json()
        assert len(project_tasks["tasks"]) == 3
        
        # Test filtering by status
        response = client.get(f"/api/tasks?project_id={project_id}&status=todo")
        assert response.status_code == 200
        todo_tasks = response.json()
        todo_task_list = [t for t in todo_tasks["tasks"] if t["status"] == "todo"]
        assert len(todo_task_list) == 2
        
        # Test filtering by priority
        response = client.get(f"/api/tasks?project_id={project_id}&priority=high")
        assert response.status_code == 200
        high_priority_tasks = response.json()
        high_priority_list = [t for t in high_priority_tasks["tasks"] if t["priority"] == "high"]
        assert len(high_priority_list) == 1
        assert high_priority_list[0]["title"] == "High Priority Task"
        
        # Test filtering by assignee
        response = client.get(f"/api/tasks?project_id={project_id}&assignee=user1")
        assert response.status_code == 200
        user1_tasks = response.json()
        user1_task_list = [t for t in user1_tasks["tasks"] if t["assignee"] == "user1"]
        assert len(user1_task_list) == 2

    def test_task_validation_errors(self, client, test_project):
        """Test validation errors are properly handled."""
        project_id = test_project["id"]
        
        # Test missing required fields
        invalid_data = {
            "project_id": project_id,
            "description": "Missing title and created_by"
        }
        
        response = client.post("/api/tasks", json=invalid_data)
        assert response.status_code == 422
        error_detail = response.json()
        assert "detail" in error_detail
        
        # Test invalid enum values
        invalid_data = {
            "project_id": project_id,
            "title": "Test Task",
            "status": "INVALID_STATUS",
            "priority": "INVALID_PRIORITY",
            "created_by": "test_user"
        }
        
        response = client.post("/api/tasks", json=invalid_data)
        assert response.status_code == 422

    def test_task_not_found_errors(self, client):
        """Test 404 errors for non-existent tasks."""
        # Test get non-existent task
        response = client.get("/api/tasks/nonexistent-id")
        assert response.status_code == 404
        
        # Test update non-existent task
        update_data = {"title": "Updated Title"}
        response = client.put("/api/tasks/nonexistent-id", json=update_data)
        assert response.status_code == 404
        
        # Test delete non-existent task
        response = client.delete("/api/tasks/nonexistent-id")
        assert response.status_code == 404

    def test_task_project_relationship_validation(self, client):
        """Test task-project relationship validation."""
        # Try to create task with non-existent project
        invalid_task_data = {
            "project_id": "nonexistent-project",
            "title": "Test Task",
            "created_by": "test_user"
        }
        
        response = client.post("/api/tasks", json=invalid_task_data)
        assert response.status_code == 404
        error_detail = response.json()
        assert "project" in error_detail["detail"].lower()
        assert "not found" in error_detail["detail"].lower()


class TestTaskRoutesErrorHandling:
    """Test error handling in task routes."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)

    def test_service_error_handling(self, client):
        """Test proper error handling when storage raises exceptions."""
        from src.api.task_routes import get_storage
        
        mock_storage = Mock()
        mock_storage.get_project.side_effect = Exception("Database error")
        
        app.dependency_overrides[get_storage] = lambda: mock_storage
        
        task_data = {
            "project_id": "test-project-1",
            "title": "Test Task",
            "created_by": "test_user"
        }
        
        response = client.post("/api/tasks", json=task_data)
        assert response.status_code == 500
        error_detail = response.json()
        assert "detail" in error_detail
        
        app.dependency_overrides.clear()

    def test_validation_error_handling(self, client):
        """Test validation error handling."""
        # Test malformed JSON
        response = client.post("/api/tasks", content="invalid json")
        assert response.status_code == 422
        
        # Test wrong content type
        response = client.post("/api/tasks", data="not json")
        assert response.status_code == 422