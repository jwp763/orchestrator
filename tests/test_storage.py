"""Tests for storage interface and SQL implementation."""

from datetime import date, datetime
from typing import Any
from unittest.mock import MagicMock, Mock
from unittest.mock import patch as mock_patch
from uuid import uuid4

import pytest

from src.models import Project, ProjectStatus, Task, TaskStatus, TaskPriority
from src.models.project import ProjectPriority
from src.models.patch import Op, Patch, ProjectPatch, TaskPatch
from src.storage.interface import StorageInterface
from src.storage.sql_implementation import SQLStorage


class TestStorageInterface:
    """Test the abstract storage interface."""

    def test_storage_interface_is_abstract(self) -> None:
        """Test that StorageInterface cannot be instantiated."""
        with pytest.raises(TypeError):
            StorageInterface()  # type: ignore


class TestSQLStorageUnit:
    """Unit tests for SQL storage implementation."""

    @pytest.fixture
    def mock_session(self) -> Mock:
        """Create a mock SQLAlchemy session."""
        return Mock()

    @pytest.fixture
    def storage(self, mock_session: Mock) -> SQLStorage:
        """Create SQLStorage instance with mocked session."""
        storage = SQLStorage("sqlite:///:memory:")
        storage._session = mock_session
        return storage

    def test_get_project_calls_session_query(self, storage: SQLStorage, mock_session: Mock) -> None:
        """Test that get_project calls the correct session methods."""
        project_id = str(uuid4())
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        result = storage.get_project(project_id)

        mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()
        assert result is None

    def test_create_project_calls_session_add(self, storage: SQLStorage, mock_session: Mock) -> None:
        """Test that create_project calls session.add."""
        project = Project(name="Test Project", created_by="test_user")

        with mock_patch.object(storage, "_convert_pydantic_project_to_sql") as mock_convert:
            mock_sql_project = Mock()
            mock_convert.return_value = mock_sql_project

            with mock_patch.object(storage, "_convert_sql_project_to_pydantic") as mock_convert_back:
                mock_convert_back.return_value = project

                result = storage.create_project(project)

                mock_session.add.assert_called_once_with(mock_sql_project)
                mock_session.flush.assert_called_once()
                assert result == project

    def test_update_project_calls_session_methods(self, storage: SQLStorage, mock_session: Mock) -> None:
        """Test that update_project calls the correct session methods."""
        project_id = str(uuid4())
        project = Project(id=project_id, name="Updated Project", created_by="test_user")

        # Mock the query to return an existing project
        mock_sql_project = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_sql_project

        with mock_patch.object(storage, "_convert_sql_project_to_pydantic") as mock_convert:
            mock_convert.return_value = project

            result = storage.update_project(project_id, project)

            mock_session.query.assert_called_once()
            mock_session.flush.assert_called_once()
            assert result == project

    def test_delete_project_calls_session_delete(self, storage: SQLStorage, mock_session: Mock) -> None:
        """Test that delete_project calls session.delete."""
        project_id = str(uuid4())

        # Mock the query to return an existing project
        mock_sql_project = Mock()
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_sql_project

        result = storage.delete_project(project_id)

        mock_session.delete.assert_called_once_with(mock_sql_project)
        mock_session.flush.assert_called_once()
        assert result is True

    def test_apply_project_patch_create_operation(self, storage: SQLStorage) -> None:
        """Test apply_project_patch handles create operation correctly."""
        patch = ProjectPatch(op=Op.CREATE, name="New Project", description="Test description", priority=ProjectPriority.MEDIUM)

        with mock_patch.object(storage, "create_project") as mock_create:
            expected_project = Project(name="New Project", created_by="system")
            mock_create.return_value = expected_project

            result = storage.apply_project_patch(patch)

            mock_create.assert_called_once()
            assert result == expected_project

    def test_apply_project_patch_update_operation(self, storage: SQLStorage) -> None:
        """Test apply_project_patch handles update operation correctly."""
        project_id = str(uuid4())
        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, name="Updated Project", priority=ProjectPriority.MEDIUM)

        existing_project = Project(id=project_id, name="Old Project", created_by="test_user")

        with mock_patch.object(storage, "get_project") as mock_get:
            with mock_patch.object(storage, "update_project") as mock_update:
                mock_get.return_value = existing_project
                mock_update.return_value = existing_project

                result = storage.apply_project_patch(patch)

                mock_get.assert_called_once_with(project_id)
                mock_update.assert_called_once()
                assert result == existing_project

    def test_apply_project_patch_delete_operation(self, storage: SQLStorage) -> None:
        """Test apply_project_patch handles delete operation correctly."""
        project_id = str(uuid4())
        patch = ProjectPatch(op=Op.DELETE, project_id=project_id, priority=ProjectPriority.MEDIUM)

        with mock_patch.object(storage, "delete_project") as mock_delete:
            mock_delete.return_value = True

            result = storage.apply_project_patch(patch)

            mock_delete.assert_called_once_with(project_id)
            assert result is not None
            assert result.id == project_id

    def test_apply_task_patch_create_operation(self, storage: SQLStorage) -> None:
        """Test apply_task_patch handles create operation correctly."""
        project_id = str(uuid4())
        patch = TaskPatch(op=Op.CREATE, project_id=project_id, title="New Task")

        with mock_patch.object(storage, "create_task") as mock_create:
            expected_task = Task(project_id=project_id, title="New Task", created_by="system")
            mock_create.return_value = expected_task

            result = storage.apply_task_patch(patch)

            mock_create.assert_called_once()
            assert result == expected_task

    def test_apply_task_patch_update_operation(self, storage: SQLStorage) -> None:
        """Test apply_task_patch handles update operation correctly."""
        task_id = str(uuid4())
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, title="Updated Task")

        existing_task = Task(id=task_id, project_id=str(uuid4()), title="Old Task", created_by="test_user")

        with mock_patch.object(storage, "get_task") as mock_get:
            with mock_patch.object(storage, "update_task") as mock_update:
                mock_get.return_value = existing_task
                mock_update.return_value = existing_task

                result = storage.apply_task_patch(patch)

                mock_get.assert_called_once_with(task_id)
                mock_update.assert_called_once()
                assert result == existing_task

    def test_apply_task_patch_delete_operation(self, storage: SQLStorage) -> None:
        """Test apply_task_patch handles delete operation correctly."""
        task_id = str(uuid4())
        patch = TaskPatch(op=Op.DELETE, task_id=task_id)

        with mock_patch.object(storage, "delete_task") as mock_delete:
            mock_delete.return_value = True

            result = storage.apply_task_patch(patch)

            mock_delete.assert_called_once_with(task_id)
            assert result is not None
            assert result.id == task_id


class TestSQLStorageIntegration:
    """Integration tests for SQL storage implementation."""

    @pytest.fixture
    def storage(self) -> SQLStorage:
        """Create SQLStorage instance with in-memory SQLite database."""
        return SQLStorage("sqlite:///:memory:")

    def test_project_lifecycle_full_crud(self, storage: SQLStorage) -> None:
        """Test full project lifecycle: create, read, update, delete."""
        # Create project
        project = Project(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="test_user",
        )

        created_project = storage.create_project(project)
        assert created_project.name == "Test Project"
        assert created_project.id is not None

        # Read project
        retrieved_project = storage.get_project(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.name == "Test Project"
        assert retrieved_project.description == "Test description"

        # Update project
        retrieved_project.name = "Updated Project"
        retrieved_project.status = ProjectStatus.COMPLETED

        updated_project = storage.update_project(retrieved_project.id, retrieved_project)
        assert updated_project is not None
        assert updated_project.name == "Updated Project"
        assert updated_project.status == ProjectStatus.COMPLETED

        # Delete project
        delete_success = storage.delete_project(updated_project.id)
        assert delete_success is True

        # Verify deletion
        deleted_project = storage.get_project(updated_project.id)
        assert deleted_project is None

    def test_task_lifecycle_full_crud(self, storage: SQLStorage) -> None:
        """Test full task lifecycle: create, read, update, delete."""
        # First create a project
        project = Project(name="Test Project", created_by="test_user")
        created_project = storage.create_project(project)

        # Create task
        task = Task(
            project_id=created_project.id,
            title="Test Task",
            description="Test task description",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            created_by="test_user",
        )

        created_task = storage.create_task(task)
        assert created_task.title == "Test Task"
        assert created_task.id is not None

        # Read task
        retrieved_task = storage.get_task(created_task.id)
        assert retrieved_task is not None
        assert retrieved_task.title == "Test Task"
        assert retrieved_task.description == "Test task description"

        # Update task
        retrieved_task.title = "Updated Task"
        retrieved_task.status = TaskStatus.COMPLETED

        updated_task = storage.update_task(retrieved_task.id, retrieved_task)
        assert updated_task is not None
        assert updated_task.title == "Updated Task"
        assert updated_task.status == TaskStatus.COMPLETED

        # Delete task
        delete_success = storage.delete_task(updated_task.id)
        assert delete_success is True

        # Verify deletion
        deleted_task = storage.get_task(updated_task.id)
        assert deleted_task is None

    def test_get_tasks_by_project(self, storage: SQLStorage) -> None:
        """Test retrieving all tasks for a project."""
        # Create project
        project = Project(name="Test Project", created_by="test_user")
        created_project = storage.create_project(project)

        # Create multiple tasks
        task1 = Task(project_id=created_project.id, title="Task 1", created_by="test_user")
        task2 = Task(project_id=created_project.id, title="Task 2", created_by="test_user")

        storage.create_task(task1)
        storage.create_task(task2)

        # Retrieve tasks by project
        tasks = storage.get_tasks_by_project(created_project.id)
        assert len(tasks) == 2
        task_titles = [task.title for task in tasks]
        assert "Task 1" in task_titles
        assert "Task 2" in task_titles

    def test_apply_patch_success_with_rollback_on_failure(self, storage: SQLStorage) -> None:
        """Test that patch application is atomic - all succeed or all fail."""
        # Create a project first and commit it
        project = Project(name="Test Project", created_by="test_user")
        created_project = storage.create_project(project)
        storage.commit_transaction()  # Ensure initial project is committed

        # Create a valid patch
        valid_patch = Patch(
            project_patches=[ProjectPatch(op=Op.CREATE, name="New Project", priority=ProjectPriority.MEDIUM)],
            task_patches=[TaskPatch(op=Op.CREATE, project_id=created_project.id, title="New Task")],
        )

        # Apply valid patch
        result = storage.apply_patch(valid_patch)
        assert result is True

        # Verify the operations were applied in a new transaction
        storage.begin_transaction()
        projects = storage.get_projects()
        assert len(projects) == 2  # Original + new project

        tasks = storage.get_tasks_by_project(created_project.id)
        assert len(tasks) == 1
        assert tasks[0].title == "New Task"
        storage.commit_transaction()

    def test_transaction_rollback_on_patch_failure(self, storage: SQLStorage) -> None:
        """Test that if one part of a patch fails, the entire transaction is rolled back."""
        # Create a project and commit it
        project = Project(name="Test Project", created_by="test_user")
        created_project = storage.create_project(project)
        storage.commit_transaction()  # Ensure it's committed

        # Get initial state in a new transaction
        storage.begin_transaction()
        initial_projects = storage.get_projects()
        initial_project_count = len(initial_projects)
        storage.commit_transaction()

        # Create a patch with one valid and one invalid operation
        mixed_patch = Patch(
            project_patches=[ProjectPatch(op=Op.CREATE, name="Valid Project", priority=ProjectPriority.MEDIUM)],
            task_patches=[
                # Invalid task patch - missing required project_id
                TaskPatch(op=Op.CREATE, title="Invalid Task")  # No project_id
            ],
        )

        # Apply patch (should fail)
        result = storage.apply_patch(mixed_patch)
        assert result is False

        # Verify rollback - should have same number of projects as before
        storage.begin_transaction()
        final_projects = storage.get_projects()
        storage.commit_transaction()
        assert len(final_projects) == initial_project_count

        # The "Valid Project" should not exist due to rollback
        project_names = [p.name for p in final_projects]
        assert "Valid Project" not in project_names

    def test_project_task_relationship(self, storage: SQLStorage) -> None:
        """Test that projects correctly include their tasks."""
        # Create project
        project = Project(name="Parent Project", created_by="test_user")
        created_project = storage.create_project(project)

        # Create tasks for the project
        task1 = Task(project_id=created_project.id, title="Child Task 1", created_by="test_user")
        task2 = Task(project_id=created_project.id, title="Child Task 2", created_by="test_user")

        storage.create_task(task1)
        storage.create_task(task2)

        # Retrieve project with tasks
        project_with_tasks = storage.get_project(created_project.id)
        assert project_with_tasks is not None
        assert len(project_with_tasks.tasks) == 2

        task_titles = [task.title for task in project_with_tasks.tasks]
        assert "Child Task 1" in task_titles
        assert "Child Task 2" in task_titles
