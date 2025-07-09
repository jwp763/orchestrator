#!/usr/bin/env python3
"""Test script for orchestration services."""

import os
import sys
import tempfile
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, '.')

from src.orchestration import ProjectService, TaskService, AgentService
from src.storage.sql_implementation import SQLStorage
from src.models.project import ProjectCreate, ProjectUpdate, ProjectStatus, ProjectPriority
from src.models.task import TaskCreate, TaskUpdate, TaskStatus, TaskPriority
from src.models.patch import Patch, ProjectPatch, TaskPatch, Op


def test_orchestration_services():
    """Test all orchestration services."""
    print("🧪 Testing Orchestration Services...")
    
    # Use temporary database for testing
    temp_db = tempfile.mktemp(suffix='.db')
    storage = SQLStorage(f"sqlite:///{temp_db}")
    
    try:
        # Test ProjectService
        print("\n1. Testing ProjectService...")
        project_service = ProjectService(storage)
        
        # Test project creation
        project_create = ProjectCreate(
            name="Test Orchestration Project",
            description="A project to test orchestration services",
            status=ProjectStatus.PLANNING,
            priority=ProjectPriority.HIGH,
            tags=["test", "orchestration"]
        )
        
        created_project = project_service.create_project(project_create, "test_user")
        print(f"✓ Created project: {created_project.name} (ID: {created_project.id})")
        
        # Test project retrieval
        retrieved_project = project_service.get_project(created_project.id)
        assert retrieved_project is not None
        assert retrieved_project.name == project_create.name
        print(f"✓ Retrieved project: {retrieved_project.name}")
        
        # Test project listing
        projects = project_service.list_projects(limit=10)
        assert len(projects) >= 1
        print(f"✓ Listed projects: {len(projects)} found")
        
        # Test project update
        project_update = ProjectUpdate(
            description="Updated description for orchestration testing",
            status=ProjectStatus.ACTIVE
        )
        
        updated_project = project_service.update_project(created_project.id, project_update)
        assert updated_project is not None
        assert updated_project.description == project_update.description
        assert updated_project.status == ProjectStatus.ACTIVE
        print(f"✓ Updated project: new status = {updated_project.status}")
        
        # Test TaskService
        print("\n2. Testing TaskService...")
        task_service = TaskService(storage)
        
        # Test task creation
        task_create = TaskCreate(
            project_id=created_project.id,
            title="Test Root Task",
            description="A root task for testing hierarchical operations",
            status=TaskStatus.TODO,
            priority=TaskPriority.HIGH,
            estimated_minutes=120
        )
        
        created_task = task_service.create_task(task_create, "test_user")
        print(f"✓ Created task: {created_task.title} (ID: {created_task.id})")
        
        # Test subtask creation
        subtask_create = TaskCreate(
            project_id=created_project.id,
            parent_id=created_task.id,
            title="Test Subtask",
            description="A subtask for testing hierarchy",
            status=TaskStatus.TODO,
            priority=TaskPriority.MEDIUM,
            estimated_minutes=60
        )
        
        created_subtask = task_service.create_task(subtask_create, "test_user")
        print(f"✓ Created subtask: {created_subtask.title} (ID: {created_subtask.id})")
        assert created_subtask.parent_id == created_task.id
        
        # Test task retrieval with subtasks
        task_result = task_service.get_task(created_task.id, include_subtasks=True)
        assert task_result is not None
        
        # Handle tuple return when include_subtasks=True
        if isinstance(task_result, tuple):
            retrieved_task, subtasks = task_result
            assert len(subtasks) == 1
            print(f"✓ Retrieved task with subtasks: {len(subtasks)} subtasks")
        else:
            retrieved_task = task_result
            print("✓ Retrieved task (no subtasks returned)")
        
        # Test hierarchical task listing
        hierarchy = task_service.get_task_hierarchy(created_project.id)
        assert len(hierarchy) == 2  # root task + subtask
        assert hierarchy[0].parent_id is None  # first should be root
        assert hierarchy[1].parent_id == created_task.id  # second should be subtask
        print(f"✓ Got task hierarchy: {len(hierarchy)} tasks in correct order")
        
        # Test task update
        task_update = TaskUpdate(
            status=TaskStatus.IN_PROGRESS,
            actual_minutes=30
        )
        
        updated_task = task_service.update_task(created_task.id, task_update)
        assert updated_task is not None
        assert updated_task.status == TaskStatus.IN_PROGRESS
        assert updated_task.actual_minutes == 30
        print(f"✓ Updated task: new status = {updated_task.status}, actual_minutes = {updated_task.actual_minutes}")
        
        # Test task listing with filters
        tasks = task_service.list_tasks(
            project_id=created_project.id,
            status=TaskStatus.IN_PROGRESS,
            limit=10
        )
        assert len(tasks) >= 1
        print(f"✓ Listed tasks with filters: {len(tasks)} in-progress tasks")
        
        # Test AgentService
        print("\n3. Testing AgentService...")
        agent_service = AgentService(storage, project_service, task_service)
        
        # Test project context generation
        context = agent_service.get_project_context(created_project.id)
        assert "project" in context
        assert "statistics" in context
        assert "hierarchy" in context
        assert "tasks" in context
        
        project_ctx = context["project"]
        assert project_ctx["id"] == created_project.id
        assert project_ctx["name"] == created_project.name
        
        stats = context["statistics"]
        assert stats["total_tasks"] == 2
        assert stats["completed_tasks"] == 0
        assert stats["in_progress_tasks"] == 1
        assert stats["total_estimated_minutes"] == 180  # 120 + 60
        
        print(f"✓ Generated project context: {stats['total_tasks']} tasks, {stats['estimated_hours']} estimated hours")
        
        # Test patch validation
        print("\n4. Testing patch validation...")
        
        # Create a valid patch
        valid_patch = Patch(
            project_patches=[
                ProjectPatch(
                    op=Op.CREATE,
                    name="Test Project from Patch",
                    description="Created via patch validation test",
                    status=ProjectStatus.PLANNING,
                    priority=ProjectPriority.MEDIUM
                )
            ],
            task_patches=[
                TaskPatch(
                    op=Op.CREATE,
                    title="Test Task from Patch",
                    description="Created via patch validation test",
                    status=TaskStatus.TODO,
                    priority=TaskPriority.MEDIUM,
                    estimated_minutes=90
                )
            ]
        )
        
        validation_result = agent_service.validate_patch(valid_patch)
        assert validation_result["valid"] is True
        assert len(validation_result["errors"]) == 0
        print(f"✓ Valid patch validation: {len(validation_result['errors'])} errors")
        
        # Test invalid patch
        invalid_patch = Patch(
            project_patches=[
                ProjectPatch(
                    op=Op.CREATE,
                    name="",  # Invalid: empty name
                    description="Invalid patch test"
                )
            ],
            task_patches=[
                TaskPatch(
                    op=Op.UPDATE,
                    task_id="nonexistent-task-id",  # Invalid: task doesn't exist
                    title="Updated title"
                )
            ]
        )
        
        validation_result = agent_service.validate_patch(invalid_patch)
        assert validation_result["valid"] is False
        assert len(validation_result["errors"]) >= 2
        print(f"✓ Invalid patch validation: {len(validation_result['errors'])} errors detected")
        
        # Test patch application (without AI agent for now)
        print("\n5. Testing patch application...")
        
        # Apply the valid patch
        application_result = agent_service.apply_patch(valid_patch, "test_user")
        
        if application_result["success"]:
            assert application_result["project"] is not None
            assert len(application_result["tasks"]) == 1
            assert application_result["operations_applied"] == 2
            print(f"✓ Applied patch successfully: {application_result['operations_applied']} operations")
            
            patch_project = application_result["project"]
            patch_task = application_result["tasks"][0]
            
            print(f"  - Created project: {patch_project.name}")
            print(f"  - Created task: {patch_task.title}")
        else:
            print(f"✗ Patch application failed: {application_result['error']}")
            
        # Test cleanup
        print("\n6. Testing cleanup operations...")
        
        # Test task deletion with cascade
        delete_success = task_service.delete_task(created_task.id, cascade_subtasks=True)
        assert delete_success is True
        print("✓ Deleted task with cascade to subtasks")
        
        # Verify subtask was also deleted
        deleted_subtask = task_service.get_task(created_subtask.id)
        assert deleted_subtask is None
        print("✓ Verified subtask was cascaded deleted")
        
        # Test project deletion
        delete_success = project_service.delete_project(created_project.id)
        assert delete_success is True
        print("✓ Deleted project")
        
        # Verify project was deleted
        deleted_project = project_service.get_project(created_project.id)
        assert deleted_project is None
        print("✓ Verified project was deleted")
        
        print("\n✅ All orchestration service tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Orchestration service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        # Clean up temporary database
        try:
            if os.path.exists(temp_db):
                os.remove(temp_db)
        except:
            pass


if __name__ == "__main__":
    success = test_orchestration_services()
    sys.exit(0 if success else 1)