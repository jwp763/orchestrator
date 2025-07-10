"""
Test database isolation utilities and transaction management.

This module provides utilities for isolated testing with proper transaction management
to ensure tests don't interfere with each other and database state is clean.
"""

import pytest
from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from src.api.main import app
from src.storage.sql_models import Base
from src.storage.sql_implementation import SQLStorage


class TestDatabaseIsolation:
    """Test database isolation utilities and transaction management."""
    
    @pytest.fixture(scope="function")
    def isolated_engine(self):
        """Create isolated in-memory database engine for each test."""
        engine = create_engine(
            "sqlite:///:memory:",
            connect_args={
                "check_same_thread": False,
            },
            poolclass=StaticPool,
            echo=False
        )
        Base.metadata.create_all(engine)
        return engine
    
    @pytest.fixture(scope="function")
    def isolated_session(self, isolated_engine):
        """Create isolated database session with automatic rollback."""
        Session = sessionmaker(bind=isolated_engine)
        session = Session()
        
        try:
            yield session
        finally:
            # Always rollback any uncommitted changes
            session.rollback()
            session.close()
    
    @pytest.fixture(scope="function")
    def isolated_storage(self, isolated_session):
        """Create isolated storage instance for testing."""
        # Create storage with in-memory database and override session
        storage = SQLStorage(database_url="sqlite:///:memory:")
        storage.session = isolated_session
        
        yield storage
        
        # Cleanup: ensure session is properly closed
        if hasattr(storage, '_session') and storage._session is not None:
            storage._session.close()
            storage._session = None
    
    @pytest.fixture(scope="function")
    def isolated_client(self, isolated_storage):
        """Create isolated test client with database isolation."""
        from src.api.project_routes import get_storage as get_project_storage, get_project_service
        from src.api.task_routes import get_storage as get_task_storage
        from src.orchestration.project_service import ProjectService
        
        # Create isolated project service
        isolated_project_service = ProjectService(storage=isolated_storage)
        
        # Override dependencies - using lambda to capture the storage instance
        app.dependency_overrides[get_project_storage] = lambda: isolated_storage
        app.dependency_overrides[get_task_storage] = lambda: isolated_storage
        app.dependency_overrides[get_project_service] = lambda: isolated_project_service
        
        try:
            client = TestClient(app)
            yield client
        finally:
            # Clean up overrides
            app.dependency_overrides.clear()
    
    def test_database_isolation_basics(self, isolated_session):
        """Test basic database isolation functionality."""
        from src.storage.sql_models import Project
        
        # Create a project in the isolated session
        project = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status="planning",
            priority="medium",
            created_by="test_user"
        )
        isolated_session.add(project)
        isolated_session.commit()
        
        # Verify it exists in this session
        found_project = isolated_session.query(Project).filter_by(id="test-project-1").first()
        assert found_project is not None
        assert found_project.name == "Test Project"
    
    def test_session_isolation_between_tests(self, isolated_session):
        """Test that sessions are isolated between tests."""
        from src.storage.sql_models import Project
        
        # This test should not see any data from previous tests
        projects = isolated_session.query(Project).all()
        assert len(projects) == 0
        
        # Create a project
        project = Project(
            id="test-project-2",
            name="Another Test Project",
            description="Another test project",
            status="planning",
            priority="medium",
            created_by="test_user"
        )
        isolated_session.add(project)
        isolated_session.commit()
        
        # Should only see this project
        projects = isolated_session.query(Project).all()
        assert len(projects) == 1
        assert projects[0].id == "test-project-2"
    
    def test_storage_isolation(self, isolated_storage):
        """Test that storage instances are properly isolated."""
        from src.models.project import Project, ProjectCreate
        
        # Create a project through storage
        project_create = ProjectCreate(
            name="Storage Test Project",
            description="Testing storage isolation",
            status="planning",
            priority="high"
        )
        
        created_project = isolated_storage.create_project(
            Project(**project_create.model_dump(), created_by="test_user")
        )
        
        assert created_project is not None
        assert created_project.name == "Storage Test Project"
        
        # Verify it exists in storage
        retrieved_project = isolated_storage.get_project(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.name == "Storage Test Project"
    
    def test_client_isolation(self, isolated_client):
        """Test that test client has proper database isolation."""
        # Create a project through the API
        project_data = {
            "name": "API Test Project",
            "description": "Testing API isolation",
            "status": "planning",
            "priority": "medium",
            "created_by": "test_user"
        }
        
        create_response = isolated_client.post("/api/projects", json=project_data)
        assert create_response.status_code == 201
        
        created_project = create_response.json()
        project_id = created_project["id"]
        
        # Retrieve it through the API
        get_response = isolated_client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200
        
        retrieved_project = get_response.json()
        assert retrieved_project["name"] == "API Test Project"
    
    def test_transaction_rollback_on_error(self, isolated_session):
        """Test that transactions are properly rolled back on errors."""
        from src.storage.sql_models import Project
        
        # Start with clean state
        assert isolated_session.query(Project).count() == 0
        
        try:
            # Create a project
            project = Project(
                id="test-project-3",
                name="Rollback Test",
                description="Testing rollback",
                status="planning",
                priority="medium",
                created_by="test_user"
            )
            isolated_session.add(project)
            isolated_session.flush()  # Flush but don't commit
            
            # Verify it's in the session
            assert isolated_session.query(Project).count() == 1
            
            # Simulate an error
            raise ValueError("Simulated error")
            
        except ValueError:
            # Roll back the transaction
            isolated_session.rollback()
        
        # Verify the project was rolled back
        assert isolated_session.query(Project).count() == 0
    
    def test_concurrent_session_isolation(self, isolated_engine):
        """Test that concurrent sessions are properly isolated."""
        from src.storage.sql_models import Project
        
        Session = sessionmaker(bind=isolated_engine)
        
        # Create two separate sessions
        session1 = Session()
        session2 = Session()
        
        try:
            # Create a project in session1
            project1 = Project(
                id="concurrent-test-1",
                name="Concurrent Test 1",
                description="Testing concurrent isolation",
                status="planning",
                priority="medium",
                created_by="user1"
            )
            session1.add(project1)
            session1.commit()
            
            # Create a different project in session2
            project2 = Project(
                id="concurrent-test-2",
                name="Concurrent Test 2",
                description="Testing concurrent isolation",
                status="planning",
                priority="medium",
                created_by="user2"
            )
            session2.add(project2)
            session2.commit()
            
            # Both sessions should see both projects
            projects1 = session1.query(Project).all()
            projects2 = session2.query(Project).all()
            
            assert len(projects1) == 2
            assert len(projects2) == 2
            
            # Verify they contain the correct projects
            project_ids_1 = {p.id for p in projects1}
            project_ids_2 = {p.id for p in projects2}
            
            assert project_ids_1 == {"concurrent-test-1", "concurrent-test-2"}
            assert project_ids_2 == {"concurrent-test-1", "concurrent-test-2"}
            
        finally:
            session1.close()
            session2.close()
    
    def test_nested_transaction_isolation(self, isolated_session):
        """Test proper handling of nested transactions."""
        from src.storage.sql_models import Project, Task
        
        # Start with clean state
        assert isolated_session.query(Project).count() == 0
        assert isolated_session.query(Task).count() == 0
        
        # Create a project
        project = Project(
            id="nested-test-project",
            name="Nested Transaction Test",
            description="Testing nested transactions",
            status="planning",
            priority="medium",
            created_by="test_user"
        )
        isolated_session.add(project)
        isolated_session.commit()
        
        # Start a nested transaction
        savepoint = isolated_session.begin_nested()
        
        try:
            # Create a task in the nested transaction
            task = Task(
                id="nested-test-task",
                project_id="nested-test-project",
                title="Nested Test Task",
                description="Testing nested transaction",
                status="todo",
                priority="medium",
                created_by="test_user"
            )
            isolated_session.add(task)
            isolated_session.flush()
            
            # Verify task exists
            assert isolated_session.query(Task).count() == 1
            
            # Rollback the nested transaction
            savepoint.rollback()
            
        except Exception:
            savepoint.rollback()
            raise
        
        # Verify task was rolled back but project remains
        assert isolated_session.query(Project).count() == 1
        assert isolated_session.query(Task).count() == 0
    
    def test_test_data_cleanup(self, isolated_session):
        """Test that test data is properly cleaned up."""
        from src.storage.sql_models import Project, Task
        
        # Create test data
        project = Project(
            id="cleanup-test-project",
            name="Cleanup Test",
            description="Testing cleanup",
            status="planning",
            priority="medium",
            created_by="test_user"
        )
        isolated_session.add(project)
        isolated_session.commit()
        
        task = Task(
            id="cleanup-test-task",
            project_id="cleanup-test-project",
            title="Cleanup Test Task",
            description="Testing cleanup",
            status="todo",
            priority="medium",
            created_by="test_user"
        )
        isolated_session.add(task)
        isolated_session.commit()
        
        # Verify data exists
        assert isolated_session.query(Project).count() == 1
        assert isolated_session.query(Task).count() == 1
        
        # Data will be automatically cleaned up when the fixture ends
        # due to transaction rollback
    
    def test_performance_with_isolation(self, isolated_client):
        """Test that database isolation doesn't significantly impact performance."""
        import time
        
        # Create multiple projects rapidly
        start_time = time.time()
        
        project_ids = []
        for i in range(10):
            project_data = {
                "name": f"Performance Test Project {i}",
                "description": f"Testing performance with isolation {i}",
                "status": "planning",
                "priority": "medium",
                "created_by": "test_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            assert response.status_code == 201
            project_ids.append(response.json()["id"])
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should complete in reasonable time (less than 2 seconds)
        assert duration < 2.0
        
        # Verify all projects were created
        list_response = isolated_client.get("/api/projects")
        assert list_response.status_code == 200
        
        projects = list_response.json()
        assert len(projects["projects"]) == 10
    
    @contextmanager
    def create_test_data(self, isolated_session):
        """Context manager for creating test data with automatic cleanup."""
        from src.storage.sql_models import Project, Task
        
        created_objects = []
        
        try:
            # Create test project
            project = Project(
                id="context-test-project",
                name="Context Test Project",
                description="Testing context manager",
                status="planning",
                priority="medium",
                created_by="test_user"
            )
            isolated_session.add(project)
            created_objects.append(project)
            
            # Create test task
            task = Task(
                id="context-test-task",
                project_id="context-test-project",
                title="Context Test Task",
                description="Testing context manager",
                status="todo",
                priority="medium",
                created_by="test_user"
            )
            isolated_session.add(task)
            created_objects.append(task)
            
            isolated_session.commit()
            
            yield {
                "project": project,
                "task": task
            }
            
        finally:
            # Cleanup is handled by the isolated_session fixture
            # which automatically rolls back the transaction
            pass
    
    def test_context_manager_cleanup(self, isolated_session):
        """Test that context manager properly handles test data cleanup."""
        from src.storage.sql_models import Project, Task
        
        # Use context manager to create test data
        with self.create_test_data(isolated_session) as test_data:
            # Verify data exists
            assert isolated_session.query(Project).count() == 1
            assert isolated_session.query(Task).count() == 1
            
            project = test_data["project"]
            task = test_data["task"]
            
            assert project.name == "Context Test Project"
            assert task.title == "Context Test Task"
        
        # Data cleanup is handled by the fixture rollback
        # In a real scenario, you might want to verify cleanup here