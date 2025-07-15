#!/usr/bin/env python3
"""
Migration automation script for the Orchestrator project.

This script provides convenient commands for managing database migrations
using Alembic in different environments.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.settings import get_settings


def run_alembic_command(command: str, *args: str) -> int:
    """
    Run an Alembic command and return the exit code.
    
    Args:
        command: The alembic command to run
        *args: Additional arguments to pass to the command
        
    Returns:
        int: Exit code from the command
    """
    cmd = ['alembic', command] + list(args)
    print(f"Running: {' '.join(cmd)}")
    
    # Change to backend directory to run alembic
    backend_dir = Path(__file__).parent.parent
    result = subprocess.run(cmd, cwd=backend_dir)
    return result.returncode


def upgrade(revision: str = "head") -> int:
    """
    Upgrade database to a specific revision.
    
    Args:
        revision: The revision to upgrade to (default: "head")
        
    Returns:
        int: Exit code
    """
    print(f"Upgrading database to revision: {revision}")
    return run_alembic_command("upgrade", revision)


def downgrade(revision: str) -> int:
    """
    Downgrade database to a specific revision.
    
    Args:
        revision: The revision to downgrade to
        
    Returns:
        int: Exit code
    """
    print(f"Downgrading database to revision: {revision}")
    return run_alembic_command("downgrade", revision)


def create_migration(message: str, autogenerate: bool = True) -> int:
    """
    Create a new migration.
    
    Args:
        message: Description of the migration
        autogenerate: Whether to use autogenerate feature
        
    Returns:
        int: Exit code
    """
    print(f"Creating new migration: {message}")
    args = ["revision", "-m", message]
    if autogenerate:
        args.append("--autogenerate")
    return run_alembic_command(*args)


def show_current() -> int:
    """
    Show current database revision.
    
    Returns:
        int: Exit code
    """
    print("Current database revision:")
    return run_alembic_command("current")


def show_history() -> int:
    """
    Show migration history.
    
    Returns:
        int: Exit code
    """
    print("Migration history:")
    return run_alembic_command("history")


def show_heads() -> int:
    """
    Show head revisions.
    
    Returns:
        int: Exit code
    """
    print("Head revisions:")
    return run_alembic_command("heads")


def init_db() -> int:
    """
    Initialize database and run all migrations.
    
    Returns:
        int: Exit code
    """
    print("Initializing database...")
    settings = get_settings()
    print(f"Database URL: {settings.database_url}")
    
    # Create database tables if they don't exist
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
    from storage.sql_models import Base
    from sqlalchemy import create_engine
    
    # Fix database URL for local execution
    database_url = settings.database_url
    if database_url.startswith('sqlite:///backend/'):
        database_url = database_url.replace('sqlite:///backend/', 'sqlite:///')
    
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)
    
    # Run migrations
    return upgrade("head")


def validate_migrations() -> int:
    """
    Validate that all migrations can be applied and reversed.
    
    Returns:
        int: Exit code
    """
    print("Validating migrations...")
    
    # Get current revision
    result = run_alembic_command("current")
    if result != 0:
        print("Failed to get current revision")
        return result
    
    # Try to upgrade to head
    result = upgrade("head")
    if result != 0:
        print("Failed to upgrade to head")
        return result
    
    print("Migration validation completed successfully")
    return 0


def main():
    """Main entry point for the migration script."""
    parser = argparse.ArgumentParser(description="Database migration management")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Upgrade command
    upgrade_parser = subparsers.add_parser('upgrade', help='Upgrade database')
    upgrade_parser.add_argument('revision', nargs='?', default='head', 
                               help='Revision to upgrade to (default: head)')
    
    # Downgrade command
    downgrade_parser = subparsers.add_parser('downgrade', help='Downgrade database')
    downgrade_parser.add_argument('revision', help='Revision to downgrade to')
    
    # Create migration command
    create_parser = subparsers.add_parser('create', help='Create new migration')
    create_parser.add_argument('message', help='Migration description')
    create_parser.add_argument('--no-autogenerate', action='store_true', 
                              help='Disable autogenerate')
    
    # Info commands
    subparsers.add_parser('current', help='Show current revision')
    subparsers.add_parser('history', help='Show migration history')
    subparsers.add_parser('heads', help='Show head revisions')
    
    # Utility commands
    subparsers.add_parser('init', help='Initialize database')
    subparsers.add_parser('validate', help='Validate migrations')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute the requested command
    if args.command == 'upgrade':
        return upgrade(args.revision)
    elif args.command == 'downgrade':
        return downgrade(args.revision)
    elif args.command == 'create':
        return create_migration(args.message, not args.no_autogenerate)
    elif args.command == 'current':
        return show_current()
    elif args.command == 'history':
        return show_history()
    elif args.command == 'heads':
        return show_heads()
    elif args.command == 'init':
        return init_db()
    elif args.command == 'validate':
        return validate_migrations()
    else:
        print(f"Unknown command: {args.command}")
        return 1


if __name__ == "__main__":
    sys.exit(main())