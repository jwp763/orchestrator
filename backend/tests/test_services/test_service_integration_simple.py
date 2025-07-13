"""
Simple integration tests for orchestration services.

Tests basic functionality of the service layer with real storage
to verify the services work correctly.
"""

import pytest
from ..test_api.test_database_isolation import TestDatabaseIsolation
from src.orchestration.project_service import ProjectService
from src.orchestration.task_service import TaskService
from src.orchestration.agent_service import AgentService
from src.models.project import ProjectCreate, ProjectStatus, ProjectPriority
from src.models.task import TaskCreate, TaskStatus, TaskPriority


class TestServiceIntegrationSimple(TestDatabaseIsolation):
    """Simple integration tests for services with real storage."""

    @pytest.fixture
    def project_service(self, isolated_storage):
        """ProjectService with isolated database."""
        return ProjectService(storage=isolated_storage)

    @pytest.fixture
    def task_service(self, isolated_storage):
        """TaskService with isolated database."""
        return TaskService(storage=isolated_storage)

    @pytest.fixture
    def agent_service(self, isolated_storage):
        """AgentService with isolated database."""
        return AgentService(storage=isolated_storage)

    def test_project_service_basic_operations(self, project_service):
        """Test basic ProjectService operations."""
        # Test service initialization
        assert project_service is not None
        assert project_service.storage is not None
        
        # Test project creation
        project_create = ProjectCreate(
            name="Test Project",
            description="A test project for service testing",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        
        created_project = project_service.create_project(project_create, "test_user")
        assert created_project is not None
        assert created_project.name == "Test Project"
        assert created_project.id is not None
        
        # Test project retrieval
        retrieved_project = project_service.get_project(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        
        # Test project listing
        projects = project_service.list_projects()
        project_ids = [p.id for p in projects]
        assert created_project.id in project_ids

    def test_task_service_basic_operations(self, task_service, project_service):
        """Test basic TaskService operations."""
        # Create a project first
        project_create = ProjectCreate(
            name="Task Test Project",
            description="Project for task testing",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="test_user"
        )
        project = project_service.create_project(project_create, "test_user")
        
        # Test task creation
        task_create = TaskCreate(
            title="Test Task",
            description="A test task for service testing",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=project.id,
            created_by="test_user"
        )
        
        created_task = task_service.create_task(task_create, "test_user")
        assert created_task is not None
        assert created_task.title == "Test Task"
        assert created_task.project_id == project.id
        assert created_task.id is not None
        
        # Test task retrieval (without subtasks to get just the task)
        retrieved_task = task_service.get_task(created_task.id, include_subtasks=False)
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        
        # Test task listing
        tasks = task_service.list_tasks()
        assert isinstance(tasks, list)
        task_ids = [t.id for t in tasks]
        assert created_task.id in task_ids

    def test_agent_service_initialization(self, agent_service):
        """Test AgentService initialization and basic functionality."""
        # Test service initialization
        assert agent_service is not None
        assert agent_service.storage is not None
        assert agent_service.project_service is not None
        assert agent_service.task_service is not None
        assert agent_service.planner_agent is not None
        
        # Test that services are properly initialized
        assert isinstance(agent_service.project_service, ProjectService)
        assert isinstance(agent_service.task_service, TaskService)

    def test_service_layer_integration(self, project_service, task_service, agent_service):
        """Test integration between different services."""
        # Create project using project service
        project_create = ProjectCreate(
            name="Integration Test Project",
            description="Testing service integration",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="integration_user"
        )
        project = project_service.create_project(project_create, "integration_user")
        
        # Create task using task service
        task_create = TaskCreate(
            title="Integration Test Task",
            description="Testing service integration",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id=project.id,
            created_by="integration_user"
        )
        task = task_service.create_task(task_create, "integration_user")
        
        # Verify services can access each other's data
        # Agent service should be able to see project
        agent_project = agent_service.project_service.get_project(project.id)
        assert agent_project is not None
        assert agent_project.id == project.id
        
        # Agent service should be able to see task
        agent_task = agent_service.task_service.get_task(task.id, include_subtasks=False)
        assert agent_task is not None
        assert agent_task.id == task.id
        
        # Verify task is linked to project
        assert agent_task.project_id == agent_project.id

    def test_error_handling_basic(self, project_service, task_service):
        """Test basic error handling in services."""
        # Test getting non-existent project
        non_existent_project = project_service.get_project("nonexistent-id")
        assert non_existent_project is None
        
        # Test getting non-existent task
        non_existent_task = task_service.get_task("nonexistent-id", include_subtasks=False)
        assert non_existent_task is None
        
        # Test listing with empty database
        projects = project_service.list_projects()
        assert isinstance(projects, list)
        
        tasks = task_service.list_tasks()
        assert isinstance(tasks, list)