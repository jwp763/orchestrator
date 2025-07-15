"""
Migration management for application startup.

This module provides functions to run database migrations automatically
during application startup, ensuring the database schema is always up-to-date.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class MigrationManager:
    """
    Manager for database migrations.
    
    Provides methods to run migrations automatically during application startup
    and check migration status.
    """
    
    def __init__(self, backend_dir: Optional[Path] = None):
        """
        Initialize the migration manager.
        
        Args:
            backend_dir: Path to the backend directory (auto-detected if None)
        """
        if backend_dir is None:
            # Auto-detect backend directory
            current_file = Path(__file__).resolve()
            self.backend_dir = current_file.parent.parent.parent
        else:
            self.backend_dir = backend_dir
            
        self.alembic_dir = self.backend_dir / "migrations"
        self.alembic_ini = self.backend_dir / "alembic.ini"
    
    def _run_alembic_command(self, command: str, *args: str) -> tuple[int, str, str]:
        """
        Run an Alembic command and return the result.
        
        Args:
            command: The alembic command to run
            *args: Additional arguments to pass to the command
            
        Returns:
            tuple: (exit_code, stdout, stderr)
        """
        cmd = ['alembic', command] + list(args)
        logger.debug(f"Running alembic command: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd, 
                cwd=self.backend_dir,
                capture_output=True,
                text=True,
                timeout=60  # 60 second timeout for migrations
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            logger.error("Migration command timed out")
            return 1, "", "Migration command timed out"
        except Exception as e:
            logger.error(f"Error running migration command: {e}")
            return 1, "", str(e)
    
    def check_migration_status(self) -> tuple[bool, Optional[str]]:
        """
        Check if the database is up-to-date with migrations.
        
        Returns:
            tuple: (is_up_to_date, current_revision)
        """
        try:
            # Check if alembic is set up
            if not self.alembic_ini.exists():
                logger.warning("Alembic configuration not found")
                return False, None
            
            # Get current revision
            exit_code, stdout, stderr = self._run_alembic_command("current")
            if exit_code != 0:
                logger.error(f"Failed to get current revision: {stderr}")
                return False, None
            
            current_revision = stdout.strip()
            
            # Get head revision
            exit_code, stdout, stderr = self._run_alembic_command("heads")
            if exit_code != 0:
                logger.error(f"Failed to get head revision: {stderr}")
                return False, None
            
            head_revision = stdout.strip()
            
            # Check if current matches head
            is_up_to_date = current_revision == head_revision
            
            logger.info(f"Current revision: {current_revision}")
            logger.info(f"Head revision: {head_revision}")
            logger.info(f"Database up-to-date: {is_up_to_date}")
            
            return is_up_to_date, current_revision
            
        except Exception as e:
            logger.error(f"Error checking migration status: {e}")
            return False, None
    
    def run_migrations(self, target_revision: str = "head") -> bool:
        """
        Run database migrations.
        
        Args:
            target_revision: The revision to upgrade to (default: "head")
            
        Returns:
            bool: True if migrations ran successfully
        """
        try:
            logger.info(f"Running migrations to revision: {target_revision}")
            
            exit_code, stdout, stderr = self._run_alembic_command("upgrade", target_revision)
            
            if exit_code == 0:
                logger.info("Migrations completed successfully")
                logger.debug(f"Migration output: {stdout}")
                return True
            else:
                logger.error(f"Migration failed with exit code {exit_code}")
                logger.error(f"Migration stderr: {stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error running migrations: {e}")
            return False
    
    def initialize_database(self) -> bool:
        """
        Initialize the database by creating tables and running migrations.
        
        Returns:
            bool: True if initialization was successful
        """
        try:
            logger.info("Initializing database...")
            
            # First, create tables using SQLAlchemy (in case migrations haven't run yet)
            try:
                from config.settings import get_settings
                from storage.sql_models import Base
                from sqlalchemy import create_engine
                
                settings = get_settings()
                database_url = settings.database_url
                
                # Fix database URL for local execution
                if database_url.startswith('sqlite:///backend/'):
                    database_url = database_url.replace('sqlite:///backend/', 'sqlite:///')
                
                engine = create_engine(database_url)
                Base.metadata.create_all(engine)
                logger.info("Database tables created/verified")
                
            except Exception as e:
                logger.error(f"Error creating database tables: {e}")
                return False
            
            # Run migrations to ensure schema is up-to-date
            success = self.run_migrations()
            if success:
                logger.info("Database initialization completed successfully")
                return True
            else:
                logger.error("Database initialization failed during migrations")
                return False
                
        except Exception as e:
            logger.error(f"Error during database initialization: {e}")
            return False
    
    def auto_migrate_on_startup(self) -> bool:
        """
        Automatically run migrations during application startup.
        
        This method checks if migrations need to be run and runs them if necessary.
        It's designed to be called during application startup.
        
        Returns:
            bool: True if database is ready (no migrations needed or migrations successful)
        """
        try:
            logger.info("Checking database migration status...")
            
            # Check if migrations are needed
            is_up_to_date, current_revision = self.check_migration_status()
            
            if is_up_to_date:
                logger.info("Database is up-to-date, no migrations needed")
                return True
            else:
                logger.info("Database needs migration, running migrations...")
                return self.run_migrations()
                
        except Exception as e:
            logger.error(f"Error during auto-migration: {e}")
            return False


# Global migration manager instance
migration_manager = MigrationManager()


def run_startup_migrations() -> bool:
    """
    Run migrations during application startup.
    
    This is a convenience function that can be called from the main application
    startup code.
    
    Returns:
        bool: True if migrations were successful or not needed
    """
    return migration_manager.auto_migrate_on_startup()


def initialize_database() -> bool:
    """
    Initialize the database with tables and migrations.
    
    Returns:
        bool: True if initialization was successful
    """
    return migration_manager.initialize_database()