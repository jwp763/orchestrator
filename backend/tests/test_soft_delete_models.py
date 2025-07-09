"""
Unit tests for soft delete model field definitions and validation.

Tests DEL-001 acceptance criteria:
- Project model has deleted_at (DateTime, nullable) and deleted_by (String, nullable) fields
- Task model has deleted_at (DateTime, nullable) and deleted_by (String, nullable) fields
- Remove cascade='all, delete-orphan' from Project-Task relationship
"""

import pytest
from datetime import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from src.storage.sql_models import Base, Project, Task
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority


class TestSoftDeleteModels:
    """Test suite for soft delete model field definitions and validation."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create database session for testing."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def test_project_model_has_soft_delete_fields(self, engine):
        """Test that Project model has deleted_at and deleted_by fields."""
        inspector = inspect(engine)
        columns = inspector.get_columns('projects')
        column_names = [col['name'] for col in columns]
        
        # Check that soft delete fields exist
        assert 'deleted_at' in column_names, "Project model missing deleted_at field"
        assert 'deleted_by' in column_names, "Project model missing deleted_by field"
        
        # Check field types and nullability
        deleted_at_col = next(col for col in columns if col['name'] == 'deleted_at')
        deleted_by_col = next(col for col in columns if col['name'] == 'deleted_by')
        
        assert deleted_at_col['nullable'] is True, "deleted_at field should be nullable"
        assert deleted_by_col['nullable'] is True, "deleted_by field should be nullable"

    def test_task_model_has_soft_delete_fields(self, engine):
        """Test that Task model has deleted_at and deleted_by fields."""
        inspector = inspect(engine)
        columns = inspector.get_columns('tasks')
        column_names = [col['name'] for col in columns]
        
        # Check that soft delete fields exist
        assert 'deleted_at' in column_names, "Task model missing deleted_at field"
        assert 'deleted_by' in column_names, "Task model missing deleted_by field"
        
        # Check field types and nullability
        deleted_at_col = next(col for col in columns if col['name'] == 'deleted_at')
        deleted_by_col = next(col for col in columns if col['name'] == 'deleted_by')
        
        assert deleted_at_col['nullable'] is True, "deleted_at field should be nullable"
        assert deleted_by_col['nullable'] is True, "deleted_by field should be nullable"

    def test_project_soft_delete_fields_default_to_null(self, session):
        """Test that soft delete fields default to NULL when creating new projects."""
        project = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        
        session.add(project)
        session.commit()
        
        # Verify soft delete fields are NULL by default
        retrieved_project = session.query(Project).filter_by(id="test-project-1").first()
        assert retrieved_project.deleted_at is None
        assert retrieved_project.deleted_by is None

    def test_task_soft_delete_fields_default_to_null(self, session):
        """Test that soft delete fields default to NULL when creating new tasks."""
        # Create a project first
        project = Project(
            id="test-project-1",
            name="Test Project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        session.add(project)
        session.commit()
        
        # Create a task
        task = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            description="A test task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_by="test_user"
        )
        
        session.add(task)
        session.commit()
        
        # Verify soft delete fields are NULL by default
        retrieved_task = session.query(Task).filter_by(id="test-task-1").first()
        assert retrieved_task.deleted_at is None
        assert retrieved_task.deleted_by is None

    def test_project_soft_delete_fields_can_be_set(self, session):
        """Test that soft delete fields can be set and retrieved correctly."""
        project = Project(
            id="test-project-1",
            name="Test Project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        
        session.add(project)
        session.commit()
        
        # Set soft delete fields
        now = datetime.now()
        project.deleted_at = now
        project.deleted_by = "admin_user"
        session.commit()
        
        # Verify fields were set correctly
        retrieved_project = session.query(Project).filter_by(id="test-project-1").first()
        assert retrieved_project.deleted_at == now
        assert retrieved_project.deleted_by == "admin_user"

    def test_task_soft_delete_fields_can_be_set(self, session):
        """Test that soft delete fields can be set and retrieved correctly."""
        # Create a project first
        project = Project(
            id="test-project-1",
            name="Test Project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        session.add(project)
        session.commit()
        
        # Create a task
        task = Task(
            id="test-task-1",
            project_id="test-project-1",
            title="Test Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_by="test_user"
        )
        
        session.add(task)
        session.commit()
        
        # Set soft delete fields
        now = datetime.now()
        task.deleted_at = now
        task.deleted_by = "admin_user"
        session.commit()
        
        # Verify fields were set correctly
        retrieved_task = session.query(Task).filter_by(id="test-task-1").first()
        assert retrieved_task.deleted_at == now
        assert retrieved_task.deleted_by == "admin_user"

    def test_project_task_relationship_no_cascade_delete_orphan(self):
        """Test that Project-Task relationship doesn't have cascade='all, delete-orphan'."""
        project_relationship = Project.__mapper__.relationships.get('tasks')
        
        # Verify relationship exists
        assert project_relationship is not None, "Project-Task relationship should exist"
        
        # Check that cascade doesn't include delete-orphan
        cascade_options = str(project_relationship.cascade)
        assert 'delete-orphan' not in cascade_options, \
            "Project-Task relationship should not have cascade='all, delete-orphan'"

    def test_soft_delete_fields_validation(self, session):
        """Test validation of soft delete fields."""
        project = Project(
            id="test-project-1",
            name="Test Project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        
        session.add(project)
        session.commit()
        
        # Test that deleted_by can accept various string formats
        valid_deleted_by_values = [
            "user123",
            "admin@example.com",
            "system_user",
            "User Name",
            "a" * 255  # Max length test
        ]
        
        for value in valid_deleted_by_values:
            project.deleted_by = value
            session.commit()
            
            retrieved_project = session.query(Project).filter_by(id="test-project-1").first()
            assert retrieved_project.deleted_by == value

    def test_multiple_projects_with_soft_delete(self, session):
        """Test that multiple projects can have soft delete fields set independently."""
        # Create two projects
        project1 = Project(
            id="test-project-1",
            name="Test Project 1",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        
        project2 = Project(
            id="test-project-2",
            name="Test Project 2",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="test_user"
        )
        
        session.add(project1)
        session.add(project2)
        session.commit()
        
        # Set soft delete on only one project
        now = datetime.now()
        project1.deleted_at = now
        project1.deleted_by = "admin_user"
        session.commit()
        
        # Verify only one project has soft delete fields set
        retrieved_project1 = session.query(Project).filter_by(id="test-project-1").first()
        retrieved_project2 = session.query(Project).filter_by(id="test-project-2").first()
        
        assert retrieved_project1.deleted_at == now
        assert retrieved_project1.deleted_by == "admin_user"
        assert retrieved_project2.deleted_at is None
        assert retrieved_project2.deleted_by is None

    def test_task_hierarchy_with_soft_delete(self, session):
        """Test that parent-child task relationships work with soft delete fields."""
        # Create a project
        project = Project(
            id="test-project-1",
            name="Test Project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        session.add(project)
        session.commit()
        
        # Create parent task
        parent_task = Task(
            id="parent-task-1",
            project_id="test-project-1",
            title="Parent Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            created_by="test_user"
        )
        session.add(parent_task)
        session.commit()
        
        # Create child task
        child_task = Task(
            id="child-task-1",
            project_id="test-project-1",
            parent_id="parent-task-1",
            title="Child Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_by="test_user"
        )
        session.add(child_task)
        session.commit()
        
        # Set soft delete on parent task
        now = datetime.now()
        parent_task.deleted_at = now
        parent_task.deleted_by = "admin_user"
        session.commit()
        
        # Verify parent task has soft delete fields set
        retrieved_parent = session.query(Task).filter_by(id="parent-task-1").first()
        retrieved_child = session.query(Task).filter_by(id="child-task-1").first()
        
        assert retrieved_parent.deleted_at == now
        assert retrieved_parent.deleted_by == "admin_user"
        assert retrieved_child.deleted_at is None
        assert retrieved_child.deleted_by is None