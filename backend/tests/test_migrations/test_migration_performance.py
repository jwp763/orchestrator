"""
Performance tests for the migration system.

This module tests migration performance to ensure migrations complete
within acceptable time limits.
"""

import time
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from tests.test_api.test_database_isolation import TestDatabaseIsolation


class TestMigrationPerformance(TestDatabaseIsolation):
    """Test migration performance requirements."""
    
    def test_migration_upgrade_performance(self):
        """Test that migration upgrade completes within time limit."""
        backend_dir = Path(__file__).parent.parent.parent
        
        start_time = time.time()
        
        # Run upgrade
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.returncode == 0, f"Migration failed: {result.stderr}"
        assert duration < 10.0, f"Migration took {duration:.2f} seconds, should be < 10 seconds"
    
    def test_migration_status_check_performance(self):
        """Test that migration status check is fast."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        start_time = time.time()
        
        # Check migration status
        is_up_to_date, current_revision = manager.check_migration_status()
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 5.0, f"Status check took {duration:.2f} seconds, should be < 5 seconds"
        assert isinstance(is_up_to_date, bool)
    
    def test_migration_script_command_performance(self):
        """Test that migration script commands are fast."""
        backend_dir = Path(__file__).parent.parent.parent
        
        commands = ['current', 'history', 'heads']
        
        for command in commands:
            start_time = time.time()
            
            result = subprocess.run(
                ['python', 'scripts/migrate.py', command],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            assert result.returncode == 0, f"Command {command} failed: {result.stderr}"
            assert duration < 3.0, f"Command {command} took {duration:.2f} seconds, should be < 3 seconds"
    
    def test_migration_manager_auto_migrate_performance(self):
        """Test that auto-migration is fast."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        start_time = time.time()
        
        # Run auto-migration
        success = manager.auto_migrate_on_startup()
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert success == True
        assert duration < 10.0, f"Auto-migration took {duration:.2f} seconds, should be < 10 seconds"
    
    def test_migration_init_performance(self):
        """Test that database initialization is reasonably fast."""
        backend_dir = Path(__file__).parent.parent.parent
        
        start_time = time.time()
        
        # Run init command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'init'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.returncode == 0, f"Init failed: {result.stderr}"
        assert duration < 15.0, f"Init took {duration:.2f} seconds, should be < 15 seconds"
    
    def test_migration_validation_performance(self):
        """Test that migration validation is fast."""
        backend_dir = Path(__file__).parent.parent.parent
        
        start_time = time.time()
        
        # Run validation
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'validate'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert duration < 10.0, f"Validation took {duration:.2f} seconds, should be < 10 seconds"


class TestMigrationScalability:
    """Test migration system scalability."""
    
    def test_migration_with_large_data_simulation(self, isolated_client):
        """Test migration performance with simulated large data."""
        # Create a moderate number of projects and tasks to simulate load
        num_projects = 50
        num_tasks_per_project = 10
        
        project_ids = []
        
        # Create projects
        for i in range(num_projects):
            project_data = {
                "name": f"Test Project {i}",
                "description": f"Test project {i} for performance testing",
                "priority": "medium"
            }
            response = isolated_client.post("/projects", json=project_data)
            assert response.status_code == 201
            project_ids.append(response.json()["id"])
        
        # Create tasks for each project
        for project_id in project_ids:
            for j in range(num_tasks_per_project):
                task_data = {
                    "title": f"Task {j} for project {project_id}",
                    "description": f"Test task {j}",
                    "project_id": project_id,
                    "priority": "medium"
                }
                response = isolated_client.post("/tasks", json=task_data)
                assert response.status_code == 201
        
        # Now run migration with this data
        backend_dir = Path(__file__).parent.parent.parent
        
        start_time = time.time()
        
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert result.returncode == 0, f"Migration with data failed: {result.stderr}"
        assert duration < 20.0, f"Migration with data took {duration:.2f} seconds, should be < 20 seconds"
        
        # Verify data integrity after migration
        response = isolated_client.get("/projects")
        assert response.status_code == 200
        projects = response.json()
        assert len(projects) == num_projects
    
    def test_migration_memory_usage(self):
        """Test that migration doesn't consume excessive memory."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Run migration
        backend_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        assert result.returncode == 0
        assert memory_increase < 100, f"Migration increased memory by {memory_increase:.2f} MB, should be < 100 MB"
    
    def test_concurrent_migration_safety(self):
        """Test that multiple migration processes don't interfere."""
        import threading
        import subprocess
        
        backend_dir = Path(__file__).parent.parent.parent
        results = []
        
        def run_migration():
            result = subprocess.run(
                ['python', 'scripts/migrate.py', 'current'],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            results.append(result.returncode)
        
        # Start multiple threads
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_migration)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All should succeed
        assert all(result == 0 for result in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])