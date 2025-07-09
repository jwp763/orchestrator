"""Comprehensive tests for patch models."""

from datetime import date
from uuid import uuid4

import pytest

from src.models.patch import Op, Patch, ProjectPatch, TaskPatch
from src.models.project import ProjectPriority, ProjectStatus
from src.models.task import TaskPriority, TaskStatus


class TestOp:
    """Test Op enum."""

    def test_all_op_values(self) -> None:
        """Test all operation enum values."""
        expected_values = ["create", "update", "delete"]
        actual_values = [op.value for op in Op]
        assert actual_values == expected_values

    def test_op_string_representation(self) -> None:
        """Test string representation of operation values."""
        assert Op.CREATE.value == "create"
        assert Op.UPDATE.value == "update"
        assert Op.DELETE.value == "delete"


class TestTaskPatch:
    """Test TaskPatch model."""

    def test_task_patch_create_operation_minimal(self) -> None:
        """Test TaskPatch for create operation with minimal fields."""
        patch = TaskPatch(op=Op.CREATE)

        assert patch.op == Op.CREATE
        assert patch.task_id is None
        assert patch.project_id is None
        assert patch.title is None
        assert patch.description is None
        assert patch.status is None
        assert patch.priority is None
        assert patch.due_date is None
        assert patch.estimated_minutes is None
        assert patch.actual_minutes is None
        assert patch.assignee is None
        assert patch.tags is None
        assert patch.labels is None
        assert patch.dependencies is None
        assert patch.metadata is None

        # Integration fields
        assert patch.motion_task_id is None
        assert patch.linear_issue_id is None
        assert patch.notion_task_id is None
        assert patch.gitlab_issue_id is None

    def test_task_patch_create_operation_full(self):
        """Test TaskPatch for create operation with all fields."""
        project_id = str(uuid4())
        dep_id = str(uuid4())
        today = date.today()

        patch = TaskPatch(
            op=Op.CREATE,
            project_id=project_id,
            title="New Task",
            description="Creating a new task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            due_date=today,
            estimated_minutes=120,
            actual_minutes=0,
            assignee="test_user",
            tags=["new", "feature"],
            labels=["backend"],
            dependencies=[dep_id],
            metadata={"version": "1.0"},
            motion_task_id="motion_123",
            linear_issue_id="linear_456",
            notion_task_id="notion_789",
            gitlab_issue_id="gitlab_101",
        )

        assert patch.op == Op.CREATE
        assert patch.project_id == project_id
        assert patch.title == "New Task"
        assert patch.description == "Creating a new task"
        assert patch.status == TaskStatus.TODO
        assert patch.priority == TaskPriority.HIGH
        assert patch.due_date == today
        assert patch.estimated_minutes == 120
        assert patch.actual_minutes == 0
        assert patch.assignee == "test_user"
        assert patch.tags == ["new", "feature"]
        assert patch.labels == ["backend"]
        assert patch.dependencies == [dep_id]
        assert patch.metadata == {"version": "1.0"}
        assert patch.motion_task_id == "motion_123"
        assert patch.linear_issue_id == "linear_456"
        assert patch.notion_task_id == "notion_789"
        assert patch.gitlab_issue_id == "gitlab_101"

    def test_task_patch_update_operation(self):
        """Test TaskPatch for update operation."""
        task_id = str(uuid4())

        patch = TaskPatch(
            op=Op.UPDATE, task_id=task_id, title="Updated Task", status=TaskStatus.COMPLETED, priority=TaskPriority.LOW
        )

        assert patch.op == Op.UPDATE
        assert patch.task_id == task_id
        assert patch.title == "Updated Task"
        assert patch.status == TaskStatus.COMPLETED
        assert patch.priority == TaskPriority.LOW
        # Other fields should remain None
        assert patch.description is None
        assert patch.project_id is None

    def test_task_patch_delete_operation(self):
        """Test TaskPatch for delete operation."""
        task_id = str(uuid4())

        patch = TaskPatch(op=Op.DELETE, task_id=task_id)

        assert patch.op == Op.DELETE
        assert patch.task_id == task_id
        # All other fields should be None for delete
        assert patch.title is None
        assert patch.description is None
        assert patch.status is None

    def test_task_patch_validation_missing_task_id_update(self):
        """Test TaskPatch validation when task_id is missing for update operation."""
        with pytest.raises(ValueError, match="task_id is required for Op.UPDATE operation"):
            TaskPatch(op=Op.UPDATE, title="Updated Task")

    def test_task_patch_validation_missing_task_id_delete(self):
        """Test TaskPatch validation when task_id is missing for delete operation."""
        with pytest.raises(ValueError, match="task_id is required for Op.DELETE operation"):
            TaskPatch(op=Op.DELETE)

    def test_task_patch_validation_task_id_not_required_for_create(self):
        """Test that task_id is not required for create operation."""
        # Should not raise any validation error
        patch = TaskPatch(op=Op.CREATE, title="New Task")
        assert patch.op == Op.CREATE
        assert patch.task_id is None
        assert patch.title == "New Task"

    def test_task_patch_invalid_status(self):
        """Test TaskPatch with invalid status."""
        with pytest.raises(ValueError):
            TaskPatch(op=Op.CREATE, status="invalid_status")

    def test_task_patch_invalid_priority(self):
        """Test TaskPatch with invalid priority."""
        with pytest.raises(ValueError):
            TaskPatch(op=Op.CREATE, priority="invalid_priority")

    def test_task_patch_serialization(self):
        """Test TaskPatch JSON serialization."""
        task_id = str(uuid4())
        patch = TaskPatch(
            op=Op.UPDATE,
            task_id=task_id,
            title="Serialization Test",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            tags=["test"],
        )

        json_data = patch.model_dump_json()
        assert "update" in json_data
        assert task_id in json_data
        assert "Serialization Test" in json_data
        assert "in_progress" in json_data
        assert "high" in json_data
        assert "test" in json_data

    def test_task_patch_deserialization(self):
        """Test TaskPatch JSON deserialization."""
        task_id = str(uuid4())
        patch_data = {
            "op": "create",
            "project_id": str(uuid4()),
            "title": "Deserialized Task",
            "status": "todo",
            "priority": "medium",
            "estimated_minutes": 60,
            "tags": ["deserialized"],
        }

        patch = TaskPatch.model_validate(patch_data)
        assert patch.op == Op.CREATE
        assert patch.title == "Deserialized Task"
        assert patch.status == TaskStatus.TODO
        assert patch.priority == TaskPriority.MEDIUM
        assert patch.estimated_minutes == 60
        assert patch.tags == ["deserialized"]

    def test_task_patch_partial_updates(self):
        """Test TaskPatch for partial field updates."""
        task_id = str(uuid4())

        # Only update status
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, status=TaskStatus.COMPLETED)
        assert patch.status == TaskStatus.COMPLETED
        assert patch.title is None
        assert patch.priority is None

        # Only update priority and assignee
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, priority=TaskPriority.CRITICAL, assignee="new_user")
        assert patch.priority == TaskPriority.CRITICAL
        assert patch.assignee == "new_user"
        assert patch.status is None
        assert patch.title is None

    def test_task_patch_edge_cases(self):
        """Test TaskPatch edge cases."""
        task_id = str(uuid4())

        # Empty lists
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, tags=[], labels=[], dependencies=[])
        assert patch.tags == []
        assert patch.labels == []
        assert patch.dependencies == []

        # Empty metadata
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, metadata={})
        assert patch.metadata == {}

        # Zero values
        patch = TaskPatch(op=Op.UPDATE, task_id=task_id, estimated_minutes=0, actual_minutes=0)
        assert patch.estimated_minutes == 0
        assert patch.actual_minutes == 0


class TestProjectPatch:
    """Test ProjectPatch model."""

    def test_project_patch_create_operation_minimal(self):
        """Test ProjectPatch for create operation with minimal fields."""
        patch = ProjectPatch(op=Op.CREATE)

        assert patch.op == Op.CREATE
        assert patch.project_id is None
        assert patch.name is None
        assert patch.description is None
        assert patch.status is None
        assert patch.priority is None
        assert patch.tags is None
        assert patch.due_date is None
        assert patch.start_date is None

        # Integration fields
        assert patch.motion_project_id is None
        assert patch.linear_project_id is None
        assert patch.notion_page_id is None
        assert patch.gitlab_project_id is None

    def test_project_patch_create_operation_full(self):
        """Test ProjectPatch for create operation with all fields."""
        today = date.today()

        patch = ProjectPatch(
            op=Op.CREATE,
            name="New Project",
            description="Creating a new project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["new", "important"],
            due_date=today,
            start_date=today,
            motion_project_id="motion_123",
            linear_project_id="linear_456",
            notion_page_id="notion_789",
            gitlab_project_id="gitlab_101",
        )

        assert patch.op == Op.CREATE
        assert patch.name == "New Project"
        assert patch.description == "Creating a new project"
        assert patch.status == ProjectStatus.PLANNING
        assert patch.priority == ProjectPriority.HIGH
        assert patch.tags == ["new", "important"]
        assert patch.due_date == today
        assert patch.start_date == today
        assert patch.motion_project_id == "motion_123"
        assert patch.linear_project_id == "linear_456"
        assert patch.notion_page_id == "notion_789"
        assert patch.gitlab_project_id == "gitlab_101"

    def test_project_patch_update_operation(self):
        """Test ProjectPatch for update operation."""
        project_id = str(uuid4())

        patch = ProjectPatch(
            op=Op.UPDATE,
            project_id=project_id,
            name="Updated Project",
            status=ProjectStatus.COMPLETED,
            priority=ProjectPriority.LOW,
        )

        assert patch.op == Op.UPDATE
        assert patch.project_id == project_id
        assert patch.name == "Updated Project"
        assert patch.status == ProjectStatus.COMPLETED
        assert patch.priority == ProjectPriority.LOW
        # Other fields should remain None
        assert patch.description is None
        assert patch.tags is None

    def test_project_patch_delete_operation(self):
        """Test ProjectPatch for delete operation."""
        project_id = str(uuid4())

        patch = ProjectPatch(op=Op.DELETE, project_id=project_id)

        assert patch.op == Op.DELETE
        assert patch.project_id == project_id
        # All other fields should be None for delete
        assert patch.name is None
        assert patch.description is None
        assert patch.status is None

    def test_project_patch_validation_missing_project_id_update(self):
        """Test ProjectPatch validation when project_id is missing for update operation."""
        with pytest.raises(ValueError, match="project_id is required for Op.UPDATE operation"):
            ProjectPatch(op=Op.UPDATE, name="Updated Project")

    def test_project_patch_validation_missing_project_id_delete(self):
        """Test ProjectPatch validation when project_id is missing for delete operation."""
        with pytest.raises(ValueError, match="project_id is required for Op.DELETE operation"):
            ProjectPatch(op=Op.DELETE)

    def test_project_patch_validation_project_id_not_required_for_create(self):
        """Test that project_id is not required for create operation."""
        # Should not raise any validation error
        patch = ProjectPatch(op=Op.CREATE, name="New Project")
        assert patch.op == Op.CREATE
        assert patch.project_id is None
        assert patch.name == "New Project"

    def test_project_patch_invalid_status(self):
        """Test ProjectPatch with invalid status."""
        with pytest.raises(ValueError):
            ProjectPatch(op=Op.CREATE, status="invalid_status")

    def test_project_patch_invalid_priority(self):
        """Test ProjectPatch with invalid priority."""
        with pytest.raises(ValueError):
            ProjectPatch(op=Op.CREATE, priority="invalid_priority")

    def test_project_patch_serialization(self):
        """Test ProjectPatch JSON serialization."""
        project_id = str(uuid4())
        patch = ProjectPatch(
            op=Op.UPDATE,
            project_id=project_id,
            name="Serialization Test",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["test"],
        )

        json_data = patch.model_dump_json()
        assert "update" in json_data
        assert project_id in json_data
        assert "Serialization Test" in json_data
        assert "active" in json_data
        assert "high" in json_data
        assert "test" in json_data

    def test_project_patch_deserialization(self):
        """Test ProjectPatch JSON deserialization."""
        patch_data = {
            "op": "create",
            "name": "Deserialized Project",
            "status": "planning",
            "priority": "medium",
            "tags": ["deserialized"],
        }

        patch = ProjectPatch.model_validate(patch_data)
        assert patch.op == Op.CREATE
        assert patch.name == "Deserialized Project"
        assert patch.status == ProjectStatus.PLANNING
        assert patch.priority == ProjectPriority.MEDIUM
        assert patch.tags == ["deserialized"]

    def test_project_patch_partial_updates(self):
        """Test ProjectPatch for partial field updates."""
        project_id = str(uuid4())

        # Only update status
        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, status=ProjectStatus.COMPLETED)
        assert patch.status == ProjectStatus.COMPLETED
        assert patch.name is None
        assert patch.priority is None

        # Only update priority and description
        patch = ProjectPatch(
            op=Op.UPDATE, project_id=project_id, priority=ProjectPriority.CRITICAL, description="Updated description"
        )
        assert patch.priority == ProjectPriority.CRITICAL
        assert patch.description == "Updated description"
        assert patch.status is None
        assert patch.name is None

    def test_project_patch_date_handling(self):
        """Test ProjectPatch with date fields."""
        project_id = str(uuid4())
        today = date.today()

        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, start_date=today, due_date=today)

        assert patch.start_date == today
        assert patch.due_date == today

        # Test serialization preserves dates
        json_data = patch.model_dump_json()
        deserialized = ProjectPatch.model_validate_json(json_data)
        assert deserialized.start_date == today
        assert deserialized.due_date == today

    def test_project_patch_edge_cases(self):
        """Test ProjectPatch edge cases."""
        project_id = str(uuid4())

        # Empty tags list
        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, tags=[])
        assert patch.tags == []

        # Very long name
        long_name = "A" * 1000
        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, name=long_name)
        assert patch.name == long_name

        # Special characters in name
        special_name = "Project with émojis 🚀 and symbols @#$%"
        patch = ProjectPatch(op=Op.UPDATE, project_id=project_id, name=special_name)
        assert patch.name == special_name


class TestPatch:
    """Test combined Patch model."""

    def test_patch_with_project_patches_only(self):
        """Test Patch with only project patches."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")

        patch = Patch(project_patches=[project_patch])

        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 0
        assert patch.project_patches[0].op == Op.CREATE
        assert patch.project_patches[0].name == "New Project"

    def test_patch_with_task_patches_only(self):
        """Test Patch with only task patches."""
        task_patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")

        patch = Patch(task_patches=[task_patch])

        assert len(patch.task_patches) == 1
        assert len(patch.project_patches) == 0
        assert patch.task_patches[0].op == Op.CREATE
        assert patch.task_patches[0].title == "New Task"

    def test_patch_with_both_patch_types(self):
        """Test Patch with both project and task patches."""
        project_patch = ProjectPatch(op=Op.CREATE, name="New Project")
        task_patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="New Task")

        patch = Patch(project_patches=[project_patch], task_patches=[task_patch])

        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 1
        assert patch.project_patches[0].name == "New Project"
        assert patch.task_patches[0].title == "New Task"

    def test_patch_with_multiple_patches_same_type(self):
        """Test Patch with multiple patches of the same type."""
        project_patch1 = ProjectPatch(op=Op.CREATE, name="Project 1")
        project_patch2 = ProjectPatch(op=Op.UPDATE, project_id=str(uuid4()), name="Project 2")

        task_patch1 = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="Task 1")
        task_patch2 = TaskPatch(op=Op.UPDATE, task_id=str(uuid4()), title="Task 2")

        patch = Patch(project_patches=[project_patch1, project_patch2], task_patches=[task_patch1, task_patch2])

        assert len(patch.project_patches) == 2
        assert len(patch.task_patches) == 2
        assert patch.project_patches[0].name == "Project 1"
        assert patch.project_patches[1].name == "Project 2"
        assert patch.task_patches[0].title == "Task 1"
        assert patch.task_patches[1].title == "Task 2"

    def test_patch_validation_empty_patches_error(self):
        """Test Patch validation when no patches are provided."""
        with pytest.raises(ValueError, match="At least one patch must be provided"):
            Patch()

        with pytest.raises(ValueError, match="At least one patch must be provided"):
            Patch(project_patches=[], task_patches=[])

    def test_patch_default_empty_lists(self):
        """Test that Patch has default empty lists."""
        # This test checks the default values before validation
        project_patch = ProjectPatch(op=Op.CREATE, name="Test Project")
        patch = Patch(project_patches=[project_patch])

        # task_patches should default to empty list
        assert patch.task_patches == []

        # Similarly for the other way around
        task_patch = TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="Test Task")
        patch = Patch(task_patches=[task_patch])

        # project_patches should default to empty list
        assert patch.project_patches == []

    def test_patch_serialization(self):
        """Test Patch JSON serialization."""
        project_patch = ProjectPatch(op=Op.CREATE, name="Serialization Project", status=ProjectStatus.PLANNING)
        task_patch = TaskPatch(
            op=Op.CREATE, project_id=str(uuid4()), title="Serialization Task", status=TaskStatus.TODO
        )

        patch = Patch(project_patches=[project_patch], task_patches=[task_patch])

        json_data = patch.model_dump_json()
        assert "project_patches" in json_data
        assert "task_patches" in json_data
        assert "Serialization Project" in json_data
        assert "Serialization Task" in json_data
        assert "create" in json_data
        assert "planning" in json_data
        assert "todo" in json_data

    def test_patch_deserialization(self):
        """Test Patch JSON deserialization."""
        patch_data = {
            "project_patches": [{"op": "create", "name": "Deserialized Project", "status": "active"}],
            "task_patches": [
                {"op": "create", "project_id": str(uuid4()), "title": "Deserialized Task", "status": "todo"}
            ],
        }

        patch = Patch.model_validate(patch_data)

        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 1
        assert patch.project_patches[0].op == Op.CREATE
        assert patch.project_patches[0].name == "Deserialized Project"
        assert patch.project_patches[0].status == ProjectStatus.ACTIVE
        assert patch.task_patches[0].op == Op.CREATE
        assert patch.task_patches[0].title == "Deserialized Task"
        assert patch.task_patches[0].status == TaskStatus.TODO

    def test_patch_complex_operations(self):
        """Test Patch with complex mix of operations."""
        project_id1 = str(uuid4())
        project_id2 = str(uuid4())
        task_id1 = str(uuid4())
        task_id2 = str(uuid4())

        patch = Patch(
            project_patches=[
                ProjectPatch(op=Op.CREATE, name="New Project"),
                ProjectPatch(op=Op.UPDATE, project_id=project_id1, status=ProjectStatus.COMPLETED),
                ProjectPatch(op=Op.DELETE, project_id=project_id2),
            ],
            task_patches=[
                TaskPatch(op=Op.CREATE, project_id=project_id1, title="New Task"),
                TaskPatch(op=Op.UPDATE, task_id=task_id1, status=TaskStatus.COMPLETED),
                TaskPatch(op=Op.DELETE, task_id=task_id2),
            ],
        )

        assert len(patch.project_patches) == 3
        assert len(patch.task_patches) == 3

        # Check operations
        project_ops = [p.op for p in patch.project_patches]
        task_ops = [t.op for t in patch.task_patches]

        assert Op.CREATE in project_ops
        assert Op.UPDATE in project_ops
        assert Op.DELETE in project_ops
        assert Op.CREATE in task_ops
        assert Op.UPDATE in task_ops
        assert Op.DELETE in task_ops

    def test_patch_edge_cases(self):
        """Test Patch edge cases."""
        # Single project patch
        patch = Patch(project_patches=[ProjectPatch(op=Op.CREATE, name="Single")])
        assert len(patch.project_patches) == 1
        assert len(patch.task_patches) == 0

        # Single task patch
        patch = Patch(task_patches=[TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title="Single")])
        assert len(patch.project_patches) == 0
        assert len(patch.task_patches) == 1

        # Many patches
        many_project_patches = [ProjectPatch(op=Op.CREATE, name=f"Project {i}") for i in range(10)]
        many_task_patches = [TaskPatch(op=Op.CREATE, project_id=str(uuid4()), title=f"Task {i}") for i in range(10)]

        patch = Patch(project_patches=many_project_patches, task_patches=many_task_patches)
        assert len(patch.project_patches) == 10
        assert len(patch.task_patches) == 10

    def test_patch_validation_with_invalid_sub_patches(self):
        """Test that Patch validation includes validation of sub-patches."""
        # Invalid task patch (missing task_id for update)
        with pytest.raises(ValueError, match="task_id is required for Op.UPDATE operation"):
            Patch(task_patches=[TaskPatch(op=Op.UPDATE, title="Invalid")])

        # Invalid project patch (missing project_id for delete)
        with pytest.raises(ValueError, match="project_id is required for Op.DELETE operation"):
            Patch(project_patches=[ProjectPatch(op=Op.DELETE)])

    def test_patch_round_trip_serialization(self):
        """Test complete round-trip serialization/deserialization."""
        original_patch = Patch(
            project_patches=[
                ProjectPatch(
                    op=Op.CREATE,
                    name="Round Trip Project",
                    description="Testing serialization",
                    status=ProjectStatus.ACTIVE,
                    priority=ProjectPriority.HIGH,
                    tags=["test", "serialization"],
                )
            ],
            task_patches=[
                TaskPatch(
                    op=Op.UPDATE,
                    task_id=str(uuid4()),
                    title="Round Trip Task",
                    status=TaskStatus.COMPLETED,
                    priority=TaskPriority.MEDIUM,
                    estimated_minutes=120,
                    tags=["completed"],
                )
            ],
        )

        # Serialize to JSON
        json_data = original_patch.model_dump_json()

        # Deserialize back
        deserialized_patch = Patch.model_validate_json(json_data)

        # Verify all fields are preserved
        assert len(deserialized_patch.project_patches) == 1
        assert len(deserialized_patch.task_patches) == 1

        project_patch = deserialized_patch.project_patches[0]
        assert project_patch.op == Op.CREATE
        assert project_patch.name == "Round Trip Project"
        assert project_patch.description == "Testing serialization"
        assert project_patch.status == ProjectStatus.ACTIVE
        assert project_patch.priority == ProjectPriority.HIGH
        assert project_patch.tags == ["test", "serialization"]

        task_patch = deserialized_patch.task_patches[0]
        assert task_patch.op == Op.UPDATE
        assert task_patch.title == "Round Trip Task"
        assert task_patch.status == TaskStatus.COMPLETED
        assert task_patch.priority == TaskPriority.MEDIUM
        assert task_patch.estimated_minutes == 120
        assert task_patch.tags == ["completed"]
