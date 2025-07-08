"""Tests for core Pydantic schemas."""

import pytest
from datetime import datetime, date
from uuid import uuid4

from src.models.schemas import (
    Task, Project, TaskPatch, ProjectPatch, Patch,
    TaskStatus, ProjectStatus, Priority, Op
)


class TestTaskSchema:
    """Test Task schema validation and functionality."""

    def test_task_creation_with_valid_data(self):
        """Test successful creation of Task with valid data."""
        task_data = {
            "project_id": str(uuid4()),
            "title": "Test Task",
            "description": "Test description",
            "status": TaskStatus.PENDING,
            "priority": Priority.HIGH,
            "created_by": "test_user"
        }
        
        task = Task(**task_data)
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.HIGH
        assert task.id is not None
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_task_creation_with_minimal_data(self):
        """Test Task creation with only required fields."""
        task = Task(
            project_id=str(uuid4()),
            title="Minimal Task",
            created_by="test_user"
        )
        
        assert task.title == "Minimal Task"
        assert task.status == TaskStatus.PENDING
        assert task.priority == Priority.MEDIUM
        assert task.tags == []
        assert task.labels == []

    def test_task_validation_missing_required_fields(self):
        """Test Task validation errors for missing required fields."""
        with pytest.raises(ValueError):
            Task(title="Task without project_id")
        
        with pytest.raises(ValueError):
            Task(project_id=str(uuid4()))
        
        with pytest.raises(ValueError):
            Task(project_id=str(uuid4()), title="Task without created_by")

    def test_task_validation_invalid_status(self):
        """Test Task validation with invalid status."""
        with pytest.raises(ValueError):
            Task(
                project_id=str(uuid4()),
                title="Test Task",
                status="invalid_status",
                created_by="test_user"
            )

    def test_task_completed_at_auto_set(self):
        """Test that completed_at is automatically set when status is COMPLETED."""
        task = Task(
            project_id=str(uuid4()),
            title="Test Task",
            status=TaskStatus.COMPLETED,
            created_by="test_user"
        )
        assert task.completed_at is not None

    def test_task_json_serialization(self):
        """Test Task JSON serialization."""
        task = Task(
            project_id=str(uuid4()),
            title="Test Task",
            created_by="test_user"
        )
        
        json_data = task.model_dump_json()
        assert "Test Task" in json_data
        assert "project_id" in json_data

    def test_task_json_deserialization(self):
        """Test Task JSON deserialization."""
        task_data = {
            "project_id": str(uuid4()),
            "title": "Test Task",
            "created_by": "test_user"
        }
        
        task = Task(**task_data)
        json_data = task.model_dump_json()
        
        # Deserialize back
        task_dict = Task.model_validate_json(json_data)
        assert task_dict.title == "Test Task"


class TestProjectSchema:
    """Test Project schema validation and functionality."""

    def test_project_creation_with_valid_data(self):
        """Test successful creation of Project with valid data."""
        project_data = {
            "name": "Test Project",
            "description": "Test description",
            "status": ProjectStatus.ACTIVE,
            "priority": 5,
            "created_by": "test_user"
        }
        
        project = Project(**project_data)
        assert project.name == "Test Project"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == 5
        assert project.id is not None
        assert project.created_at is not None

    def test_project_creation_with_minimal_data(self):
        """Test Project creation with only required fields."""
        project = Project(
            name="Minimal Project",
            created_by="test_user"
        )
        
        assert project.name == "Minimal Project"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == 3
        assert project.tasks == []

    def test_project_validation_missing_required_fields(self):
        """Test Project validation errors for missing required fields."""
        with pytest.raises(ValueError):
            Project(created_by="test_user")
        
        with pytest.raises(ValueError):
            Project(name="Project without created_by")

    def test_project_validation_invalid_priority(self):
        """Test Project validation with invalid priority."""
        with pytest.raises(ValueError):
            Project(
                name="Test Project",
                priority=0,  # Below minimum
                created_by="test_user"
            )
        
        with pytest.raises(ValueError):
            Project(
                name="Test Project",
                priority=6,  # Above maximum
                created_by="test_user"
            )

    def test_project_task_count_properties(self):
        """Test Project task count properties."""
        project = Project(
            name="Test Project",
            created_by="test_user"
        )
        
        # Add some tasks
        task1 = Task(
            project_id=project.id,
            title="Task 1",
            status=TaskStatus.COMPLETED,
            created_by="test_user"
        )
        task2 = Task(
            project_id=project.id,
            title="Task 2",
            status=TaskStatus.PENDING,
            created_by="test_user"
        )
        
        project.tasks = [task1, task2]
        
        assert project.task_count == 2
        assert project.completed_task_count == 1

    def test_project_json_serialization(self):
        """Test Project JSON serialization."""
        project = Project(
            name="Test Project",
            created_by="test_user"
        )
        
        json_data = project.model_dump_json()
        assert "Test Project" in json_data
        assert "created_by" in json_data

    def test_project_json_deserialization(self):
        """Test Project JSON deserialization."""
        project_data = {
            "name": "Test Project",
            "created_by": "test_user"
        }
        
        project = Project(**project_data)
        json_data = project.model_dump_json()
        
        # Deserialize back
        project_dict = Project.model_validate_json(json_data)
        assert project_dict.name == "Test Project"


class TestTaskPatchSchema:
    """Test TaskPatch schema validation and functionality."""

    def test_task_patch_create_operation(self):
        """Test TaskPatch for create operation."""
        patch = TaskPatch(
            op=Op.CREATE,
            project_id=str(uuid4()),
            title="New Task",
            status=TaskStatus.PENDING
        )
        
        assert patch.op == Op.CREATE
        assert patch.title == "New Task"
        assert patch.task_id is None  # Not required for create

    def test_task_patch_update_operation(self):
        """Test TaskPatch for update operation."""
        patch = TaskPatch(
            op=Op.UPDATE,
            task_id=str(uuid4()),
            title="Updated Task",
            status=TaskStatus.COMPLETED
        )
        
        assert patch.op == Op.UPDATE
        assert patch.task_id is not None
        assert patch.title == "Updated Task"

    def test_task_patch_delete_operation(self):
        """Test TaskPatch for delete operation."""
        patch = TaskPatch(
            op=Op.DELETE,
            task_id=str(uuid4())
        )
        
        assert patch.op == Op.DELETE
        assert patch.task_id is not None

    def test_task_patch_validation_missing_task_id(self):
        """Test TaskPatch validation when task_id is missing for update/delete."""
        with pytest.raises(ValueError):
            TaskPatch(op=Op.UPDATE, title="Updated Task")
        
        with pytest.raises(ValueError):
            TaskPatch(op=Op.DELETE)

    def test_task_patch_json_serialization(self):
        """Test TaskPatch JSON serialization."""
        patch = TaskPatch(
            op=Op.CREATE,
            project_id=str(uuid4()),
            title="New Task"
        )
        
        json_data = patch.model_dump_json()
        assert "create" in json_data  # Enum is serialized as lowercase
        assert "New Task" in json_data

    def test_task_patch_json_deserialization(self):
        """Test TaskPatch JSON deserialization."""
        patch_data = {
            "op": "create",
            "project_id": str(uuid4()),
            "title": "New Task"
        }
        
        patch = TaskPatch(**patch_data)
        json_data = patch.model_dump_json()
        
        # Deserialize back
        patch_dict = TaskPatch.model_validate_json(json_data)
        assert patch_dict.op == Op.CREATE
        assert patch_dict.title == "New Task"


class TestProjectPatchSchema:
    """Test ProjectPatch schema validation and functionality."""

    def test_project_patch_create_operation(self):
        """Test ProjectPatch for create operation."""
        patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project",
            description="New project description"
        )
        
        assert patch.op == Op.CREATE
        assert patch.name == "New Project"
        assert patch.project_id is None  # Not required for create

    def test_project_patch_update_operation(self):
        """Test ProjectPatch for update operation."""
        patch = ProjectPatch(
            op=Op.UPDATE,
            project_id=str(uuid4()),
            name="Updated Project",
            status=ProjectStatus.COMPLETED
        )
        
        assert patch.op == Op.UPDATE
        assert patch.project_id is not None
        assert patch.name == "Updated Project"

    def test_project_patch_validation_missing_project_id(self):
        """Test ProjectPatch validation when project_id is missing for update/delete."""
        with pytest.raises(ValueError):
            ProjectPatch(op=Op.UPDATE, name="Updated Project")
        
        with pytest.raises(ValueError):
            ProjectPatch(op=Op.DELETE)

    def test_project_patch_json_serialization(self):
        """Test ProjectPatch JSON serialization."""
        patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project"
        )
        
        json_data = patch.model_dump_json()
        assert "create" in json_data  # Enum is serialized as lowercase
        assert "New Project" in json_data

    def test_project_patch_json_deserialization(self):
        """Test ProjectPatch JSON deserialization."""
        patch_data = {
            "op": "create",
            "name": "New Project"
        }
        
        patch = ProjectPatch(**patch_data)
        json_data = patch.model_dump_json()
        
        # Deserialize back
        patch_dict = ProjectPatch.model_validate_json(json_data)
        assert patch_dict.op == Op.CREATE
        assert patch_dict.name == "New Project"


class TestPatchSchema:
    """Test Patch schema validation and functionality."""

    def test_patch_with_project_patches(self):
        """Test Patch with project patches."""
        project_patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project"
        )
        
        patch = Patch(project_patches=[project_patch])
        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 0

    def test_patch_with_task_patches(self):
        """Test Patch with task patches."""
        task_patch = TaskPatch(
            op=Op.CREATE,
            project_id=str(uuid4()),
            title="New Task"
        )
        
        patch = Patch(task_patches=[task_patch])
        assert len(patch.task_patches) == 1
        assert len(patch.project_patches) == 0

    def test_patch_with_both_patches(self):
        """Test Patch with both project and task patches."""
        project_patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project"
        )
        task_patch = TaskPatch(
            op=Op.CREATE,
            project_id=str(uuid4()),
            title="New Task"
        )
        
        patch = Patch(
            project_patches=[project_patch],
            task_patches=[task_patch]
        )
        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 1

    def test_patch_json_serialization(self):
        """Test Patch JSON serialization."""
        project_patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project"
        )
        
        patch = Patch(project_patches=[project_patch])
        json_data = patch.model_dump_json()
        assert "project_patches" in json_data
        assert "New Project" in json_data

    def test_patch_json_deserialization(self):
        """Test Patch JSON deserialization."""
        patch_data = {
            "project_patches": [
                {
                    "op": "create",
                    "name": "New Project"
                }
            ],
            "task_patches": []
        }
        
        patch = Patch(**patch_data)
        json_data = patch.model_dump_json()
        
        # Deserialize back
        patch_dict = Patch.model_validate_json(json_data)
        assert len(patch_dict.project_patches) == 1
        assert patch_dict.project_patches[0].name == "New Project"