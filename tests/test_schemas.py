"""Tests for core Pydantic schemas."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.models import Project, Task, ProjectStatus, TaskStatus, TaskPriority, ProjectPriority
from src.models.patches import Op, Patch, ProjectPatch, TaskPatch


class TestTaskSchema:
    """Test Task schema validation and functionality."""

    def test_task_creation_with_valid_data(self) -> None:
        """Test successful creation of Task with valid data."""
        task = Task(
            project_id=str(uuid4()),
            title="Test Task",
            description="Test description",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            created_by="test_user",
        )
        assert task.title == "Test Task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.HIGH
        assert task.id is not None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_creation_with_minimal_data(self) -> None:
        """Test Task creation with only required fields."""
        task = Task(project_id=str(uuid4()), title="Minimal Task", created_by="test_user")

        assert task.title == "Minimal Task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.tags == []
        assert task.labels == []

    def test_task_validation_missing_required_fields(self) -> None:
        """Test Task validation errors for missing required fields."""
        with pytest.raises(ValueError):
            Task(title="Task without project_id")  # type: ignore

        with pytest.raises(ValueError):
            Task(project_id=str(uuid4()))  # type: ignore

        with pytest.raises(ValueError):
            Task(project_id=str(uuid4()), title="Task without created_by")  # type: ignore

    def test_task_validation_invalid_status(self) -> None:
        """Test Task validation with invalid status."""
        with pytest.raises(ValueError):
            Task(project_id=str(uuid4()), title="Test Task", status="invalid_status", created_by="test_user")  # type: ignore

    def test_task_completed_at_auto_set(self) -> None:
        """Test that completed_at is automatically set when status is COMPLETED."""
        task = Task(project_id=str(uuid4()), title="Test Task", status=TaskStatus.COMPLETED, created_by="test_user")
        assert task.completed_at is not None

    def test_task_json_serialization(self) -> None:
        """Test Task JSON serialization."""
        task = Task(project_id=str(uuid4()), title="Test Task", created_by="test_user")

        json_data = task.model_dump_json()
        assert "Test Task" in json_data
        assert "project_id" in json_data

    def test_task_json_deserialization(self) -> None:
        """Test Task JSON deserialization."""
        task = Task(project_id=str(uuid4()), title="Test Task", created_by="test_user")
        json_data = task.model_dump_json()

        # Deserialize back
        task_dict = Task.model_validate_json(json_data)
        assert task_dict.title == "Test Task"


class TestProjectSchema:
    """Test Project schema validation and functionality."""

    def test_project_creation_with_valid_data(self) -> None:
        """Test successful creation of Project with valid data."""
        project = Project(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user",
        )
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.id is not None
        assert project.created_at is not None

    def test_project_creation_with_minimal_data(self) -> None:
        """Test Project creation with only required fields."""
        project = Project(name="Minimal Project", created_by="test_user")

        assert project.name == "Minimal Project"
        assert project.status == ProjectStatus.PLANNING
        assert project.priority == ProjectPriority.MEDIUM
        assert project.tasks == []

    def test_project_validation_missing_required_fields(self) -> None:
        """Test Project validation errors for missing required fields."""
        with pytest.raises(ValueError):
            Project(created_by="test_user")  # type: ignore

        with pytest.raises(ValueError):
            Project(name="Project without created_by")  # type: ignore

    def test_project_validation_invalid_priority(self) -> None:
        """Test Project validation with invalid priority."""
        with pytest.raises(ValueError):
            Project(name="Test Project", priority="invalid_priority", created_by="test_user")  # Invalid enum value

    def test_project_task_count_properties(self) -> None:
        """Test Project task count properties."""
        project = Project(name="Test Project", created_by="test_user")

        # Add some tasks
        task1 = Task(project_id=project.id, title="Task 1", status=TaskStatus.COMPLETED, created_by="test_user")
        task2 = Task(project_id=project.id, title="Task 2", status=TaskStatus.TODO, created_by="test_user")

        project.tasks = [task1, task2]

        assert project.task_count == 2
        assert project.completed_task_count == 1

    def test_project_json_serialization(self) -> None:
        """Test Project JSON serialization."""
        project = Project(name="Test Project", created_by="test_user")

        json_data = project.model_dump_json()
        assert "Test Project" in json_data
        assert "created_by" in json_data

    def test_project_json_deserialization(self) -> None:
        """Test Project JSON deserialization."""
        project = Project(name="Test Project", created_by="test_user")
        json_data = project.model_dump_json()

        # Deserialize back
        project_dict = Project.model_validate_json(json_data)
        assert project_dict.name == "Test Project"


class TestTaskPatchSchema:
    """Test TaskPatch schema validation and functionality."""

    def test_task_patch_create_operation(self) -> None:
        """Test TaskPatch for create operation."""
        patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task", status=TaskStatus.TODO)

        assert patch.op == Op.CREATE
        assert patch.title == "New Task"
        assert patch.task_id is None  # Not required for create

    def test_task_patch_update_operation(self) -> None:
        """Test TaskPatch for update operation."""
        patch = TaskPatch(op=Op.UPDATE, task_id=str(uuid4()), title="Updated Task", status=TaskStatus.COMPLETED)

        assert patch.op == Op.UPDATE
        assert patch.task_id is not None
        assert patch.title == "Updated Task"

    def test_task_patch_delete_operation(self) -> None:
        """Test TaskPatch for delete operation."""
        patch = TaskPatch(op=Op.DELETE, task_id=str(uuid4()))

        assert patch.op == Op.DELETE
        assert patch.task_id is not None

    def test_task_patch_validation_missing_task_id(self) -> None:
        """Test TaskPatch validation when task_id is missing for update/delete."""
        with pytest.raises(ValueError):
            TaskPatch(op=Op.UPDATE, title="Updated Task")

        with pytest.raises(ValueError):
            TaskPatch(op=Op.DELETE)

    def test_task_patch_json_serialization(self) -> None:
        """Test TaskPatch JSON serialization."""
        patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")

        json_data = patch.model_dump_json()
        assert "create" in json_data  # Enum is serialized as lowercase
        assert "New Task" in json_data

    def test_task_patch_json_deserialization(self) -> None:
        """Test TaskPatch JSON deserialization."""
        patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")
        json_data = patch.model_dump_json()

        # Deserialize back
        patch_dict = TaskPatch.model_validate_json(json_data)
        assert patch_dict.op == Op.CREATE
        assert patch_dict.title == "New Task"


class TestProjectPatchSchema:
    """Test ProjectPatch schema validation and functionality."""

    def test_project_patch_create_operation(self) -> None:
        """Test ProjectPatch for create operation."""
        patch = ProjectPatch(op=Op.CREATE, name="New Project", description="New project description")

        assert patch.op == Op.CREATE
        assert patch.name == "New Project"
        assert patch.project_id is None  # Not required for create

    def test_project_patch_update_operation(self) -> None:
        """Test ProjectPatch for update operation."""
        patch = ProjectPatch(
            op=Op.UPDATE, project_id=str(uuid4()), name="Updated Project", status=ProjectStatus.COMPLETED
        )

        assert patch.op == Op.UPDATE
        assert patch.project_id is not None
        assert patch.name == "Updated Project"

    def test_project_patch_validation_missing_project_id(self) -> None:
        """Test ProjectPatch validation when project_id is missing for update/delete."""
        with pytest.raises(ValueError):
            ProjectPatch(op=Op.UPDATE, name="Updated Project")

        with pytest.raises(ValueError):
            ProjectPatch(op=Op.DELETE)

    def test_project_patch_json_serialization(self) -> None:
        """Test ProjectPatch JSON serialization."""
        patch = ProjectPatch(op=Op.CREATE, name="New Project")

        json_data = patch.model_dump_json()
        assert "create" in json_data  # Enum is serialized as lowercase
        assert "New Project" in json_data

    def test_project_patch_json_deserialization(self) -> None:
        """Test ProjectPatch JSON deserialization."""
        patch = ProjectPatch(op=Op.CREATE, name="New Project")
        json_data = patch.model_dump_json()

        # Deserialize back
        patch_dict = ProjectPatch.model_validate_json(json_data)
        assert patch_dict.op == Op.CREATE
        assert patch_dict.name == "New Project"


class TestPatchSchema:
    """Test Patch schema validation and functionality."""

    def test_patch_with_project_patches(self) -> None:
        """Test Patch with project patches."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")

        patch = Patch(project_patches=[project_patch])
        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 0

    def test_patch_with_task_patches(self) -> None:
        """Test Patch with task patches."""
        task_patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")

        patch = Patch(task_patches=[task_patch])
        assert len(patch.task_patches) == 1
        assert len(patch.project_patches) == 0

    def test_patch_with_both_patches(self) -> None:
        """Test Patch with both project and task patches."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")
        task_patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")

        patch = Patch(project_patches=[project_patch], task_patches=[task_patch])
        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 1

    def test_patch_json_serialization(self) -> None:
        """Test Patch JSON serialization."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")

        patch = Patch(project_patches=[project_patch])
        json_data = patch.model_dump_json()
        assert "project_patches" in json_data
        assert "New Project" in json_data

    def test_patch_json_deserialization(self) -> None:
        """Test Patch JSON deserialization."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")
        patch = Patch(project_patches=[project_patch], task_patches=[])
        json_data = patch.model_dump_json()

        # Deserialize back
        patch_dict = Patch.model_validate_json(json_data)
        assert len(patch_dict.project_patches) == 1
        assert patch_dict.project_patches[0].name == "New Project"
