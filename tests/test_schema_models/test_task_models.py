"""Comprehensive tests for task models."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.models.task import Task, TaskBase, TaskCreate, TaskPriority, TaskStatus, TaskUpdate


class TestTaskStatus:
    """Test TaskStatus enum."""

    def test_all_status_values(self):
        """Test all task status enum values."""
        expected_values = ["todo", "in_progress", "blocked", "in_review", "completed", "cancelled"]
        actual_values = [status.value for status in TaskStatus]
        assert actual_values == expected_values

    def test_status_string_representation(self):
        """Test string representation of status values."""
        assert TaskStatus.TODO.value == "todo"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.BLOCKED.value == "blocked"
        assert TaskStatus.IN_REVIEW.value == "in_review"
        assert TaskStatus.COMPLETED.value == "completed"
        assert TaskStatus.CANCELLED.value == "cancelled"


class TestTaskPriority:
    """Test TaskPriority enum."""

    def test_all_priority_values(self):
        """Test all task priority enum values."""
        expected_values = ["critical", "high", "medium", "low", "backlog"]
        actual_values = [priority.value for priority in TaskPriority]
        assert actual_values == expected_values

    def test_priority_string_representation(self):
        """Test string representation of priority values."""
        assert TaskPriority.CRITICAL.value == "critical"
        assert TaskPriority.HIGH.value == "high"
        assert TaskPriority.MEDIUM.value == "medium"
        assert TaskPriority.LOW.value == "low"
        assert TaskPriority.BACKLOG.value == "backlog"


class TestTaskBase:
    """Test TaskBase model."""

    def test_minimal_task_base(self):
        """Test TaskBase with minimal required data."""
        project_id = str(uuid4())
        task = TaskBase(title="Test Task", project_id=project_id)

        assert task.title == "Test Task"
        assert task.project_id == project_id
        assert task.description is None
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM
        assert task.parent_id is None
        assert task.estimated_minutes is None
        assert task.actual_minutes is None
        assert task.depth == 0
        assert task.dependencies == []
        assert task.due_date is None
        assert task.assignee is None
        assert task.tags == []
        assert task.labels == []
        assert task.metadata == {}

        # Integration fields should be None
        assert task.motion_task_id is None
        assert task.linear_issue_id is None
        assert task.notion_task_id is None
        assert task.gitlab_issue_id is None

    def test_task_base_with_all_fields(self):
        """Test TaskBase with all fields populated."""
        project_id = str(uuid4())
        parent_id = str(uuid4())
        dep_id = str(uuid4())
        today = date.today()

        task = TaskBase(
            title="Comprehensive Task",
            description="A test task with all fields",
            project_id=project_id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            parent_id=parent_id,
            estimated_minutes=120,
            actual_minutes=90,
            depth=2,
            dependencies=[dep_id],
            due_date=today,
            assignee="test_user",
            tags=["urgent", "feature"],
            labels=["frontend", "bug"],
            metadata={"custom": "value"},
            motion_task_id="motion_123",
            linear_issue_id="linear_456",
            notion_task_id="notion_789",
            gitlab_issue_id="gitlab_101",
        )

        assert task.title == "Comprehensive Task"
        assert task.description == "A test task with all fields"
        assert task.project_id == project_id
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.priority == TaskPriority.HIGH
        assert task.parent_id == parent_id
        assert task.estimated_minutes == 120
        assert task.actual_minutes == 90
        assert task.depth == 2
        assert task.dependencies == [dep_id]
        assert task.due_date == today
        assert task.assignee == "test_user"
        assert task.tags == ["urgent", "feature"]
        assert task.labels == ["frontend", "bug"]
        assert task.metadata == {"custom": "value"}
        assert task.motion_task_id == "motion_123"
        assert task.linear_issue_id == "linear_456"
        assert task.notion_task_id == "notion_789"
        assert task.gitlab_issue_id == "gitlab_101"

    def test_task_base_estimated_minutes_validation(self):
        """Test estimated_minutes validation."""
        project_id = str(uuid4())

        # Valid positive value
        task = TaskBase(title="Test", project_id=project_id, estimated_minutes=60)
        assert task.estimated_minutes == 60

        # Zero should raise error
        with pytest.raises(ValueError, match="estimated_minutes must be positive"):
            TaskBase(title="Test", project_id=project_id, estimated_minutes=0)

        # Negative should raise error
        with pytest.raises(ValueError, match="estimated_minutes must be positive"):
            TaskBase(title="Test", project_id=project_id, estimated_minutes=-30)

        # None should be allowed
        task = TaskBase(title="Test", project_id=project_id, estimated_minutes=None)
        assert task.estimated_minutes is None

    def test_task_base_actual_minutes_validation(self):
        """Test actual_minutes validation."""
        project_id = str(uuid4())

        # Valid positive value
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=60)
        assert task.actual_minutes == 60

        # Zero should be allowed
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=0)
        assert task.actual_minutes == 0

        # Negative should raise error
        with pytest.raises(ValueError, match="actual_minutes cannot be negative"):
            TaskBase(title="Test", project_id=project_id, actual_minutes=-30)

        # None should be allowed
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=None)
        assert task.actual_minutes is None

    def test_task_base_depth_validation(self):
        """Test depth validation."""
        project_id = str(uuid4())

        # Valid depths (0-5)
        for depth in range(6):
            task = TaskBase(title="Test", project_id=project_id, depth=depth)
            assert task.depth == depth

        # Negative depth should raise error
        with pytest.raises(ValueError, match="depth cannot be negative"):
            TaskBase(title="Test", project_id=project_id, depth=-1)

        # Depth > 5 should raise error
        with pytest.raises(ValueError, match="depth cannot exceed 5 levels"):
            TaskBase(title="Test", project_id=project_id, depth=6)

    def test_task_base_dependencies_validation(self):
        """Test dependencies validation."""
        project_id = str(uuid4())

        # Valid dependencies
        dep1 = str(uuid4())
        dep2 = str(uuid4())
        task = TaskBase(title="Test", project_id=project_id, dependencies=[dep1, dep2])
        assert task.dependencies == [dep1, dep2]

        # Empty list should be allowed
        task = TaskBase(title="Test", project_id=project_id, dependencies=[])
        assert task.dependencies == []

        # Empty string dependency should raise error
        with pytest.raises(ValueError, match="dependency IDs must be non-empty strings"):
            TaskBase(title="Test", project_id=project_id, dependencies=[""])

        # Whitespace-only dependency should raise error
        with pytest.raises(ValueError, match="dependency IDs must be non-empty strings"):
            TaskBase(title="Test", project_id=project_id, dependencies=["   "])

        # Non-string dependency should raise error (Pydantic type validation)
        with pytest.raises(ValueError, match="Input should be a valid string"):
            TaskBase(title="Test", project_id=project_id, dependencies=[123])

    def test_task_base_estimated_hours_property(self):
        """Test estimated_hours computed property."""
        project_id = str(uuid4())

        # No estimated_minutes
        task = TaskBase(title="Test", project_id=project_id)
        assert task.estimated_hours is None

        # 60 minutes = 1 hour
        task = TaskBase(title="Test", project_id=project_id, estimated_minutes=60)
        assert task.estimated_hours == 1.0

        # 90 minutes = 1.5 hours
        task = TaskBase(title="Test", project_id=project_id, estimated_minutes=90)
        assert task.estimated_hours == 1.5

        # 30 minutes = 0.5 hours
        task = TaskBase(title="Test", project_id=project_id, estimated_minutes=30)
        assert task.estimated_hours == 0.5

    def test_task_base_actual_hours_property(self):
        """Test actual_hours computed property."""
        project_id = str(uuid4())

        # No actual_minutes
        task = TaskBase(title="Test", project_id=project_id)
        assert task.actual_hours is None

        # 120 minutes = 2 hours
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=120)
        assert task.actual_hours == 2.0

        # 45 minutes = 0.75 hours
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=45)
        assert task.actual_hours == 0.75

        # 0 minutes = 0 hours
        task = TaskBase(title="Test", project_id=project_id, actual_minutes=0)
        assert task.actual_hours == 0.0

    def test_task_base_invalid_status(self):
        """Test invalid status value."""
        project_id = str(uuid4())
        with pytest.raises(ValueError):
            TaskBase(title="Test", project_id=project_id, status="invalid_status")

    def test_task_base_invalid_priority(self):
        """Test invalid priority value."""
        project_id = str(uuid4())
        with pytest.raises(ValueError):
            TaskBase(title="Test", project_id=project_id, priority="invalid_priority")

    def test_task_base_serialization(self):
        """Test JSON serialization of TaskBase."""
        project_id = str(uuid4())
        task = TaskBase(
            title="Serialization Test",
            project_id=project_id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            estimated_minutes=120,
            tags=["test", "serialization"],
        )

        json_data = task.model_dump_json()
        assert "Serialization Test" in json_data
        assert "in_progress" in json_data
        assert "high" in json_data
        assert "120" in json_data
        assert "test" in json_data


class TestTaskCreate:
    """Test TaskCreate model."""

    def test_task_create_inherits_from_base(self):
        """Test that TaskCreate inherits all TaskBase functionality."""
        project_id = str(uuid4())
        task = TaskCreate(
            title="New Task",
            project_id=project_id,
            description="Creating a new task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
        )

        assert task.title == "New Task"
        assert task.project_id == project_id
        assert task.description == "Creating a new task"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.HIGH

    def test_task_create_minimal(self):
        """Test TaskCreate with minimal data."""
        project_id = str(uuid4())
        task = TaskCreate(title="Minimal Create", project_id=project_id)

        assert task.title == "Minimal Create"
        assert task.project_id == project_id
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.MEDIUM

    def test_task_create_validation_inheritance(self):
        """Test that TaskCreate inherits validation from TaskBase."""
        project_id = str(uuid4())

        # Should inherit estimated_minutes validation
        with pytest.raises(ValueError, match="estimated_minutes must be positive"):
            TaskCreate(title="Test", project_id=project_id, estimated_minutes=-30)


class TestTaskUpdate:
    """Test TaskUpdate model."""

    def test_task_update_all_fields_optional(self):
        """Test that all TaskUpdate fields are optional."""
        update = TaskUpdate()

        assert update.title is None
        assert update.description is None
        assert update.project_id is None
        assert update.status is None
        assert update.priority is None
        assert update.parent_id is None
        assert update.estimated_minutes is None
        assert update.actual_minutes is None
        assert update.depth is None
        assert update.dependencies is None
        assert update.due_date is None
        assert update.assignee is None
        assert update.tags is None
        assert update.labels is None
        assert update.motion_task_id is None
        assert update.linear_issue_id is None
        assert update.notion_task_id is None
        assert update.gitlab_issue_id is None
        assert update.metadata is None

    def test_task_update_partial_fields(self):
        """Test TaskUpdate with partial field updates."""
        today = date.today()

        update = TaskUpdate(title="Updated Title", status=TaskStatus.COMPLETED, estimated_minutes=180, due_date=today)

        assert update.title == "Updated Title"
        assert update.status == TaskStatus.COMPLETED
        assert update.estimated_minutes == 180
        assert update.due_date == today
        # Other fields should remain None
        assert update.description is None
        assert update.priority is None

    def test_task_update_validation_inheritance(self):
        """Test that TaskUpdate inherits validation from base validators."""
        # Should validate estimated_minutes
        with pytest.raises(ValueError, match="estimated_minutes must be positive"):
            TaskUpdate(estimated_minutes=-30)

        # Should validate actual_minutes
        with pytest.raises(ValueError, match="actual_minutes cannot be negative"):
            TaskUpdate(actual_minutes=-15)

        # Should validate depth
        with pytest.raises(ValueError, match="depth must be between 0 and 5"):
            TaskUpdate(depth=10)

        # Valid values should work
        update = TaskUpdate(estimated_minutes=60, actual_minutes=45, depth=3)
        assert update.estimated_minutes == 60
        assert update.actual_minutes == 45
        assert update.depth == 3


class TestTask:
    """Test full Task model."""

    def test_task_creation_with_required_fields(self):
        """Test Task creation with required fields."""
        project_id = str(uuid4())
        task = Task(title="Full Task", project_id=project_id, created_by="test_user")

        assert task.title == "Full Task"
        assert task.project_id == project_id
        assert task.created_by == "test_user"
        assert task.id is not None
        assert len(task.id) == 36  # UUID4 string length
        assert task.created_at is not None
        assert task.updated_at is not None
        assert task.completed_at is None
        assert task.is_overdue is False
        assert task.days_until_due is None

    def test_task_timestamp_auto_generation(self):
        """Test that timestamps are automatically generated."""
        project_id = str(uuid4())
        before = datetime.now()
        task = Task(title="Timestamp Test", project_id=project_id, created_by="test_user")
        after = datetime.now()

        assert before <= task.created_at <= after
        assert before <= task.updated_at <= after

    def test_task_completed_at_auto_set_on_completion(self):
        """Test that completed_at is set when status is COMPLETED."""
        project_id = str(uuid4())
        before = datetime.now()
        task = Task(title="Completion Test", project_id=project_id, status=TaskStatus.COMPLETED, created_by="test_user")
        after = datetime.now()

        assert task.completed_at is not None
        assert before <= task.completed_at <= after

    def test_task_completed_at_not_set_for_other_statuses(self):
        """Test that completed_at is not set for non-completed statuses."""
        project_id = str(uuid4())

        for status in [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED, TaskStatus.CANCELLED]:
            task = Task(title="Status Test", project_id=project_id, status=status, created_by="test_user")
            assert task.completed_at is None

    def test_task_model_validator_sets_updated_at(self):
        """Test that model validator updates the updated_at field."""
        project_id = str(uuid4())

        # Create task first
        task = Task(title="Test", project_id=project_id, created_by="user")
        original_updated_at = task.updated_at

        # Simulate an update by creating a new instance with same id
        updated_task = Task(
            id=task.id, title="Updated Test", project_id=project_id, created_by="user", created_at=task.created_at
        )

        # updated_at should be refreshed
        assert updated_task.updated_at > original_updated_at

    def test_task_model_validator_completed_at_logic(self):
        """Test model validator logic for completed_at."""
        project_id = str(uuid4())

        # When changing to completed, completed_at should be set
        task_data = {"title": "Test", "project_id": project_id, "status": TaskStatus.COMPLETED, "created_by": "user"}
        task = Task.model_validate(task_data)
        assert task.completed_at is not None

        # When changing from completed to another status, completed_at should be cleared
        task_data = {
            "id": task.id,
            "title": "Test",
            "project_id": project_id,
            "status": TaskStatus.TODO,
            "created_by": "user",
            "completed_at": task.completed_at,  # Existing completed_at
        }
        updated_task = Task.model_validate(task_data)
        assert updated_task.completed_at is None

    def test_task_validate_parent_not_self(self):
        """Test validation that task cannot be its own parent."""
        project_id = str(uuid4())
        task = Task(title="Self Parent Test", project_id=project_id, created_by="test_user")

        # Set parent_id to own id should raise error
        task.parent_id = task.id
        with pytest.raises(ValueError, match="Task cannot be its own parent"):
            task.validate_parent_not_self()

        # Different parent_id should be fine
        task.parent_id = str(uuid4())
        task.validate_parent_not_self()  # Should not raise

    def test_task_validate_no_circular_dependencies_simple(self):
        """Test simple circular dependency validation."""
        project_id = str(uuid4())

        # Create tasks
        task1 = Task(title="Task 1", project_id=project_id, created_by="user")
        task2 = Task(title="Task 2", project_id=project_id, created_by="user")

        # No dependencies should be fine
        task1.validate_no_circular_dependencies([task1, task2])

        # task1 depends on task2 should be fine
        task1.dependencies = [task2.id]
        task1.validate_no_circular_dependencies([task1, task2])

        # task1 depends on itself should raise error
        task1.dependencies = [task1.id]
        with pytest.raises(ValueError, match="Circular dependency detected"):
            task1.validate_no_circular_dependencies([task1, task2])

    def test_task_validate_no_circular_dependencies_complex(self):
        """Test complex circular dependency validation."""
        project_id = str(uuid4())

        # Create tasks
        task1 = Task(title="Task 1", project_id=project_id, created_by="user")
        task2 = Task(title="Task 2", project_id=project_id, created_by="user")
        task3 = Task(title="Task 3", project_id=project_id, created_by="user")

        # Chain: task1 -> task2 -> task3 (no cycle)
        task1.dependencies = [task2.id]
        task2.dependencies = [task3.id]
        task3.dependencies = []

        task1.validate_no_circular_dependencies([task1, task2, task3])  # Should not raise

        # Create cycle: task3 -> task1
        task3.dependencies = [task1.id]

        with pytest.raises(ValueError, match="Circular dependency detected"):
            task1.validate_no_circular_dependencies([task1, task2, task3])

    def test_task_is_parent_property(self):
        """Test is_parent property (placeholder implementation)."""
        project_id = str(uuid4())
        task = Task(title="Parent Test", project_id=project_id, created_by="user")

        # Placeholder implementation always returns False
        assert task.is_parent is False

    def test_task_total_estimated_minutes_property(self):
        """Test total_estimated_minutes property (placeholder implementation)."""
        project_id = str(uuid4())
        task = Task(title="Estimation Test", project_id=project_id, created_by="user", estimated_minutes=120)

        # Placeholder implementation returns own estimated_minutes
        assert task.total_estimated_minutes == 120

        # With no estimate
        task_no_estimate = Task(title="No Estimate", project_id=project_id, created_by="user")
        assert task_no_estimate.total_estimated_minutes is None

    def test_task_validation_missing_required_fields(self):
        """Test validation errors for missing required fields."""
        project_id = str(uuid4())

        with pytest.raises(ValueError, match="created_by"):
            Task(title="Test Task", project_id=project_id)

        with pytest.raises(ValueError, match="title"):
            Task(project_id=project_id, created_by="user")

        with pytest.raises(ValueError, match="project_id"):
            Task(title="Test Task", created_by="user")

    def test_task_serialization_complete(self):
        """Test complete Task serialization."""
        project_id = str(uuid4())
        parent_id = str(uuid4())
        dep_id = str(uuid4())

        task = Task(
            title="Complete Task",
            description="Full serialization test",
            project_id=project_id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            parent_id=parent_id,
            estimated_minutes=180,
            actual_minutes=120,
            depth=1,
            dependencies=[dep_id],
            assignee="test_user",
            tags=["serialization", "test"],
            labels=["backend"],
            metadata={"version": "1.0"},
            created_by="test_user",
        )

        json_data = task.model_dump_json()
        assert "Complete Task" in json_data
        assert "in_progress" in json_data
        assert "high" in json_data
        assert "180" in json_data
        assert "serialization" in json_data

        # Test deserialization
        deserialized = Task.model_validate_json(json_data)
        assert deserialized.title == "Complete Task"
        assert deserialized.status == TaskStatus.IN_PROGRESS
        assert deserialized.priority == TaskPriority.HIGH
        assert deserialized.estimated_minutes == 180
        assert deserialized.dependencies == [dep_id]

    def test_task_from_attributes_config(self):
        """Test that ConfigDict allows creation from SQLAlchemy models."""

        # Mock SQLAlchemy-like object
        class MockSQLTask:
            def __init__(self):
                self.id = str(uuid4())
                self.title = "SQL Task"
                self.description = "From SQL"
                self.project_id = str(uuid4())
                self.status = "todo"
                self.priority = "high"
                self.created_by = "sql_user"
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.completed_at = None
                self.estimated_minutes = 60
                self.actual_minutes = None
                self.depth = 0
                self.dependencies = []
                self.tags = ["sql", "test"]
                self.labels = []
                self.metadata = {}
                self.is_overdue = False
                self.days_until_due = None

        sql_task = MockSQLTask()
        task = Task.model_validate(sql_task)

        assert task.title == "SQL Task"
        assert task.description == "From SQL"
        assert task.status == TaskStatus.TODO
        assert task.priority == TaskPriority.HIGH
        assert task.estimated_minutes == 60

    def test_task_edge_cases(self):
        """Test edge cases and boundary conditions."""
        project_id = str(uuid4())

        # Empty lists
        task = Task(
            title="Edge Test",
            project_id=project_id,
            created_by="user",
            tags=[],
            labels=[],
            dependencies=[],
            metadata={},
        )
        assert task.tags == []
        assert task.labels == []
        assert task.dependencies == []
        assert task.metadata == {}

        # Very long title
        long_title = "A" * 1000
        task = Task(title=long_title, project_id=project_id, created_by="user")
        assert task.title == long_title

        # Special characters in title
        special_title = "Task with émojis 🚀 and symbols @#$%"
        task = Task(title=special_title, project_id=project_id, created_by="user")
        assert task.title == special_title

        # Maximum depth
        task = Task(title="Max Depth", project_id=project_id, created_by="user", depth=5)
        assert task.depth == 5

    def test_task_time_calculations(self):
        """Test time-related calculations and properties."""
        project_id = str(uuid4())

        # Test hours properties with various minute values
        test_cases = [
            (60, 1.0),  # 1 hour
            (90, 1.5),  # 1.5 hours
            (30, 0.5),  # 0.5 hours
            (45, 0.75),  # 0.75 hours
            (1, 1 / 60),  # 1 minute
            (1440, 24.0),  # 24 hours (1 day)
        ]

        for minutes, expected_hours in test_cases:
            task = Task(
                title="Time Test",
                project_id=project_id,
                created_by="user",
                estimated_minutes=minutes,
                actual_minutes=minutes,
            )
            assert task.estimated_hours == expected_hours
            assert task.actual_hours == expected_hours


class TestTaskHierarchicalFeatures:
    """Test hierarchical and advanced task features."""

    def test_hierarchical_task_creation(self):
        """Test creating tasks with hierarchical fields."""
        # Create parent task
        parent_task = Task(
            title="Parent Task", project_id="test_project", created_by="test_user", estimated_minutes=240
        )

        # Create child task with dependencies
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

    def test_task_status_updates_with_validation(self):
        """Test task status updates and validation."""
        task = Task(title="Update Test", project_id="test_project", created_by="test_user")

        # Update status
        original_updated_at = task.updated_at
        task.status = TaskStatus.COMPLETED
        assert task.status == TaskStatus.COMPLETED

        # Create new instance to test model validator
        updated_task = Task(
            id=task.id,
            title=task.title,
            project_id=task.project_id,
            created_by=task.created_by,
            status=TaskStatus.COMPLETED,
            created_at=task.created_at,
        )

        # Should have completed_at set
        assert updated_task.completed_at is not None

    def test_dependency_relationships(self):
        """Test task dependency functionality."""
        project_id = "test_project"

        # Create tasks with dependencies
        task1 = Task(title="Task 1", project_id=project_id, created_by="test_user", dependencies=["task2_id"])

        task2 = Task(title="Task 2", project_id=project_id, created_by="test_user", dependencies=["task3_id"])

        task3 = Task(title="Task 3", project_id=project_id, created_by="test_user", dependencies=[])

        # Test dependencies are set correctly
        assert task1.dependencies == ["task2_id"]
        assert task2.dependencies == ["task3_id"]
        assert task3.dependencies == []

        # Test chain validation (no cycles)
        task1.validate_no_circular_dependencies([task1, task2, task3])

    def test_computed_properties_comprehensive(self):
        """Test computed properties work correctly in various scenarios."""
        project_id = "test_project"

        # Test with both estimated and actual time
        task_with_time = Task(
            title="Time Test", project_id=project_id, created_by="test_user", estimated_minutes=150, actual_minutes=90
        )

        assert task_with_time.estimated_hours == 2.5
        assert task_with_time.actual_hours == 1.5

        # Test with None values
        task_no_time = Task(title="No Time Test", project_id=project_id, created_by="test_user")

        assert task_no_time.estimated_hours is None
        assert task_no_time.actual_hours is None

        # Test placeholder properties
        assert task_no_time.is_parent is False
        assert task_no_time.total_estimated_minutes is None

        # Test with estimated time
        assert task_with_time.total_estimated_minutes == 150


class TestTaskProjectIntegration:
    """Test integration between Task and Project models."""

    def test_task_project_relationship(self):
        """Test that tasks properly reference projects."""
        from src.models.project import Project

        # Create project
        project = Project(name="Integration Test Project", created_by="test_user")

        # Create tasks for the project
        task1 = Task(
            title="Integration Task 1", project_id=project.id, status=TaskStatus.COMPLETED, created_by="test_user"
        )

        task2 = Task(title="Integration Task 2", project_id=project.id, status=TaskStatus.TODO, created_by="test_user")

        # Add tasks to project
        project.tasks = [task1, task2]

        # Test project properties
        assert project.task_count == 2
        assert project.completed_task_count == 1

        # Test task references
        assert task1.project_id == project.id
        assert task2.project_id == project.id

    def test_task_serialization_with_project_context(self):
        """Test task serialization in project context."""
        from src.models.project import Project

        project = Project(name="Serialization Project", created_by="test_user")

        task = Task(
            title="Serialization Task",
            project_id=project.id,
            description="Test serialization",
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.HIGH,
            estimated_minutes=120,
            tags=["serialization", "test"],
            created_by="test_user",
        )

        # Test individual serialization
        task_json = task.model_dump_json()
        assert project.id in task_json
        assert "Serialization Task" in task_json

        # Test project with tasks serialization
        project.tasks = [task]
        project_json = project.model_dump_json()
        assert "Serialization Project" in project_json
        assert "Serialization Task" in project_json
