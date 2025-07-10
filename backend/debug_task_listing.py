#!/usr/bin/env python3
"""Debug script to analyze task listing pagination issues."""

import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from src.storage.sql_implementation import SQLStorage
from src.models.task import Task
from src.models.project import Project

def debug_task_listing():
    """Debug task listing pagination issues."""
    storage = SQLStorage()
    
    print("=== TASK LISTING ANALYSIS ===")
    
    # 1. Check total projects
    projects = storage.get_projects()
    print(f"Total projects in database: {len(projects)}")
    
    # 2. Check total tasks across all projects
    all_tasks = []
    for project in projects:
        project_tasks = storage.get_tasks_by_project(project.id)
        all_tasks.extend(project_tasks)
        print(f"Project '{project.name}' ({project.id[:8]}...): {len(project_tasks)} tasks")
    
    print(f"Total tasks across all projects: {len(all_tasks)}")
    
    # 3. Check what the current task listing endpoint logic would return
    print("\n=== SIMULATING CURRENT API LOGIC ===")
    
    # Simulate the current API logic from task_routes.py lines 115-138
    # Get all tasks from all projects (lines 120-123)
    api_all_tasks = []
    for project in projects:
        api_all_tasks.extend(storage.get_tasks_by_project(project.id))
    
    print(f"Tasks collected by API logic: {len(api_all_tasks)}")
    
    # Apply pagination (default skip=0, limit=100)
    skip = 0
    limit = 100
    paginated_tasks = api_all_tasks[skip:skip + limit]
    
    print(f"Tasks after pagination (skip={skip}, limit={limit}): {len(paginated_tasks)}")
    
    # 4. Check ordering - is there any ordering in the current implementation?
    print("\n=== TASK ORDERING ANALYSIS ===")
    if all_tasks:
        print("First 5 tasks by database order:")
        for i, task in enumerate(all_tasks[:5]):
            print(f"  {i+1}. {task.title} (created: {task.created_at})")
        
        print("\nLast 5 tasks by database order:")
        for i, task in enumerate(all_tasks[-5:]):
            print(f"  {len(all_tasks)-4+i}. {task.title} (created: {task.created_at})")
    
    # 5. Create a test task and see where it appears
    print("\n=== CREATING TEST TASK ===")
    
    # Find a project to use
    if projects:
        test_project = projects[0]
        print(f"Using project: {test_project.name}")
        
        # Count tasks before
        before_tasks = storage.get_tasks_by_project(test_project.id)
        print(f"Tasks in project before creation: {len(before_tasks)}")
        
        # Create a test task
        test_task = Task(
            project_id=test_project.id,
            title="DEBUG TEST TASK - Should appear in listing",
            description="This task is created to test pagination issues",
            status="todo",
            priority="high",
            created_by="debug_script"
        )
        
        created_task = storage.create_task(test_task)
        print(f"Created test task: {created_task.id}")
        
        # Count tasks after
        after_tasks = storage.get_tasks_by_project(test_project.id)
        print(f"Tasks in project after creation: {len(after_tasks)}")
        
        # Simulate API call again
        api_all_tasks_after = []
        for project in projects:
            api_all_tasks_after.extend(storage.get_tasks_by_project(project.id))
        
        # Check if our task appears in first 100
        paginated_tasks_after = api_all_tasks_after[skip:skip + limit]
        our_task_in_listing = any(t.id == created_task.id for t in paginated_tasks_after)
        
        print(f"Total tasks after creation: {len(api_all_tasks_after)}")
        print(f"Our test task appears in first {limit} tasks: {our_task_in_listing}")
        
        if not our_task_in_listing:
            print("ISSUE IDENTIFIED: Newly created task does not appear in default pagination!")
            print("This is likely due to:")
            print("  1. No ordering - tasks appear in database insertion order")
            print("  2. With many existing tasks, new tasks appear at the end")
            print("  3. Default pagination only shows first 100 tasks")
        
        # Find our task position
        task_position = next((i for i, t in enumerate(api_all_tasks_after) if t.id == created_task.id), -1)
        if task_position >= 0:
            print(f"Our test task is at position {task_position + 1} in the full list")
        
        # Clean up
        storage.delete_task(created_task.id)
        print("Cleaned up test task")
    
    print("\n=== RECOMMENDED SOLUTIONS ===")
    print("1. Add ORDER BY created_at DESC to show newest tasks first")
    print("2. Reduce default limit or add better pagination metadata")
    print("3. Add proper filtering and search capabilities")
    print("4. Add database indexes for performance")

if __name__ == "__main__":
    debug_task_listing()