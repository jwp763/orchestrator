"""
Performance tests for API response times under load.

Tests API-001 acceptance criteria:
- Performance tests for API response times under load with multiple concurrent requests
"""

import pytest
import time
import asyncio
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from fastapi.testclient import TestClient

from src.api.main import app
from .test_database_isolation import TestDatabaseIsolation


class TestAPIPerformance(TestDatabaseIsolation):
    """Performance tests for API response times under load."""
    
    def test_project_crud_performance(self, isolated_client):
        """Test project CRUD operations performance."""
        # Create multiple projects and measure response times
        create_times = []
        read_times = []
        update_times = []
        delete_times = []
        
        project_ids = []
        
        # Test project creation performance
        for i in range(20):
            project_data = {
                "name": f"Performance Test Project {i}",
                "description": f"Testing performance {i}",
                "status": "planning",
                "priority": "medium",
                "created_by": "perf_user"
            }
            
            start_time = time.time()
            response = isolated_client.post("/api/projects", json=project_data)
            end_time = time.time()
            
            assert response.status_code == 201
            create_times.append(end_time - start_time)
            project_ids.append(response.json()["id"])
        
        # Test project read performance
        for project_id in project_ids:
            start_time = time.time()
            response = isolated_client.get(f"/api/projects/{project_id}")
            end_time = time.time()
            
            assert response.status_code == 200
            read_times.append(end_time - start_time)
        
        # Test project update performance
        for project_id in project_ids:
            update_data = {
                "description": "Updated description for performance test",
                "status": "active"
            }
            
            start_time = time.time()
            response = isolated_client.put(f"/api/projects/{project_id}", json=update_data)
            end_time = time.time()
            
            assert response.status_code == 200
            update_times.append(end_time - start_time)
        
        # Test project delete performance
        for project_id in project_ids:
            start_time = time.time()
            response = isolated_client.delete(f"/api/projects/{project_id}")
            end_time = time.time()
            
            assert response.status_code == 204
            delete_times.append(end_time - start_time)
        
        # Verify performance metrics
        avg_create_time = statistics.mean(create_times)
        avg_read_time = statistics.mean(read_times)
        avg_update_time = statistics.mean(update_times)
        avg_delete_time = statistics.mean(delete_times)
        
        # Performance assertions (adjust thresholds as needed)
        assert avg_create_time < 0.1, f"Average create time too slow: {avg_create_time:.3f}s"
        assert avg_read_time < 0.05, f"Average read time too slow: {avg_read_time:.3f}s"
        assert avg_update_time < 0.1, f"Average update time too slow: {avg_update_time:.3f}s"
        assert avg_delete_time < 0.1, f"Average delete time too slow: {avg_delete_time:.3f}s"
        
        print(f"Performance metrics:")
        print(f"  Create: {avg_create_time:.3f}s avg, {max(create_times):.3f}s max")
        print(f"  Read: {avg_read_time:.3f}s avg, {max(read_times):.3f}s max")
        print(f"  Update: {avg_update_time:.3f}s avg, {max(update_times):.3f}s max")
        print(f"  Delete: {avg_delete_time:.3f}s avg, {max(delete_times):.3f}s max")
    
    def test_task_crud_performance(self, isolated_client):
        """Test task CRUD operations performance."""
        # First create a project for the tasks
        project_data = {
            "name": "Performance Test Project",
            "description": "Project for task performance testing",
            "status": "planning",
            "priority": "high",
            "created_by": "perf_user"
        }
        
        project_response = isolated_client.post("/api/projects", json=project_data)
        assert project_response.status_code == 201
        project_id = project_response.json()["id"]
        
        # Test task operations performance
        create_times = []
        read_times = []
        update_times = []
        delete_times = []
        
        task_ids = []
        
        # Test task creation performance
        for i in range(50):
            task_data = {
                "project_id": project_id,
                "title": f"Performance Test Task {i}",
                "description": f"Testing task performance {i}",
                "status": "todo",
                "priority": "medium",
                "estimated_minutes": 60,
                "created_by": "perf_user"
            }
            
            start_time = time.time()
            response = isolated_client.post("/api/tasks", json=task_data)
            end_time = time.time()
            
            assert response.status_code == 201
            create_times.append(end_time - start_time)
            task_ids.append(response.json()["id"])
        
        # Test task read performance
        for task_id in task_ids:
            start_time = time.time()
            response = isolated_client.get(f"/api/tasks/{task_id}")
            end_time = time.time()
            
            assert response.status_code == 200
            read_times.append(end_time - start_time)
        
        # Test task update performance
        for task_id in task_ids:
            update_data = {
                "description": "Updated description for performance test",
                "status": "in_progress",
                "actual_minutes": 30
            }
            
            start_time = time.time()
            response = isolated_client.put(f"/api/tasks/{task_id}", json=update_data)
            end_time = time.time()
            
            assert response.status_code == 200
            update_times.append(end_time - start_time)
        
        # Test task delete performance
        for task_id in task_ids:
            start_time = time.time()
            response = isolated_client.delete(f"/api/tasks/{task_id}")
            end_time = time.time()
            
            assert response.status_code == 204
            delete_times.append(end_time - start_time)
        
        # Verify performance metrics
        avg_create_time = statistics.mean(create_times)
        avg_read_time = statistics.mean(read_times)
        avg_update_time = statistics.mean(update_times)
        avg_delete_time = statistics.mean(delete_times)
        
        # Performance assertions (adjust thresholds as needed)
        assert avg_create_time < 0.1, f"Average create time too slow: {avg_create_time:.3f}s"
        assert avg_read_time < 0.05, f"Average read time too slow: {avg_read_time:.3f}s"
        assert avg_update_time < 0.1, f"Average update time too slow: {avg_update_time:.3f}s"
        assert avg_delete_time < 0.1, f"Average delete time too slow: {avg_delete_time:.3f}s"
        
        print(f"Task performance metrics:")
        print(f"  Create: {avg_create_time:.3f}s avg, {max(create_times):.3f}s max")
        print(f"  Read: {avg_read_time:.3f}s avg, {max(read_times):.3f}s max")
        print(f"  Update: {avg_update_time:.3f}s avg, {max(update_times):.3f}s max")
        print(f"  Delete: {avg_delete_time:.3f}s avg, {max(delete_times):.3f}s max")
    
    def test_concurrent_requests_performance(self, isolated_client):
        """Test API performance under concurrent load."""
        def create_project(client, project_num):
            """Create a single project and return response time."""
            project_data = {
                "name": f"Concurrent Test Project {project_num}",
                "description": f"Testing concurrent performance {project_num}",
                "status": "planning",
                "priority": "medium",
                "created_by": f"concurrent_user_{project_num}"
            }
            
            start_time = time.time()
            response = client.post("/api/projects", json=project_data)
            end_time = time.time()
            
            return {
                "status_code": response.status_code,
                "response_time": end_time - start_time,
                "project_id": response.json().get("id") if response.status_code == 201 else None
            }
        
        # Test concurrent project creation
        concurrent_requests = 10
        response_times = []
        successful_requests = 0
        
        with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            # Submit all requests concurrently
            futures = [
                executor.submit(create_project, isolated_client, i)
                for i in range(concurrent_requests)
            ]
            
            # Collect results
            for future in as_completed(futures):
                result = future.result()
                response_times.append(result["response_time"])
                if result["status_code"] == 201:
                    successful_requests += 1
        
        # Verify all requests succeeded
        assert successful_requests == concurrent_requests, f"Only {successful_requests}/{concurrent_requests} requests succeeded"
        
        # Verify performance under load
        avg_response_time = statistics.mean(response_times)
        max_response_time = max(response_times)
        
        assert avg_response_time < 0.2, f"Average response time too slow under load: {avg_response_time:.3f}s"
        assert max_response_time < 0.5, f"Maximum response time too slow under load: {max_response_time:.3f}s"
        
        print(f"Concurrent performance metrics:")
        print(f"  Requests: {concurrent_requests}")
        print(f"  Success rate: {successful_requests}/{concurrent_requests}")
        print(f"  Average response time: {avg_response_time:.3f}s")
        print(f"  Maximum response time: {max_response_time:.3f}s")
    
    def test_list_endpoints_performance(self, isolated_client):
        """Test performance of list endpoints with various data sizes."""
        # Create test projects with tasks
        project_ids = []
        
        for i in range(10):
            project_data = {
                "name": f"List Performance Project {i}",
                "description": f"Testing list performance {i}",
                "status": "planning",
                "priority": "medium",
                "created_by": "list_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            assert response.status_code == 201
            project_ids.append(response.json()["id"])
        
        # Create tasks for each project
        task_ids = []
        for project_id in project_ids:
            for j in range(5):
                task_data = {
                    "project_id": project_id,
                    "title": f"List Performance Task {j}",
                    "description": f"Testing list performance {j}",
                    "status": "todo",
                    "priority": "medium",
                    "created_by": "list_user"
                }
                
                response = isolated_client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
                task_ids.append(response.json()["id"])
        
        # Test project listing performance
        start_time = time.time()
        response = isolated_client.get("/api/projects")
        end_time = time.time()
        
        assert response.status_code == 200
        project_list_time = end_time - start_time
        
        projects = response.json()
        assert len(projects["projects"]) == 10
        
        # Test task listing performance
        start_time = time.time()
        response = isolated_client.get("/api/tasks?limit=100")  # Increase limit to get all tasks
        end_time = time.time()
        
        assert response.status_code == 200
        task_list_time = end_time - start_time
        
        tasks = response.json()
        assert len(tasks["tasks"]) == 50
        
        # Test filtered listing performance
        start_time = time.time()
        response = isolated_client.get(f"/api/tasks?project_id={project_ids[0]}")
        end_time = time.time()
        
        assert response.status_code == 200
        filtered_list_time = end_time - start_time
        
        filtered_tasks = response.json()
        assert len(filtered_tasks["tasks"]) == 5
        
        # Performance assertions
        assert project_list_time < 0.1, f"Project listing too slow: {project_list_time:.3f}s"
        assert task_list_time < 0.1, f"Task listing too slow: {task_list_time:.3f}s"
        assert filtered_list_time < 0.1, f"Filtered listing too slow: {filtered_list_time:.3f}s"
        
        print(f"List performance metrics:")
        print(f"  Project listing: {project_list_time:.3f}s")
        print(f"  Task listing: {task_list_time:.3f}s")
        print(f"  Filtered listing: {filtered_list_time:.3f}s")
    
    def test_pagination_performance(self, isolated_client):
        """Test performance of pagination with various page sizes."""
        # Create test data
        project_data = {
            "name": "Pagination Performance Project",
            "description": "Testing pagination performance",
            "status": "planning",
            "priority": "medium",
            "created_by": "pagination_user"
        }
        
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create many tasks
        task_count = 100
        for i in range(task_count):
            task_data = {
                "project_id": project_id,
                "title": f"Pagination Test Task {i}",
                "description": f"Testing pagination performance {i}",
                "status": "todo",
                "priority": "medium",
                "created_by": "pagination_user"
            }
            
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code == 201
        
        # Test different page sizes
        page_sizes = [10, 20, 50]
        for page_size in page_sizes:
            start_time = time.time()
            response = isolated_client.get(f"/api/tasks?project_id={project_id}&limit={page_size}")
            end_time = time.time()
            
            assert response.status_code == 200
            page_time = end_time - start_time
            
            tasks = response.json()
            assert len(tasks["tasks"]) == page_size
            
            # Performance assertion
            assert page_time < 0.1, f"Pagination too slow for page size {page_size}: {page_time:.3f}s"
            
            print(f"Pagination performance (page size {page_size}): {page_time:.3f}s")
    
    def test_deep_hierarchy_performance(self, isolated_client):
        """Test performance with deep task hierarchies."""
        # Create test project
        project_data = {
            "name": "Hierarchy Performance Project",
            "description": "Testing hierarchy performance",
            "status": "planning",
            "priority": "medium",
            "created_by": "hierarchy_user"
        }
        
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create deep hierarchy (5 levels)
        parent_id = None
        task_ids = []
        
        for level in range(5):
            for i in range(3):  # 3 tasks per level
                task_data = {
                    "project_id": project_id,
                    "title": f"Level {level} Task {i}",
                    "description": f"Testing hierarchy performance level {level}",
                    "status": "todo",
                    "priority": "medium",
                    "created_by": "hierarchy_user"
                }
                
                if parent_id:
                    task_data["parent_id"] = parent_id
                
                response = isolated_client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
                
                task_id = response.json()["id"]
                task_ids.append(task_id)
                
                # Use first task of each level as parent for next level
                if i == 0:
                    parent_id = task_id
        
        # Test performance of retrieving tasks with hierarchy
        start_time = time.time()
        response = isolated_client.get(f"/api/tasks/{task_ids[0]}")  # Get root task
        end_time = time.time()
        
        assert response.status_code == 200
        hierarchy_time = end_time - start_time
        
        task = response.json()
        assert len(task["subtasks"]) > 0
        
        # Performance assertion
        assert hierarchy_time < 0.1, f"Hierarchy retrieval too slow: {hierarchy_time:.3f}s"
        
        print(f"Hierarchy performance: {hierarchy_time:.3f}s")
    
    def test_memory_usage_performance(self, isolated_client):
        """Test memory usage doesn't grow excessively during operations."""
        try:
            import psutil
        except ImportError:
            pytest.skip("psutil not available")
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Perform many operations
        for i in range(100):
            # Create project
            project_data = {
                "name": f"Memory Test Project {i}",
                "description": f"Testing memory usage {i}",
                "status": "planning",
                "priority": "medium",
                "created_by": "memory_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            assert response.status_code == 201
            project_id = response.json()["id"]
            
            # Create some tasks
            for j in range(5):
                task_data = {
                    "project_id": project_id,
                    "title": f"Memory Test Task {j}",
                    "description": f"Testing memory usage {j}",
                    "status": "todo",
                    "priority": "medium",
                    "created_by": "memory_user"
                }
                
                response = isolated_client.post("/api/tasks", json=task_data)
                assert response.status_code == 201
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100, f"Memory usage increased too much: {memory_increase:.2f}MB"
        
        print(f"Memory usage: {initial_memory:.2f}MB -> {final_memory:.2f}MB (+{memory_increase:.2f}MB)")