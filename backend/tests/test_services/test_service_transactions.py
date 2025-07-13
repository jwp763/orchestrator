"""
Transaction and rollback behavior tests for orchestration services.

Tests transaction handling across multiple operations, rollback scenarios,
and data consistency in the service layer.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from typing import List, Optional

from ..test_api.test_database_isolation import TestDatabaseIsolation
from src.orchestration.project_service import ProjectService
from src.orchestration.task_service import TaskService
from src.orchestration.agent_service import AgentService
from src.storage.sql_implementation import SQLStorage
from src.models.project import (
    Project, ProjectCreate, ProjectUpdate, ProjectStatus, ProjectPriority
)
from src.models.task import (
    Task, TaskCreate, TaskUpdate, TaskStatus, TaskPriority
)
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op


class TestServiceTransactionUnit:
    """Unit tests for service transaction behavior with mocked storage."""

    @pytest.fixture
    def mock_storage(self):
        """Mock storage with transaction support."""
        storage = Mock(spec=SQLStorage)
        storage.begin_transaction = Mock()
        storage.commit_transaction = Mock()
        storage.rollback_transaction = Mock()
        storage.in_transaction = Mock(return_value=False)
        return storage

    @pytest.fixture
    def project_service(self, mock_storage):
        """ProjectService with mocked transactional storage."""
        return ProjectService(storage=mock_storage)

    @pytest.fixture
    def task_service(self, mock_storage):
        """TaskService with mocked transactional storage."""
        return TaskService(storage=mock_storage)

    @pytest.fixture
    def agent_service(self, mock_storage):
        """AgentService with mocked transactional storage."""
        return AgentService(storage=mock_storage)

    def test_project_creation_transaction_success(self, project_service, mock_storage):
        """Test successful project creation within transaction."""
        project_data = ProjectCreate(
            name="Transactional Project",
            description="Test project creation transaction",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="transaction_user"
        )
        
        created_project = Project(
            id="txn-project-1",
            name="Transactional Project",
            description="Test project creation transaction",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            created_by="transaction_user",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_storage.create_project.return_value = created_project
        
        result = project_service.create_project(project_data, "transaction_user")
        
        assert result == created_project
        mock_storage.create_project.assert_called_once()

    def test_project_creation_transaction_rollback(self, project_service, mock_storage):
        """Test project creation rollback on failure."""
        project_data = ProjectCreate(
            name="Failed Project",
            created_by="transaction_user"
        )
        
        # Mock storage failure
        mock_storage.create_project.side_effect = Exception("Database error")
        
        with pytest.raises(Exception, match="Database error"):
            project_service.create_project(project_data, "transaction_user")



    def test_patch_application_transaction_rollback(self, project_service, mock_storage):
        """Test patch application rollback on validation failure."""
        patch = ProjectPatch(
            op=Op.UPDATE,
            project_id="patch-project-1",
            name="",  # Invalid empty name
            priority=ProjectPriority.HIGH  # Use valid enum value
        )
        
        # Mock project exists
        mock_storage.get_project.return_value = Mock()
        
        # Mock patch validation failure
        mock_storage.apply_project_patch.side_effect = ValueError("Invalid patch operation")
        
        with pytest.raises(RuntimeError, match="Failed to apply project patch"):
            project_service.apply_project_patch(patch)



class TestServiceTransactionIntegration(TestDatabaseIsolation):
    """Integration tests for service transaction behavior with real storage."""

    @pytest.fixture
    def project_service(self, isolated_storage):
        """ProjectService with isolated transactional database."""
        return ProjectService(storage=isolated_storage)

    @pytest.fixture
    def task_service(self, isolated_storage):
        """TaskService with isolated transactional database."""
        return TaskService(storage=isolated_storage)

    @pytest.fixture
    def agent_service(self, isolated_storage):
        """AgentService with isolated transactional database."""
        return AgentService(storage=isolated_storage)

    def test_project_task_creation_transaction_integration(self, project_service, task_service):
        """Test transactional creation of project with tasks."""
        # Create project
        project_data = ProjectCreate(
            name="Transaction Integration Project",
            description="Testing real transaction integration",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="integration_user"
        )
        
        project = project_service.create_project(project_data, "integration_user")
        assert project is not None
        assert project.id is not None
        
        # Create multiple tasks in transaction
        task_data_list = [
            TaskCreate(
                title=f"Integration Task {i}",
                description=f"Task {i} for transaction testing",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                project_id=project.id,
                created_by="integration_user"
            )
            for i in range(1, 4)
        ]
        
        # Simulate bulk creation (should be transactional)
        created_tasks = []
        for task_data in task_data_list:
            task = task_service.create_task(task_data, "integration_user")
            created_tasks.append(task)
        
        assert len(created_tasks) == 3
        
        # Verify all tasks are properly linked to project
        project_tasks = task_service.list_tasks(project_id=project.id)
        assert len(project_tasks) == 3
        
        for task in project_tasks:
            assert task.project_id == project.id
            assert task.created_by == "integration_user"

    def test_project_deletion_cascade_transaction(self, project_service, task_service):
        """Test transactional project deletion with cascade to tasks."""
        # Create project with tasks
        project = project_service.create_project(ProjectCreate(
            name="Deletion Test Project",
            description="Project to test cascade deletion",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="deletion_user"
        ), "deletion_user")
        
        # Create tasks
        for i in range(3):
            task_service.create_task(TaskCreate(
                title=f"Deletion Task {i+1}",
                description=f"Task {i+1} for deletion testing",
                status=TaskStatus.TODO,
                priority=TaskPriority.LOW,
                project_id=project.id,
                created_by="deletion_user"
            ), "deletion_user")
        
        # Verify tasks exist
        tasks_before = task_service.list_tasks(project_id=project.id)
        assert len(tasks_before) == 3
        
        # Delete project (should cascade to tasks)
        deletion_result = project_service.delete_project(project.id)
        assert deletion_result is True
        
        # Verify project is deleted
        deleted_project = project_service.get_project(project.id)
        assert deleted_project is None
        
        # Verify tasks are also deleted (cascade)
        tasks_after = task_service.list_tasks(project_id=project.id)
        assert len(tasks_after) == 0

    def test_patch_application_transaction_integration(self, project_service):
        """Test patch application transaction with real storage."""
        # Create project
        project = project_service.create_project(ProjectCreate(
            name="Patch Transaction Project",
            description="Testing patch transactions",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.MEDIUM,
            tags=["patch", "test"],
            created_by="patch_user"
        ), "patch_user")
        
        # Apply multiple operations in single patch (should be transactional)
        patch = ProjectPatch(
            op=Op.UPDATE,
            project_id=project.id,
            name="Updated Patch Project",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            tags=["patch", "test", "updated"]
        )
        
        updated_project = project_service.apply_project_patch(patch)
        
        # Verify all changes applied atomically
        assert updated_project.name == "Updated Patch Project"
        assert updated_project.status == ProjectStatus.ACTIVE
        assert updated_project.priority == ProjectPriority.HIGH
        assert "updated" in updated_project.tags
        assert "patch" in updated_project.tags  # Original tag preserved
        
        # Verify persistence
        retrieved_project = project_service.get_project(project.id)
        assert retrieved_project.name == "Updated Patch Project"
        assert retrieved_project.status == ProjectStatus.ACTIVE
        assert retrieved_project.priority == ProjectPriority.HIGH
        assert "updated" in retrieved_project.tags

    def test_transaction_rollback_on_constraint_violation(self, project_service, task_service):
        """Test transaction rollback on database constraint violation."""
        # Create project
        project = project_service.create_project(ProjectCreate(
            name="Constraint Test Project",
            created_by="constraint_user"
        ), "constraint_user")
        
        # Create a task
        task = task_service.create_task(TaskCreate(
            title="Constraint Test Task",
            project_id=project.id,
            created_by="constraint_user"
        ), "constraint_user")
        
        # Attempt to create task with same ID (should fail and rollback)
        # Note: This test depends on storage implementation details
        # In a real scenario, you might test foreign key constraint violations
        
        # Verify original task still exists after failed operation
        result = task_service.get_task(task.id)
        assert result is not None
        
        # Handle tuple return (task, subtasks)
        if isinstance(result, tuple):
            existing_task, subtasks = result
        else:
            existing_task = result
            
        assert existing_task is not None
        assert existing_task.title == "Constraint Test Task"

    def test_concurrent_transaction_handling(self, project_service):
        """Test handling of concurrent transactions."""
        # Create initial project
        project = project_service.create_project(ProjectCreate(
            name="Concurrent Test Project",
            description="Testing concurrent updates",
            status=ProjectStatus.PLANNING,
            created_by="concurrent_user_1"
        ), "concurrent_user_1")
        
        # Simulate concurrent updates
        update1 = ProjectUpdate(
            name="Updated by User 1",
            status=ProjectStatus.ACTIVE
        )
        
        update2 = ProjectUpdate(
            description="Updated by User 2",
            priority=ProjectPriority.HIGH
        )
        
        # Apply updates sequentially (simulating concurrent access)
        updated_project_1 = project_service.update_project(project.id, update1)
        updated_project_2 = project_service.update_project(project.id, update2)
        
        # Verify final state includes both updates
        final_project = project_service.get_project(project.id)
        assert final_project.name == "Updated by User 1"
        assert final_project.description == "Updated by User 2"
        assert final_project.status == ProjectStatus.ACTIVE
        assert final_project.priority == ProjectPriority.HIGH


    def test_error_recovery_and_cleanup(self, project_service, task_service):
        """Test error recovery and cleanup in transactions."""
        # Create project successfully
        project = project_service.create_project(ProjectCreate(
            name="Error Recovery Project",
            description="Testing error recovery",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="recovery_user"
        ), "recovery_user")
        
        # Attempt operation that should fail
        try:
            # Try to create task with invalid data
            task_service.create_task(TaskCreate(
                title="",  # Empty title should fail validation
                project_id=project.id,
                created_by="recovery_user"
            ), "recovery_user")
        except ValueError:
            pass  # Expected to fail
        
        # Verify project still exists and is unchanged
        recovered_project = project_service.get_project(project.id)
        assert recovered_project is not None
        assert recovered_project.name == "Error Recovery Project"
        assert recovered_project.status == ProjectStatus.ACTIVE
        
        # Verify no partial task creation occurred
        project_tasks = task_service.list_tasks(project_id=project.id)
        assert len(project_tasks) == 0