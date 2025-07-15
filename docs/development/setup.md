# Development Setup Guide

*For the most up-to-date setup instructions, see the [Quick Start Guide](../deployment/quick-start.md) or [Complete Setup Guide](../deployment/setup-guide.md).*

## Quick Setup (5 minutes)

For the fastest setup experience, use the automated scripts:

```bash
# Clone repository
git clone <repository-url>
cd databricks_orchestrator

# Run automated setup
python scripts/setup_development.py

# Start development environment
npm run start:dev
```

**Complete instructions**: [Quick Start Guide (5 min)](../deployment/quick-start.md)

## Development Workflow

### Environment Management

The project supports three isolated environments:

| Environment | Ports | Database | Use Case |
|-------------|-------|----------|----------|
| Development | 8000/5174 | `orchestrator_dev.db` | Active development |
| Staging | 8001/5175 | `orchestrator_staging.db` | Testing builds |
| Production | 8002/5176 | `orchestrator_prod.db` | Stable usage |

```bash
# Start different environments
npm run start:dev      # Development with hot-reload
npm run start:staging  # Staging environment  
npm run start:prod     # Production environment

# Run multiple environments simultaneously
npm run start:dev &
npm run start:staging &
```

**Complete setup instructions**: [Development Setup Guide](../deployment/setup-guide.md)

### Code Quality Tools

#### Backend
```bash
# Format and check code
black .                         # Format Python code
mypy .                          # Type checking
cd backend && pytest            # Run tests

# Or use root-level commands
npm run lint:backend            # Format + type check
npm run test:backend           # Run backend tests
```

#### Frontend
```bash
# Format and check code
cd frontend
npm run format                  # Prettier formatting
npm run lint                    # ESLint linting
npm test                       # Run tests

# Or use root-level commands
npm run lint:frontend          # Format + lint
npm run test:frontend         # Run frontend tests
```

#### All-in-One Commands
```bash
# From project root
npm run test:all               # Run all tests
npm run lint:all               # Lint all code
```

### Database Management

```bash
# Environment-specific database operations
npm run db:reset-dev           # Reset development database
npm run db:backup              # Backup production database
npm run db:copy-prod-to-staging # Copy prod data to staging
```

### Testing

```bash
# Backend testing (run from backend directory)
cd backend && pytest                    # All tests
cd backend && pytest --cov=src         # With coverage
cd backend && pytest tests/test_api/   # Specific directory

# Frontend testing
cd frontend && npm test                 # All tests
cd frontend && npm run test:watch      # Watch mode
cd frontend && npm run test:coverage   # With coverage

# Full stack testing (from root)
npm run test:all                       # All backend + frontend tests
```

**Complete testing guide**: [Testing Documentation](../testing.md)

## IDE Configuration

### VS Code Recommended Extensions

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance", 
    "ms-python.black-formatter",
    "dbaeumer.vscode-eslint",
    "esbenp.prettier-vscode",
    "bradlc.vscode-tailwindcss"
  ]
}
```

### VS Code Settings

```json
{
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Troubleshooting

For common issues and solutions:

- **Setup Problems**: [Troubleshooting Guide](../deployment/troubleshooting.md)
- **Environment Issues**: Run `python scripts/validate_environment.py`
- **Service Issues**: Check [health endpoints](../deployment/guide.md#monitoring--health-checks)
- **Test Issues**: See [Testing Troubleshooting](../testing.md#troubleshooting-guide)

## Related Documentation

### Setup & Deployment
- [Quick Start Guide (5 min)](../deployment/quick-start.md) - Get running fast
- [Complete Deployment Guide](../deployment/guide.md) - Comprehensive instructions
- [Development Setup Guide](../deployment/setup-guide.md) - Detailed development setup
- [Troubleshooting Guide](../deployment/troubleshooting.md) - Common issues

### Development
- [Testing Documentation](../testing.md) - Testing strategies and patterns
- [Architecture Overview](../architecture/overview.md) - System architecture
- [API Documentation](../api/README.md) - API reference

### Project Management
- [Current Tasks](../../PROJECT.md) - Active development tasks and sprint focus
- [MVP Overview](../planning/mvp-overview.md) - Product roadmap