"""
Comprehensive tests for task listing pagination and filtering.

Tests FIX-001 acceptance criteria:
- Fix task listing pagination: ensure newly created tasks appear in listings
- Fix task listing filtering: support project_id, status, assignee, and other filters
- Improve default ordering: tasks should be ordered by created_at DESC
- Add proper pagination metadata: total count, page info, has_next/has_prev
- Add search functionality: enable searching tasks by title and description
- Support multiple filter combinations and enhanced filtering options
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.api.main import app
from .test_database_isolation import TestDatabaseIsolation


class TestTaskPagination(TestDatabaseIsolation):
    """Test task listing pagination and filtering functionality."""
    
    def test_default_pagination_shows_newest_first(self, isolated_client):
        """Test that default pagination shows newest tasks first."""
        # Create a project for testing
        project_data = {
            "name": "Pagination Test Project",
            "description": "Testing pagination functionality",
            "status": "planning", 
            "priority": "medium",
            "created_by": "pagination_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create multiple tasks with known order
        task_ids = []
        for i in range(5):
            task_data = {
                "project_id": project_id,
                "title": f"Task {i:02d}",
                "description": f"Task created at position {i}",
                "status": "todo",
                "priority": "medium",
                "created_by": "pagination_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
            task_ids.append(response.json()["id"])
        
        # Test default listing (should show newest first)
        list_response = isolated_client.get("/api/tasks?limit=5")
        assert list_response.status_code == 200
        
        tasks_data = list_response.json()
        tasks = tasks_data["tasks"]
        
        # Should have all our tasks
        assert len(tasks) == 5
        assert tasks_data["total"] == 5
        
        # Should be ordered by created_at DESC (newest first)
        assert tasks[0]["title"] == "Task 04"  # Last created
        assert tasks[4]["title"] == "Task 00"  # First created
        
        # Check pagination metadata
        assert tasks_data["page"] == 1
        assert tasks_data["per_page"] == 5
        assert tasks_data["has_next"] == False
        assert tasks_data["has_prev"] == False
    
    def test_pagination_with_multiple_pages(self, isolated_client):
        """Test pagination across multiple pages."""
        # Create a project
        project_data = {
            "name": "Multi-page Test Project",
            "description": "Testing multi-page pagination",
            "status": "planning",
            "priority": "medium", 
            "created_by": "multipage_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create 10 tasks
        for i in range(10):
            task_data = {
                "project_id": project_id,
                "title": f"Page Test Task {i:02d}",
                "description": f"Task for pagination testing {i}",
                "status": "todo",
                "priority": "medium",
                "created_by": "multipage_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test page 1 (first 3 tasks)
        page1_response = isolated_client.get("/api/tasks?limit=3&skip=0")
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        
        assert len(page1_data["tasks"]) == 3
        assert page1_data["total"] == 10
        assert page1_data["page"] == 1
        assert page1_data["has_next"] == True
        assert page1_data["has_prev"] == False
        
        # Test page 2 (next 3 tasks)
        page2_response = isolated_client.get("/api/tasks?limit=3&skip=3")
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        
        assert len(page2_data["tasks"]) == 3
        assert page2_data["total"] == 10
        assert page2_data["page"] == 2
        assert page2_data["has_next"] == True
        assert page2_data["has_prev"] == True
        
        # Test last page (remaining tasks)
        page4_response = isolated_client.get("/api/tasks?limit=3&skip=9")
        assert page4_response.status_code == 200
        page4_data = page4_response.json()
        
        assert len(page4_data["tasks"]) == 1
        assert page4_data["total"] == 10
        assert page4_data["page"] == 4
        assert page4_data["has_next"] == False
        assert page4_data["has_prev"] == True
    
    def test_task_filtering_by_project(self, isolated_client):
        """Test filtering tasks by project ID."""
        # Create two projects
        project1_data = {
            "name": "Filter Project 1",
            "description": "First project for filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "filter_user"
        }
        
        project2_data = {
            "name": "Filter Project 2", 
            "description": "Second project for filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "filter_user"
        }
        
        proj1_response = isolated_client.post("/api/projects", json=project1_data)
        proj2_response = isolated_client.post("/api/projects", json=project2_data)
        assert proj1_response.status_code == 201
        assert proj2_response.status_code == 201
        
        project1_id = proj1_response.json()["id"]
        project2_id = proj2_response.json()["id"]
        
        # Create tasks in both projects
        for project_id, project_name in [(project1_id, "Project1"), (project2_id, "Project2")]:
            for i in range(3):
                task_data = {
                    "project_id": project_id,
                    "title": f"{project_name} Task {i}",
                    "description": f"Task {i} in {project_name}",
                    "status": "todo",
                    "priority": "medium",
                    "created_by": "filter_user"
                }
                
                response = isolated_client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
        
        # Test filtering by project 1
        proj1_response = isolated_client.get(f"/api/tasks?project_id={project1_id}")
        assert proj1_response.status_code == 200
        proj1_tasks = proj1_response.json()
        
        assert proj1_tasks["total"] == 3
        for task in proj1_tasks["tasks"]:
            assert task["project_id"] == project1_id
            assert "Project1" in task["title"]
        
        # Test filtering by project 2
        proj2_response = isolated_client.get(f"/api/tasks?project_id={project2_id}")
        assert proj2_response.status_code == 200
        proj2_tasks = proj2_response.json()
        
        assert proj2_tasks["total"] == 3
        for task in proj2_tasks["tasks"]:
            assert task["project_id"] == project2_id
            assert "Project2" in task["title"]
    
    def test_task_filtering_by_status(self, isolated_client):
        """Test filtering tasks by status."""
        # Create a project
        project_data = {
            "name": "Status Filter Project",
            "description": "Testing status filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "status_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with different statuses
        statuses = ["todo", "in_progress", "completed"]
        for i, task_status in enumerate(statuses):
            for j in range(2):  # 2 tasks per status
                task_data = {
                    "project_id": project_id,
                    "title": f"{task_status.title()} Task {j}",
                    "description": f"Task with status {task_status}",
                    "status": task_status,
                    "priority": "medium",
                    "created_by": "status_user"
                }
                
                response = isolated_client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
        
        # Test filtering by each status
        for test_status in statuses:
            status_response = isolated_client.get(f"/api/tasks?task_status={test_status}")
            assert status_response.status_code == 200
            status_tasks = status_response.json()
            
            assert status_tasks["total"] == 2
            for task in status_tasks["tasks"]:
                assert task["status"] == test_status
    
    def test_task_filtering_by_priority(self, isolated_client):
        """Test filtering tasks by priority."""
        # Create a project
        project_data = {
            "name": "Priority Filter Project",
            "description": "Testing priority filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "priority_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with different priorities
        priorities = ["low", "medium", "high"]
        for priority in priorities:
            task_data = {
                "project_id": project_id,
                "title": f"{priority.title()} Priority Task",
                "description": f"Task with {priority} priority",
                "status": "todo",
                "priority": priority,
                "created_by": "priority_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test filtering by high priority
        high_response = isolated_client.get("/api/tasks?priority=high")
        assert high_response.status_code == 200
        high_tasks = high_response.json()
        
        assert high_tasks["total"] == 1
        assert high_tasks["tasks"][0]["priority"] == "high"
    
    def test_task_filtering_by_assignee(self, isolated_client):
        """Test filtering tasks by assignee."""
        # Create a project
        project_data = {
            "name": "Assignee Filter Project",
            "description": "Testing assignee filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "assignee_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with different assignees
        assignees = ["alice", "bob", "charlie"]
        for assignee in assignees:
            task_data = {
                "project_id": project_id,
                "title": f"Task assigned to {assignee}",
                "description": f"Task for {assignee}",
                "status": "todo",
                "priority": "medium",
                "assignee": assignee,
                "created_by": "assignee_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test filtering by assignee
        alice_response = isolated_client.get("/api/tasks?assignee=alice")
        assert alice_response.status_code == 200
        alice_tasks = alice_response.json()
        
        assert alice_tasks["total"] == 1
        assert alice_tasks["tasks"][0]["assignee"] == "alice"
    
    def test_task_search_functionality(self, isolated_client):
        """Test searching tasks by title and description."""
        # Create a project
        project_data = {
            "name": "Search Test Project",
            "description": "Testing search functionality",
            "status": "planning",
            "priority": "medium",
            "created_by": "search_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with searchable content
        tasks_data = [
            ("Database migration task", "Migrate database schema to new version"),
            ("Frontend update", "Update React components for better UX"),
            ("Database backup", "Setup automated database backups"),
            ("API documentation", "Write comprehensive API docs"),
        ]
        
        for title, description in tasks_data:
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": description,
                "status": "todo",
                "priority": "medium",
                "created_by": "search_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test searching by title keyword
        frontend_response = isolated_client.get("/api/tasks?search=frontend")
        assert frontend_response.status_code == 200
        frontend_tasks = frontend_response.json()
        
        assert frontend_tasks["total"] == 1
        assert "Frontend" in frontend_tasks["tasks"][0]["title"]
        
        # Test searching by description keyword
        database_response = isolated_client.get("/api/tasks?search=database")
        assert database_response.status_code == 200
        database_tasks = database_response.json()
        
        assert database_tasks["total"] == 2  # Both database tasks should match
        for task in database_tasks["tasks"]:
            assert "database" in task["title"].lower() or "database" in task["description"].lower()
        
        # Test case-insensitive search
        api_response = isolated_client.get("/api/tasks?search=API")
        assert api_response.status_code == 200
        api_tasks = api_response.json()
        
        assert api_tasks["total"] == 1
        assert "API" in api_tasks["tasks"][0]["description"]
    
    def test_task_sorting_functionality(self, isolated_client):
        """Test sorting tasks by different fields."""
        # Create a project
        project_data = {
            "name": "Sort Test Project",
            "description": "Testing sorting functionality",
            "status": "planning",
            "priority": "medium",
            "created_by": "sort_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with different attributes for sorting
        tasks_data = [
            ("Alpha Task", "high"),
            ("Beta Task", "low"),
            ("Charlie Task", "medium"),
        ]
        
        for title, priority in tasks_data:
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": f"Task for sorting test",
                "status": "todo",
                "priority": priority,
                "created_by": "sort_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test sorting by title ascending
        title_asc_response = isolated_client.get("/api/tasks?sort_by=title&sort_order=asc")
        assert title_asc_response.status_code == 200
        title_asc_tasks = title_asc_response.json()
        
        titles = [task["title"] for task in title_asc_tasks["tasks"]]
        assert titles == ["Alpha Task", "Beta Task", "Charlie Task"]
        
        # Test sorting by title descending
        title_desc_response = isolated_client.get("/api/tasks?sort_by=title&sort_order=desc")
        assert title_desc_response.status_code == 200
        title_desc_tasks = title_desc_response.json()
        
        titles = [task["title"] for task in title_desc_tasks["tasks"]]
        assert titles == ["Charlie Task", "Beta Task", "Alpha Task"]
    
    def test_combined_filtering_and_search(self, isolated_client):
        """Test combining multiple filters and search."""
        # Create a project
        project_data = {
            "name": "Combined Filter Project",
            "description": "Testing combined filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "combined_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create various tasks
        tasks_data = [
            ("Database migration", "todo", "high", "alice"),
            ("Database backup", "todo", "medium", "bob"),
            ("Frontend update", "in_progress", "high", "alice"),
            ("API migration", "todo", "high", "alice"),
        ]
        
        for title, status, priority, assignee in tasks_data:
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": f"Task: {title}",
                "status": status,
                "priority": priority,
                "assignee": assignee,
                "created_by": "combined_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test combined filters: status=todo AND priority=high AND assignee=alice
        combined_response = isolated_client.get(
            f"/api/tasks?task_status=todo&priority=high&assignee=alice"
        )
        assert combined_response.status_code == 200
        combined_tasks = combined_response.json()
        
        # Should match "Database migration" and "API migration"
        assert combined_tasks["total"] == 2
        for task in combined_tasks["tasks"]:
            assert task["status"] == "todo"
            assert task["priority"] == "high"
            assert task["assignee"] == "alice"
        
        # Test combining search with filters: search=migration AND priority=high
        search_filter_response = isolated_client.get(
            "/api/tasks?search=migration&priority=high"
        )
        assert search_filter_response.status_code == 200
        search_filter_tasks = search_filter_response.json()
        
        # Should match "Database migration" and "API migration"
        assert search_filter_tasks["total"] == 2
        for task in search_filter_tasks["tasks"]:
            assert "migration" in task["title"].lower()
            assert task["priority"] == "high"
    
    def test_tag_filtering(self, isolated_client):
        """Test filtering tasks by tags."""
        # Create a project
        project_data = {
            "name": "Tag Filter Project",
            "description": "Testing tag filtering",
            "status": "planning",
            "priority": "medium",
            "created_by": "tag_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Create tasks with different tags
        tasks_data = [
            ("Backend task", ["backend", "python"]),
            ("Frontend task", ["frontend", "react"]),
            ("Database task", ["backend", "database"]),
            ("API task", ["backend", "api"]),
        ]
        
        for title, tags in tasks_data:
            task_data = {
                "project_id": project_id,
                "title": title,
                "description": f"Task: {title}",
                "status": "todo",
                "priority": "medium",
                "tags": tags,
                "created_by": "tag_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test filtering by single tag
        backend_response = isolated_client.get("/api/tasks?tags=backend")
        assert backend_response.status_code == 200
        backend_tasks = backend_response.json()
        
        assert backend_tasks["total"] == 3  # Backend, Database, API tasks
        for task in backend_tasks["tasks"]:
            assert "backend" in task["tags"]
        
        # Test filtering by multiple tags
        python_response = isolated_client.get("/api/tasks?tags=python")
        assert python_response.status_code == 200
        python_tasks = python_response.json()
        
        assert python_tasks["total"] == 1  # Only Backend task
        assert "python" in python_tasks["tasks"][0]["tags"]
    
    def test_parameter_validation(self, isolated_client):
        """Test parameter validation for sorting and filtering."""
        # Test invalid sort_by field
        invalid_sort_response = isolated_client.get("/api/tasks?sort_by=invalid_field")
        assert invalid_sort_response.status_code == 422
        
        # Test invalid sort_order
        invalid_order_response = isolated_client.get("/api/tasks?sort_order=invalid")
        assert invalid_order_response.status_code == 422
        
        # Test invalid date format
        invalid_date_response = isolated_client.get("/api/tasks?created_after=invalid-date")
        assert invalid_date_response.status_code == 422
    
    def test_empty_results_handling(self, isolated_client):
        """Test handling of empty results."""
        # Test filtering with no matches
        no_match_response = isolated_client.get("/api/tasks?search=nonexistent_keyword_xyz123")
        assert no_match_response.status_code == 200
        no_match_tasks = no_match_response.json()
        
        assert no_match_tasks["total"] == 0
        assert no_match_tasks["tasks"] == []
        assert no_match_tasks["has_next"] == False
        assert no_match_tasks["has_prev"] == False
    
    def test_newly_created_task_appears_first(self, isolated_client):
        """Test FIX-001 critical requirement: newly created tasks appear in listings."""
        # Create a project
        project_data = {
            "name": "New Task Visibility Project",
            "description": "Testing that new tasks appear in listings",
            "status": "planning",
            "priority": "medium",
            "created_by": "visibility_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Get initial task count
        initial_response = isolated_client.get("/api/tasks?limit=1")
        assert initial_response.status_code == 200
        initial_total = initial_response.json()["total"]
        
        # Create a new task
        new_task_data = {
            "project_id": project_id,
            "title": "Newly Created Task - Should Appear First",
            "description": "This task should appear at the top of the list",
            "status": "todo",
            "priority": "high",
            "created_by": "visibility_user"
        }
        
        create_response = isolated_client.post("/api/tasks", json=new_task_data)
        assert create_response.status_code == 201
        created_task = create_response.json()
        
        # Verify the new task appears in the listing
        list_response = isolated_client.get("/api/tasks?limit=5")
        assert list_response.status_code == 200
        tasks_data = list_response.json()
        
        # Task count should have increased
        assert tasks_data["total"] == initial_total + 1
        
        # New task should be first (newest first ordering)
        assert len(tasks_data["tasks"]) > 0
        first_task = tasks_data["tasks"][0]
        assert first_task["id"] == created_task["id"]
        assert first_task["title"] == "Newly Created Task - Should Appear First"