#!/usr/bin/env python3
"""
Advanced Database Restore Script (DEL-009)
Improved restore functionality with metadata and validation
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
    """Main restore script entry point"""
    parser = argparse.ArgumentParser(description="Advanced database restore utility")
    
    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'development', 'staging', 'prod', 'production'],
        default='dev',
        help='Environment to restore to (default: dev)'
    )
    
    parser.add_argument(
        '--backup-file', '-b',
        required=True,
        help='Path to backup file to restore from'
    )
    
    parser.add_argument(
        '--backup-dir', '-d',
        default='backups',
        help='Backup directory (default: backups)'
    )
    
    parser.add_argument(
        '--no-backup',
        action='store_true',
        help='Skip creating backup before restore (dangerous!)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force restore without confirmation prompts'
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
    
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='List available backup files and exit'
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
    
    # Initialize database manager
    db_manager = DatabaseManager(
        database_path=db_path,
        backup_directory=args.backup_dir
    )
    
    # Handle list backups command
    if args.list_backups:
        backups = db_manager.list_available_backups()
        if not backups:
            print("📭 No backup files found")
            return
        
        print(f"📂 Available backups ({len(backups)}):")
        for backup in backups:
            print(f"   - {backup['name']}")
            if args.verbose:
                print(f"     Size: {backup['size']} bytes")
                print(f"     Created: {backup['created_at']}")
                print(f"     Path: {backup['path']}")
        return
    
    # Validate backup file path
    if not os.path.isabs(args.backup_file):
        # Try relative to backup directory
        backup_file_path = os.path.join(args.backup_dir, args.backup_file)
        if not os.path.exists(backup_file_path):
            backup_file_path = args.backup_file
    else:
        backup_file_path = args.backup_file
    
    if not os.path.exists(backup_file_path):
        print(f"❌ Backup file not found: {backup_file_path}")
        print("   Use --list-backups to see available backups")
        sys.exit(1)
    
    # Safety confirmations for production
    if args.environment in ['prod', 'production'] and not args.force:
        print(f"⚠️  WARNING: You are about to restore the PRODUCTION database!")
        print(f"   Target: {db_path}")
        print(f"   Backup: {backup_file_path}")
        
        if not args.no_backup:
            print(f"   A backup will be created before restore")
        else:
            print(f"   ❌ NO BACKUP will be created (--no-backup flag)")
        
        confirm = input("\nType 'RESTORE' to confirm: ")
        if confirm != 'RESTORE':
            print("Restore cancelled")
            sys.exit(0)
    
    # Confirm restore for other environments if current database exists
    if not args.force and os.path.exists(db_path):
        current_size = os.path.getsize(db_path)
        backup_size = os.path.getsize(backup_file_path)
        
        print(f"🔄 About to restore {args.environment} database:")
        print(f"   Current: {db_path} ({current_size} bytes)")
        print(f"   Backup:  {backup_file_path} ({backup_size} bytes)")
        
        if not args.no_backup:
            print(f"   Current database will be backed up first")
        
        confirm = input("\nProceed with restore? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Restore cancelled")
            sys.exit(0)
    
    try:
        if args.verbose:
            print(f"🔄 Starting restore of {args.environment} database...")
            print(f"   Target: {db_path}")
            print(f"   Backup: {backup_file_path}")
            print(f"   Create backup: {'No' if args.no_backup else 'Yes'}")
        
        # Perform restore
        if args.with_metadata:
            result = db_manager.restore_database_with_metadata(backup_file_path)
            
            if args.verbose:
                print(f"✅ Restore completed successfully!")
                print(f"   Restored from: {result['backup_file']}")
                print(f"   Backup size: {result['backup_size']} bytes")
                print(f"   Restored at: {result['restored_at']}")
                if result['pre_restore_backup']:
                    print(f"   Pre-restore backup: {result['pre_restore_backup']}")
            else:
                print(f"✅ Database restored from: {os.path.basename(backup_file_path)}")
        else:
            db_manager.restore_database(backup_file_path, create_backup=not args.no_backup)
            
            if args.verbose:
                restored_size = os.path.getsize(db_path)
                print(f"✅ Restore completed successfully!")
                print(f"   Database size: {restored_size} bytes")
            else:
                print(f"✅ Database restored from: {os.path.basename(backup_file_path)}")
        
        # Show current backups after restore
        if args.verbose:
            backups = db_manager.list_available_backups()
            print(f"📊 Available backups ({len(backups)}):")
            for backup in backups[-5:]:  # Show last 5
                print(f"   - {backup['name']} ({backup['size']} bytes)")
        
        # Validation message
        if args.verbose:
            print(f"🔍 Restore validation:")
            if db_manager.validate_database_connection():
                print(f"   ✅ Database connection valid")
            else:
                print(f"   ⚠️  Database connection validation failed")
        
    except Exception as e:
        print(f"❌ Restore failed: {str(e)}")
        if args.verbose:
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()