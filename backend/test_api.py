#!/usr/bin/env python3
"""Simple test script to verify API endpoints work."""

import json
import sys
import asyncio
from datetime import datetime
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, '.')

from src.api.main import app

def test_api_endpoints():
    """Test the main API endpoints."""
    client = TestClient(app)
    
    print("Testing API endpoints...")
    
    # Test health check
    print("\n1. Testing health check...")
    response = client.get("/health")
    assert response.status_code == 200
    print(f"✓ Health check: {response.json()}")
    
    # Test project creation
    print("\n2. Testing project creation...")
    project_data = {
        "name": "Test Project",
        "description": "A test project for API verification",
        "status": "planning",
        "priority": "medium",
        "tags": ["test", "api"],
        "created_by": "test_user"
    }
    
    response = client.post("/api/projects", json=project_data)
    if response.status_code == 201:
        project = response.json()
        project_id = project["id"]
        print(f"✓ Project created: {project['name']} (ID: {project_id})")
        
        # Test project retrieval
        print("\n3. Testing project retrieval...")
        response = client.get(f"/api/projects/{project_id}")
        if response.status_code == 200:
            project = response.json()
            print(f"✓ Project retrieved: {project['name']}")
            
            # Test task creation
            print("\n4. Testing task creation...")
            task_data = {
                "project_id": project_id,
                "title": "Test Task",
                "description": "A test task",
                "status": "todo",
                "priority": "medium",
                "estimated_minutes": 60,
                "created_by": "test_user"
            }
            
            response = client.post("/api/tasks", json=task_data)
            if response.status_code == 201:
                task = response.json()
                task_id = task["id"]
                print(f"✓ Task created: {task['title']} (ID: {task_id})")
                
                # Test task retrieval
                print("\n5. Testing task retrieval...")
                response = client.get(f"/api/tasks/{task_id}")
                if response.status_code == 200:
                    task = response.json()
                    print(f"✓ Task retrieved: {task['title']}")
                    
                    # Test project tasks retrieval
                    print("\n6. Testing project tasks retrieval...")
                    response = client.get(f"/api/projects/{project_id}/tasks")
                    if response.status_code == 200:
                        tasks = response.json()
                        print(f"✓ Project tasks retrieved: {len(tasks)} tasks")
                        
                        # Test task update
                        print("\n7. Testing task update...")
                        update_data = {
                            "status": "in_progress",
                            "actual_minutes": 30
                        }
                        
                        response = client.put(f"/api/tasks/{task_id}", json=update_data)
                        if response.status_code == 200:
                            updated_task = response.json()
                            print(f"✓ Task updated: status={updated_task['status']}, actual_minutes={updated_task['actual_minutes']}")
                            
                            # Test projects list
                            print("\n8. Testing projects list...")
                            response = client.get("/api/projects")
                            if response.status_code == 200:
                                projects_list = response.json()
                                print(f"✓ Projects list retrieved: {projects_list['total']} projects")
                                
                                # Test tasks list
                                print("\n9. Testing tasks list...")
                                response = client.get("/api/tasks")
                                if response.status_code == 200:
                                    tasks_list = response.json()
                                    print(f"✓ Tasks list retrieved: {tasks_list['total']} tasks")
                                    
                                    print("\n✅ All API tests passed!")
                                    return True
                                else:
                                    print(f"❌ Tasks list failed: {response.status_code} - {response.text}")
                            else:
                                print(f"❌ Projects list failed: {response.status_code} - {response.text}")
                        else:
                            print(f"❌ Task update failed: {response.status_code} - {response.text}")
                    else:
                        print(f"❌ Project tasks retrieval failed: {response.status_code} - {response.text}")
                else:
                    print(f"❌ Task retrieval failed: {response.status_code} - {response.text}")
            else:
                print(f"❌ Task creation failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Project retrieval failed: {response.status_code} - {response.text}")
    else:
        print(f"❌ Project creation failed: {response.status_code} - {response.text}")
    
    return False

if __name__ == "__main__":
    success = test_api_endpoints()
    sys.exit(0 if success else 1)