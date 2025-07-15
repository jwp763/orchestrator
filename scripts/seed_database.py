#!/usr/bin/env python3
"""
Database Seeding Script (DEL-009)
Seeds databases with environment-appropriate data
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
    """Main seeding script entry point"""
    parser = argparse.ArgumentParser(description="Database seeding utility")
    
    parser.add_argument(
        '--environment', '-e',
        choices=['dev', 'development', 'staging', 'prod', 'production'],
        default='dev',
        help='Environment to seed (default: dev)'
    )
    
    parser.add_argument(
        '--seed-type', '-t',
        choices=['development', 'dogfooding', 'performance', 'hierarchical', 'custom'],
        default='development',
        help='Type of seed data (default: development)'
    )
    
    parser.add_argument(
        '--backup-dir', '-d',
        default='backups',
        help='Backup directory (default: backups)'
    )
    
    parser.add_argument(
        '--created-by',
        default='seeding-script',
        help='User to mark as creator of seeded data'
    )
    
    parser.add_argument(
        '--skip-existing',
        action='store_true',
        help='Skip seeding if data already exists'
    )
    
    parser.add_argument(
        '--clear-first',
        action='store_true',
        help='Clear existing data before seeding (dangerous!)'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force seeding without confirmation prompts'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    # Performance testing specific options
    parser.add_argument(
        '--project-count',
        type=int,
        default=100,
        help='Number of projects for performance testing (default: 100)'
    )
    
    parser.add_argument(
        '--tasks-per-project',
        type=int,
        default=50,
        help='Number of tasks per project for performance testing (default: 50)'
    )
    
    # Hierarchical testing specific options
    parser.add_argument(
        '--max-depth',
        type=int,
        default=3,
        help='Maximum depth for hierarchical tasks (default: 3)'
    )
    
    parser.add_argument(
        '--tasks-per-level',
        type=int,
        default=5,
        help='Number of tasks per level for hierarchical structure (default: 5)'
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
    
    # Safety confirmations for production
    if args.environment in ['prod', 'production'] and not args.force:
        print(f"⚠️  WARNING: You are about to seed the PRODUCTION database!")
        print(f"   Target: {db_path}")
        print(f"   Seed type: {args.seed_type}")
        
        if args.clear_first:
            print(f"   ❌ ALL EXISTING DATA WILL BE DELETED (--clear-first flag)")
        
        confirm = input("\nType 'SEED' to confirm: ")
        if confirm != 'SEED':
            print("Seeding cancelled")
            sys.exit(0)
    
    # Confirm for other environments if clearing data
    if args.clear_first and not args.force:
        print(f"⚠️  WARNING: About to clear all data in {args.environment} database")
        print(f"   This will delete all projects, tasks, and users!")
        
        confirm = input("\nProceed with clearing data? (y/N): ")
        if confirm.lower() not in ['y', 'yes']:
            print("Seeding cancelled")
            sys.exit(0)
    
    try:
        if args.verbose:
            print(f"🌱 Starting seeding of {args.environment} database...")
            print(f"   Database: {db_path}")
            print(f"   Seed type: {args.seed_type}")
            print(f"   Created by: {args.created_by}")
            print(f"   Skip existing: {args.skip_existing}")
            print(f"   Clear first: {args.clear_first}")
        
        # Clear data if requested
        if args.clear_first:
            if args.verbose:
                print(f"🧹 Clearing existing data...")
            
            clear_result = db_manager.clear_all_data()
            
            if args.verbose:
                print(f"   Cleared {clear_result['projects_deleted']} projects")
                print(f"   Cleared {clear_result['tasks_deleted']} tasks")
        
        # Perform seeding based on type
        if args.seed_type == 'development':
            result = db_manager.seed_development_data(
                created_by=args.created_by,
                skip_existing=args.skip_existing
            )
        elif args.seed_type == 'dogfooding':
            result = db_manager.seed_dogfooding_data()
        elif args.seed_type == 'performance':
            result = db_manager.seed_performance_testing_data(
                project_count=args.project_count,
                tasks_per_project=args.tasks_per_project
            )
        elif args.seed_type == 'hierarchical':
            # For hierarchical, we need a project ID - create one first
            dev_result = db_manager.seed_development_data(skip_existing=True)
            projects = db_manager.get_all_projects()
            project_id = projects[0]['id'] if projects else 'test_project'
            
            result = db_manager.seed_hierarchical_tasks(
                project_id=project_id,
                max_depth=args.max_depth,
                tasks_per_level=args.tasks_per_level
            )
        else:  # custom
            result = db_manager.seed_environment_data(args.environment)
        
        # Display results
        if args.verbose:
            print(f"✅ Seeding completed successfully!")
            
            for key, value in result.items():
                if key.endswith('_created') or key.endswith('_deleted'):
                    print(f"   {key.replace('_', ' ').title()}: {value}")
            
            # Show current data summary
            projects = db_manager.get_all_projects()
            tasks = db_manager.get_all_tasks()
            
            print(f"📊 Database summary:")
            print(f"   Total projects: {len(projects)}")
            print(f"   Total tasks: {len(tasks)}")
            
            # Show some sample data
            if projects:
                print(f"   Sample projects:")
                for project in projects[:3]:
                    print(f"     - {project['name']} (ID: {project['id']})")
            
            if tasks:
                print(f"   Sample tasks:")
                for task in tasks[:5]:
                    print(f"     - {task['title']} (Project: {task['project_id']})")
        else:
            print(f"✅ Seeded {args.environment} database with {args.seed_type} data")
            
            if 'projects_created' in result:
                print(f"   Created {result['projects_created']} projects and {result.get('tasks_created', 0)} tasks")
        
    except Exception as e:
        print(f"❌ Seeding failed: {str(e)}")
        if args.verbose:
            import traceback
            print(f"   Error details: {traceback.format_exc()}")
        sys.exit(1)


if __name__ == '__main__':
    main()