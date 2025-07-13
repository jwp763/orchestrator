"""
Unit and integration tests for ProjectService.

Tests the orchestration service layer for project-related business logic,
including unit tests with mocked dependencies and integration tests with
real storage connections.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Optional

from ..test_api.test_database_isolation import TestDatabaseIsolation
from src.orchestration.project_service import ProjectService
from src.storage.interface import StorageInterface
from src.storage.sql_implementation import SQLStorage
from src.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectStatus, ProjectPriority
)
from src.models.patch import Patch, ProjectPatch, Op


class TestProjectServiceUnit:
    """Unit tests for ProjectService with mocked dependencies."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage interface for unit tests."""
        return Mock(spec=StorageInterface)

    @pytest.fixture
    def project_service(self, mock_storage):
        """ProjectService instance with mocked storage."""
        return ProjectService(storage=mock_storage)

    @pytest.fixture
    def sample_project(self):
        """Sample project for testing."""
        return Project(
            id="test-project-1",
            name="Test Project",
            description="A test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "example"],
            created_by="test_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    @pytest.fixture
    def sample_project_create(self):
        """Sample project create data."""
        return ProjectCreate(
            name="New Project",
            description="A new test project",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
            tags=["new", "test"],
            created_by="test_user"
        )

    def test_init_default_storage(self):
        """Test ProjectService initialization with default storage."""
        service = ProjectService()
        assert isinstance(service.storage, SQLStorage)

    def test_init_custom_storage(self, mock_storage):
        """Test ProjectService initialization with custom storage."""
        service = ProjectService(storage=mock_storage)
        assert service.storage is mock_storage

    def test_list_projects_success(self, project_service, mock_storage, sample_project):
        """Test successful project listing."""
        mock_storage.get_projects.return_value = [sample_project]
        
        result = project_service.list_projects()
        
        assert len(result) == 1
        assert result[0] == sample_project
        mock_storage.get_projects.assert_called_once()

    def test_list_projects_with_filters(self, project_service, mock_storage):
        """Test project listing with status and priority filters."""
        mock_storage.get_projects.return_value = []
        
        result = project_service.list_projects(
            skip=10, 
            limit=50, 
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH
        )
        
        assert result == []
        mock_storage.get_projects.assert_called_once()

    def test_list_projects_pagination_validation(self, project_service, mock_storage):
        """Test pagination parameter validation."""
        with pytest.raises(ValueError, match="Skip parameter must be non-negative"):
            project_service.list_projects(skip=-1)
        
        with pytest.raises(ValueError, match="Limit must be between 1 and 1000"):
            project_service.list_projects(limit=0)
        
        with pytest.raises(ValueError, match="Limit must be between 1 and 1000"):
            project_service.list_projects(limit=1001)

    def test_get_project_success(self, project_service, mock_storage, sample_project):
        """Test successful project retrieval."""
        mock_storage.get_project.return_value = sample_project
        mock_storage.get_tasks_by_project.return_value = []
        
        result = project_service.get_project("test-project-1")
        
        assert result == sample_project
        mock_storage.get_project.assert_called_once_with("test-project-1")
        mock_storage.get_tasks_by_project.assert_called_once_with("test-project-1")

    def test_get_project_not_found(self, project_service, mock_storage):
        """Test project retrieval when project doesn't exist."""
        mock_storage.get_project.return_value = None
        
        result = project_service.get_project("nonexistent")
        
        assert result is None
        mock_storage.get_project.assert_called_once_with("nonexistent")

    def test_create_project_success(self, project_service, mock_storage, sample_project_create, sample_project):
        """Test successful project creation."""
        mock_storage.create_project.return_value = sample_project
        
        result = project_service.create_project(sample_project_create, "test_user")
        
        assert result == sample_project
        mock_storage.create_project.assert_called_once()
        
        # Verify the project passed to storage has correct data
        call_args = mock_storage.create_project.call_args[0][0]
        assert call_args.name == sample_project_create.name
        assert call_args.description == sample_project_create.description
        assert call_args.status == sample_project_create.status

    def test_create_project_validation_error(self, project_service, mock_storage):
        """Test project creation with invalid data."""
        invalid_create = ProjectCreate(
            name="",  # Empty name should fail validation
            created_by="test_user"
        )
        
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            project_service.create_project(invalid_create, "test_user")
        
        mock_storage.create_project.assert_not_called()

    def test_update_project_success(self, project_service, mock_storage, sample_project):
        """Test successful project update."""
        update_data = ProjectUpdate(
            name="Updated Project Name",
            description="Updated description"
        )
        updated_project = sample_project.model_copy(update={"name": "Updated Project Name"})
        
        mock_storage.get_project.return_value = sample_project
        mock_storage.update_project.return_value = updated_project
        
        result = project_service.update_project("test-project-1", update_data)
        
        assert result == updated_project
        mock_storage.update_project.assert_called_once()

    def test_update_project_not_found(self, project_service, mock_storage):
        """Test project update when project doesn't exist."""
        update_data = ProjectUpdate(name="Updated Name")
        mock_storage.get_project.return_value = None
        
        result = project_service.update_project("test-project-1", update_data)
        
        assert result is None
        mock_storage.update_project.assert_not_called()

    def test_delete_project_success(self, project_service, mock_storage, sample_project):
        """Test successful project deletion."""
        mock_storage.get_project.return_value = sample_project
        mock_storage.get_tasks_by_project.return_value = []  # No associated tasks
        mock_storage.delete_project.return_value = True
        
        result = project_service.delete_project("test-project-1")
        
        assert result is True
        mock_storage.delete_project.assert_called_once_with("test-project-1")

    def test_delete_project_not_found(self, project_service, mock_storage):
        """Test project deletion when project doesn't exist."""
        mock_storage.get_project.return_value = None
        
        result = project_service.delete_project("test-project-1")
        
        assert result is False
        mock_storage.delete_project.assert_not_called()

    def test_apply_patch_success(self, project_service, mock_storage, sample_project):
        """Test successful patch application."""
        patch = ProjectPatch(
            project_id="test-project-1",
            op=Op.UPDATE,
            name="Patched Project Name",
            created_by="test_user"
        )
        patched_project = sample_project.model_copy(update={"name": "Patched Project Name"})
        
        mock_storage.get_project.return_value = sample_project
        mock_storage.apply_project_patch.return_value = patched_project
        
        result = project_service.apply_patch(patch)
        
        assert result == patched_project
        mock_storage.apply_project_patch.assert_called_once_with(patch)

    def test_apply_patch_invalid_project(self, project_service, mock_storage):
        """Test patch application on non-existent project."""
        patch = ProjectPatch(
            project_id="nonexistent",
            op=Op.UPDATE,
            name="New Name",
            created_by="test_user"
        )
        
        mock_storage.get_project.return_value = None
        
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            project_service.apply_patch(patch)
        
        mock_storage.apply_project_patch.assert_not_called()


class TestProjectServiceIntegration(TestDatabaseIsolation):
    """Integration tests for ProjectService with real storage."""

    @pytest.fixture
    def project_service(self, isolated_storage):
        """ProjectService with isolated database."""
        return ProjectService(storage=isolated_storage)

    @pytest.fixture
    def sample_project_create(self):
        """Sample project create data for integration tests."""
        return ProjectCreate(
            name="Integration Test Project",
            description="A project for integration testing",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["integration", "test"],
            created_by="integration_user"
        )

    def test_project_lifecycle_integration(self, project_service, sample_project_create):
        """Test complete project lifecycle with real storage."""
        # Create project
        created_project = project_service.create_project(sample_project_create, "integration_test")
        assert created_project is not None
        assert created_project.name == sample_project_create.name
        assert created_project.id is not None
        
        # Get project
        retrieved_project = project_service.get_project(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.id == created_project.id
        assert retrieved_project.name == created_project.name
        
        # Update project
        update_data = ProjectUpdate(
            name="Updated Integration Project",
            status=ProjectStatus.ACTIVE
        )
        updated_project = project_service.update_project(created_project.id, update_data)
        assert updated_project.name == "Updated Integration Project"
        assert updated_project.status == ProjectStatus.ACTIVE
        
        # List projects (should include our project)
        projects = project_service.list_projects()
        project_ids = [p.id for p in projects]
        assert created_project.id in project_ids
        
        # Delete project
        deletion_result = project_service.delete_project(created_project.id)
        assert deletion_result is True
        
        # Verify deletion
        deleted_project = project_service.get_project(created_project.id)
        assert deleted_project is None

    def test_project_filtering_integration(self, project_service):
        """Test project filtering with real storage."""
        # Create projects with different statuses and priorities
        project1 = project_service.create_project(ProjectCreate(
            name="High Priority Active",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        ), "integration_test")
        project2 = project_service.create_project(ProjectCreate(
            name="Medium Priority Planning",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
            created_by="test_user"
        ), "integration_test")
        
        # Test status filtering
        active_projects = project_service.list_projects(status=ProjectStatus.ACTIVE)
        active_ids = [p.id for p in active_projects]
        assert project1.id in active_ids
        assert project2.id not in active_ids
        
        # Test priority filtering
        high_priority_projects = project_service.list_projects(priority=ProjectPriority.HIGH)
        high_priority_ids = [p.id for p in high_priority_projects]
        assert project1.id in high_priority_ids
        assert project2.id not in high_priority_ids
        
        # Test combined filtering
        active_high_projects = project_service.list_projects(
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH
        )
        active_high_ids = [p.id for p in active_high_projects]
        assert project1.id in active_high_ids
        assert project2.id not in active_high_ids

    def test_project_patch_integration(self, project_service, sample_project_create):
        """Test patch application with real storage."""
        # Create project
        project = project_service.create_project(sample_project_create, "integration_test")
        
        # Apply patch
        patch = ProjectPatch(
            project_id=project.id,
            op=Op.UPDATE,
            name="Patched Project Name",
            priority=ProjectPriority.LOW,
            created_by="patch_user"
        )
        
        patched_project = project_service.apply_patch(patch)
        assert patched_project.name == "Patched Project Name"
        assert patched_project.priority == ProjectPriority.LOW
        
        # Verify persistence
        retrieved_project = project_service.get_project(project.id)
        assert retrieved_project.name == "Patched Project Name"
        assert retrieved_project.priority == ProjectPriority.LOW

    def test_project_validation_integration(self, project_service):
        """Test business rule validation with real storage."""
        # Test empty name validation
        with pytest.raises(ValueError, match="Project name cannot be empty"):
            project_service.create_project(ProjectCreate(
                name="",
                created_by="test_user"
            ), "integration_test")
        
        # Test duplicate name validation (if implemented)
        project1 = project_service.create_project(ProjectCreate(
            name="Unique Project Name",
            created_by="test_user"
        ), "integration_test")
        
        # Note: Uncomment if duplicate name validation is implemented
        # with pytest.raises(ValueError, match="Project name already exists"):
        #     project_service.create_project(ProjectCreate(
        #         name="Unique Project Name",
        #         created_by="test_user"
        #     ))

    def test_error_handling_integration(self, project_service):
        """Test error handling with real storage."""
        # Test operations on non-existent project
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            project_service.update_project("nonexistent", ProjectUpdate(name="New Name"))
        
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            project_service.delete_project("nonexistent")
        
        # Test invalid patch
        with pytest.raises(ValueError, match="Project with ID nonexistent not found"):
            project_service.apply_patch(ProjectPatch(
                project_id="nonexistent",
                op=Op.UPDATE,
                name="New Name",
                created_by="test_user"
            ))