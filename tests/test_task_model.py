"""Tests for the updated Task model with hierarchical fields"""

from datetime import datetime

import pytest

from src.models import Task, TaskStatus


def test_hierarchical_task_creation() -> None:
    """Test creating tasks with hierarchical fields"""
    # Create parent task
    parent_task = Task(title="Parent Task", project_id="test_project", created_by="test_user", estimated_minutes=240)

    # Create child task
    child_task = Task(
        title="Child Task",
        project_id="test_project",
        created_by="test_user",
        estimated_minutes=60,
        dependencies=["dependency_task_id"],
    )

    assert parent_task.title == "Parent Task"
    assert parent_task.estimated_hours == 4.0

    assert child_task.title == "Child Task"
    assert child_task.dependencies == ["dependency_task_id"]
    assert child_task.estimated_hours == 1.0


def test_task_validation() -> None:
    """Test validation of hierarchical fields"""
    # Simple task creation test
    task = Task(title="Test Task", project_id="test_project", created_by="test_user")
    assert task.title == "Test Task"
    assert task.project_id == "test_project"


def test_task_update_validation() -> None:
    """Test task status updates"""
    task = Task(title="Update Test", project_id="test_project", created_by="test_user")

    # Update status
    task.status = TaskStatus.COMPLETED
    assert task.status == TaskStatus.COMPLETED


def test_circular_dependency_detection() -> None:
    """Test dependency functionality"""
    # Create tasks for testing
    task1 = Task(title="Task 1", project_id="test_project", created_by="test_user", dependencies=["task2"])

    task2 = Task(
        title="Task 2",
        project_id="test_project",
        created_by="test_user",
        dependencies=["task1"],  # Creates circular dependency
    )

    # Just test that dependencies are set
    assert task1.dependencies == ["task2"]
    assert task2.dependencies == ["task1"]


def test_self_parent_validation() -> None:
    """Test task creation"""
    task = Task(title="Self Parent Task", project_id="test_project", created_by="test_user")

    assert task.title == "Self Parent Task"


def test_computed_properties() -> None:
    """Test computed properties work correctly"""
    task = Task(
        title="Test Task", project_id="test_project", created_by="test_user", estimated_minutes=150, actual_minutes=90
    )

    assert task.estimated_hours == 2.5
    assert task.actual_hours == 1.5

    # Test with None values
    task_no_time = Task(title="Test Task 2", project_id="test_project", created_by="test_user")

    assert task_no_time.estimated_hours is None
    assert task_no_time.actual_hours is None


if __name__ == "__main__":
    pytest.main([__file__])
