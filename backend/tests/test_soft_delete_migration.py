"""
Integration tests for migration script execution and rollback.

Tests DEL-001 acceptance criteria:
- Migration script adds columns with proper indexes
- Migration is backwards compatible with existing data
- Database indexes created on deleted_at fields for query performance
"""

import pytest
import os
import tempfile
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

from src.storage.sql_models import Base, Project, Task
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority
from migrations.add_soft_delete_fields import SoftDeleteMigration, run_migration


class TestSoftDeleteMigration:
    """Test suite for soft delete migration script."""

    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database file for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.remove(db_path)

    @pytest.fixture
    def engine_with_old_schema(self, temp_db_path):
        """Create engine with old schema (without soft delete fields)."""
        engine = create_engine(f'sqlite:///{temp_db_path}', echo=False)
        
        # Create old schema without soft delete fields
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE projects (
                    id VARCHAR NOT NULL, 
                    name VARCHAR NOT NULL, 
                    description TEXT, 
                    status VARCHAR(9), 
                    priority VARCHAR(8), 
                    tags JSON, 
                    due_date DATE, 
                    start_date DATE, 
                    created_at DATETIME, 
                    updated_at DATETIME, 
                    created_by VARCHAR NOT NULL, 
                    PRIMARY KEY (id)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE tasks (
                    id VARCHAR NOT NULL, 
                    project_id VARCHAR NOT NULL, 
                    title VARCHAR NOT NULL, 
                    description TEXT, 
                    status VARCHAR(11), 
                    priority VARCHAR(8), 
                    parent_id VARCHAR, 
                    estimated_minutes INTEGER, 
                    actual_minutes INTEGER, 
                    depth INTEGER, 
                    dependencies JSON, 
                    due_date DATE, 
                    assignee VARCHAR, 
                    tags JSON, 
                    labels JSON, 
                    motion_task_id VARCHAR, 
                    linear_issue_id VARCHAR, 
                    notion_task_id VARCHAR, 
                    gitlab_issue_id VARCHAR, 
                    task_metadata JSON, 
                    created_at DATETIME, 
                    updated_at DATETIME, 
                    completed_at DATETIME, 
                    created_by VARCHAR NOT NULL, 
                    PRIMARY KEY (id), 
                    FOREIGN KEY(project_id) REFERENCES projects (id), 
                    FOREIGN KEY(parent_id) REFERENCES tasks (id)
                )
            """))
            
            # Insert some test data
            conn.execute(text("""
                INSERT INTO projects (id, name, description, status, priority, tags, created_by, created_at, updated_at)
                VALUES ('test-project-1', 'Test Project', 'A test project', 'PLANNING', 'HIGH', '[]', 'test_user', '2024-01-01 00:00:00', '2024-01-01 00:00:00')
            """))
            
            conn.execute(text("""
                INSERT INTO tasks (id, project_id, title, description, status, priority, created_by, created_at, updated_at)
                VALUES ('test-task-1', 'test-project-1', 'Test Task', 'A test task', 'TODO', 'MEDIUM', 'test_user', '2024-01-01 00:00:00', '2024-01-01 00:00:00')
            """))
        
        return engine

    def test_migration_upgrade_adds_columns(self, engine_with_old_schema):
        """Test that migration upgrade adds soft delete columns."""
        engine = engine_with_old_schema
        
        # Verify columns don't exist before migration
        inspector = inspect(engine)
        
        projects_columns_before = [col['name'] for col in inspector.get_columns('projects')]
        tasks_columns_before = [col['name'] for col in inspector.get_columns('tasks')]
        
        assert 'deleted_at' not in projects_columns_before
        assert 'deleted_by' not in projects_columns_before
        assert 'deleted_at' not in tasks_columns_before
        assert 'deleted_by' not in tasks_columns_before
        
        # Run migration upgrade
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Create new inspector to avoid cache issues
        inspector_after = inspect(engine)
        projects_columns_after = [col['name'] for col in inspector_after.get_columns('projects')]
        tasks_columns_after = [col['name'] for col in inspector_after.get_columns('tasks')]
        
        assert 'deleted_at' in projects_columns_after
        assert 'deleted_by' in projects_columns_after
        assert 'deleted_at' in tasks_columns_after
        assert 'deleted_by' in tasks_columns_after

    def test_migration_creates_indexes(self, engine_with_old_schema):
        """Test that migration creates performance indexes."""
        engine = engine_with_old_schema
        
        # Run migration upgrade
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Check that indexes were created
        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%_deleted_at'
            """))
            index_names = [row[0] for row in result.fetchall()]
            
            assert 'idx_projects_deleted_at' in index_names
            assert 'idx_tasks_deleted_at' in index_names
            
            # Check composite indexes
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%_active'
            """))
            composite_index_names = [row[0] for row in result.fetchall()]
            
            assert 'idx_projects_active' in composite_index_names
            assert 'idx_tasks_active' in composite_index_names

    def test_migration_preserves_existing_data(self, engine_with_old_schema):
        """Test that migration preserves existing data."""
        engine = engine_with_old_schema
        
        # Get existing data before migration
        with engine.begin() as conn:
            result = conn.execute(text("SELECT id, name, created_by FROM projects"))
            projects_before = result.fetchall()
            
            result = conn.execute(text("SELECT id, title, project_id FROM tasks"))
            tasks_before = result.fetchall()
        
        # Run migration upgrade
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Verify existing data is preserved
        with engine.begin() as conn:
            result = conn.execute(text("SELECT id, name, created_by, deleted_at, deleted_by FROM projects"))
            projects_after = result.fetchall()
            
            result = conn.execute(text("SELECT id, title, project_id, deleted_at, deleted_by FROM tasks"))
            tasks_after = result.fetchall()
        
        # Check that original data is preserved
        assert len(projects_after) == len(projects_before)
        assert len(tasks_after) == len(tasks_before)
        
        # Check that new fields are NULL for existing records
        for project in projects_after:
            assert project[3] is None  # deleted_at
            assert project[4] is None  # deleted_by
        
        for task in tasks_after:
            assert task[3] is None  # deleted_at
            assert task[4] is None  # deleted_by

    def test_migration_is_idempotent(self, engine_with_old_schema):
        """Test that migration can be run multiple times without issues."""
        engine = engine_with_old_schema
        
        # Run migration first time
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Verify migration was successful
        assert migration.validate_migration()
        
        # Run migration again (should be idempotent)
        migration.upgrade()
        
        # Verify migration is still valid
        assert migration.validate_migration()

    def test_migration_rollback_removes_columns(self, engine_with_old_schema):
        """Test that migration rollback removes soft delete columns."""
        engine = engine_with_old_schema
        
        # Run migration upgrade
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Verify columns were added
        inspector = inspect(engine)
        projects_columns_after_upgrade = [col['name'] for col in inspector.get_columns('projects')]
        tasks_columns_after_upgrade = [col['name'] for col in inspector.get_columns('tasks')]
        
        assert 'deleted_at' in projects_columns_after_upgrade
        assert 'deleted_by' in projects_columns_after_upgrade
        assert 'deleted_at' in tasks_columns_after_upgrade
        assert 'deleted_by' in tasks_columns_after_upgrade
        
        # Run migration rollback
        migration.downgrade()
        
        # Verify columns were removed (create new inspector to avoid caching)
        inspector_after_rollback = inspect(engine)
        projects_columns_after_rollback = [col['name'] for col in inspector_after_rollback.get_columns('projects')]
        tasks_columns_after_rollback = [col['name'] for col in inspector_after_rollback.get_columns('tasks')]
        
        assert 'deleted_at' not in projects_columns_after_rollback
        assert 'deleted_by' not in projects_columns_after_rollback
        assert 'deleted_at' not in tasks_columns_after_rollback
        assert 'deleted_by' not in tasks_columns_after_rollback

    def test_migration_rollback_removes_indexes(self, engine_with_old_schema):
        """Test that migration rollback removes indexes."""
        engine = engine_with_old_schema
        
        # Run migration upgrade
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        
        # Verify indexes were created
        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%_deleted_at'
            """))
            assert result.fetchone()[0] >= 2  # At least projects and tasks indexes
        
        # Run migration rollback
        migration.downgrade()
        
        # Verify indexes were removed
        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*) FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%_deleted_at'
            """))
            assert result.fetchone()[0] == 0

    def test_migration_rollback_preserves_original_data(self, engine_with_old_schema):
        """Test that migration rollback preserves original data."""
        engine = engine_with_old_schema
        
        # Get original data
        with engine.begin() as conn:
            result = conn.execute(text("SELECT id, name, created_by FROM projects"))
            original_projects = result.fetchall()
            
            result = conn.execute(text("SELECT id, title, project_id FROM tasks"))
            original_tasks = result.fetchall()
        
        # Run migration upgrade and rollback
        migration = SoftDeleteMigration(engine)
        migration.upgrade()
        migration.downgrade()
        
        # Verify original data is preserved
        with engine.begin() as conn:
            result = conn.execute(text("SELECT id, name, created_by FROM projects"))
            final_projects = result.fetchall()
            
            result = conn.execute(text("SELECT id, title, project_id FROM tasks"))
            final_tasks = result.fetchall()
        
        assert final_projects == original_projects
        assert final_tasks == original_tasks

    def test_migration_validation_function(self, engine_with_old_schema):
        """Test the migration validation function."""
        engine = engine_with_old_schema
        migration = SoftDeleteMigration(engine)
        
        # Validation should fail before migration
        assert not migration.validate_migration()
        
        # Run migration
        migration.upgrade()
        
        # Validation should pass after migration
        assert migration.validate_migration()
        
        # Run rollback
        migration.downgrade()
        
        # Validation should fail after rollback
        assert not migration.validate_migration()

    def test_run_migration_function(self, temp_db_path):
        """Test the run_migration function interface."""
        engine = create_engine(f'sqlite:///{temp_db_path}', echo=False)
        
        # Create old schema
        with engine.begin() as conn:
            conn.execute(text("""
                CREATE TABLE projects (
                    id VARCHAR NOT NULL, 
                    name VARCHAR NOT NULL, 
                    created_by VARCHAR NOT NULL, 
                    created_at DATETIME, 
                    updated_at DATETIME,
                    PRIMARY KEY (id)
                )
            """))
            
            conn.execute(text("""
                CREATE TABLE tasks (
                    id VARCHAR NOT NULL, 
                    project_id VARCHAR NOT NULL, 
                    title VARCHAR NOT NULL, 
                    created_by VARCHAR NOT NULL, 
                    created_at DATETIME, 
                    updated_at DATETIME,
                    PRIMARY KEY (id)
                )
            """))
        
        # Test upgrade
        run_migration(engine, "upgrade")
        
        # Verify migration was successful
        migration = SoftDeleteMigration(engine)
        assert migration.validate_migration()
        
        # Test downgrade
        run_migration(engine, "downgrade")
        
        # Verify rollback was successful
        assert not migration.validate_migration()

    def test_migration_with_invalid_direction(self, temp_db_path):
        """Test that migration raises error for invalid direction."""
        engine = create_engine(f'sqlite:///{temp_db_path}', echo=False)
        
        with pytest.raises(ValueError, match="Direction must be 'upgrade' or 'downgrade'"):
            run_migration(engine, "invalid_direction")