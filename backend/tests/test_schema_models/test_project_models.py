"""Comprehensive tests for project models."""

from datetime import date, datetime
from uuid import uuid4

import pytest

from src.models.project import Project, ProjectBase, ProjectCreate, ProjectPriority, ProjectStatus, ProjectUpdate
from src.models.task import Task, TaskPriority, TaskStatus


class TestProjectStatus:
    """Test ProjectStatus enum."""

    def test_all_status_values(self) -> None:
        """Test all project status enum values."""
        expected_values = ["planning", "active", "on_hold", "completed", "archived"]
        actual_values = [status.value for status in ProjectStatus]
        assert actual_values == expected_values

    def test_status_string_representation(self) -> None:
        """Test string representation of status values."""
        assert ProjectStatus.PLANNING.value == "planning"
        assert ProjectStatus.ACTIVE.value == "active"
        assert ProjectStatus.ON_HOLD.value == "on_hold"
        assert ProjectStatus.COMPLETED.value == "completed"
        assert ProjectStatus.ARCHIVED.value == "archived"


class TestProjectPriority:
    """Test ProjectPriority enum."""

    def test_all_priority_values(self) -> None:
        """Test all project priority enum values."""
        expected_values = ["critical", "high", "medium", "low", "backlog"]
        actual_values = [priority.value for priority in ProjectPriority]
        assert actual_values == expected_values

    def test_priority_string_representation(self) -> None:
        """Test string representation of priority values."""
        assert ProjectPriority.CRITICAL.value == "critical"
        assert ProjectPriority.HIGH.value == "high"
        assert ProjectPriority.MEDIUM.value == "medium"
        assert ProjectPriority.LOW.value == "low"
        assert ProjectPriority.BACKLOG.value == "backlog"


class TestProjectBase:
    """Test ProjectBase model."""

    def test_minimal_project_base(self) -> None:
        """Test ProjectBase with minimal required data."""
        project = ProjectBase(name="Test Project")

        assert project.name == "Test Project"
        assert project.description is None
        assert project.status == ProjectStatus.PLANNING
        assert project.priority == ProjectPriority.MEDIUM
        assert project.tags == []
        assert project.due_date is None
        assert project.start_date is None

        # Integration fields should be None
        assert project.motion_project_id is None
        assert project.linear_project_id is None
        assert project.notion_page_id is None
        assert project.gitlab_project_id is None

    def test_project_base_with_all_fields(self) -> None:
        """Test ProjectBase with all fields populated."""
        today = date.today()

        project = ProjectBase(
            name="Comprehensive Project",
            description="A test project with all fields",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["urgent", "feature"],
            due_date=today,
            start_date=today,
            motion_project_id="motion_123",
            linear_project_id="linear_456",
            notion_page_id="notion_789",
            gitlab_project_id="gitlab_101",
        )

        assert project.name == "Comprehensive Project"
        assert project.description == "A test project with all fields"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.tags == ["urgent", "feature"]
        assert project.due_date == today
        assert project.start_date == today
        assert project.motion_project_id == "motion_123"
        assert project.linear_project_id == "linear_456"
        assert project.notion_page_id == "notion_789"
        assert project.gitlab_project_id == "gitlab_101"

    def test_project_base_validation_missing_name(self) -> None:
        """Test that missing name raises validation error."""
        with pytest.raises(ValueError, match="Field required"):
            ProjectBase()  # type: ignore

    def test_project_base_invalid_status(self) -> None:
        """Test invalid status value."""
        with pytest.raises(ValueError):
            ProjectBase(name="Test", status="invalid_status")  # type: ignore

    def test_project_base_invalid_priority(self) -> None:
        """Test invalid priority value."""
        with pytest.raises(ValueError):
            ProjectBase(name="Test", priority="invalid_priority")  # type: ignore

    def test_project_base_serialization(self) -> None:
        """Test JSON serialization of ProjectBase."""
        project = ProjectBase(
            name="Test Project",
            description="Test description",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["test", "validation"],
        )

        json_data = project.model_dump_json()
        assert "Test Project" in json_data
        assert "active" in json_data
        assert "high" in json_data
        assert "test" in json_data

    def test_project_base_deserialization(self) -> None:
        """Test JSON deserialization of ProjectBase."""
        project_data = {
            "name": "Deserialized Project",
            "description": "From JSON",
            "status": "active",
            "priority": "high",
            "tags": ["deserialized"],
        }

        project = ProjectBase.model_validate(project_data)
        assert project.name == "Deserialized Project"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.tags == ["deserialized"]


class TestProjectCreate:
    """Test ProjectCreate model."""

    def test_project_create_inherits_from_base(self) -> None:
        """Test that ProjectCreate inherits all ProjectBase functionality."""
        project = ProjectCreate(
            name="New Project",
            description="Creating a new project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
        )

        assert project.name == "New Project"
        assert project.description == "Creating a new project"
        assert project.status == ProjectStatus.PLANNING
        assert project.priority == ProjectPriority.MEDIUM

    def test_project_create_minimal(self) -> None:
        """Test ProjectCreate with minimal data."""
        project = ProjectCreate(name="Minimal Create")

        assert project.name == "Minimal Create"
        assert project.status == ProjectStatus.PLANNING
        assert project.priority == ProjectPriority.MEDIUM


class TestProjectUpdate:
    """Test ProjectUpdate model."""

    def test_project_update_all_fields_optional(self) -> None:
        """Test that all ProjectUpdate fields are optional."""
        update = ProjectUpdate()

        assert update.name is None
        assert update.description is None
        assert update.status is None
        assert update.priority is None
        assert update.tags is None
        assert update.due_date is None
        assert update.start_date is None
        assert update.motion_project_id is None
        assert update.linear_project_id is None
        assert update.notion_page_id is None
        assert update.gitlab_project_id is None

    def test_project_update_partial_fields(self) -> None:
        """Test ProjectUpdate with partial field updates."""
        today = date.today()

        update = ProjectUpdate(name="Updated Name", status=ProjectStatus.COMPLETED, due_date=today)

        assert update.name == "Updated Name"
        assert update.status == ProjectStatus.COMPLETED
        assert update.due_date == today
        # Other fields should remain None
        assert update.description is None
        assert update.priority is None

    def test_project_update_serialization(self) -> None:
        """Test ProjectUpdate JSON serialization."""
        update = ProjectUpdate(name="Updated Project", priority=ProjectPriority.CRITICAL)

        json_data = update.model_dump_json()
        assert "Updated Project" in json_data
        assert "critical" in json_data


class TestProject:
    """Test full Project model."""

    def test_project_creation_with_required_fields(self) -> None:
        """Test Project creation with required fields."""
        project = Project(name="Full Project", created_by="test_user")

        assert project.name == "Full Project"
        assert project.created_by == "test_user"
        assert project.id is not None
        assert len(project.id) == 36  # UUID4 string length
        assert project.created_at is not None
        assert project.updated_at is not None
        assert project.tasks == []

    def test_project_with_all_fields(self) -> None:
        """Test Project with all fields populated."""
        today = date.today()
        project_id = str(uuid4())

        project = Project(
            id=project_id,
            name="Complete Project",
            description="Full project test",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["complete", "test"],
            due_date=today,
            start_date=today,
            created_by="test_user",
            motion_project_id="motion_123",
            linear_project_id="linear_456",
            notion_page_id="notion_789",
            gitlab_project_id="gitlab_101",
        )

        assert project.id == project_id
        assert project.name == "Complete Project"
        assert project.description == "Full project test"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.tags == ["complete", "test"]
        assert project.due_date == today
        assert project.start_date == today
        assert project.created_by == "test_user"
        assert project.motion_project_id == "motion_123"

    def test_project_timestamp_auto_generation(self) -> None:
        """Test that timestamps are automatically generated."""
        before = datetime.now()
        project = Project(name="Timestamp Test", created_by="test_user")
        after = datetime.now()

        assert before <= project.created_at <= after
        assert before <= project.updated_at <= after

    def test_project_model_validator_sets_updated_at(self) -> None:
        """Test that model validator updates the updated_at field."""
        # Create project first
        project = Project(name="Test", created_by="user")
        original_updated_at = project.updated_at

        # Simulate an update by creating a new instance with same id
        updated_project = Project(id=project.id, name="Updated Test", created_by="user", created_at=project.created_at)

        # updated_at should be refreshed
        assert updated_project.updated_at > original_updated_at

    def test_project_task_count_property(self) -> None:
        """Test task_count property."""
        project = Project(name="Task Count Test", created_by="test_user")

        # No tasks initially
        assert project.task_count == 0

        # Add some tasks
        task1 = Task(project_id=project.id, title="Task 1", created_by="test_user")
        task2 = Task(project_id=project.id, title="Task 2", created_by="test_user")

        project.tasks = [task1, task2]
        assert project.task_count == 2

    def test_project_completed_task_count_property(self) -> None:
        """Test completed_task_count property."""
        project = Project(name="Completion Test", created_by="test_user")

        # Create tasks with different statuses
        task1 = Task(project_id=project.id, title="Completed Task", status=TaskStatus.COMPLETED, created_by="test_user")
        task2 = Task(project_id=project.id, title="Pending Task", status=TaskStatus.TODO, created_by="test_user")
        task3 = Task(
            project_id=project.id, title="Another Completed", status=TaskStatus.COMPLETED, created_by="test_user"
        )

        project.tasks = [task1, task2, task3]

        assert project.task_count == 3
        assert project.completed_task_count == 2

    def test_project_validation_missing_required_fields(self) -> None:
        """Test validation errors for missing required fields."""
        with pytest.raises(ValueError, match="created_by"):
            Project(name="Test Project")  # type: ignore

        with pytest.raises(ValueError, match="name"):
            Project(created_by="test_user")  # type: ignore

    def test_project_serialization_with_tasks(self) -> None:
        """Test Project serialization including tasks."""
        project = Project(name="Serialization Test", created_by="test_user")

        task = Task(project_id=project.id, title="Test Task", created_by="test_user")
        project.tasks = [task]

        json_data = project.model_dump_json()
        assert "Serialization Test" in json_data
        assert "Test Task" in json_data
        assert "tasks" in json_data

    def test_project_deserialization_from_dict(self) -> None:
        """Test Project deserialization from dictionary."""
        project_data = {
            "name": "Dict Project",
            "description": "From dictionary",
            "status": "active",
            "priority": "high",
            "created_by": "test_user",
            "tags": ["dict", "test"],
            "tasks": [],
        }

        project = Project.model_validate(project_data)
        assert project.name == "Dict Project"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.created_by == "test_user"
        assert project.tags == ["dict", "test"]

    def test_project_from_attributes_config(self) -> None:
        """Test that ConfigDict allows creation from SQLAlchemy models."""
        # This tests the from_attributes=True configuration

        # Mock SQLAlchemy-like object
        class MockSQLProject:
            def __init__(self) -> None:
                self.id = str(uuid4())
                self.name = "SQL Project"
                self.description = "From SQL"
                self.status = "active"
                self.priority = "high"
                self.created_by = "sql_user"
                self.created_at = datetime.now()
                self.updated_at = datetime.now()
                self.tags = ["sql", "test"]
                self.tasks: list = []

        sql_project = MockSQLProject()
        project = Project.model_validate(sql_project)

        assert project.name == "SQL Project"
        assert project.description == "From SQL"
        assert project.status == ProjectStatus.ACTIVE
        assert project.priority == ProjectPriority.HIGH
        assert project.created_by == "sql_user"

    def test_project_edge_cases(self) -> None:
        """Test edge cases and boundary conditions."""
        # Empty tags list
        project = Project(name="Edge Test", created_by="user", tags=[])
        assert project.tags == []

        # Very long name
        long_name = "A" * 1000
        project = Project(name=long_name, created_by="user")
        assert project.name == long_name

        # Special characters in name
        special_name = "Project with émojis 🚀 and symbols @#$%"
        project = Project(name=special_name, created_by="user")
        assert project.name == special_name

    def test_project_date_handling(self) -> None:
        """Test date field handling."""
        today = date.today()

        project = Project(name="Date Test", created_by="user", start_date=today, due_date=today)

        assert project.start_date == today
        assert project.due_date == today

        # Test serialization preserves dates
        json_data = project.model_dump_json()
        deserialized = Project.model_validate_json(json_data)
        assert deserialized.start_date == today
        assert deserialized.due_date == today


class TestProjectTaskIntegration:
    """Test integration between Project and Task models."""

    def test_project_with_multiple_task_statuses(self) -> None:
        """Test project behavior with tasks in different statuses."""
        project = Project(name="Multi-Status Project", created_by="test_user")

        # Create tasks with different statuses
        tasks = []
        statuses = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED, TaskStatus.CANCELLED]

        for i, status in enumerate(statuses):
            task = Task(title=f"Task {i+1}", project_id=project.id, status=status, created_by="test_user")
            tasks.append(task)

        project.tasks = tasks

        # Test counts
        assert project.task_count == 4
        assert project.completed_task_count == 1  # Only one COMPLETED task

    def test_project_task_lifecycle(self) -> None:
        """Test complete lifecycle of project with tasks."""
        # Create project in planning phase
        project = Project(name="Lifecycle Project", status=ProjectStatus.PLANNING, created_by="test_user")

        # Add initial tasks
        task1 = Task(title="Setup Task", project_id=project.id, status=TaskStatus.TODO, created_by="test_user")

        task2 = Task(title="Implementation Task", project_id=project.id, status=TaskStatus.TODO, created_by="test_user")

        project.tasks = [task1, task2]

        # Project starts - move to active
        project.status = ProjectStatus.ACTIVE
        assert project.status == ProjectStatus.ACTIVE
        assert project.completed_task_count == 0

        # Complete tasks
        task1.status = TaskStatus.COMPLETED
        task2.status = TaskStatus.COMPLETED

        # Simulate project completion
        project.status = ProjectStatus.COMPLETED

        assert project.status == ProjectStatus.COMPLETED
        assert project.completed_task_count == 2
        assert project.task_count == 2

    def test_project_serialization_with_full_tasks(self) -> None:
        """Test project serialization with complex task data."""
        today = date.today()

        project = Project(
            name="Complex Project",
            description="Project with complex tasks",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            due_date=today,
            created_by="test_user",
            tags=["complex", "test"],
        )

        # Create complex task
        task = Task(
            title="Complex Task",
            description="Task with all fields",
            project_id=project.id,
            status=TaskStatus.IN_PROGRESS,
            priority=TaskPriority.CRITICAL,
            estimated_minutes=240,
            actual_minutes=120,
            depth=1,
            dependencies=["other_task_id"],
            assignee="assigned_user",
            tags=["critical", "feature"],
            labels=["backend", "api"],
            metadata={"complexity": "high", "version": "2.0"},
            created_by="test_user",
        )

        project.tasks = [task]

        # Test serialization
        json_data = project.model_dump_json()

        # Verify project data
        assert "Complex Project" in json_data
        assert "complex" in json_data
        assert "high" in json_data

        # Verify task data
        assert "Complex Task" in json_data
        assert "critical" in json_data
        assert "240" in json_data
        assert "assigned_user" in json_data

        # Test deserialization
        deserialized = Project.model_validate_json(json_data)
        assert deserialized.name == "Complex Project"
        assert len(deserialized.tasks) == 1
        assert deserialized.tasks[0].title == "Complex Task"
        assert deserialized.tasks[0].estimated_minutes == 240
        assert deserialized.tasks[0].metadata["complexity"] == "high"


class TestProjectAdvancedFeatures:
    """Test advanced project features and edge cases."""

    def test_project_with_hierarchical_tasks(self) -> None:
        """Test project with parent-child task relationships."""
        project = Project(name="Hierarchical Project", created_by="test_user")

        # Create parent task
        parent_task = Task(
            title="Parent Feature", project_id=project.id, estimated_minutes=480, created_by="test_user"  # 8 hours
        )

        # Create child tasks
        child_task1 = Task(
            title="Child Task 1",
            project_id=project.id,
            parent_id=parent_task.id,
            depth=1,
            estimated_minutes=240,  # 4 hours
            created_by="test_user",
        )

        child_task2 = Task(
            title="Child Task 2",
            project_id=project.id,
            parent_id=parent_task.id,
            depth=1,
            estimated_minutes=240,  # 4 hours
            dependencies=[child_task1.id],
            created_by="test_user",
        )

        project.tasks = [parent_task, child_task1, child_task2]

        # Test hierarchy
        assert project.task_count == 3
        assert child_task1.parent_id == parent_task.id
        assert child_task2.parent_id == parent_task.id
        assert child_task2.dependencies == [child_task1.id]

        # Test time calculations
        assert parent_task.estimated_hours == 8.0
        assert child_task1.estimated_hours == 4.0
        assert child_task2.estimated_hours == 4.0

    def test_project_integration_fields(self) -> None:
        """Test project integration with external systems."""
        project = Project(
            name="Integration Project",
            description="Project with external integrations",
            created_by="test_user",
            motion_project_id="motion_123",
            linear_project_id="linear_456",
            notion_page_id="notion_789",
            gitlab_project_id="gitlab_101",
        )

        # Create task with integrations
        task = Task(
            title="Integration Task",
            project_id=project.id,
            created_by="test_user",
            motion_task_id="motion_task_123",
            linear_issue_id="linear_issue_456",
            notion_task_id="notion_task_789",
            gitlab_issue_id="gitlab_issue_101",
        )

        project.tasks = [task]

        # Test all integration fields are preserved
        assert project.motion_project_id == "motion_123"
        assert project.linear_project_id == "linear_456"
        assert project.notion_page_id == "notion_789"
        assert project.gitlab_project_id == "gitlab_101"

        assert task.motion_task_id == "motion_task_123"
        assert task.linear_issue_id == "linear_issue_456"
        assert task.notion_task_id == "notion_task_789"
        assert task.gitlab_issue_id == "gitlab_issue_101"

        # Test serialization preserves integration data
        json_data = project.model_dump_json()
        deserialized = Project.model_validate_json(json_data)

        assert deserialized.motion_project_id == "motion_123"
        assert deserialized.tasks[0].motion_task_id == "motion_task_123"
