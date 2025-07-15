# Database Management Scripts (DEL-009)

## Overview

This directory contains comprehensive database management tools developed using Test-Driven Development (TDD) for the dogfooding workflow. All functionality is backed by 40 passing tests.

## Scripts

### Core Management

- **`database_manager.py`** - Comprehensive database management class with backup, restore, and seeding capabilities
- **`backup_database.py`** - CLI script for creating timestamped database backups with metadata
- **`restore_database.py`** - CLI script for restoring databases with safety validations
- **`seed_database.py`** - CLI script for seeding databases with environment-specific data

### Usage Examples

```bash
# Backup production database
./scripts/backup_database.py --environment prod --verbose

# Restore from backup with confirmation
./scripts/restore_database.py --environment staging --backup-file prod_backup_20250715_084431.db

# Seed development environment with test data
./scripts/seed_database.py --environment dev --seed-type development --verbose

# Seed staging with realistic dogfooding data
./scripts/seed_database.py --environment staging --seed-type dogfooding

# List available backups
./scripts/restore_database.py --list-backups
```

## Test Coverage

The implementation includes comprehensive TDD test coverage located in `backend/tests/test_deployment/`:

- **`test_database_backup.py`** - 14 tests covering backup functionality
- **`test_database_restore.py`** - 12 tests covering restore functionality  
- **`test_data_seeding.py`** - 14 tests covering data seeding functionality

All 40 tests are passing with full coverage of edge cases, error conditions, and integration scenarios.

### Running Tests

```bash
# Run all deployment tests
cd backend && python -m pytest tests/test_deployment/ -v

# Run specific test files
cd backend && python -m pytest tests/test_deployment/test_database_backup.py -v
```

## Features

### Backup Management
- Timestamped backup creation
- Integrity validation with checksums
- Metadata collection and reporting
- Automatic cleanup of old backups
- Multi-environment support

### Restore Operations
- Atomic restore operations
- Pre-restore backup creation
- Backup integrity validation
- Environment-specific safety checks
- Cross-environment data copying

### Data Seeding
- Development test data
- Realistic dogfooding data
- Performance testing datasets
- Hierarchical task structures
- Environment-specific configurations

## Safety Features

- Production environment confirmations
- Backup-before-restore by default
- Integrity validation for all operations
- Atomic operations with rollback on failure
- Clear error messages and troubleshooting

## Integration

These scripts integrate seamlessly with:
- Multi-environment database setup (dev/staging/prod)
- Existing npm script workflow
- SQLite database files
- Future SQLAlchemy model integration

Developed as part of DEL-009 deployment refactor plan to enable safe dogfooding workflows.