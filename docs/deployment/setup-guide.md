# Development Environment Setup Guide

This guide helps new developers set up the Orchestrator project environment correctly using the DEL-007 validation and setup scripts.

## Quick Start (5 minutes)

### 1. Prerequisites

- **Python 3.8+** - Download from [python.org](https://python.org)
- **Node.js 16+** - Download from [nodejs.org](https://nodejs.org)
- **Git** - For cloning the repository

### 2. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd databricks_orchestrator

# Run automated setup
python scripts/setup_development.py --no-interactive

# Or run interactive setup (recommended for first time)
python scripts/setup_development.py
```

### 3. Verify Installation

```bash
# Validate environment
python scripts/validate_environment.py

# Start development servers
npm run start:dev
```

That's it! The application should be running at:
- Frontend: http://localhost:5174
- Backend API: http://localhost:8000

## Detailed Setup Process

### Environment Validation

Before setting up, you can validate your environment:

```bash
# Check current environment
python scripts/validate_environment.py

# Check specific environment
python scripts/validate_environment.py --environment production

# Get JSON output for automation
python scripts/validate_environment.py --json

# Check all environments
python scripts/validate_environment.py --all
```

### Development Setup

The setup script automates:

1. **Dependency Installation**
   - Python packages from `backend/requirements.txt`
   - Node.js packages from `package.json` and `frontend/package.json`

2. **Environment Configuration**
   - Creates `.env.development`, `.env.staging`, `.env.production`
   - Creates `.env.local` for your personal API keys
   - Sets up appropriate defaults

3. **Database Initialization**
   - Configures SQLite database for development
   - Sets up database URL in environment files

4. **API Key Setup** (Interactive mode)
   - Prompts for AI provider API keys
   - Stores them securely in `.env.local`

### Setup Options

```bash
# Interactive setup with prompts
python scripts/setup_development.py

# Automated setup (no prompts)
python scripts/setup_development.py --no-interactive

# Skip test verification
python scripts/setup_development.py --skip-tests

# Setup for specific environment
python scripts/setup_development.py --environment staging

# JSON output for automation
python scripts/setup_development.py --json
```

## Environment Configuration

### Environment Files

The project uses layered environment configuration:

- **`.env.defaults`** - Shared defaults (committed)
- **`.env.development`** - Development settings (committed)
- **`.env.staging`** - Staging settings (committed)
- **`.env.production`** - Production settings (committed)
- **`.env.local`** - Your personal secrets (git-ignored)
- **`.env.example`** - Template for new developers

### API Keys

Configure at least one AI provider API key in `.env.local`:

```bash
# Anthropic Claude (recommended)
ANTHROPIC_API_KEY=sk-ant-your-key-here

# OpenAI GPT
OPENAI_API_KEY=sk-your-openai-key-here

# Google Gemini
GEMINI_API_KEY=your-gemini-key-here

# xAI Grok
XAI_API_KEY=xai-your-key-here
```

Get API keys from:
- [Anthropic Console](https://console.anthropic.com)
- [OpenAI Platform](https://platform.openai.com)
- [Google AI Studio](https://makersuite.google.com)
- [xAI Platform](https://x.ai)

### Database Configuration

**Development** (default):
```bash
DATABASE_URL=sqlite:///orchestrator_dev.db
```

**Production** (PostgreSQL recommended):
```bash
DATABASE_URL=postgresql://username:password@host:port/database
```

## Running the Application

### Development Mode

```bash
# Start both backend and frontend
npm run start:dev

# Or start individually
npm run start:backend:dev    # Backend only (port 8000)
npm run start:frontend:dev   # Frontend only (port 5174)
```

### Other Environments

```bash
# Staging environment
npm run start:staging        # Ports 8001/5175

# Production environment  
npm run start:prod          # Ports 8002/5176
```

### Testing

```bash
# Run all tests
npm run test:all

# Backend tests only
cd backend && pytest

# Frontend tests only
cd frontend && npm test

# Run with coverage
cd backend && pytest --cov=src
cd frontend && npm run test:coverage
```

## Troubleshooting

### Common Issues

**1. Python version too old**
```bash
# Error: Python 3.7 found, but 3.8+ required
# Solution: Install Python 3.8+ from python.org
```

**2. Node.js not found**
```bash
# Error: Node.js is not installed or not in PATH
# Solution: Install Node.js 16+ from nodejs.org
```

**3. Missing API keys**
```bash
# Warning: No AI provider API keys configured
# Solution: Add API keys to .env.local file
```

**4. Database connection failed**
```bash
# Error: Cannot connect to SQLite database
# Solution: Check database directory permissions
```

**5. Port already in use**
```bash
# Error: Port 8000 already in use
# Solution: Stop other services or change port in .env file
```

### Validation Errors

Run validation to diagnose issues:

```bash
# Get detailed validation report
python scripts/validate_environment.py

# Check specific environment
python scripts/validate_environment.py --environment production
```

### Reset Development Environment

```bash
# Reset development database
rm orchestrator_dev.db

# Clean and reinstall dependencies
rm -rf node_modules frontend/node_modules
rm -rf backend/.venv
python scripts/setup_development.py
```

### Get Help

1. **Run validation**: `python scripts/validate_environment.py`
2. **Check logs**: Application logs will show detailed error information
3. **Re-run setup**: `python scripts/setup_development.py`
4. **Check documentation**: See other files in `docs/` directory

## Advanced Configuration

### Custom Environment

Create custom environment files:

```bash
# Create .env.custom
ENVIRONMENT=custom
DATABASE_URL=sqlite:///orchestrator_custom.db
API_PORT=8003
FRONTEND_PORT=5177

# Use custom environment
python scripts/validate_environment.py --environment custom
```

### Development with Docker

```bash
# Coming in Phase 3 (DEL-012)
# Will include Docker containerization
```

### Production Deployment

```bash
# Coming in Phase 3 (DEL-015)
# Will include CI/CD pipeline and production automation
```

## Performance

The setup and validation scripts are optimized for speed:

- **Environment validation**: < 5 seconds
- **Complete setup**: < 60 seconds (excluding downloads)
- **Minimal memory usage**: < 50MB additional

## Security

- API keys are stored in `.env.local` (git-ignored)
- No secrets are logged or exposed in error messages
- Input sanitization prevents injection attacks
- File permissions are properly validated

## Next Steps

After successful setup:

1. **Explore the codebase**:
   - Backend: `backend/src/`
   - Frontend: `frontend/src/`
   - Documentation: `docs/`

2. **Run tests** to verify everything works
3. **Start development** with your favorite IDE
4. **Check out the architecture docs** in `docs/architecture/`

## Support

If you encounter issues not covered here:

1. Check existing issues in the project repository
2. Run `python scripts/validate_environment.py` for diagnostics
3. Create a new issue with validation output and error details