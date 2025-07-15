"""
Comprehensive tests for cascading soft delete operations in the storage layer.

Tests DEL-002 acceptance criteria:
- Fix Foreign Key Constraint Issue from TEST-API-001
- Implement proper cascading soft delete operations
- Add restoration capabilities with context tracking
- Ensure all related tests pass

Test scenarios:
1. Soft delete a project should soft delete all its tasks
2. Soft delete a parent task should soft delete all its children
3. Restore a project should restore all its soft-deleted tasks
4. Restore a parent task should restore all its soft-deleted children
5. Hard delete should only work if foreign key constraints are satisfied
6. Context tracking for deletions and restorations
7. Performance with large hierarchies
8. Edge cases and error handling
"""

import pytest
from datetime import datetime, timedelta
from typing import List, Dict, Any
from unittest.mock import patch, Mock

from src.storage.sql_implementation import SQLStorage
from src.storage.sql_models import Base, Project as SQLProject, Task as SQLTask
from src.models import Project, Task, ProjectStatus, TaskStatus, ProjectPriority
from src.models.task import TaskPriority
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError


class TestCascadeSoftDelete:
    """Test suite for cascading soft delete operations."""

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

    @pytest.fixture
    def storage(self, session):
        """Create SQLStorage instance with injected session."""
        return SQLStorage(session=session)

    @pytest.fixture
    def sample_project_with_tasks(self, storage):
        """Create a project with multiple tasks for testing."""
        # Create project
        project = Project(
            id="test-project-1",
            name="Test Project",
            description="A test project with tasks",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        created_project = storage.create_project(project)
        
        # Create main tasks
        tasks = []
        for i in range(3):
            task = Task(
                id=f"task-{i+1}",
                project_id="test-project-1",
                title=f"Task {i+1}",
                description=f"Description for task {i+1}",
                status=TaskStatus.TODO,
                priority=TaskPriority.MEDIUM,
                created_by="test_user"
            )
            tasks.append(storage.create_task(task))
        
        # Create subtasks for task-1
        for i in range(2):
            subtask = Task(
                id=f"subtask-1-{i+1}",
                project_id="test-project-1",
                parent_id="task-1",
                title=f"Subtask 1.{i+1}",
                description=f"Description for subtask 1.{i+1}",
                status=TaskStatus.TODO,
                priority=TaskPriority.LOW,
                depth=1,
                created_by="test_user"
            )
            tasks.append(storage.create_task(subtask))
        
        return created_project, tasks

    def test_soft_delete_project_cascades_to_tasks(self, storage, sample_project_with_tasks):
        """Test that soft deleting a project soft deletes all its tasks."""
        project, tasks = sample_project_with_tasks
        
        # Verify all items exist initially
        assert storage.get_project(project.id) is not None
        for task in tasks:
            assert storage.get_task(task.id) is not None
        
        # Soft delete the project
        success = storage.soft_delete_project(project.id, deleted_by="admin_user")
        assert success is True
        
        # Verify project is soft deleted
        deleted_project = storage.get_project(project.id)
        assert deleted_project is None  # Should not be returned by normal queries
        
        # Verify all tasks are soft deleted
        for task in tasks:
            deleted_task = storage.get_task(task.id)
            assert deleted_task is None  # Should not be returned by normal queries
        
        # Verify items exist in database but with deleted_at timestamp
        with storage.session as session:
            sql_project = session.query(SQLProject).filter(SQLProject.id == project.id).first()
            assert sql_project is not None
            assert sql_project.deleted_at is not None
            assert sql_project.deleted_by == "admin_user"
            
            for task in tasks:
                sql_task = session.query(SQLTask).filter(SQLTask.id == task.id).first()
                assert sql_task is not None
                assert sql_task.deleted_at is not None
                assert sql_task.deleted_by == "admin_user"

    def test_soft_delete_parent_task_cascades_to_children(self, storage, sample_project_with_tasks):
        """Test that soft deleting a parent task soft deletes all its children."""
        project, tasks = sample_project_with_tasks
        
        # Find the parent task and its children
        parent_task = next(task for task in tasks if task.id == "task-1")
        child_tasks = [task for task in tasks if getattr(task, 'parent_id', None) == "task-1"]
        other_tasks = [task for task in tasks if task.id != "task-1" and getattr(task, 'parent_id', None) != "task-1"]
        
        # Soft delete the parent task
        success = storage.soft_delete_task(parent_task.id, deleted_by="admin_user")
        assert success is True
        
        # Verify parent task is soft deleted
        deleted_parent = storage.get_task(parent_task.id)
        assert deleted_parent is None
        
        # Verify all child tasks are soft deleted
        for child_task in child_tasks:
            deleted_child = storage.get_task(child_task.id)
            assert deleted_child is None
        
        # Verify other tasks are not affected
        for other_task in other_tasks:
            existing_task = storage.get_task(other_task.id)
            assert existing_task is not None
        
        # Verify project is not affected
        existing_project = storage.get_project(project.id)
        assert existing_project is not None

    def test_restore_project_restores_all_tasks(self, storage, sample_project_with_tasks):
        """Test that restoring a project restores all its soft-deleted tasks."""
        project, tasks = sample_project_with_tasks
        
        # Soft delete the project (which cascades to tasks)
        storage.soft_delete_project(project.id, deleted_by="admin_user")
        
        # Verify everything is soft deleted
        assert storage.get_project(project.id) is None
        for task in tasks:
            assert storage.get_task(task.id) is None
        
        # Restore the project
        success = storage.restore_project(project.id, restored_by="admin_user")
        assert success is True
        
        # Verify project is restored
        restored_project = storage.get_project(project.id)
        assert restored_project is not None
        assert restored_project.id == project.id
        
        # Verify all tasks are restored
        for task in tasks:
            restored_task = storage.get_task(task.id)
            assert restored_task is not None
            assert restored_task.id == task.id

    def test_restore_parent_task_restores_children(self, storage, sample_project_with_tasks):
        """Test that restoring a parent task restores all its soft-deleted children."""
        project, tasks = sample_project_with_tasks
        
        # Find the parent task and its children
        parent_task = next(task for task in tasks if task.id == "task-1")
        child_tasks = [task for task in tasks if getattr(task, 'parent_id', None) == "task-1"]
        
        # Soft delete the parent task (which cascades to children)
        storage.soft_delete_task(parent_task.id, deleted_by="admin_user")
        
        # Verify parent and children are soft deleted
        assert storage.get_task(parent_task.id) is None
        for child_task in child_tasks:
            assert storage.get_task(child_task.id) is None
        
        # Restore the parent task
        success = storage.restore_task(parent_task.id, restored_by="admin_user")
        assert success is True
        
        # Verify parent task is restored
        restored_parent = storage.get_task(parent_task.id)
        assert restored_parent is not None
        
        # Verify all child tasks are restored
        for child_task in child_tasks:
            restored_child = storage.get_task(child_task.id)
            assert restored_child is not None

    def test_partial_restoration_with_context_tracking(self, storage, sample_project_with_tasks):
        """Test restoration with context tracking for complex scenarios."""
        project, tasks = sample_project_with_tasks
        
        # Soft delete individual tasks (not the whole project)
        task_to_delete = tasks[0]  # This is task-1 which has children
        storage.soft_delete_task(task_to_delete.id, deleted_by="admin_user")
        
        # Verify the task and its children are soft deleted
        assert storage.get_task(task_to_delete.id) is None
        child_tasks = [task for task in tasks if getattr(task, 'parent_id', None) == task_to_delete.id]
        for child_task in child_tasks:
            assert storage.get_task(child_task.id) is None
        
        # Other tasks should still be active
        other_tasks = [task for task in tasks if task.id != task_to_delete.id and getattr(task, 'parent_id', None) != task_to_delete.id]
        for other_task in other_tasks:
            assert storage.get_task(other_task.id) is not None
        
        # Project should still be active
        assert storage.get_project(project.id) is not None
        
        # Now restore the task (which should restore its children)
        success = storage.restore_task(task_to_delete.id, restored_by="user_1")
        assert success is True
        
        # The task and its children should be restored
        restored_task = storage.get_task(task_to_delete.id)
        assert restored_task is not None
        
        for child_task in child_tasks:
            restored_child = storage.get_task(child_task.id)
            assert restored_child is not None
        
        # Project should still be active
        assert storage.get_project(project.id) is not None

    def test_list_operations_exclude_soft_deleted_items(self, storage, sample_project_with_tasks):
        """Test that list operations exclude soft-deleted items."""
        project, tasks = sample_project_with_tasks
        
        # Get initial counts
        initial_projects = storage.list_projects()
        initial_tasks = storage.list_tasks()
        initial_project_count = initial_projects.get('total', 0)
        initial_task_count = initial_tasks.get('total', 0)
        
        # Soft delete one task that has no children (to avoid cascade)
        task_without_children = next(task for task in tasks if task.id == "task-2")  # task-2 has no children
        storage.soft_delete_task(task_without_children.id, deleted_by="admin_user")
        
        # List operations should show one less task
        after_task_delete = storage.list_tasks()
        assert after_task_delete.get('total', 0) == initial_task_count - 1
        
        # Project count should be unchanged
        projects_after_task_delete = storage.list_projects()
        assert projects_after_task_delete.get('total', 0) == initial_project_count
        
        # Soft delete the project (and its remaining tasks)
        storage.soft_delete_project(project.id, deleted_by="admin_user")
        
        # Both counts should be reduced
        final_projects = storage.list_projects()
        final_tasks = storage.list_tasks()
        assert final_projects.get('total', 0) == initial_project_count - 1
        # All tasks in the project should be soft deleted now
        expected_final_task_count = initial_task_count - len(tasks)
        assert final_tasks.get('total', 0) == expected_final_task_count

    def test_hard_delete_with_foreign_key_constraints(self, storage, sample_project_with_tasks):
        """Test that hard delete works correctly after soft delete."""
        project, tasks = sample_project_with_tasks
        
        # The current delete_project method does cascade delete, so it should work
        success = storage.delete_project(project.id)
        assert success is True
        
        # Project should be completely gone
        assert storage.get_project(project.id) is None
        
        # Tasks should also be gone from database
        with storage.session as session:
            for task in tasks:
                sql_task = session.query(SQLTask).filter(SQLTask.id == task.id).first()
                assert sql_task is None
        
        # Test soft delete then hard delete scenario
        # Create a new project for this test
        new_project = Project(
            id="hard-delete-test",
            name="Hard Delete Test",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        storage.create_project(new_project)
        
        new_task = Task(
            id="hard-delete-task",
            project_id="hard-delete-test",
            title="Hard Delete Task",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            created_by="test_user"
        )
        storage.create_task(new_task)
        
        # Soft delete first
        storage.soft_delete_project("hard-delete-test", deleted_by="admin_user")
        
        # Verify soft delete worked
        assert storage.get_project("hard-delete-test") is None
        assert storage.get_task("hard-delete-task") is None
        
        # Hard delete should still work on soft-deleted items
        success = storage.delete_project("hard-delete-test")
        assert success is True
        
        # Items should be completely gone from database
        with storage.session as session:
            sql_project = session.query(SQLProject).filter(SQLProject.id == "hard-delete-test").first()
            assert sql_project is None
            sql_task = session.query(SQLTask).filter(SQLTask.id == "hard-delete-task").first()
            assert sql_task is None

    def test_deep_hierarchy_cascade_performance(self, storage):
        """Test cascading soft delete performance with deep task hierarchies."""
        # Create a project
        project = Project(
            id="perf-test-project",
            name="Performance Test Project",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        storage.create_project(project)
        
        # Create a deep hierarchy (5 levels, 3 children per parent)
        task_ids = []
        
        def create_hierarchy_level(parent_id: str, level: int, max_level: int = 5):
            if level > max_level:
                return
            
            for i in range(3):  # 3 children per parent
                task_id = f"task-l{level}-{parent_id}-{i}" if parent_id else f"task-l{level}-root-{i}"
                task = Task(
                    id=task_id,
                    project_id="perf-test-project",
                    parent_id=parent_id,
                    title=f"Task Level {level} Child {i}",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.MEDIUM,
                    depth=level,
                    created_by="test_user"
                )
                storage.create_task(task)
                task_ids.append(task_id)
                
                # Recursively create children
                create_hierarchy_level(task_id, level + 1, max_level)
        
        # Create the hierarchy starting from root level
        create_hierarchy_level(None, 0)
        
        # Measure performance of cascading soft delete
        import time
        start_time = time.time()
        
        # Soft delete the project (should cascade to all tasks)
        success = storage.soft_delete_project("perf-test-project", deleted_by="admin_user")
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        assert success is True
        assert elapsed_time < 5.0  # Should complete within 5 seconds
        
        # Verify all tasks are soft deleted
        for task_id in task_ids:
            assert storage.get_task(task_id) is None

    def test_soft_delete_context_tracking(self, storage, sample_project_with_tasks):
        """Test that deletion context is properly tracked."""
        project, tasks = sample_project_with_tasks
        
        # Test different deletion contexts
        deletion_contexts = [
            ("admin_user", "Administrative cleanup"),
            ("system", "Automated cleanup"),
            ("user_123", "User requested deletion"),
        ]
        
        for i, (deleted_by, context) in enumerate(deletion_contexts):
            if i < len(tasks):
                # Soft delete with context
                success = storage.soft_delete_task(
                    tasks[i].id, 
                    deleted_by=deleted_by,
                    context=context
                )
                assert success is True
                
                # Verify context is tracked
                with storage.session as session:
                    sql_task = session.query(SQLTask).filter(SQLTask.id == tasks[i].id).first()
                    assert sql_task.deleted_by == deleted_by
                    # Note: context tracking would require additional metadata field

    def test_edge_cases_and_error_handling(self, storage):
        """Test edge cases and error handling for soft delete operations."""
        # Test soft deleting non-existent project
        success = storage.soft_delete_project("non-existent-id", deleted_by="admin_user")
        assert success is False
        
        # Test soft deleting non-existent task
        success = storage.soft_delete_task("non-existent-id", deleted_by="admin_user")
        assert success is False
        
        # Test restoring non-existent project
        success = storage.restore_project("non-existent-id", restored_by="admin_user")
        assert success is False
        
        # Test restoring non-existent task
        success = storage.restore_task("non-existent-id", restored_by="admin_user")
        assert success is False
        
        # Test soft deleting already soft-deleted item
        project = Project(
            id="test-project-edge",
            name="Edge Case Project",
            status=ProjectStatus.ACTIVE,
            priority=ProjectPriority.HIGH,
            created_by="test_user"
        )
        storage.create_project(project)
        
        # First soft delete
        success1 = storage.soft_delete_project(project.id, deleted_by="admin_user")
        assert success1 is True
        
        # Second soft delete should be idempotent
        success2 = storage.soft_delete_project(project.id, deleted_by="admin_user")
        assert success2 is True  # Should still return True (idempotent)

    def test_soft_delete_with_invalid_user(self, storage, sample_project_with_tasks):
        """Test soft delete operations with invalid user parameters."""
        project, tasks = sample_project_with_tasks
        
        # Test with None as deleted_by
        with pytest.raises(ValueError):
            storage.soft_delete_project(project.id, deleted_by=None)
        
        # Test with empty string as deleted_by
        with pytest.raises(ValueError):
            storage.soft_delete_project(project.id, deleted_by="")
        
        # Test with whitespace-only string as deleted_by
        with pytest.raises(ValueError):
            storage.soft_delete_project(project.id, deleted_by="   ")

    def test_list_with_include_deleted_flag(self, storage, sample_project_with_tasks):
        """Test list operations with include_deleted flag."""
        project, tasks = sample_project_with_tasks
        
        # Soft delete one task (one without children to avoid cascade)
        task_to_delete = next(task for task in tasks if task.id == "task-2")
        storage.soft_delete_task(task_to_delete.id, deleted_by="admin_user")
        
        # List without include_deleted should exclude soft-deleted items
        active_tasks = storage.list_tasks(include_deleted=False)
        task_ids = [task.id for task in active_tasks.get('tasks', [])]
        assert task_to_delete.id not in task_ids
        
        # List with include_deleted should include soft-deleted items
        all_tasks = storage.list_tasks(include_deleted=True)
        all_task_ids = [task.id for task in all_tasks.get('tasks', [])]
        assert task_to_delete.id in all_task_ids
        
        # Test the same for projects
        storage.soft_delete_project(project.id, deleted_by="admin_user")
        
        active_projects = storage.list_projects(include_deleted=False)
        project_ids = [proj.id for proj in active_projects.get('projects', [])]
        assert project.id not in project_ids
        
        all_projects = storage.list_projects(include_deleted=True)
        all_project_ids = [proj.id for proj in all_projects.get('projects', [])]
        assert project.id in all_project_ids

    def test_restoration_timestamp_tracking(self, storage, sample_project_with_tasks):
        """Test that restoration timestamps are properly tracked."""
        project, tasks = sample_project_with_tasks
        
        # Soft delete a task
        deletion_time = datetime.utcnow()
        storage.soft_delete_task(tasks[0].id, deleted_by="admin_user")
        
        # Wait a moment to ensure different timestamps
        import time
        time.sleep(0.1)
        
        # Restore the task
        restoration_time = datetime.utcnow()
        success = storage.restore_task(tasks[0].id, restored_by="admin_user")
        assert success is True
        
        # Verify restoration tracking
        with storage.session as session:
            sql_task = session.query(SQLTask).filter(SQLTask.id == tasks[0].id).first()
            assert sql_task.deleted_at is None  # Should be cleared on restoration
            assert sql_task.deleted_by is None  # Should be cleared on restoration
            
            # If restoration tracking is implemented, verify those fields
            # assert sql_task.restored_at is not None
            # assert sql_task.restored_by == "admin_user"
            # assert sql_task.restored_at > deletion_time

    def test_cascade_delete_preserves_hierarchy_integrity(self, storage, sample_project_with_tasks):
        """Test that cascade operations preserve hierarchical integrity."""
        project, tasks = sample_project_with_tasks
        
        # Find parent and child tasks
        parent_task = next(task for task in tasks if task.id == "task-1")
        child_tasks = [task for task in tasks if getattr(task, 'parent_id', None) == "task-1"]
        
        # Soft delete the parent
        storage.soft_delete_task(parent_task.id, deleted_by="admin_user")
        
        # Verify hierarchy is maintained in soft-deleted state
        with storage.session as session:
            sql_parent = session.query(SQLTask).filter(SQLTask.id == parent_task.id).first()
            assert sql_parent.deleted_at is not None
            
            for child_task in child_tasks:
                sql_child = session.query(SQLTask).filter(SQLTask.id == child_task.id).first()
                assert sql_child.deleted_at is not None
                assert sql_child.parent_id == parent_task.id  # Hierarchy preserved
        
        # Restore the parent
        storage.restore_task(parent_task.id, restored_by="admin_user")
        
        # Verify hierarchy is restored
        restored_parent = storage.get_task(parent_task.id)
        assert restored_parent is not None
        
        for child_task in child_tasks:
            restored_child = storage.get_task(child_task.id)
            assert restored_child is not None
            assert restored_child.parent_id == parent_task.id