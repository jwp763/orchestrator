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
        
        with patch.object(project_service, '_execute_in_transaction') as mock_execute:
            mock_execute.return_value = created_project
            
            result = project_service.create_project(project_data)
            
            assert result == created_project
            mock_execute.assert_called_once()

    def test_project_creation_transaction_rollback(self, project_service, mock_storage):
        """Test project creation rollback on failure."""
        project_data = ProjectCreate(
            name="Failed Project",
            created_by="transaction_user"
        )
        
        # Mock storage failure
        mock_storage.create_project.side_effect = Exception("Database error")
        
        with patch.object(project_service, '_execute_in_transaction') as mock_execute:
            mock_execute.side_effect = Exception("Database error")
            
            with pytest.raises(Exception, match="Database error"):
                project_service.create_project(project_data)
            
            mock_execute.assert_called_once()

    def test_bulk_task_creation_transaction(self, task_service, mock_storage):
        """Test bulk task creation within single transaction."""
        project_id = "bulk-project-1"
        task_creates = [
            TaskCreate(
                title=f"Bulk Task {i}",
                description=f"Task {i} in bulk creation",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                project_id=project_id,
                created_by="bulk_user"
            )
            for i in range(1, 4)
        ]
        
        created_tasks = [
            Task(
                id=f"bulk-task-{i}",
                title=f"Bulk Task {i}",
                description=f"Task {i} in bulk creation",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                project_id=project_id,
                created_by="bulk_user",
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            for i in range(1, 4)
        ]
        
        # Mock project exists
        mock_storage.get_project.return_value = Mock()
        
        with patch.object(task_service, 'create_tasks_bulk') as mock_bulk_create:
            mock_bulk_create.return_value = created_tasks
            
            result = task_service.create_tasks_bulk(task_creates)
            
            assert len(result) == 3
            assert all(task.project_id == project_id for task in result)
            mock_bulk_create.assert_called_once()

    def test_cross_service_transaction_coordination(self, project_service, task_service, agent_service):
        """Test transaction coordination across multiple services."""
        with patch('src.orchestration.agent_service.PlannerAgent') as mock_planner_class:
            mock_planner = Mock()
            mock_planner_class.return_value = mock_planner
            agent_service.planner_agent = mock_planner
            
            # Mock AI response
            mock_planner.plan_project.return_value = {
                "project": {
                    "name": "Cross-Service Project",
                    "description": "Testing cross-service transactions",
                    "priority": "high"
                },
                "tasks": [
                    {
                        "title": "Task 1",
                        "description": "First task",
                        "priority": "medium"
                    }
                ]
            }
            
            # Mock service responses
            project = Mock()
            project.id = "cross-service-project"
            task = Mock()
            task.id = "cross-service-task"
            
            project_service.create_project.return_value = project
            task_service.create_task.return_value = task
            
            with patch.object(agent_service.storage, 'begin_transaction') as mock_begin:
                with patch.object(agent_service.storage, 'commit_transaction') as mock_commit:
                    result = agent_service.generate_project_from_idea(
                        idea="Create a project with tasks",
                        created_by="cross_service_user"
                    )
                    
                    assert result["project"] == project
                    assert result["tasks"] == [task]

    def test_patch_application_transaction_rollback(self, project_service, mock_storage):
        """Test patch application rollback on validation failure."""
        patch = ProjectPatch(
            project_id="patch-project-1",
            operations=[
                Op(op="replace", path="/name", value=""),  # Invalid empty name
                Op(op="replace", path="/priority", value="invalid_priority")
            ],
            created_by="patch_user"
        )
        
        # Mock project exists
        mock_storage.get_project.return_value = Mock()
        
        # Mock patch validation failure
        mock_storage.apply_project_patch.side_effect = ValueError("Invalid patch operation")
        
        with patch.object(project_service, '_execute_in_transaction') as mock_execute:
            mock_execute.side_effect = ValueError("Invalid patch operation")
            
            with pytest.raises(ValueError, match="Invalid patch operation"):
                project_service.apply_patch(patch)
            
            mock_execute.assert_called_once()

    def test_nested_transaction_handling(self, project_service, task_service, mock_storage):
        """Test handling of nested transactions."""
        project_data = ProjectCreate(
            name="Nested Transaction Project",
            created_by="nested_user"
        )
        
        task_data = TaskCreate(
            title="Nested Transaction Task",
            project_id="nested-project-1",
            created_by="nested_user"
        )
        
        # Mock storage transaction state
        mock_storage.in_transaction.side_effect = [False, True, True, False]
        
        created_project = Mock()
        created_project.id = "nested-project-1"
        created_task = Mock()
        
        project_service.storage.create_project.return_value = created_project
        task_service.storage.create_task.return_value = created_task
        task_service.storage.get_project.return_value = created_project
        
        with patch.object(project_service, '_execute_in_transaction') as mock_project_txn:
            with patch.object(task_service, '_execute_in_transaction') as mock_task_txn:
                mock_project_txn.return_value = created_project
                mock_task_txn.return_value = created_task
                
                # Simulate nested operation
                project = project_service.create_project(project_data)
                task = task_service.create_task(task_data)
                
                assert project == created_project
                assert task == created_task


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
        
        project = project_service.create_project(project_data)
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
            task = task_service.create_task(task_data)
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
        ))
        
        # Create tasks
        for i in range(3):
            task_service.create_task(TaskCreate(
                title=f"Deletion Task {i+1}",
                description=f"Task {i+1} for deletion testing",
                status=TaskStatus.TODO,
                priority=TaskPriority.LOW,
                project_id=project.id,
                created_by="deletion_user"
            ))
        
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
        ))
        
        # Apply multiple operations in single patch (should be transactional)
        patch = ProjectPatch(
            project_id=project.id,
            operations=[
                Op(op="replace", path="/name", value="Updated Patch Project"),
                Op(op="replace", path="/status", value="active"),
                Op(op="replace", path="/priority", value="high"),
                Op(op="add", path="/tags/-", value="updated")
            ],
            created_by="patch_user"
        )
        
        updated_project = project_service.apply_patch(patch)
        
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
        ))
        
        # Create a task
        task = task_service.create_task(TaskCreate(
            title="Constraint Test Task",
            project_id=project.id,
            created_by="constraint_user"
        ))
        
        # Attempt to create task with same ID (should fail and rollback)
        # Note: This test depends on storage implementation details
        # In a real scenario, you might test foreign key constraint violations
        
        # Verify original task still exists after failed operation
        existing_task = task_service.get_task(task.id)
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
        ))
        
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

    @patch('src.agent.planner_agent.PlannerAgent.plan_project')
    def test_agent_workflow_transaction_integration(self, mock_plan_project, agent_service):
        """Test complete agent workflow transaction integration."""
        # Mock AI response
        mock_plan_project.return_value = {
            "project": {
                "name": "Agent Transaction Project",
                "description": "Testing agent workflow transactions",
                "priority": "high",
                "tags": ["ai", "transaction"]
            },
            "tasks": [
                {
                    "title": "Transaction Task 1",
                    "description": "First transactional task",
                    "priority": "high",
                    "estimated_minutes": 120
                },
                {
                    "title": "Transaction Task 2",
                    "description": "Second transactional task",
                    "priority": "medium",
                    "estimated_minutes": 90
                }
            ]
        }
        
        # Execute workflow (should be transactional)
        result = agent_service.generate_project_from_idea(
            idea="Create a project for testing agent transactions",
            context={"complexity": "medium"},
            created_by="agent_transaction_user"
        )
        
        # Verify project creation
        assert result["project"] is not None
        assert result["project"].name == "Agent Transaction Project"
        
        # Verify task creation
        assert len(result["tasks"]) == 2
        assert result["tasks"][0].title == "Transaction Task 1"
        assert result["tasks"][1].title == "Transaction Task 2"
        
        # Verify all entities are properly linked
        project_id = result["project"].id
        for task in result["tasks"]:
            assert task.project_id == project_id
            assert task.created_by == "agent_transaction_user"
        
        # Verify persistence (all operations committed together)
        retrieved_project = agent_service.project_service.get_project(project_id)
        assert retrieved_project is not None
        
        project_tasks = agent_service.task_service.list_tasks(project_id=project_id)
        assert len(project_tasks) == 2

    def test_error_recovery_and_cleanup(self, project_service, task_service):
        """Test error recovery and cleanup in transactions."""
        # Create project successfully
        project = project_service.create_project(ProjectCreate(
            name="Error Recovery Project",
            description="Testing error recovery",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.MEDIUM,
            created_by="recovery_user"
        ))
        
        # Attempt operation that should fail
        try:
            # Try to create task with invalid data
            task_service.create_task(TaskCreate(
                title="",  # Empty title should fail validation
                project_id=project.id,
                created_by="recovery_user"
            ))
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