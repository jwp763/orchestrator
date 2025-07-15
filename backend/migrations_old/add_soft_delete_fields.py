"""
Database migration to add soft delete fields to projects and tasks tables.

This migration adds:
- deleted_at (DateTime, nullable) to projects and tasks tables
- deleted_by (String, nullable) to projects and tasks tables
- Indexes on deleted_at fields for query performance

The migration is designed to be backwards compatible and includes rollback functionality.
"""

from sqlalchemy import text, DateTime, String, Column, Index
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)


class SoftDeleteMigration:
    """Migration class for adding soft delete fields."""
    
    def __init__(self, engine):
        self.engine = engine
        
    def upgrade(self):
        """Apply the migration - add soft delete fields and indexes."""
        try:
            with self.engine.begin() as conn:
                logger.info("Starting soft delete migration...")
                
                # Check if columns already exist (for idempotency)
                def column_exists(table_name, column_name):
                    # First check if table exists
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as count FROM sqlite_master 
                        WHERE type='table' AND name='{table_name}'
                    """))
                    if result.fetchone()[0] == 0:
                        return False
                    
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as count FROM pragma_table_info('{table_name}') 
                        WHERE name = '{column_name}'
                    """))
                    return result.fetchone()[0] > 0
                
                # Add deleted_at and deleted_by columns to projects table
                if not column_exists('projects', 'deleted_at'):
                    logger.info("Adding deleted_at field to projects table...")
                    conn.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN deleted_at DATETIME NULL
                    """))
                else:
                    logger.info("deleted_at field already exists in projects table")
                
                if not column_exists('projects', 'deleted_by'):
                    logger.info("Adding deleted_by field to projects table...")
                    conn.execute(text("""
                        ALTER TABLE projects 
                        ADD COLUMN deleted_by VARCHAR(255) NULL
                    """))
                else:
                    logger.info("deleted_by field already exists in projects table")
                
                # Add deleted_at and deleted_by columns to tasks table
                if not column_exists('tasks', 'deleted_at'):
                    logger.info("Adding deleted_at field to tasks table...")
                    conn.execute(text("""
                        ALTER TABLE tasks 
                        ADD COLUMN deleted_at DATETIME NULL
                    """))
                else:
                    logger.info("deleted_at field already exists in tasks table")
                
                if not column_exists('tasks', 'deleted_by'):
                    logger.info("Adding deleted_by field to tasks table...")
                    conn.execute(text("""
                        ALTER TABLE tasks 
                        ADD COLUMN deleted_by VARCHAR(255) NULL
                    """))
                else:
                    logger.info("deleted_by field already exists in tasks table")
                
                # Create indexes for performance (if they don't exist)
                def index_exists(index_name):
                    result = conn.execute(text(f"""
                        SELECT COUNT(*) as count FROM sqlite_master 
                        WHERE type='index' AND name='{index_name}'
                    """))
                    return result.fetchone()[0] > 0
                
                logger.info("Creating indexes on deleted_at fields...")
                
                if not index_exists('idx_projects_deleted_at'):
                    conn.execute(text("""
                        CREATE INDEX idx_projects_deleted_at ON projects(deleted_at)
                    """))
                    logger.info("Created idx_projects_deleted_at index")
                else:
                    logger.info("idx_projects_deleted_at index already exists")
                
                if not index_exists('idx_tasks_deleted_at'):
                    conn.execute(text("""
                        CREATE INDEX idx_tasks_deleted_at ON tasks(deleted_at)
                    """))
                    logger.info("Created idx_tasks_deleted_at index")
                else:
                    logger.info("idx_tasks_deleted_at index already exists")
                
                # Create composite indexes for common queries
                if not index_exists('idx_projects_active'):
                    conn.execute(text("""
                        CREATE INDEX idx_projects_active ON projects(id, deleted_at) 
                        WHERE deleted_at IS NULL
                    """))
                    logger.info("Created idx_projects_active index")
                else:
                    logger.info("idx_projects_active index already exists")
                
                if not index_exists('idx_tasks_active'):
                    conn.execute(text("""
                        CREATE INDEX idx_tasks_active ON tasks(project_id, deleted_at) 
                        WHERE deleted_at IS NULL
                    """))
                    logger.info("Created idx_tasks_active index")
                else:
                    logger.info("idx_tasks_active index already exists")
                
                logger.info("Soft delete migration completed successfully!")
                
        except SQLAlchemyError as e:
            logger.error(f"Migration failed: {e}")
            raise
            
    def downgrade(self):
        """Rollback the migration - remove soft delete fields and indexes."""
        try:
            with self.engine.begin() as conn:
                logger.info("Rolling back soft delete migration...")
                
                # Drop indexes first
                logger.info("Dropping indexes...")
                try:
                    conn.execute(text("DROP INDEX IF EXISTS idx_projects_active"))
                    conn.execute(text("DROP INDEX IF EXISTS idx_tasks_active"))
                    conn.execute(text("DROP INDEX IF EXISTS idx_projects_deleted_at"))
                    conn.execute(text("DROP INDEX IF EXISTS idx_tasks_deleted_at"))
                except SQLAlchemyError as e:
                    logger.warning(f"Error dropping indexes (may not exist): {e}")
                
                # SQLite doesn't support DROP COLUMN directly, so we need to recreate tables
                # This is a more complex rollback process for SQLite
                logger.info("Recreating tables without soft delete fields...")
                
                # First, back up the data dynamically based on existing columns
                # Get current columns for projects table
                result = conn.execute(text("PRAGMA table_info(projects)"))
                projects_columns = [row[1] for row in result.fetchall() if row[1] not in ['deleted_at', 'deleted_by']]
                projects_columns_str = ", ".join(projects_columns)
                
                # Get current columns for tasks table (if it exists)
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name='tasks'
                """))
                
                conn.execute(text(f"""
                    CREATE TABLE projects_backup AS 
                    SELECT {projects_columns_str}
                    FROM projects
                """))
                
                if result.fetchone()[0] > 0:
                    result = conn.execute(text("PRAGMA table_info(tasks)"))
                    tasks_columns = [row[1] for row in result.fetchall() if row[1] not in ['deleted_at', 'deleted_by']]
                    tasks_columns_str = ", ".join(tasks_columns)
                    
                    conn.execute(text(f"""
                        CREATE TABLE tasks_backup AS 
                        SELECT {tasks_columns_str}
                        FROM tasks
                    """))
                else:
                    logger.warning("tasks table not found during rollback preparation")
                
                # Drop original tables
                conn.execute(text("DROP TABLE IF EXISTS tasks"))
                conn.execute(text("DROP TABLE IF EXISTS projects"))
                
                # Recreate tables from backup (this will have the original structure)
                # For SQLite, we need to explicitly recreate the table with proper constraints
                conn.execute(text("""
                    CREATE TABLE projects AS SELECT * FROM projects_backup
                """))
                
                # Check if tasks table exists in backup before recreating
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM sqlite_master 
                    WHERE type='table' AND name='tasks_backup'
                """))
                if result.fetchone()[0] > 0:
                    conn.execute(text("""
                        CREATE TABLE tasks AS SELECT * FROM tasks_backup
                    """))
                else:
                    logger.warning("tasks_backup table not found during rollback")
                
                # Drop backup tables
                conn.execute(text("DROP TABLE IF EXISTS projects_backup"))
                conn.execute(text("DROP TABLE IF EXISTS tasks_backup"))
                
                logger.info("Soft delete migration rollback completed!")
                
        except SQLAlchemyError as e:
            logger.error(f"Migration rollback failed: {e}")
            raise
    
    def validate_migration(self):
        """Validate that the migration was applied correctly."""
        try:
            with self.engine.begin() as conn:
                # Check if columns exist in projects table
                result = conn.execute(text("""
                    SELECT COUNT(*) as count FROM pragma_table_info('projects') 
                    WHERE name IN ('deleted_at', 'deleted_by')
                """))
                projects_columns = result.fetchone()[0]
                
                # Check if columns exist in tasks table
                result = conn.execute(text("""
                    SELECT COUNT(*) as count FROM pragma_table_info('tasks') 
                    WHERE name IN ('deleted_at', 'deleted_by')
                """))
                tasks_columns = result.fetchone()[0]
                
                # Check if indexes exist
                result = conn.execute(text("""
                    SELECT COUNT(*) as count FROM sqlite_master 
                    WHERE type='index' AND name LIKE 'idx_%_deleted_at'
                """))
                indexes_count = result.fetchone()[0]
                
                if projects_columns == 2 and tasks_columns == 2 and indexes_count >= 2:
                    logger.info("Migration validation successful!")
                    return True
                else:
                    logger.error(f"Migration validation failed. Projects columns: {projects_columns}, Tasks columns: {tasks_columns}, Indexes: {indexes_count}")
                    return False
                    
        except SQLAlchemyError as e:
            logger.error(f"Migration validation failed: {e}")
            return False


def run_migration(engine, direction="upgrade"):
    """Run the migration in the specified direction."""
    migration = SoftDeleteMigration(engine)
    
    if direction == "upgrade":
        migration.upgrade()
        if migration.validate_migration():
            logger.info("Migration completed and validated successfully!")
        else:
            raise Exception("Migration validation failed!")
    elif direction == "downgrade":
        migration.downgrade()
        logger.info("Migration rollback completed!")
    else:
        raise ValueError("Direction must be 'upgrade' or 'downgrade'")


if __name__ == "__main__":
    # Example usage - this would be called by a migration runner
    from sqlalchemy import create_engine
    
    # Replace with your database URL
    DATABASE_URL = "sqlite:///orchestrator.db"
    engine = create_engine(DATABASE_URL)
    
    # Run the migration
    run_migration(engine, "upgrade")