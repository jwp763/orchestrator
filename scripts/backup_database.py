#!/usr/bin/env python3
"""
Advanced Database Backup Script (DEL-009)
Improved backup functionality with metadata and validation
"""

import os
import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add backend src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend', 'src'))

from database_manager import DatabaseManager


def main():
    """Main backup script entry point"""
    parser = argparse.ArgumentParser(description="Advanced database backup utility")
    
    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'development', 'staging', 'prod', 'production'],
        default='dev',
        help='Environment to backup (default: dev)'
    )
    
    parser.add_argument(
        '--backup-name', '-n',
        help='Custom backup name (default: auto-generated)'
    )
    
    parser.add_argument(
        '--backup-dir', '-d',
        default='backups',
        help='Backup directory (default: backups)'
    )
    
    parser.add_argument(
        '--keep-count', '-k',
        type=int,
        default=10,
        help='Number of backups to keep (default: 10)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--with-metadata',
        action='store_true',
        help='Include detailed metadata in output'
    )
    
    args = parser.parse_args()
    
    # Map environment names to database paths
    env_map = {
        'dev': 'backend/orchestrator_dev.db',
        'development': 'backend/orchestrator_dev.db',
        'staging': 'backend/orchestrator_staging.db',
        'prod': 'backend/orchestrator_prod.db',
        'production': 'backend/orchestrator_prod.db'
    }
    
    db_path = env_map[args.environment]
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print(f"   Run the {args.environment} environment first to create the database")
        sys.exit(1)
    
    # Initialize database manager
    db_manager = DatabaseManager(
        database_path=db_path,
        backup_directory=args.backup_dir
    )
    
    try:
        if args.verbose:
            print(f"💾 Starting backup of {args.environment} database...")
            print(f"   Source: {db_path}")
            print(f"   Backup directory: {args.backup_dir}")
        
        # Perform backup
        if args.with_metadata:
            result = db_manager.backup_database_with_metadata()
            backup_path = result['backup_path']
            
            if args.verbose:
                print(f"✅ Backup completed successfully!")
                print(f"   Backup path: {backup_path}")
                print(f"   Original size: {result['original_size']} bytes")
                print(f"   Backup size: {result['backup_size']} bytes")
                print(f"   Created at: {result['created_at']}")
                print(f"   Checksum: {result['checksum']}")
            else:
                print(f"✅ Backup created: {backup_path}")
        else:
            backup_path = db_manager.backup_database(backup_name=args.backup_name)
            
            if args.verbose:
                backup_size = os.path.getsize(backup_path)
                print(f"✅ Backup completed successfully!")
                print(f"   Backup path: {backup_path}")
                print(f"   Size: {backup_size} bytes")
            else:
                print(f"✅ Backup created: {backup_path}")
        
        # Cleanup old backups
        if args.verbose:
            print(f"🧹 Cleaning up old backups (keeping {args.keep_count} most recent)...")
        
        db_manager.cleanup_old_backups(keep_count=args.keep_count)
        
        if args.verbose:
            backups = db_manager.list_available_backups()
            print(f"📊 Current backups ({len(backups)}):")
            for backup in backups:
                print(f"   - {backup['name']} ({backup['size']} bytes)")
        
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        if args.verbose:
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()