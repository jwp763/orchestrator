# Quick Start Guide (5 Minutes)

Get the Orchestrator running in under 5 minutes with automated setup and validation.

## Prerequisites

Verify you have the required tools:

```bash
# Check Python version (3.8+ required)
python --version

# Check Node.js version (16+ required)  
node --version

# Check Git
git --version
```

If any are missing:
- **Python 3.8+**: Download from [python.org](https://python.org)
- **Node.js 16+**: Download from [nodejs.org](https://nodejs.org)
- **Git**: Download from [git-scm.com](https://git-scm.com)

## 1. Clone and Setup (2 minutes)

```bash
# Clone the repository
git clone <repository-url>
cd databricks_orchestrator

# Run automated setup (installs dependencies, creates environment files)
python scripts/setup_development.py
```

The setup script will:
- ✅ Install Python and Node.js dependencies
- ✅ Create environment configuration files
- ✅ Setup development database
- ✅ Configure API keys (interactive prompts)

## 2. Validate Environment (30 seconds)

```bash
# Verify everything is configured correctly
python scripts/validate_environment.py
```

Expected output:
```
✅ VALID - Environment: development
Errors: 0, Warnings: 0
```

If you see errors, check the [Troubleshooting Guide](troubleshooting.md).

## 3. Start Development Environment (30 seconds)

```bash
# Start both backend and frontend services
npm run start:dev
```

You should see:
```
Backend starting on http://localhost:8000
Frontend starting on http://localhost:5174
Services are ready!
```

## 4. Verify Everything Works (1 minute)

Open these URLs in your browser:

| Service | URL | Expected |
|---------|-----|----------|
| **Frontend** | http://localhost:5174 | Orchestrator UI loads |
| **Backend API** | http://localhost:8000/api/docs | FastAPI documentation |
| **Health Check** | http://localhost:8000/health | `{"status": "healthy"}` |

## Success! 🎉

You now have a fully working development environment:

- **Frontend**: React app with hot reload at http://localhost:5174
- **Backend**: FastAPI server with auto-reload at http://localhost:8000  
- **Database**: SQLite development database (`orchestrator_dev.db`)
- **Environment**: Isolated development configuration

## Next Steps

### Daily Development
```bash
# Start development environment
npm run start:dev

# Run tests
npm run test:all

# Check code quality
npm run lint:all
```

### Multiple Environments
```bash
# Staging environment (ports 8001/5175)
npm run start:staging

# Production environment (ports 8002/5176)
npm run start:prod
```

### Database Management
```bash
# Backup production database
npm run db:backup

# Copy production data to staging
npm run db:copy-prod-to-staging

# Reset development database
npm run db:reset-dev
```

## Common Issues

**Setup fails?**
```bash
# Re-run with verbose output
python scripts/setup_development.py --interactive
```

**Validation fails?**
```bash
# Get detailed validation report
python scripts/validate_environment.py --json
```

**Port conflicts?**
- Development uses ports 8000/5174
- Staging uses ports 8001/5175  
- Production uses ports 8002/5176
- Stop other services or use different environments

**Need help?** See the [Troubleshooting Guide](troubleshooting.md) or [Complete Deployment Guide](guide.md).

---

**That's it!** You have a working Orchestrator development environment in under 5 minutes.