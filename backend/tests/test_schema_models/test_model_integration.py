"""Integration tests between different model types."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.models.patch import Op, Patch, ProjectPatch, TaskPatch
from src.models.project import Project, ProjectPriority, ProjectStatus
from src.models.task import Task, TaskPriority, TaskStatus


class TestModelIntegration:
    """Test integration between Project, Task, and Patch models."""

    def test_complete_project_workflow(self) -> None:
        """Test a complete project workflow using all models."""
        # Create project
        project = Project(
            name="Integration Workflow",
            description="Testing complete workflow",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user",
        )

        # Create tasks for the project
        task1 = Task(
            title="Design Phase",
            project_id=project.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            estimated_minutes=480,  # 8 hours
            created_by="test_user",
        )

        task2 = Task(
            title="Implementation Phase",
            project_id=project.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            estimated_minutes=960,  # 16 hours
            dependencies=[task1.id],
            created_by="test_user",
        )

        task3 = Task(
            title="Testing Phase",
            project_id=project.id,
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            estimated_minutes=240,  # 4 hours
            dependencies=[task2.id],
            created_by="test_user",
        )

        project.tasks = [task1, task2, task3]

        # Test initial state
        assert project.task_count == 3
        assert project.completed_task_count == 0
        assert project.status == ProjectStatus.PLANNING

        # Create patches to start the project
        start_project_patch = ProjectPatch(op=Op.UPDATE, project_id=project.id, status=ProjectStatus.ACTIVE)

        start_task_patch = TaskPatch(op=Op.UPDATE, task_id=task1.id, status=TaskStatus.IN_PROGRESS)

        workflow_patch = Patch(project_patches=[start_project_patch], task_patches=[start_task_patch])

        # Apply patches (simulated)
        project.status = ProjectStatus.ACTIVE
        task1.status = TaskStatus.IN_PROGRESS

        assert project.status == ProjectStatus.ACTIVE
        assert task1.status == TaskStatus.IN_PROGRESS

        # Complete task 1
        task1.status = TaskStatus.COMPLETED
        assert project.completed_task_count == 1

        # Start task 2
        task2.status = TaskStatus.IN_PROGRESS

        # Complete task 2 and start task 3
        task2.status = TaskStatus.COMPLETED
        task3.status = TaskStatus.IN_PROGRESS
        assert project.completed_task_count == 2

        # Complete final task
        task3.status = TaskStatus.COMPLETED
        project.status = ProjectStatus.COMPLETED

        assert project.completed_task_count == 3
        assert project.status == ProjectStatus.COMPLETED

    def test_patch_operations_on_complex_models(self) -> None:
        """Test patch operations on models with complex data."""
        # Create project with full data
        project = Project(
            name="Complex Patch Test",
            description="Testing patches on complex models",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.CRITICAL,
            tags=["complex", "patch", "test"],
            due_date=date.today(),
            created_by="test_user",
            motion_project_id="motion_123",
            linear_project_id="linear_456",
        )

        # Create task with full data
        task = Task(
            title="Complex Task",
            description="Task with complex data",
            project_id=project.id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            estimated_minutes=480,
            actual_minutes=240,
            depth=1,
            dependencies=["other_task"],
            assignee="assigned_user",
            tags=["backend", "api"],
            labels=["feature", "critical"],
            metadata={"complexity": "high", "version": "2.0"},
            created_by="test_user",
            motion_task_id="motion_task_123",
        )

        project.tasks = [task]

        # Create comprehensive patches
        project_patch = ProjectPatch(
            op=Op.UPDATE,
            project_id=project.id,
            priority=ProjectPriority.MEDIUM,
            tags=["updated", "patch"],
            notion_page_id="notion_updated",
        )

        task_patch = TaskPatch(
            op=Op.UPDATE,
            task_id=task.id,
            status=TaskStatus.COMPLETED,
            actual_minutes=360,
            tags=["completed", "updated"],
            metadata={"complexity": "medium", "completed": True},
        )

        combined_patch = Patch(project_patches=[project_patch], task_patches=[task_patch])

        # Test patch serialization
        patch_json = combined_patch.model_dump_json()
        assert "updated" in patch_json
        assert "completed" in patch_json
        assert "notion_updated" in patch_json

        # Test patch deserialization
        deserialized_patch = Patch.model_validate_json(patch_json)
        assert len(deserialized_patch.project_patches) == 1
        assert len(deserialized_patch.task_patches) == 1
        assert deserialized_patch.project_patches[0].notion_page_id == "notion_updated"
        assert deserialized_patch.task_patches[0].metadata is not None
        assert deserialized_patch.task_patches[0].metadata["completed"] is True

    def test_model_validation_across_types(self) -> None:
        """Test validation that spans multiple model types."""
        project = Project(name="Validation Test", created_by="test_user")

        # Create tasks with various validation scenarios
        valid_task = Task(
            title="Valid Task",
            project_id=project.id,
            estimated_minutes=60,
            actual_minutes=45,
            depth=2,
            dependencies=["valid_dep_id"],
            created_by="test_user",
        )

        # Test task validation methods
        valid_task.validate_parent_not_self()  # Should not raise

        # Test with circular dependency detection
        task1 = Task(title="Task 1", project_id=project.id, created_by="test_user")
        task2 = Task(title="Task 2", project_id=project.id, created_by="test_user")
        task3 = Task(title="Task 3", project_id=project.id, created_by="test_user")

        # Linear dependencies (valid)
        task1.dependencies = [task2.id]
        task2.dependencies = [task3.id]
        task3.dependencies = []

        task1.validate_no_circular_dependencies([task1, task2, task3])

        project.tasks = [valid_task, task1, task2, task3]
        assert project.task_count == 4

    def test_serialization_consistency_across_models(self) -> None:
        """Test that serialization is consistent across all model types."""
        # Create interconnected models
        project = Project(
            name="Serialization Test",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user",
        )

        task = Task(
            title="Serialization Task",
            project_id=project.id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.CRITICAL,
            created_by="test_user",
        )

        project.tasks = [task]

        # Test individual serialization
        project_json = project.model_dump_json()
        task_json = task.model_dump_json()

        # Test deserialization
        project_restored = Project.model_validate_json(project_json)
        task_restored = Task.model_validate_json(task_json)

        # Verify consistency
        assert project_restored.name == project.name
        assert project_restored.status == project.status
        assert task_restored.title == task.title
        assert task_restored.project_id == task.project_id

        # Test patch serialization consistency
        patch = Patch(
            project_patches=[ProjectPatch(op=Op.UPDATE, project_id=project.id, name="Updated")],
            task_patches=[TaskPatch(op=Op.UPDATE, task_id=task.id, status=TaskStatus.COMPLETED)],
        )

        patch_json = patch.model_dump_json()
        patch_restored = Patch.model_validate_json(patch_json)

        assert len(patch_restored.project_patches) == 1
        assert len(patch_restored.task_patches) == 1
        assert patch_restored.project_patches[0].name == "Updated"
        assert patch_restored.task_patches[0].status == TaskStatus.COMPLETED

    def test_model_relationships_and_references(self) -> None:
        """Test relationships and references between models."""
        # Create project
        project = Project(name="Reference Test", created_by="test_user")

        # Create parent task
        parent_task = Task(title="Parent Task", project_id=project.id, created_by="test_user")

        # Create child tasks with references
        child1 = Task(title="Child 1", project_id=project.id, parent_id=parent_task.id, depth=1, created_by="test_user")

        child2 = Task(
            title="Child 2",
            project_id=project.id,
            parent_id=parent_task.id,
            depth=1,
            dependencies=[child1.id],
            created_by="test_user",
        )

        # Create patches that reference these models
        patches = []

        # Patch to update parent
        patches.append(TaskPatch(op=Op.UPDATE, task_id=parent_task.id, status=TaskStatus.IN_PROGRESS))

        # Patch to complete child1
        patches.append(TaskPatch(op=Op.UPDATE, task_id=child1.id, status=TaskStatus.COMPLETED))

        # Patch to start child2 (after child1 completion)
        patches.append(TaskPatch(op=Op.UPDATE, task_id=child2.id, status=TaskStatus.IN_PROGRESS))

        combined_patch = Patch(task_patches=patches)

        # Test all references are maintained
        assert all(p.task_id is not None for p in combined_patch.task_patches)
        assert child1.parent_id == parent_task.id
        assert child2.parent_id == parent_task.id
        assert child2.dependencies == [child1.id]
        assert all(task.project_id == project.id for task in [parent_task, child1, child2])


class TestModelEdgeCases:
    """Test edge cases and boundary conditions across models."""

    def test_empty_and_minimal_models(self) -> None:
        """Test models with minimal or empty data."""
        # Minimal project
        project = Project(name="Minimal", created_by="user")
        assert project.tasks == []
        assert project.task_count == 0

        # Minimal task
        task = Task(title="Minimal", project_id=project.id, created_by="user")
        assert task.dependencies == []
        assert task.tags == []
        assert task.metadata == {}

        # Minimal patches
        empty_patch = Patch(project_patches=[ProjectPatch(op=Op.CREATE, name="Empty")])
        assert len(empty_patch.task_patches) == 0

    def test_large_scale_models(self) -> None:
        """Test models with large amounts of data."""
        # Project with many tasks
        project = Project(name="Large Scale", created_by="user")

        tasks = []
        for i in range(100):
            task = Task(title=f"Task {i}", project_id=project.id, created_by="user")
            tasks.append(task)

        project.tasks = tasks
        assert project.task_count == 100

        # Large patch with many operations
        task_patches = [
            TaskPatch(op=Op.UPDATE, task_id=task.id, status=TaskStatus.COMPLETED)
            for task in tasks[:50]  # Complete first 50 tasks
        ]

        large_patch = Patch(task_patches=task_patches)
        assert len(large_patch.task_patches) == 50

        # Test serialization of large models
        json_data = large_patch.model_dump_json()
        assert len(json_data) > 1000  # Should be substantial

        # Test deserialization
        restored = Patch.model_validate_json(json_data)
        assert len(restored.task_patches) == 50
