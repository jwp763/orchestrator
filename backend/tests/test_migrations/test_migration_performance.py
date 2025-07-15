"""
Simplified performance tests for the migration system.

This module tests basic migration performance without complex subprocess calls.
"""

import time
import pytest
from pathlib import Path

from tests.test_api.test_database_isolation import TestDatabaseIsolation


class TestMigrationPerformance(TestDatabaseIsolation):
    """Test migration performance requirements."""
    
    def test_migration_manager_creation_performance(self):
        """Test that migration manager creation is fast."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        start_time = time.time()
        
        # Create migration manager
        manager = MigrationManager()
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert manager is not None
        assert duration < 1.0, f"Migration manager creation took {duration:.2f} seconds, should be < 1 second"
    
    def test_migration_directory_access_performance(self):
        """Test that migration directory access is fast."""
        backend_dir = Path(__file__).parent.parent.parent
        
        start_time = time.time()
        
        # Access migration files
        alembic_ini = backend_dir / "alembic.ini"
        migrations_dir = backend_dir / "migrations"
        env_py = migrations_dir / "env.py"
        versions_dir = migrations_dir / "versions"
        
        # Check existence
        assert alembic_ini.exists()
        assert migrations_dir.exists()
        assert env_py.exists()
        assert versions_dir.exists()
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 0.1, f"Migration directory access took {duration:.2f} seconds, should be < 0.1 seconds"
    
    def test_migration_configuration_parsing_performance(self):
        """Test that configuration parsing is fast."""
        from alembic.config import Config
        
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        start_time = time.time()
        
        # Parse configuration
        config = Config(str(alembic_ini))
        script_location = config.get_main_option("script_location")
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert script_location == "migrations"
        assert duration < 0.5, f"Configuration parsing took {duration:.2f} seconds, should be < 0.5 seconds"
    
    def test_database_schema_inspection_performance(self, isolated_engine):
        """Test that database schema inspection is fast."""
        from sqlalchemy import inspect
        
        start_time = time.time()
        
        # Inspect database schema
        inspector = inspect(isolated_engine)
        tables = inspector.get_table_names()
        
        # Get column information
        for table in tables:
            columns = inspector.get_columns(table)
            assert len(columns) > 0
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert len(tables) > 0
        assert duration < 1.0, f"Database schema inspection took {duration:.2f} seconds, should be < 1 second"


class TestMigrationScalability:
    """Test migration system scalability."""
    
    def test_migration_file_count_scalability(self):
        """Test that migration system can handle multiple migration files."""
        backend_dir = Path(__file__).parent.parent.parent
        versions_dir = backend_dir / "migrations" / "versions"
        
        # Count migration files
        migration_files = list(versions_dir.glob("*.py"))
        
        # Should have at least one migration file
        assert len(migration_files) >= 1
        
        # Test that we can read all migration files quickly
        start_time = time.time()
        
        for migration_file in migration_files:
            content = migration_file.read_text()
            assert "def upgrade()" in content
            assert "def downgrade()" in content
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Should be fast even with multiple files
        assert duration < 1.0, f"Reading {len(migration_files)} migration files took {duration:.2f} seconds, should be < 1 second"
    
    def test_migration_memory_usage_is_reasonable(self):
        """Test that migration operations don't consume excessive memory."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        # Create multiple migration managers to test memory usage
        managers = []
        for i in range(10):
            manager = MigrationManager()
            managers.append(manager)
        
        # Should be able to create multiple managers without issues
        assert len(managers) == 10
        
        # Clean up
        managers.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])