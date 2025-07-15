# Deployment Guide

*Last Updated: 2025-07-15*

A comprehensive guide for deploying the Orchestrator across development, staging, and production environments using the modern npm script workflow.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Environment Architecture](#environment-architecture)
- [Quick Setup](#quick-setup)
- [Manual Setup](#manual-setup)
- [Environment Configuration](#environment-configuration)
- [API Provider Setup](#api-provider-setup)
- [Database Management](#database-management)
- [Service Coordination](#service-coordination)
- [Development Workflow](#development-workflow)
- [Production Deployment](#production-deployment)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Backup & Recovery](#backup--recovery)
- [Security Best Practices](#security-best-practices)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)

## Overview

The Orchestrator uses a modern npm script-based deployment system with multi-environment isolation. Each environment (development, staging, production) runs independently with separate databases, ports, and configurations.

### Architecture Highlights

- **Service Coordination**: npm-run-all for parallel service management
- **Environment Isolation**: Separate databases and ports per environment
- **Configuration Management**: Layered environment files with secret protection
- **Health Monitoring**: Built-in health checks and validation
- **Database Management**: Automated backup, restore, and migration support

## Prerequisites

### System Requirements

- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **Git** for version control
- **SQLite 3** (included with Python)
- **PostgreSQL 13+** (production recommended)

### Development Tools

```bash
# Verify prerequisites
python --version   # Should be 3.8+
node --version     # Should be 16+
git --version      # Any recent version
sqlite3 --version  # Should be 3.x+
```

### Required Dependencies

The setup script automatically installs:

**Backend (Python)**:
- FastAPI, SQLAlchemy, Pydantic
- AI provider SDKs (OpenAI, Anthropic, etc.)
- Testing and validation tools

**Frontend (TypeScript)**:
- React 18, Vite, TypeScript
- Tailwind CSS, React Testing Library

**Development Tools**:
- npm-run-all, cross-env, wait-on
- dotenv-cli for environment management

## Environment Architecture

### Multi-Environment Isolation

The system supports three isolated environments:

| Environment | Backend Port | Frontend Port | Database | Configuration |
|-------------|--------------|---------------|----------|---------------|
| **Development** | 8000 | 5174 | `orchestrator_dev.db` | `.env.development` |
| **Staging** | 8001 | 5175 | `orchestrator_staging.db` | `.env.staging` |
| **Production** | 8002 | 5176 | `orchestrator_prod.db` | `.env.production` |

### Service Coordination

Each environment runs coordinated services:

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │
│   React + Vite  │◄──►│   FastAPI       │
│   Port 5174     │    │   Port 8000     │
└─────────────────┘    └─────────────────┘
         │                       │
         └───────────────────────┘
                   │
         ┌─────────────────┐
         │   Database      │
         │   SQLite/       │
         │   PostgreSQL    │
         └─────────────────┘
```

## Quick Setup

### Automated Setup (Recommended)

```bash
# Clone and enter project
git clone <repository-url>
cd databricks_orchestrator

# Run automated setup
python scripts/setup_development.py

# Validate environment
python scripts/validate_environment.py

# Start development environment
npm run start:dev
```

**Success Indicators**:
- Frontend accessible at http://localhost:5174
- Backend API docs at http://localhost:8000/api/docs  
- Health check returns `{"status": "healthy"}` at http://localhost:8000/health

### Setup Options

```bash
# Interactive setup with prompts
python scripts/setup_development.py

# Non-interactive setup
python scripts/setup_development.py --no-interactive

# Setup specific environment
python scripts/setup_development.py --environment staging

# Skip test verification
python scripts/setup_development.py --skip-tests
```

## Manual Setup

### Backend Setup

```bash
# Create and activate virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import fastapi; print('FastAPI installed')"
```

### Frontend Setup

```bash
# Install dependencies
cd frontend
npm install

# Verify installation
npm run build --dry-run
```

### Root Dependencies

```bash
# Install coordination tools
npm install

# Verify npm scripts
npm run --silent
```

## Environment Configuration

### Configuration Architecture

The system uses layered configuration files:

```
.env.defaults       # Shared defaults (committed)
    ↓ overridden by
.env.development    # Development settings (committed)  
    ↓ overridden by
.env.local         # Personal secrets (git-ignored)
```

### Environment Files

#### `.env.defaults` (Shared Settings)
```bash
# Application
APP_NAME=orchestrator
VERSION=1.0.0

# Logging
LOG_LEVEL=INFO

# API Settings
API_HOST=0.0.0.0

# Frontend
VITE_APP_NAME=Orchestrator
```

#### `.env.development` (Development)
```bash
# Environment
ENVIRONMENT=development
DEBUG=true

# Services
API_PORT=8000
FRONTEND_PORT=5174

# Database
DATABASE_URL=sqlite:///orchestrator_dev.db

# Development Features
RELOAD=true
HOT_RELOAD=true
```

#### `.env.staging` (Staging)
```bash
# Environment  
ENVIRONMENT=staging
DEBUG=false

# Services
API_PORT=8001
FRONTEND_PORT=5175

# Database
DATABASE_URL=sqlite:///orchestrator_staging.db

# Staging Features
RELOAD=false
BACKUP_ENABLED=true
```

#### `.env.production` (Production)
```bash
# Environment
ENVIRONMENT=production
DEBUG=false

# Services
API_PORT=8002
FRONTEND_PORT=5176

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/orchestrator

# Production Features
RELOAD=false
BACKUP_ENABLED=true
LOG_LEVEL=WARNING
```

#### `.env.local` (Secrets)
```bash
# AI Provider API Keys (configure at least one)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
GEMINI_API_KEY=your-gemini-key-here
XAI_API_KEY=xai-your-key-here

# Production Database (if using PostgreSQL)
DATABASE_URL=postgresql://user:secure_password@host:port/database

# Optional: Override any defaults
# LOG_LEVEL=DEBUG
```

### Configuration Loading

Environment variables are loaded in this order:
1. System environment variables
2. `.env.local` (highest priority)
3. `.env.{environment}` 
4. `.env.defaults` (lowest priority)

## API Provider Setup

### Supported Providers

The system supports multiple AI providers:

- **Anthropic Claude** (recommended)
- **OpenAI GPT**
- **Google Gemini**  
- **xAI Grok**

### API Key Configuration

#### Interactive Setup
```bash
# Run setup with API key configuration
python scripts/setup_development.py

# Follow prompts to configure providers
```

#### Manual Configuration
```bash
# Edit .env.local file
nano .env.local

# Add your API keys
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
```

### Getting API Keys

| Provider | URL | Key Format |
|----------|-----|------------|
| **Anthropic** | https://console.anthropic.com | `sk-ant-*` |
| **OpenAI** | https://platform.openai.com | `sk-*` |
| **Google** | https://makersuite.google.com | Various formats |
| **xAI** | https://x.ai | `xai-*` |

### Validation

```bash
# Validate API key configuration
python scripts/validate_environment.py

# Test specific provider
python -c "
from backend.src.config.settings import Settings
settings = Settings()
print(f'Anthropic key configured: {bool(settings.anthropic_api_key)}')
"
```

## Database Management

### SQLite (Development/Staging)

#### Database Files
- Development: `orchestrator_dev.db`
- Staging: `orchestrator_staging.db`
- Production: `orchestrator_prod.db`

#### Basic Operations
```bash
# Check database
sqlite3 orchestrator_dev.db ".tables"

# Database size
ls -lh *.db
```

### PostgreSQL (Production)

#### Setup
```sql
-- Create database and user
CREATE DATABASE orchestrator;
CREATE USER orchestrator_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE orchestrator TO orchestrator_user;

-- Performance optimization
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
```

#### Configuration
```bash
# Update .env.production or .env.local
DATABASE_URL=postgresql://orchestrator_user:secure_password@localhost:5432/orchestrator
```

### Database Scripts

```bash
# Backup production database
npm run db:backup

# Copy production data to staging
npm run db:copy-prod-to-staging

# Reset development database
npm run db:reset-dev
```

#### Backup Features
- Timestamped backups in `backups/` directory
- Automatic retention (keeps last 10 backups)
- Size reporting and verification
- Cross-environment data copying

## Service Coordination

### npm Script Architecture

The system uses npm-run-all for service coordination:

```bash
# Full stack development
npm run start:dev
# Runs: backend:dev + frontend:dev in parallel

# Backend only
npm run backend:dev
# Loads environment + starts FastAPI with reload

# Frontend only  
npm run frontend:dev
# Starts Vite dev server with hot reload
```

### Service Dependencies

Services start with dependency management:

```bash
# Health check coordination
npm run services:health
# Waits for: backend health + frontend ready

# Custom coordination
wait-on http://localhost:8000/health && echo "Backend ready"
wait-on http://localhost:5174 && echo "Frontend ready"
```

### Process Management

#### Development (Auto-restart)
```bash
# Backend: uvicorn with --reload
# Frontend: Vite with hot module replacement
npm run start:dev
```

#### Production (Stable)
```bash
# Backend: uvicorn without reload
# Frontend: Built static files
npm run start:prod
```

### Environment Switching

```bash
# Switch between environments instantly
npm run start:dev      # Development (8000/5174)
npm run start:staging  # Staging (8001/5175)  
npm run start:prod     # Production (8002/5176)

# Run multiple environments simultaneously
npm run start:dev &
npm run start:staging &
# Each uses different ports and databases
```

## Development Workflow

### Daily Development

```bash
# Start development environment
npm run start:dev

# In separate terminals:
# Run tests continuously
npm run test:all

# Code quality checks
npm run lint:all

# Database operations
npm run db:reset-dev  # Reset dev database
```

### Code Quality

```bash
# Backend linting and formatting
cd backend
black .                # Format Python code
mypy .                 # Type checking
pytest --cov=src       # Tests with coverage

# Frontend linting and formatting  
cd frontend
npm run lint:fix       # ESLint fixes
npm run format         # Prettier formatting
npm test               # Vitest tests
```

### Testing

```bash
# Run all tests
npm run test:all

# Individual test suites
npm run test:backend   # Python tests
npm run test:frontend  # TypeScript tests

# With coverage
cd backend && pytest --cov=src --cov-report=html
cd frontend && npm run test:coverage
```

## Production Deployment

### Production Environment Setup

#### Prerequisites
- PostgreSQL database server
- Reverse proxy (nginx recommended)
- SSL certificates
- Process supervisor (systemd recommended)

#### Environment Configuration
```bash
# Create production environment file
cp .env.example .env.production

# Edit production settings
nano .env.production

# Configure production database
DATABASE_URL=postgresql://user:password@host:5432/orchestrator
ENVIRONMENT=production
DEBUG=false
```

#### Database Setup
```bash
# Run production database migrations
export DATABASE_URL=postgresql://user:password@host:5432/orchestrator
cd backend
alembic upgrade head
```

### Production Deployment Process

#### 1. Build Frontend
```bash
cd frontend
npm run build
# Creates optimized build in dist/
```

#### 2. Configure Backend
```bash
# Install production dependencies
cd backend
pip install gunicorn uvloop httptools

# Test production server
gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

#### 3. Process Management

##### Systemd Service
```ini
# /etc/systemd/system/orchestrator-backend.service
[Unit]
Description=Orchestrator Backend API
After=network.target

[Service]
Type=notify
User=orchestrator
Group=orchestrator
WorkingDirectory=/opt/orchestrator/backend
Environment="PATH=/opt/orchestrator/venv/bin"
EnvironmentFile=/opt/orchestrator/.env.production
ExecStart=/opt/orchestrator/venv/bin/gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind unix:/tmp/orchestrator.sock
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. Reverse Proxy

##### Nginx Configuration
```nginx
# /etc/nginx/sites-available/orchestrator
server {
    listen 80;
    server_name orchestrator.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name orchestrator.example.com;
    
    ssl_certificate /etc/ssl/certs/orchestrator.crt;
    ssl_certificate_key /etc/ssl/private/orchestrator.key;
    
    # Frontend static files
    location / {
        root /opt/orchestrator/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # Backend API
    location /api {
        proxy_pass http://unix:/tmp/orchestrator.sock;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # AI request timeouts
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }
    
    # Health check
    location /health {
        proxy_pass http://unix:/tmp/orchestrator.sock;
        access_log off;
    }
}
```

### Production Startup

```bash
# Start backend service
sudo systemctl start orchestrator-backend
sudo systemctl enable orchestrator-backend

# Verify backend health
curl http://localhost/health

# Start nginx
sudo systemctl start nginx
sudo systemctl enable nginx

# Verify full stack
curl https://orchestrator.example.com/health
```

## Monitoring & Health Checks

### Health Check Endpoints

#### Backend Health
```bash
# Basic health check
curl http://localhost:8000/health

# Response:
{
  "status": "healthy",
  "timestamp": "2025-07-15T06:42:05Z",
  "checks": {
    "database": true,
    "ai_providers": true
  }
}
```

#### Detailed Health
```bash
# Detailed health information
curl http://localhost:8000/health?detailed=true

# Response includes:
# - Database connection status
# - AI provider connectivity
# - System resource usage
# - Service uptime
```

### Service Monitoring

#### Health Check Scripts
```bash
# Check all services
npm run services:health

# Individual service checks
wait-on http://localhost:8000/health
wait-on http://localhost:5174
```

#### Monitoring Commands
```bash
# Service status
ps aux | grep -E "(uvicorn|node)"

# Port usage
netstat -tlnp | grep -E "(8000|5174)"

# Log monitoring
tail -f backend/logs/app.log
```

### Performance Monitoring

#### Backend Metrics
```bash
# Request stats
curl http://localhost:8000/metrics

# Database performance
sqlite3 orchestrator_dev.db ".stats"

# Memory usage
ps -o pid,vsz,rss,comm -p $(pgrep uvicorn)
```

## Backup & Recovery

### Automated Backup System

The built-in backup system provides:

```bash
# Backup production database
npm run db:backup

# Features:
# - Timestamped backups: backups/orchestrator_prod_backup_20250715_064205.db
# - Automatic retention (keeps last 10)
# - Size reporting and verification
# - Backup integrity checking
```

### Backup Scripts

#### Production Backup
```bash
#!/bin/bash
# ./scripts/backup-prod.sh

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="backups"
SOURCE_DB="backend/orchestrator_prod.db"
BACKUP_FILE="${BACKUP_DIR}/orchestrator_prod_backup_${TIMESTAMP}.db"

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Create backup
cp "$SOURCE_DB" "$BACKUP_FILE"

# Verify backup
sqlite3 "$BACKUP_FILE" "PRAGMA integrity_check;"

# Report
echo "Backup created: $BACKUP_FILE"
ls -lh "$BACKUP_FILE"
```

### Environment Data Management

```bash
# Copy production to staging
npm run db:copy-prod-to-staging

# Reset development database  
npm run db:reset-dev

# Manual backup
cp orchestrator_prod.db "backup_$(date +%Y%m%d).db"
```

### Disaster Recovery

#### Recovery Procedure
1. **Identify backup**: List available backups
2. **Stop services**: Stop all running services
3. **Restore database**: Copy backup to production location
4. **Verify integrity**: Check database integrity
5. **Restart services**: Start services and verify
6. **Health check**: Confirm full system health

```bash
# Recovery example
sudo systemctl stop orchestrator-backend
cp backups/orchestrator_prod_backup_20250715_064205.db orchestrator_prod.db
sqlite3 orchestrator_prod.db "PRAGMA integrity_check;"
sudo systemctl start orchestrator-backend
curl http://localhost/health
```

## Security Best Practices

### API Key Security

#### Storage
- Store keys in `.env.local` (git-ignored)
- Never commit API keys to version control
- Use environment-specific keys
- Rotate keys regularly

#### Validation
```bash
# Validate key configuration
python scripts/validate_environment.py

# Check for exposed secrets
git log --all -p | grep -i "api.*key"  # Should find nothing
```

### Environment Security

#### File Permissions
```bash
# Secure environment files
chmod 600 .env.local
chmod 644 .env.development .env.staging .env.production
```

#### Secret Management
```bash
# Check git ignore
cat .gitignore | grep -E "\.env\.local"

# Verify no secrets in git
git ls-files | xargs grep -l "sk-" || echo "No secrets found"
```

### Network Security

#### Firewall Configuration
```bash
# Allow only necessary ports
sudo ufw allow 22    # SSH
sudo ufw allow 80    # HTTP
sudo ufw allow 443   # HTTPS
sudo ufw deny 8000   # Block direct backend access
```

#### SSL/TLS
```bash
# Generate certificates with Let's Encrypt
certbot --nginx -d orchestrator.example.com

# Verify SSL configuration
curl -I https://orchestrator.example.com
```

### Input Validation

The backend implements comprehensive input validation:
- Request payload validation with Pydantic
- SQL injection prevention with SQLAlchemy
- XSS protection with input sanitization
- Rate limiting on API endpoints

## Performance Optimization

### Backend Performance

#### Database Optimization
```bash
# SQLite optimization
sqlite3 orchestrator_prod.db "PRAGMA optimize;"

# PostgreSQL optimization (production)
psql -d orchestrator -c "VACUUM ANALYZE;"
```

#### Service Configuration
```bash
# Production backend with optimal workers
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --max-requests 1000 \
  --max-requests-jitter 50 \
  --timeout 300 \
  --keep-alive 5
```

### Frontend Performance

#### Build Optimization
```bash
cd frontend

# Production build with optimization
npm run build

# Analyze bundle size
npm run build -- --analyze

# Serve optimized build
npm run preview
```

#### Asset Optimization
- Code splitting with Vite
- Tree shaking for unused code
- Asset minification and compression
- CDN-ready static assets

### System Performance

#### Resource Monitoring
```bash
# Memory usage
free -h

# CPU usage
top -p $(pgrep -d',' uvicorn)

# Disk I/O
iostat -x 1 5

# Network
netstat -i
```

#### Performance Benchmarks
- **Backend startup**: < 3 seconds
- **Frontend build**: < 30 seconds
- **API response time**: < 100ms (typical)
- **Database queries**: < 50ms (SQLite)
- **Health checks**: < 50ms

## Troubleshooting

### Common Issues

#### Setup Problems
```bash
# Python version too old
python --version  # Must be 3.8+
# Solution: Install Python 3.8+ from python.org

# Node.js not found
node --version  # Must be 16+
# Solution: Install Node.js 16+ from nodejs.org

# Permission errors
# Solution: Check file permissions and user access
```

#### Service Issues
```bash
# Port already in use
netstat -tlnp | grep 8000
# Solution: Kill process or use different environment

# Database locked
# Solution: Stop all services, remove .db-wal files

# API key validation failed
python scripts/validate_environment.py
# Solution: Check .env.local configuration
```

#### Performance Issues
```bash
# High memory usage
ps aux --sort=-%mem | head

# Slow database queries
sqlite3 orchestrator_dev.db "PRAGMA stats;"

# Frontend build failures
cd frontend && npm run build --verbose
```

### Diagnostic Tools

```bash
# Environment validation
python scripts/validate_environment.py --json

# Service health
curl http://localhost:8000/health?detailed=true

# Log analysis  
tail -f backend/logs/app.log | grep ERROR

# Network debugging
curl -v http://localhost:8000/health
```

### Getting Help

1. **Run validation**: `python scripts/validate_environment.py`
2. **Check logs**: Review application and error logs
3. **Health checks**: Verify all services are healthy
4. **Documentation**: See [Troubleshooting Guide](troubleshooting.md)
5. **Issues**: Create GitHub issue with validation output

## Related Documentation

- [Quick Start Guide](quick-start.md) - 5-minute setup guide
- [Troubleshooting Guide](troubleshooting.md) - Common issues and solutions
- [Architecture Overview](../architecture/overview.md) - System architecture
- [API Documentation](../api/README.md) - API reference
- [Testing Documentation](../testing.md) - Testing strategies

---

*This deployment guide reflects the actual implementation using npm scripts, environment isolation, and validation tooling. No Docker or Kubernetes knowledge required.*