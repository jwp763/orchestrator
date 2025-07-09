#!/usr/bin/env python3
"""Test script to verify API integration with orchestration services."""

import json
import sys
from fastapi.testclient import TestClient

# Add the src directory to the path
sys.path.insert(0, '.')

from src.api.main import app

def test_api_with_orchestration():
    """Test the API endpoints with orchestration services."""
    client = TestClient(app)
    
    print("Testing API with orchestration services...")
    
    # Test health check
    print("\n1. Testing health check...")
    response = client.get("/health")
    assert response.status_code == 200
    print(f"✓ Health check: {response.json()}")
    
    # Test project creation through orchestration
    print("\n2. Testing project creation...")
    project_data = {
        "name": "Orchestrated Test Project",
        "description": "A test project created through orchestration services",
        "status": "planning",
        "priority": "high",
        "tags": ["test", "orchestration", "api"],
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
            
            # Test projects list
            print("\n4. Testing projects list...")
            response = client.get("/api/projects")
            if response.status_code == 200:
                projects_list = response.json()
                print(f"✓ Projects list retrieved: {projects_list['total']} projects")
                
                # Test project filtering
                print("\n5. Testing project filtering...")
                response = client.get("/api/projects?status=planning&priority=high")
                if response.status_code == 200:
                    filtered_projects = response.json()
                    print(f"✓ Filtered projects: {filtered_projects['total']} projects with status=planning and priority=high")
                    
                    print("\n✅ All API orchestration tests passed!")
                    return True
                else:
                    print(f"❌ Project filtering failed: {response.status_code} - {response.text}")
            else:
                print(f"❌ Projects list failed: {response.status_code} - {response.text}")
        else:
            print(f"❌ Project retrieval failed: {response.status_code} - {response.text}")
    else:
        print(f"❌ Project creation failed: {response.status_code} - {response.text}")
    
    return False

if __name__ == "__main__":
    success = test_api_with_orchestration()
    sys.exit(0 if success else 1)