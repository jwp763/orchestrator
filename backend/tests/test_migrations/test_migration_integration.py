"""
Simplified integration tests for the migration system.

This module tests basic migration functionality without complex subprocess calls.
"""

import os
import pytest
from pathlib import Path

from tests.test_api.test_database_isolation import TestDatabaseIsolation


class TestMigrationIntegration(TestDatabaseIsolation):
    """Test basic migration integration."""
    
    def test_migration_script_exists(self):
        """Test that migration script exists and is executable."""
        backend_dir = Path(__file__).parent.parent.parent
        migrate_script = backend_dir / "scripts" / "migrate.py"
        
        assert migrate_script.exists()
        assert migrate_script.is_file()
        # Check that it's executable
        assert os.access(migrate_script, os.X_OK)
    
    def test_migration_manager_can_be_imported(self):
        """Test that migration manager can be imported."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        # Test that we can create a migration manager
        manager = MigrationManager()
        assert manager is not None
        assert hasattr(manager, 'check_migration_status')
        assert hasattr(manager, 'run_migrations')
        assert hasattr(manager, 'auto_migrate_on_startup')
    
    def test_migration_directories_exist(self):
        """Test that migration directories exist."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Check Alembic structure
        assert (backend_dir / "alembic.ini").exists()
        assert (backend_dir / "migrations").exists()
        assert (backend_dir / "migrations" / "env.py").exists()
        assert (backend_dir / "migrations" / "versions").exists()
    
    def test_migration_with_test_database(self, isolated_engine):
        """Test migration functionality with test database."""
        from sqlalchemy import inspect
        
        # Check that we can inspect the test database
        inspector = inspect(isolated_engine)
        tables = inspector.get_table_names()
        
        # Should have our main tables
        assert 'projects' in tables
        assert 'tasks' in tables
        
        # Check that soft delete columns exist
        project_columns = [col['name'] for col in inspector.get_columns('projects')]
        assert 'deleted_at' in project_columns
        assert 'deleted_by' in project_columns
        
        task_columns = [col['name'] for col in inspector.get_columns('tasks')]
        assert 'deleted_at' in task_columns
        assert 'deleted_by' in task_columns


class TestMigrationConfiguration:
    """Test migration configuration."""
    
    def test_alembic_configuration(self):
        """Test that Alembic configuration is valid."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        # Read and verify configuration
        config_content = alembic_ini.read_text()
        assert 'script_location = migrations' in config_content
        assert 'file_template' in config_content
    
    def test_migration_environment_configuration(self):
        """Test that migration environment is configured correctly."""
        backend_dir = Path(__file__).parent.parent.parent
        env_py = backend_dir / "migrations" / "env.py"
        
        env_content = env_py.read_text()
        assert 'from storage.sql_models import Base' in env_content
        assert 'from config.settings import get_settings' in env_content
        assert 'target_metadata = Base.metadata' in env_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])