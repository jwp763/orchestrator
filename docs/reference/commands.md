# Commands Reference

*Last Updated: 2025-01-11*

## Table of Contents

- [Overview](#overview)
- [Development Commands](#development-commands)
- [Testing Commands](#testing-commands)
- [Code Quality Commands](#code-quality-commands)
- [Git Commands](#git-commands)
- [Build & Deployment Commands](#build--deployment-commands)
- [Database Management](#database-management)
- [Monitoring Commands](#monitoring-commands)
- [Utility Commands](#utility-commands)
- [AI Development Commands](#ai-development-commands)
- [Makefile Shortcuts](#makefile-shortcuts)
- [Environment Variables](#environment-variables)
- [Troubleshooting Commands](#troubleshooting-commands)
- [CI/CD Commands](#cicd-commands)

## Overview

This document provides a comprehensive reference for all commands used in the Databricks Orchestrator project, including development, testing, deployment, and maintenance commands.

## Development Commands

### Backend Development

#### Setup Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"
```

#### Run Development Server
```bash
# Start FastAPI development server
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# With custom settings
ENVIRONMENT=development uvicorn src.main:app --reload

# With debugging
python -m debugpy --listen 5678 -m uvicorn src.main:app --reload
```

#### Database Commands
```bash
# Initialize database
python -m src.scripts.init_db

# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Add user table"

# Rollback migration
alembic downgrade -1

# Reset database
python -m src.scripts.reset_db --confirm
```

### Frontend Development

#### Setup
```bash
# Install dependencies
cd frontend
npm install

# Install specific package
npm install package-name
npm install -D package-name  # Dev dependency
```

#### Development Server
```bash
# Start development server
npm run dev

# With custom port
npm run dev -- --port 3001

# With HTTPS
npm run dev -- --https

# Open in browser
npm run dev -- --open
```

#### Build Commands
```bash
# Production build
npm run build

# Preview production build
npm run preview

# Analyze bundle size
npm run build -- --analyze
```

## Testing Commands

### Backend Testing

#### Run All Tests
```bash
# CRITICAL: Always run from backend directory
cd backend && pytest

# With coverage
cd backend && pytest --cov=src --cov-report=html

# Verbose output
cd backend && pytest -v

# Stop on first failure
cd backend && pytest -x

# Run in parallel
cd backend && pytest -n auto
```

#### Run Specific Tests
```bash
# Test single file
cd backend && pytest tests/test_storage.py

# Test single function
cd backend && pytest tests/test_storage.py::test_create_project

# Test by marker
cd backend && pytest -m "unit"
cd backend && pytest -m "integration"
cd backend && pytest -m "slow"
```

#### Test Options
```bash
# Show print statements
cd backend && pytest -s

# Show local variables on failure
cd backend && pytest -l

# Generate XML report
cd backend && pytest --junit-xml=report.xml

# Run failed tests from last run
cd backend && pytest --lf

# Run new tests first
cd backend && pytest --ff
```

### Frontend Testing

#### Run Tests
```bash
# Run all tests
cd frontend && npm test

# Watch mode
cd frontend && npm run test:watch

# Coverage report
cd frontend && npm run test:coverage

# UI mode
cd frontend && npm run test:ui

# Run specific file
cd frontend && npm test ProjectSidebar.test.tsx

# Update snapshots
cd frontend && npm test -- -u
```

## Code Quality Commands

### Linting

#### Python (Backend)
```bash
# Run all linters
make lint

# Run specific linters
black src tests                    # Format code
ruff check src tests              # Check style
mypy src                          # Type checking

# Fix issues automatically
black src tests
ruff check --fix src tests
```

#### TypeScript (Frontend)
```bash
# ESLint
cd frontend && npm run lint

# Fix automatically
cd frontend && npm run lint:fix

# Type checking
cd frontend && npm run type-check
```

### Formatting

```bash
# Backend
black src tests --line-length 120

# Frontend
cd frontend && npm run format

# Check formatting without changes
black src tests --check
cd frontend && npm run format:check
```

## Git Commands

### Branch Management
```bash
# Create feature branch
git checkout -b feature/new-feature

# Create from specific branch
git checkout -b feature/new-feature origin/develop

# List branches
git branch -a

# Delete local branch
git branch -d feature/old-feature

# Delete remote branch
git push origin --delete feature/old-feature
```

### Committing
```bash
# Stage changes
git add .
git add -p  # Interactive staging

# Commit with message
git commit -m "feat: Add project creation endpoint"

# Amend last commit
git commit --amend

# Interactive rebase
git rebase -i HEAD~3
```

### Pull Requests
```bash
# Push branch
git push -u origin feature/new-feature

# Create PR using GitHub CLI
gh pr create --title "Add project creation" --body "Description"

# List PRs
gh pr list

# Check out PR
gh pr checkout 123
```

## Build & Deployment Commands

### Docker Commands
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Clean up
docker-compose down -v  # Remove volumes
docker system prune    # Remove unused resources
```

### Production Build
```bash
# Backend
python setup.py bdist_wheel

# Frontend
cd frontend && npm run build

# Build all
make build
```

### Deployment
```bash
# Deploy to staging
make deploy-staging

# Deploy to production
make deploy-production

# Rollback
make rollback VERSION=1.2.3
```

## Database Management

### Backup & Restore
```bash
# Backup database
python -m src.scripts.backup_db --output backups/

# Restore database
python -m src.scripts.restore_db --input backups/backup-2025-01-11.sql

# Export data
python -m src.scripts.export_data --format json --output data.json

# Import data
python -m src.scripts.import_data --input data.json
```

### Maintenance
```bash
# Vacuum database (SQLite)
sqlite3 orchestrator.db "VACUUM;"

# Analyze query performance
python -m src.scripts.analyze_queries

# Clean old data
python -m src.scripts.cleanup --days 90
```

## Monitoring Commands

### Logs
```bash
# View application logs
tail -f logs/app.log

# View error logs
grep ERROR logs/app.log

# View logs by date
grep "2025-01-11" logs/app.log

# Follow logs with filtering
tail -f logs/app.log | grep -E "(ERROR|CRITICAL)"
```

### Performance
```bash
# Profile backend
python -m cProfile -o profile.stats src.main

# Analyze profile
python -m pstats profile.stats

# Memory profiling
python -m memory_profiler src.main

# Load testing
locust -f tests/load/locustfile.py --host http://localhost:8000
```

## Utility Commands

### Project Management
```bash
# Update dependencies
pip install --upgrade -r requirements.txt
cd frontend && npm update

# Check for outdated packages
pip list --outdated
cd frontend && npm outdated

# Security audit
pip-audit
cd frontend && npm audit

# Fix vulnerabilities
cd frontend && npm audit fix
```

### Documentation
```bash
# Generate API docs
python -m src.scripts.generate_api_docs

# Serve documentation
mkdocs serve

# Build documentation
mkdocs build

# Generate changelog
git-changelog -o CHANGELOG.md
```

## AI Development Commands

### Agent Testing
```bash
# Test planner agent
python -m src.scripts.test_agent --agent planner --prompt "Build a todo app"

# Test with specific provider
python -m src.scripts.test_agent --provider anthropic --model claude-3

# Benchmark agents
python -m src.scripts.benchmark_agents
```

### Prompt Management
```bash
# Validate prompts
python -m src.scripts.validate_prompts

# Test prompt variations
python -m src.scripts.test_prompts --iterations 10

# Export prompts
python -m src.scripts.export_prompts --format yaml
```

## Makefile Shortcuts

```makefile
# Common shortcuts
make install      # Install all dependencies
make test         # Run all tests
make lint         # Run all linters
make format       # Format all code
make build        # Build for production
make clean        # Clean build artifacts

# Development
make dev          # Start development servers
make shell        # Python shell with context
make db-shell     # Database shell

# Deployment
make deploy       # Deploy to production
make staging      # Deploy to staging
make rollback     # Rollback deployment
```

## Environment Variables

### Required Variables
```bash
# Backend
export DATABASE_URL="sqlite:///./orchestrator.db"
export AI_PROVIDER="openai"
export AI_API_KEY="sk-..."

# Frontend
export VITE_API_URL="http://localhost:8000"
export VITE_WS_URL="ws://localhost:8000"
```

### Development Overrides
```bash
# Enable debug mode
export DEBUG=true
export LOG_LEVEL=DEBUG

# Use test database
export DATABASE_URL="sqlite:///./test.db"

# Mock external services
export MOCK_AI_RESPONSES=true
```

## Troubleshooting Commands

### Debug Issues
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Check installed packages
pip freeze

# Verify imports
python -c "import src.models; print(src.models.__file__)"

# Test database connection
python -m src.scripts.test_connection
```

### Reset Environment
```bash
# Full reset
make clean
rm -rf venv node_modules
python -m venv venv
source venv/bin/activate
make install
```

## CI/CD Commands

### GitHub Actions
```bash
# Run workflow locally
act -j test

# Run specific job
act -j backend-tests

# List workflows
gh workflow list

# View workflow runs
gh run list
```

### Pre-commit Hooks
```bash
# Install hooks
pre-commit install

# Run manually
pre-commit run --all-files

# Update hooks
pre-commit autoupdate

# Skip hooks
git commit --no-verify
```

## Related Documentation

- [Development Setup](../development/setup.md)
- [Testing Guide](../testing/overview.md)
- [Deployment Guide](../deployment/guide.md)
- [CLAUDE.md](../../CLAUDE.md) - Workflow commands