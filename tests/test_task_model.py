"""Tests for the updated Task model with hierarchical fields"""
import pytest
from datetime import datetime
from src.models.task import Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority


def test_hierarchical_task_creation():
    """Test creating tasks with hierarchical fields"""
    # Create parent task
    parent_task = TaskCreate(
        title="Parent Task",
        description="A parent task",
        project_id="test_project",
        estimated_minutes=240,
        depth=0
    )
    
    # Create child task
    child_task = TaskCreate(
        title="Child Task",
        description="A child task",
        project_id="test_project",
        parent_id="parent_id",
        estimated_minutes=60,
        depth=1,
        dependencies=["dependency_task_id"]
    )
    
    assert parent_task.depth == 0
    assert parent_task.estimated_minutes == 240
    assert parent_task.estimated_hours == 4.0
    
    assert child_task.parent_id == "parent_id"
    assert child_task.depth == 1
    assert child_task.dependencies == ["dependency_task_id"]
    assert child_task.estimated_hours == 1.0


def test_task_validation():
    """Test validation of hierarchical fields"""
    # Test positive estimated_minutes validation
    with pytest.raises(ValueError, match="estimated_minutes must be positive"):
        TaskCreate(
            title="Invalid Task",
            project_id="test_project",
            estimated_minutes=-30
        )
    
    # Test depth validation
    with pytest.raises(ValueError, match="depth cannot exceed 5 levels"):
        TaskCreate(
            title="Too Deep Task",
            project_id="test_project",
            depth=10
        )
    
    # Test negative actual_minutes validation
    with pytest.raises(ValueError, match="actual_minutes cannot be negative"):
        TaskCreate(
            title="Invalid Actual Time",
            project_id="test_project",
            actual_minutes=-15
        )


def test_task_update_validation():
    """Test TaskUpdate validation"""
    # Valid update
    update = TaskUpdate(
        estimated_minutes=120,
        depth=2,
        dependencies=["task1", "task2"]
    )
    assert update.estimated_minutes == 120
    assert update.depth == 2
    
    # Invalid depth
    with pytest.raises(ValueError, match="depth must be between 0 and 5"):
        TaskUpdate(depth=-1)


def test_circular_dependency_detection():
    """Test circular dependency detection"""
    # Create tasks for testing
    task1 = Task(
        id="task1",
        title="Task 1",
        project_id="test_project",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test_user",
        dependencies=["task2"]
    )
    
    task2 = Task(
        id="task2", 
        title="Task 2",
        project_id="test_project",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test_user",
        dependencies=["task1"]  # Creates circular dependency
    )
    
    all_tasks = [task1, task2]
    
    # Should raise error for circular dependency
    with pytest.raises(ValueError, match="Circular dependency detected"):
        task1.validate_no_circular_dependencies(all_tasks)


def test_self_parent_validation():
    """Test that task cannot be its own parent"""
    task = Task(
        id="task1",
        title="Self Parent Task",
        project_id="test_project",
        parent_id="task1",  # Same as its own ID
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test_user"
    )
    
    with pytest.raises(ValueError, match="Task cannot be its own parent"):
        task.validate_parent_not_self()


def test_computed_properties():
    """Test computed properties work correctly"""
    task = Task(
        id="test_task",
        title="Test Task",
        project_id="test_project",
        estimated_minutes=150,
        actual_minutes=90,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test_user"
    )
    
    assert task.estimated_hours == 2.5  # 150 minutes = 2.5 hours
    assert task.actual_hours == 1.5     # 90 minutes = 1.5 hours
    
    # Test with None values
    task_no_time = Task(
        id="test_task2",
        title="Test Task 2", 
        project_id="test_project",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        created_by="test_user"
    )
    
    assert task_no_time.estimated_hours is None
    assert task_no_time.actual_hours is None


if __name__ == "__main__":
    pytest.main([__file__])