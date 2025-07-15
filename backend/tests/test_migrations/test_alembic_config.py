"""
Tests for Alembic configuration and setup.

This module tests the Alembic configuration, environment setup,
and basic migration functionality.
"""

import os
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String


class TestAlembicConfig:
    """Test Alembic configuration and setup."""
    
    def test_alembic_ini_exists(self):
        """Test that alembic.ini exists and is properly configured."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        assert alembic_ini.exists(), "alembic.ini file should exist"
        
        # Test that the config can be loaded
        config = Config(str(alembic_ini))
        assert config is not None
        
        # Check key configuration values
        script_location = config.get_main_option("script_location")
        assert script_location == "migrations"
        
        # Check that file template is set for timestamped migrations
        file_template = config.get_main_option("file_template")
        assert file_template is not None
        assert "%(year)d_%(month).2d_%(day).2d" in file_template
    
    def test_migrations_directory_exists(self):
        """Test that migrations directory exists with proper structure."""
        backend_dir = Path(__file__).parent.parent.parent
        migrations_dir = backend_dir / "migrations"
        
        assert migrations_dir.exists(), "migrations directory should exist"
        assert migrations_dir.is_dir(), "migrations should be a directory"
        
        # Check required files exist
        assert (migrations_dir / "env.py").exists()
        assert (migrations_dir / "script.py.mako").exists()
        assert (migrations_dir / "versions").exists()
        assert (migrations_dir / "versions").is_dir()
    
    def test_env_py_configuration(self):
        """Test that env.py is properly configured."""
        backend_dir = Path(__file__).parent.parent.parent
        migrations_dir = backend_dir / "migrations"
        env_py = migrations_dir / "env.py"
        
        # Read env.py content
        with open(env_py, 'r') as f:
            content = f.read()
        
        # Check that our custom imports are present
        assert "from storage.sql_models import Base" in content
        assert "from config.settings import get_settings" in content
        assert "target_metadata = Base.metadata" in content
        
        # Check that database URL handling is present
        assert "database_url = settings.database_url" in content
        assert "backend/" in content  # Should handle backend/ prefix
    
    def test_alembic_script_directory(self):
        """Test that Alembic script directory is properly configured."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        config = Config(str(alembic_ini))
        script_dir = ScriptDirectory.from_config(config)
        
        assert script_dir is not None
        assert script_dir.dir.endswith("migrations")
        
        # Test that we can get revisions
        revisions = list(script_dir.walk_revisions())
        assert isinstance(revisions, list)
    
    def test_metadata_import(self):
        """Test that metadata can be imported from our models."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from storage.sql_models import Base
        
        assert Base.metadata is not None
        assert hasattr(Base.metadata, 'tables')
        
        # Should have our main tables
        table_names = Base.metadata.tables.keys()
        assert 'projects' in table_names
        assert 'tasks' in table_names
    
    def test_database_url_handling(self):
        """Test that database URL is handled correctly."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from config.settings import get_settings
        
        settings = get_settings()
        database_url = settings.database_url
        
        # Should be a valid SQLite URL
        assert database_url.startswith('sqlite:///')
        assert 'orchestrator' in database_url
        
        # Test URL path handling
        if database_url.startswith('sqlite:///backend/'):
            fixed_url = database_url.replace('sqlite:///backend/', 'sqlite:///')
            assert not fixed_url.startswith('sqlite:///backend/')
            assert fixed_url.startswith('sqlite:///')


class TestAlembicMigrationGeneration:
    """Test migration generation functionality."""
    
    def test_migration_file_template(self):
        """Test that migration files are generated with correct template."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        config = Config(str(alembic_ini))
        file_template = config.get_main_option("file_template")
        
        # Should include timestamp in filename
        assert "%(year)d_%(month).2d_%(day).2d" in file_template
        assert "%(hour).2d%(minute).2d" in file_template
        assert "%(rev)s_%(slug)s" in file_template
    
    def test_migration_context_creation(self):
        """Test that migration context can be created."""
        # Use in-memory SQLite for testing
        engine = create_engine("sqlite:///:memory:")
        
        # Create a simple table for testing
        metadata = MetaData()
        test_table = Table(
            'test_table',
            metadata,
            Column('id', Integer, primary_key=True),
            Column('name', String(50))
        )
        metadata.create_all(engine)
        
        # Create migration context
        with engine.connect() as conn:
            context = MigrationContext.configure(conn)
            assert context is not None
            
            # Test that we can create operations
            ops = Operations(context)
            assert ops is not None
    
    def test_migration_script_structure(self):
        """Test that migration scripts have correct structure."""
        backend_dir = Path(__file__).parent.parent.parent
        versions_dir = backend_dir / "migrations" / "versions"
        
        # Find migration files
        migration_files = list(versions_dir.glob("*.py"))
        
        if migration_files:
            # Test the first migration file
            migration_file = migration_files[0]
            
            with open(migration_file, 'r') as f:
                content = f.read()
            
            # Check required elements
            assert "revision:" in content
            assert "down_revision:" in content
            assert "def upgrade():" in content
            assert "def downgrade():" in content
            assert "from alembic import op" in content
            assert "import sqlalchemy as sa" in content


class TestAlembicValidation:
    """Test validation of Alembic setup."""
    
    def test_config_validation(self):
        """Test that Alembic configuration is valid."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        # Should be able to load config without errors
        config = Config(str(alembic_ini))
        
        # Test script location
        script_location = config.get_main_option("script_location")
        script_path = backend_dir / script_location
        assert script_path.exists()
        
        # Test that script directory can be created
        script_dir = ScriptDirectory.from_config(config)
        assert script_dir is not None
    
    def test_environment_variables(self):
        """Test that environment variables are handled correctly."""
        # Test with different environment values
        with patch.dict(os.environ, {'ENVIRONMENT': 'test'}):
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
            
            from config.settings import get_settings
            settings = get_settings()
            
            assert settings.environment == 'test'
            assert settings.database_url is not None
    
    def test_migration_environment_setup(self):
        """Test that migration environment can be set up."""
        backend_dir = Path(__file__).parent.parent.parent
        alembic_ini = backend_dir / "alembic.ini"
        
        config = Config(str(alembic_ini))
        script_dir = ScriptDirectory.from_config(config)
        
        # Test that env.py can be loaded
        env_py_path = script_dir.dir / "env.py"
        assert env_py_path.exists()
        
        # Test that the environment module has required functions
        import importlib.util
        spec = importlib.util.spec_from_file_location("env", env_py_path)
        env_module = importlib.util.module_from_spec(spec)
        
        # Should have main functions
        assert hasattr(env_module, 'run_migrations_offline') or 'run_migrations_offline' in str(env_py_path.read_text())
        assert hasattr(env_module, 'run_migrations_online') or 'run_migrations_online' in str(env_py_path.read_text())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])