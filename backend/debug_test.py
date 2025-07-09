#!/usr/bin/env python3

"""Debug script to identify the specific issues causing test failures."""

from fastapi.testclient import TestClient
from src.api.main import app
import json

def debug_project_task_relationship():
    """Debug the project-task relationship lifecycle test."""
    client = TestClient(app)
    
    print("=== DEBUGGING PROJECT-TASK RELATIONSHIP LIFECYCLE ===")
    
    # 1. Create project
    project_data = {
        "name": "Debug Relationship Test Project",
        "description": "Testing project-task relationships",
        "status": "planning",
        "priority": "high",
        "created_by": "debug_user"
    }
    
    project_response = client.post("/api/projects", json=project_data)
    print(f"Create project response: {project_response.status_code}")
    if project_response.status_code != 201:
        print(f"Error creating project: {project_response.text}")
        return
    
    project = project_response.json()
    project_id = project["id"]
    print(f"Created project ID: {project_id}")
    
    # 2. Create a task
    task_data = {
        "project_id": project_id,
        "title": "Debug Task",
        "description": "Debug task",
        "status": "todo",
        "priority": "high",
        "estimated_minutes": 60,
        "created_by": "debug_user"
    }
    
    task_response = client.post("/api/tasks", json=task_data)
    print(f"Create task response: {task_response.status_code}")
    if task_response.status_code != 201:
        print(f"Error creating task: {task_response.text}")
        return
    
    task = task_response.json()
    task_id = task["id"]
    print(f"Created task ID: {task_id}")
    
    # 3. Check project with tasks
    get_project_response = client.get(f"/api/projects/{project_id}")
    print(f"Get project with tasks response: {get_project_response.status_code}")
    if get_project_response.status_code == 200:
        project_with_tasks = get_project_response.json()
        print(f"Project has {len(project_with_tasks.get('tasks', []))} tasks")
    else:
        print(f"Error getting project: {get_project_response.text}")
    
    # 4. Try to delete project with tasks
    delete_project_response = client.delete(f"/api/projects/{project_id}")
    print(f"Delete project response: {delete_project_response.status_code}")
    if delete_project_response.status_code != 204:
        print(f"Error deleting project: {delete_project_response.text}")
        
        # Let's try deleting the task first
        print("\n--- Trying to delete task first ---")
        delete_task_response = client.delete(f"/api/tasks/{task_id}")
        print(f"Delete task response: {delete_task_response.status_code}")
        if delete_task_response.status_code != 204:
            print(f"Error deleting task: {delete_task_response.text}")
        else:
            print("Task deleted successfully")
            
            # Now try deleting project again
            delete_project_response2 = client.delete(f"/api/projects/{project_id}")
            print(f"Delete project (2nd try) response: {delete_project_response2.status_code}")
            if delete_project_response2.status_code != 204:
                print(f"Error deleting project (2nd try): {delete_project_response2.text}")
            else:
                print("Project deleted successfully after deleting task")

def debug_task_lifecycle():
    """Debug the task lifecycle test."""
    client = TestClient(app)
    
    print("\n=== DEBUGGING TASK LIFECYCLE ===")
    
    # 1. Create project
    project_data = {
        "name": "Debug Task Lifecycle Project",
        "description": "Project for task lifecycle debugging",
        "status": "planning",
        "priority": "high",
        "created_by": "debug_user"
    }
    
    project_response = client.post("/api/projects", json=project_data)
    print(f"Create project response: {project_response.status_code}")
    if project_response.status_code != 201:
        print(f"Error creating project: {project_response.text}")
        return
    
    project = project_response.json()
    project_id = project["id"]
    print(f"Created project ID: {project_id}")
    
    # 2. Create task
    task_data = {
        "project_id": project_id,
        "title": "Debug Lifecycle Task",
        "description": "Testing complete task lifecycle",
        "status": "todo",
        "priority": "medium",
        "tags": ["lifecycle", "integration"],
        "estimated_minutes": 120,
        "assignee": "debug_user",
        "created_by": "debug_user"
    }
    
    task_response = client.post("/api/tasks", json=task_data)
    print(f"Create task response: {task_response.status_code}")
    if task_response.status_code != 201:
        print(f"Error creating task: {task_response.text}")
        return
    
    task = task_response.json()
    task_id = task["id"]
    print(f"Created task ID: {task_id}")
    
    # 3. Update task
    update_data = {
        "title": "Updated Debug Task",
        "status": "in_progress",
        "priority": "high"
    }
    
    update_response = client.put(f"/api/tasks/{task_id}", json=update_data)
    print(f"Update task response: {update_response.status_code}")
    if update_response.status_code != 200:
        print(f"Error updating task: {update_response.text}")
    else:
        updated_task = update_response.json()
        print(f"Updated task title: {updated_task['title']}")
    
    # 4. Check if task appears in listings
    list_response = client.get("/api/tasks")
    print(f"List tasks response: {list_response.status_code}")
    if list_response.status_code == 200:
        tasks_list = list_response.json()
        print(f"Total tasks in listing: {len(tasks_list['tasks'])}")
        our_task = next((t for t in tasks_list["tasks"] if t["id"] == task_id), None)
        print(f"Our task found in listing: {our_task is not None}")
        if our_task:
            print(f"Our task title in listing: {our_task['title']}")
    else:
        print(f"Error listing tasks: {list_response.text}")

if __name__ == "__main__":
    debug_project_task_relationship()
    debug_task_lifecycle()