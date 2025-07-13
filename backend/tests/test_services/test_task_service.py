"""
Unit and integration tests for TaskService.

Tests the orchestration service layer for task-related business logic,
including hierarchical operations, unit tests with mocked dependencies,
and integration tests with real storage connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Optional

from ..test_api.test_database_isolation import TestDatabaseIsolation
from src.orchestration.task_service import TaskService
from src.storage.interface import StorageInterface
from src.storage.sql_implementation import SQLStorage
from src.models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
)
from src.models.project import ProjectCreate, ProjectStatus, ProjectPriority
from src.models.patch import Patch, TaskPatch, Op


class TestTaskServiceUnit:
    """Unit tests for TaskService with mocked dependencies."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage interface for unit tests."""
        return Mock(spec=StorageInterface)

    @pytest.fixture
    def task_service(self, mock_storage):
        """TaskService instance with mocked storage."""
        return TaskService(storage=mock_storage)

    @pytest.fixture
    def sample_task(self):
        """Sample task for testing."""
        return Task(
            id="test-task-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id="test-project-1",
            parent_id=None,
            assignee="test_user",
            tags=["test", "example"],
            estimated_minutes=120,
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def sample_task_create(self):
        """Sample task create data."""
        return TaskCreate(
            title="New Task",
            description="A new test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id="test-project-1",
            assignee="test_user",
            tags=["new", "test"],
            estimated_minutes=60,
            created_by="test_user"
        )

    def test_init_default_storage(self):
        """Test TaskService initialization with default storage."""
        service = TaskService()
        assert isinstance(service.storage, SQLStorage)

    def test_init_custom_storage(self, mock_storage):
        """Test TaskService initialization with custom storage."""
        service = TaskService(storage=mock_storage)
        assert service.storage is mock_storage

    def test_list_tasks_success(self, task_service, mock_storage, sample_task):
        """Test successful task listing."""
        mock_storage.list_tasks.return_value = {"tasks": [sample_task], "total": 1, "page": 1}
        
        result = task_service.list_tasks()
        
        assert len(result) == 1
        assert result[0] == sample_task
        mock_storage.list_tasks.assert_called_once_with(
            skip=0, limit=100, project_id=None, parent_id=None,
            status=None, priority=None, assignee=None
        )

    def test_list_tasks_with_filters(self, task_service, mock_storage):
        """Test task listing with various filters."""
        mock_storage.list_tasks.return_value = {"tasks": [], "total": 0, "page": 1}
        
        task_service.list_tasks(
            skip=10,
            limit=50,
            project_id="test-project-1",
            parent_id="parent-task-1",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            assignee="test_user"
        )
        
        mock_storage.list_tasks.assert_called_once_with(
            skip=10, limit=50, project_id="test-project-1", parent_id="parent-task-1",
            status=TaskStatus.IN_PROGRESS, priority=TaskPriority.HIGH, assignee="test_user"
        )

    def test_list_tasks_pagination_validation(self, task_service, mock_storage):
        """Test pagination parameter validation."""
        with pytest.raises(ValueError, match="Skip must be non-negative"):
            task_service.list_tasks(skip=-1)
        
        with pytest.raises(ValueError, match="Limit must be positive"):
            task_service.list_tasks(limit=0)
        
        with pytest.raises(ValueError, match="Limit must not exceed 1000"):
            task_service.list_tasks(limit=1001)

    def test_get_task_success(self, task_service, mock_storage, sample_task):
        """Test successful task retrieval."""
        mock_storage.get_task.return_value = sample_task
        
        result = task_service.get_task("test-task-1")
        
        assert result == sample_task
        mock_storage.get_task.assert_called_once_with("test-task-1")

    def test_get_task_not_found(self, task_service, mock_storage):
        """Test task retrieval when task doesn't exist."""
        mock_storage.get_task.return_value = None
        
        result = task_service.get_task("nonexistent")
        
        assert result is None
        mock_storage.get_task.assert_called_once_with("nonexistent")

    def test_create_task_success(self, task_service, mock_storage, sample_task_create, sample_task):
        """Test successful task creation."""
        mock_storage.get_project.return_value = Mock()  # Project exists
        mock_storage.create_task.return_value = sample_task
        
        result = task_service.create_task(sample_task_create)
        
        assert result == sample_task
        mock_storage.create_task.assert_called_once()
        
        # Verify the task passed to storage has correct data
        call_args = mock_storage.create_task.call_args[0][0]
        assert call_args.title == sample_task_create.title
        assert call_args.project_id == sample_task_create.project_id

    def test_create_task_invalid_project(self, task_service, mock_storage, sample_task_create):
        """Test task creation with invalid project ID."""
        mock_storage.get_project.return_value = None  # Project doesn't exist
        
        with pytest.raises(ValueError, match="Project with ID test-project-1 not found"):
            task_service.create_task(sample_task_create)
        
        mock_storage.create_task.assert_not_called()

    def test_create_task_invalid_parent(self, task_service, mock_storage, sample_task_create):
        """Test task creation with invalid parent task ID."""
        task_create_with_parent = sample_task_create.model_copy(update={"parent_id": "invalid-parent"})
        
        mock_storage.get_project.return_value = Mock()  # Project exists
        mock_storage.get_task.return_value = None  # Parent doesn't exist
        
        with pytest.raises(ValueError, match="Parent task with ID invalid-parent not found"):
            task_service.create_task(task_create_with_parent)
        
        mock_storage.create_task.assert_not_called()

    def test_create_task_validation_error(self, task_service, mock_storage):
        """Test task creation with invalid data."""
        invalid_create = TaskCreate(
            title="",  # Empty title should fail validation
            project_id="test-project-1",
            created_by="test_user"
        )
        
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task_service.create_task(invalid_create)
        
        mock_storage.create_task.assert_not_called()

    def test_update_task_success(self, task_service, mock_storage, sample_task):
        """Test successful task update."""
        update_data = TaskUpdate(
            title="Updated Task Title",
            description="Updated description",
            status=TaskStatus.IN_PROGRESS
        )
        updated_task = sample_task.model_copy(update={"title": "Updated Task Title"})
        
        mock_storage.get_task.return_value = sample_task
        mock_storage.update_task.return_value = updated_task
        
        result = task_service.update_task("test-task-1", update_data)
        
        assert result == updated_task
        mock_storage.update_task.assert_called_once()

    def test_update_task_not_found(self, task_service, mock_storage):
        """Test task update when task doesn't exist."""
        update_data = TaskUpdate(title="Updated Title")
        mock_storage.get_task.return_value = None
        
        with pytest.raises(ValueError, match="Task with ID test-task-1 not found"):
            task_service.update_task("test-task-1", update_data)
        
        mock_storage.update_task.assert_not_called()

    def test_delete_task_success(self, task_service, mock_storage, sample_task):
        """Test successful task deletion."""
        mock_storage.get_task.return_value = sample_task
        mock_storage.delete_task.return_value = True
        
        result = task_service.delete_task("test-task-1")
        
        assert result is True
        mock_storage.delete_task.assert_called_once_with("test-task-1")

    def test_delete_task_not_found(self, task_service, mock_storage):
        """Test task deletion when task doesn't exist."""
        mock_storage.get_task.return_value = None
        
        with pytest.raises(ValueError, match="Task with ID test-task-1 not found"):
            task_service.delete_task("test-task-1")
        
        mock_storage.delete_task.assert_not_called()

    def test_get_task_hierarchy_success(self, task_service, mock_storage):
        """Test successful task hierarchy retrieval."""
        parent_task = Mock()
        child_tasks = [Mock(), Mock()]
        mock_storage.get_task.return_value = parent_task
        mock_storage.get_task_children.return_value = child_tasks
        
        result = task_service.get_task_hierarchy("parent-task-1")
        
        assert result["task"] == parent_task
        assert result["children"] == child_tasks
        mock_storage.get_task.assert_called_once_with("parent-task-1")
        mock_storage.get_task_children.assert_called_once_with("parent-task-1")

    def test_get_task_hierarchy_not_found(self, task_service, mock_storage):
        """Test task hierarchy retrieval when task doesn't exist."""
        mock_storage.get_task.return_value = None
        
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.get_task_hierarchy("nonexistent")

    def test_apply_patch_success(self, task_service, mock_storage, sample_task):
        """Test successful patch application."""
        patch = TaskPatch(
            task_id="test-task-1",
            operations=[
                Op(op="replace", path="/title", value="Patched Task Title")
            ],
            created_by="test_user"
        )
        patched_task = sample_task.model_copy(update={"title": "Patched Task Title"})
        
        mock_storage.get_task.return_value = sample_task
        mock_storage.apply_task_patch.return_value = patched_task
        
        result = task_service.apply_patch(patch)
        
        assert result == patched_task
        mock_storage.apply_task_patch.assert_called_once_with(patch)

    def test_apply_patch_invalid_task(self, task_service, mock_storage):
        """Test patch application on non-existent task."""
        patch = TaskPatch(
            task_id="nonexistent",
            operations=[Op(op="replace", path="/title", value="New Title")],
            created_by="test_user"
        )
        
        mock_storage.get_task.return_value = None
        
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.apply_patch(patch)
        
        mock_storage.apply_task_patch.assert_not_called()


class TestTaskServiceIntegration(TestDatabaseIsolation):
    """Integration tests for TaskService with real storage."""

    @pytest.fixture
    def task_service(self, isolated_storage):
        """TaskService with isolated database."""
        return TaskService(storage=isolated_storage)

    @pytest.fixture
    def sample_project(self, isolated_storage):
        """Create a sample project for task tests."""
        from src.orchestration.project_service import ProjectService
        project_service = ProjectService(storage=isolated_storage)
        return project_service.create_project(ProjectCreate(
            name="Task Test Project",
            description="Project for task testing",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="test_user"
        ))

    @pytest.fixture
    def sample_task_create(self, sample_project):
        """Sample task create data for integration tests."""
        return TaskCreate(
            title="Integration Test Task",
            description="A task for integration testing",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=sample_project.id,
            assignee="integration_user",
            tags=["integration", "test"],
            estimated_minutes=90,
            created_by="integration_user"
        )

    def test_task_lifecycle_integration(self, task_service, sample_task_create):
        """Test complete task lifecycle with real storage."""
        # Create task
        created_task = task_service.create_task(sample_task_create)
        assert created_task is not None
        assert created_task.title == sample_task_create.title
        assert created_task.id is not None
        
        # Get task
        retrieved_task = task_service.get_task(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.id == created_task.id
        assert retrieved_task.title == created_task.title
        
        # Update task
        update_data = TaskUpdate(
            title="Updated Integration Task",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.MEDIUM
        )
        updated_task = task_service.update_task(created_task.id, update_data)
        assert updated_task.title == "Updated Integration Task"
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.priority == TaskPriority.MEDIUM
        
        # List tasks (should include our task)
        tasks = task_service.list_tasks()
        task_ids = [t.id for t in tasks]
        assert created_task.id in task_ids
        
        # Delete task
        deletion_result = task_service.delete_task(created_task.id)
        assert deletion_result is True
        
        # Verify deletion
        deleted_task = task_service.get_task(created_task.id)
        assert deleted_task is None

    def test_task_hierarchy_integration(self, task_service, sample_project):
        """Test task hierarchical operations with real storage."""
        # Create parent task
        parent_create = TaskCreate(
            title="Parent Task",
            description="A parent task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            project_id=sample_project.id,
            created_by="test_user"
        )
        parent_task = task_service.create_task(parent_create)
        
        # Create child tasks
        child1_create = TaskCreate(
            title="Child Task 1",
            description="First child task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id=sample_project.id,
            parent_id=parent_task.id,
            created_by="test_user"
        )
        child1 = task_service.create_task(child1_create)
        
        child2_create = TaskCreate(
            title="Child Task 2",
            description="Second child task",
            status=TaskStatus.TODO,
            priority=TaskPriority.LOW,
            project_id=sample_project.id,
            parent_id=parent_task.id,
            created_by="test_user"
        )
        child2 = task_service.create_task(child2_create)
        
        # Test hierarchy retrieval
        hierarchy = task_service.get_task_hierarchy(parent_task.id)
        assert hierarchy["task"].id == parent_task.id
        assert len(hierarchy["children"]) == 2
        child_ids = [child.id for child in hierarchy["children"]]
        assert child1.id in child_ids
        assert child2.id in child_ids

    def test_task_filtering_integration(self, task_service, sample_project):
        """Test task filtering with real storage."""
        # Create tasks with different properties
        task1 = task_service.create_task(TaskCreate(
            title="High Priority In Progress",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            project_id=sample_project.id,
            assignee="user1",
            created_by="test_user"
        ))
        task2 = task_service.create_task(TaskCreate(
            title="Medium Priority Todo",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            project_id=sample_project.id,
            assignee="user2",
            created_by="test_user"
        ))
        
        # Test status filtering
        in_progress_tasks = task_service.list_tasks(status=TaskStatus.IN_PROGRESS)
        in_progress_ids = [t.id for t in in_progress_tasks]
        assert task1.id in in_progress_ids
        assert task2.id not in in_progress_ids
        
        # Test priority filtering
        high_priority_tasks = task_service.list_tasks(priority=TaskPriority.HIGH)
        high_priority_ids = [t.id for t in high_priority_tasks]
        assert task1.id in high_priority_ids
        assert task2.id not in high_priority_ids
        
        # Test assignee filtering
        user1_tasks = task_service.list_tasks(assignee="user1")
        user1_ids = [t.id for t in user1_tasks]
        assert task1.id in user1_ids
        assert task2.id not in user1_ids
        
        # Test project filtering
        project_tasks = task_service.list_tasks(project_id=sample_project.id)
        project_task_ids = [t.id for t in project_tasks]
        assert task1.id in project_task_ids
        assert task2.id in project_task_ids

    def test_task_patch_integration(self, task_service, sample_task_create):
        """Test patch application with real storage."""
        # Create task
        task = task_service.create_task(sample_task_create)
        
        # Apply patch
        patch = TaskPatch(
            task_id=task.id,
            operations=[
                Op(op="replace", path="/title", value="Patched Task Title"),
                Op(op="replace", path="/priority", value="low"),
                Op(op="replace", path="/status", value="in_progress")
            ],
            created_by="patch_user"
        )
        
        patched_task = task_service.apply_patch(patch)
        assert patched_task.title == "Patched Task Title"
        assert patched_task.priority == TaskPriority.LOW
        assert patched_task.status == TaskStatus.IN_PROGRESS
        
        # Verify persistence
        retrieved_task = task_service.get_task(task.id)
        assert retrieved_task.title == "Patched Task Title"
        assert retrieved_task.priority == TaskPriority.LOW
        assert retrieved_task.status == TaskStatus.IN_PROGRESS

    def test_task_validation_integration(self, task_service, sample_project):
        """Test business rule validation with real storage."""
        # Test empty title validation
        with pytest.raises(ValueError, match="Task title cannot be empty"):
            task_service.create_task(TaskCreate(
                title="",
                project_id=sample_project.id,
                created_by="test_user"
            ))
        
        # Test invalid parent task validation
        with pytest.raises(ValueError, match="Parent task with ID nonexistent not found"):
            task_service.create_task(TaskCreate(
                title="Valid Title",
                project_id=sample_project.id,
                parent_id="nonexistent",
                created_by="test_user"
            ))

    def test_error_handling_integration(self, task_service):
        """Test error handling with real storage."""
        # Test operations on non-existent task
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.update_task("nonexistent", TaskUpdate(title="New Title"))
        
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.delete_task("nonexistent")
        
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.get_task_hierarchy("nonexistent")
        
        # Test invalid patch
        with pytest.raises(ValueError, match="Task with ID nonexistent not found"):
            task_service.apply_patch(TaskPatch(
                task_id="nonexistent",
                operations=[Op(op="replace", path="/title", value="New Title")],
                created_by="test_user"
            ))