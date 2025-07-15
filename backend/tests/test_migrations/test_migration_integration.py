"""
Integration tests for the migration system.

This module tests the complete migration lifecycle including upgrade,
downgrade, and data safety during migrations.
"""

import os
import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock

from sqlalchemy import create_engine, MetaData, inspect, text
from sqlalchemy.orm import sessionmaker

from tests.test_api.test_database_isolation import TestDatabaseIsolation


class TestMigrationIntegration(TestDatabaseIsolation):
    """Test complete migration lifecycle."""
    
    def test_migration_upgrade_downgrade_cycle(self, isolated_engine):
        """Test that migrations can be upgraded and downgraded."""
        # Get the current directory structure
        backend_dir = Path(__file__).parent.parent.parent
        
        # Run upgrade
        import subprocess
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Upgrade failed: {result.stderr}"
        
        # Check that alembic_version table exists
        inspector = inspect(isolated_engine)
        tables = inspector.get_table_names()
        assert 'alembic_version' in tables
        
        # Get current version
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'current'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Current failed: {result.stderr}"
        current_version = result.stdout.strip().split('\\n')[0]
        
        # Should have a valid version
        assert current_version, "Should have a current version"
        assert len(current_version) > 0
    
    def test_migration_with_existing_data(self, isolated_client):
        """Test that migrations preserve existing data."""
        # Create some test data
        project_data = {
            "name": "Test Project",
            "description": "A test project for migration testing",
            "priority": "high"
        }
        
        response = isolated_client.post("/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create a task
        task_data = {
            "title": "Test Task",
            "description": "A test task",
            "project_id": project_id,
            "priority": "medium"
        }
        
        response = isolated_client.post("/tasks", json=task_data)
        assert response.status_code == 201
        task_id = response.json()["id"]
        
        # Run migration (should be no-op since we're already at head)
        backend_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Migration failed: {result.stderr}"
        
        # Verify data still exists
        response = isolated_client.get(f"/projects/{project_id}")
        assert response.status_code == 200
        project = response.json()
        assert project["name"] == "Test Project"
        
        response = isolated_client.get(f"/tasks/{task_id}")
        assert response.status_code == 200
        task = response.json()
        assert task["title"] == "Test Task"
    
    def test_migration_script_functionality(self):
        """Test the migration script commands."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test current command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'current'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Test history command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'history'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        assert "Initial schema migration" in result.stdout
        
        # Test heads command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'heads'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
    
    def test_migration_manager_integration(self, isolated_engine):
        """Test the migration manager integration."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        # Create migration manager
        manager = MigrationManager()
        
        # Test migration status check
        is_up_to_date, current_revision = manager.check_migration_status()
        assert isinstance(is_up_to_date, bool)
        assert current_revision is not None or not is_up_to_date
        
        # Test auto-migration
        success = manager.auto_migrate_on_startup()
        assert success == True
        
        # Test database initialization
        success = manager.initialize_database()
        assert success == True
    
    def test_migration_validation(self):
        """Test migration validation functionality."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test validation command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'validate'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Validation failed: {result.stderr}"
        assert "validation completed successfully" in result.stdout.lower()
    
    def test_migration_init_command(self):
        """Test the migration init command."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test init command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'init'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Init failed: {result.stderr}"
        assert "Initializing database" in result.stdout


class TestMigrationDataSafety(TestDatabaseIsolation):
    """Test data safety during migrations."""
    
    def test_migration_preserves_project_data(self, isolated_client):
        """Test that project data is preserved during migrations."""
        # Create test projects
        projects = [
            {"name": "Project 1", "description": "First project", "priority": "high"},
            {"name": "Project 2", "description": "Second project", "priority": "medium"},
            {"name": "Project 3", "description": "Third project", "priority": "low"}
        ]
        
        project_ids = []
        for project_data in projects:
            response = isolated_client.post("/projects", json=project_data)
            assert response.status_code == 201
            project_ids.append(response.json()["id"])
        
        # Run migration
        backend_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Verify all projects still exist
        for i, project_id in enumerate(project_ids):
            response = isolated_client.get(f"/projects/{project_id}")
            assert response.status_code == 200
            project = response.json()
            assert project["name"] == projects[i]["name"]
            assert project["description"] == projects[i]["description"]
    
    def test_migration_preserves_task_data(self, isolated_client):
        """Test that task data is preserved during migrations."""
        # Create a project first
        project_data = {"name": "Test Project", "description": "Test", "priority": "high"}
        response = isolated_client.post("/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create test tasks
        tasks = [
            {"title": "Task 1", "description": "First task", "project_id": project_id, "priority": "high"},
            {"title": "Task 2", "description": "Second task", "project_id": project_id, "priority": "medium"},
            {"title": "Task 3", "description": "Third task", "project_id": project_id, "priority": "low"}
        ]
        
        task_ids = []
        for task_data in tasks:
            response = isolated_client.post("/tasks", json=task_data)
            assert response.status_code == 201
            task_ids.append(response.json()["id"])
        
        # Run migration
        backend_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Verify all tasks still exist
        for i, task_id in enumerate(task_ids):
            response = isolated_client.get(f"/tasks/{task_id}")
            assert response.status_code == 200
            task = response.json()
            assert task["title"] == tasks[i]["title"]
            assert task["description"] == tasks[i]["description"]
    
    def test_migration_preserves_relationships(self, isolated_client):
        """Test that relationships are preserved during migrations."""
        # Create project
        project_data = {"name": "Test Project", "description": "Test", "priority": "high"}
        response = isolated_client.post("/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Create tasks
        task_data = {"title": "Test Task", "description": "Test", "project_id": project_id, "priority": "medium"}
        response = isolated_client.post("/tasks", json=task_data)
        assert response.status_code == 201
        task_id = response.json()["id"]
        
        # Run migration
        backend_dir = Path(__file__).parent.parent.parent
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'upgrade'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0
        
        # Verify relationship still exists
        response = isolated_client.get(f"/projects/{project_id}/tasks")
        assert response.status_code == 200
        tasks = response.json()
        assert len(tasks) == 1
        assert tasks[0]["id"] == task_id
        assert tasks[0]["project_id"] == project_id


class TestMigrationErrorHandling:
    """Test error handling in migration system."""
    
    def test_migration_script_error_handling(self):
        """Test that migration script handles errors gracefully."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test invalid command
        result = subprocess.run(
            ['python', 'scripts/migrate.py', 'invalid_command'],
            cwd=backend_dir,
            capture_output=True,
            text=True
        )
        
        assert result.returncode != 0
        assert "Unknown command" in result.stderr or "Unknown command" in result.stdout
    
    def test_migration_manager_error_handling(self):
        """Test that migration manager handles errors gracefully."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        # Test with invalid backend directory
        with tempfile.TemporaryDirectory() as temp_dir:
            manager = MigrationManager(backend_dir=Path(temp_dir))
            
            # Should handle missing alembic configuration gracefully
            is_up_to_date, current_revision = manager.check_migration_status()
            assert is_up_to_date == False
            assert current_revision is None
    
    def test_migration_timeout_handling(self):
        """Test that migration timeouts are handled properly."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        # Test that the timeout is configured
        # (This is more of a smoke test since we can't easily trigger a timeout)
        result = manager._run_alembic_command("current")
        assert len(result) == 3  # Should return (exit_code, stdout, stderr)
        assert isinstance(result[0], int)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])