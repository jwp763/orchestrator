# Deployment Troubleshooting Guide

*Last Updated: 2025-07-15*

A comprehensive troubleshooting guide for common deployment and setup issues with the Orchestrator.

## Table of Contents

- [Quick Diagnostics](#quick-diagnostics)
- [Setup Issues](#setup-issues)
- [Environment Problems](#environment-problems)
- [Service Startup Issues](#service-startup-issues)
- [Database Problems](#database-problems)
- [API Provider Issues](#api-provider-issues)
- [Performance Problems](#performance-problems)
- [Network and Port Issues](#network-and-port-issues)
- [Development Workflow Issues](#development-workflow-issues)
- [Production Deployment Issues](#production-deployment-issues)
- [Advanced Diagnostics](#advanced-diagnostics)

## Quick Diagnostics

### Environment Validation

Always start with environment validation:

```bash
# Quick health check
python scripts/validate_environment.py

# Detailed validation
python scripts/validate_environment.py --json

# Check all environments
python scripts/validate_environment.py --all
```

### Service Health Check

```bash
# Check if services are running
curl http://localhost:8000/health      # Development
curl http://localhost:8001/health      # Staging  
curl http://localhost:8002/health      # Production

# Check ports in use
netstat -tlnp | grep -E "(8000|8001|8002|5174|5175|5176)"

# Check processes
ps aux | grep -E "(uvicorn|node|vite)"
```

### Common Quick Fixes

```bash
# Restart all services
npm run start:dev

# Reset development environment
npm run db:reset-dev

# Reinstall dependencies
npm run install:all

# Clear caches
rm -rf node_modules frontend/node_modules backend/.pytest_cache
```

## Setup Issues

### Python Version Problems

**Error**: `Python 3.7 found, but 3.8+ required`

**Solutions**:
```bash
# Check current version
python --version
python3 --version

# Install Python 3.8+ from python.org
# Then create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**Error**: `python command not found`

**Solutions**:
```bash
# On macOS with Homebrew
brew install python@3.11

# On Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# On Windows
# Download from python.org and add to PATH
```

### Node.js Version Problems

**Error**: `Node.js is not installed or not in PATH`

**Solutions**:
```bash
# Check if Node.js is installed
node --version
npm --version

# Install Node.js 16+ from nodejs.org
# Or using version managers:

# macOS/Linux with nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18

# Windows with nvm-windows
# Download from github.com/coreybutler/nvm-windows
```

**Error**: `npm command not found`

**Solutions**:
```bash
# Node.js installation should include npm
# If missing, reinstall Node.js

# Or install npm separately
curl -L https://www.npmjs.com/install.sh | sh
```

### Dependency Installation Issues

**Error**: `pip install failed` or `npm install failed`

**Solutions**:
```bash
# Backend dependency issues
cd backend
python -m pip install --upgrade pip
pip install -r requirements.txt --upgrade

# If still failing, try with --no-cache-dir
pip install -r requirements.txt --no-cache-dir

# Frontend dependency issues
cd frontend
rm -rf node_modules package-lock.json
npm install

# If npm registry issues, try different registry
npm install --registry https://registry.npmjs.org/
```

**Error**: `Permission denied` during installation

**Solutions**:
```bash
# Don't use sudo with pip (use virtual environment)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# For npm permission issues
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

## Environment Problems

### Environment File Issues

**Error**: `Environment variables not loaded`

**Symptoms**:
- API keys not found
- Wrong database URL
- Services start with wrong configuration

**Solutions**:
```bash
# Check if environment files exist
ls -la .env*

# Verify environment loading
python scripts/validate_environment.py --environment development

# Re-create environment files
python scripts/setup_development.py --no-interactive

# Manual environment file creation
cp .env.example .env.local
# Edit .env.local with your API keys
```

### Configuration Hierarchy Issues

The configuration loads in this order:
1. System environment variables (highest priority)
2. `.env.local`
3. `.env.{environment}`
4. `.env.defaults` (lowest priority)

**Debug configuration loading**:
```bash
# Check which variables are set
python -c "
from backend.src.config.settings import Settings
settings = Settings()
print(f'Environment: {settings.environment}')
print(f'Database URL: {settings.database_url}')
print(f'API Port: {settings.api_port}')
"
```

### API Key Configuration Issues

**Error**: `No AI provider API keys configured`

**Solutions**:
```bash
# Check current configuration
python scripts/validate_environment.py

# Add API keys to .env.local
cat >> .env.local << EOF
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-openai-key-here
EOF

# Test API key validation
python -c "
from backend.src.config.settings import Settings
settings = Settings()
print(f'Anthropic key: {bool(settings.anthropic_api_key)}')
print(f'OpenAI key: {bool(settings.openai_api_key)}')
"
```

## Service Startup Issues

### Backend Startup Problems

**Error**: `uvicorn: command not found`

**Solutions**:
```bash
# Ensure virtual environment is activated
cd backend
source venv/bin/activate

# Install uvicorn if missing
pip install uvicorn

# Check if uvicorn is installed
uvicorn --version
```

**Error**: `Address already in use` or `Port 8000 is already in use`

**Solutions**:
```bash
# Find process using the port
lsof -i :8000
netstat -tlnp | grep 8000

# Kill the process
kill $(lsof -ti:8000)

# Or use different port/environment
npm run start:staging  # Uses port 8001
npm run start:prod     # Uses port 8002
```

**Error**: `Database connection failed`

**Solutions**:
```bash
# Check database file permissions
ls -la orchestrator_*.db

# Check database directory permissions
ls -la backend/

# Reset database
rm orchestrator_dev.db
npm run start:dev  # Will recreate database
```

### Frontend Startup Problems

**Error**: `Vite dev server failed to start`

**Solutions**:
```bash
# Check if port is available
lsof -i :5174

# Clear Vite cache
cd frontend
rm -rf node_modules/.vite
npm run dev

# Try different port
npm run dev -- --port 5175
```

**Error**: `Cannot resolve dependencies`

**Solutions**:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install

# If peer dependency issues
npm install --legacy-peer-deps
```

### npm-run-all Coordination Issues

**Error**: Services start out of order or fail to coordinate

**Solutions**:
```bash
# Start services individually to debug
npm run backend:dev     # Start backend first
# Wait for backend to be ready, then:
npm run frontend:dev    # Start frontend

# Check if npm-run-all is installed
npm list npm-run-all

# Reinstall coordination tools
npm install npm-run-all cross-env wait-on --save-dev
```

## Database Problems

### SQLite Issues

**Error**: `database is locked`

**Symptoms**:
- Cannot write to database
- Database operations hang
- Multiple processes accessing same database

**Solutions**:
```bash
# Stop all services
pkill -f uvicorn
pkill -f vite

# Remove lock files
rm -f orchestrator_*.db-wal orchestrator_*.db-shm

# Restart services
npm run start:dev
```

**Error**: `no such table` errors

**Solutions**:
```bash
# Check if database exists and has tables
sqlite3 orchestrator_dev.db ".tables"

# If empty, database migrations may have failed
# Reset and recreate
rm orchestrator_dev.db
npm run start:dev
```

### Database Migration Issues

**Error**: `Table already exists` or migration failures

**Solutions**:
```bash
# Check current database schema
sqlite3 orchestrator_dev.db ".schema"

# Backup and reset development database
cp orchestrator_dev.db orchestrator_dev_backup.db
rm orchestrator_dev.db
npm run start:dev
```

### Database Permission Issues

**Error**: `Permission denied` when accessing database

**Solutions**:
```bash
# Check database file permissions
ls -la orchestrator_*.db

# Fix permissions
chmod 644 orchestrator_*.db
chmod 755 backend/  # Ensure directory is accessible
```

## API Provider Issues

### API Key Validation Failures

**Error**: `Invalid API key` or `Authentication failed`

**Solutions**:
```bash
# Test API key format
python -c "
import os
key = os.getenv('ANTHROPIC_API_KEY', '')
print(f'Key length: {len(key)}')
print(f'Key prefix: {key[:10]}...')
print(f'Key format OK: {key.startswith(\"sk-ant-\")}')
"

# Test API connectivity
curl -H "Authorization: Bearer $ANTHROPIC_API_KEY" \
     -H "Content-Type: application/json" \
     https://api.anthropic.com/v1/messages
```

### Provider Connection Issues

**Error**: `Connection timeout` or `Network error`

**Solutions**:
```bash
# Test network connectivity
curl -I https://api.anthropic.com
curl -I https://api.openai.com

# Check firewall/proxy settings
echo $HTTP_PROXY
echo $HTTPS_PROXY

# Test with different provider
# Add different API key in .env.local
```

## Performance Problems

### Slow Startup Times

**Symptoms**:
- Services take > 30 seconds to start
- High CPU/memory usage during startup

**Solutions**:
```bash
# Check system resources
free -h
df -h
top

# Reduce startup load
# Remove unnecessary dependencies
# Check for large log files

# Optimize database
sqlite3 orchestrator_dev.db "VACUUM; PRAGMA optimize;"
```

### High Memory Usage

**Solutions**:
```bash
# Monitor memory usage
ps aux --sort=-%mem | head -10

# Reduce backend workers in production
# Edit startup script to use fewer workers

# Clear caches
rm -rf backend/.pytest_cache
rm -rf frontend/node_modules/.vite
```

### Slow API Responses

**Solutions**:
```bash
# Check database performance
sqlite3 orchestrator_dev.db ".timer on" ".stats"

# Monitor API response times
curl -w "@curl-format.txt" http://localhost:8000/health

# Check for database lock issues
sqlite3 orchestrator_dev.db "PRAGMA wal_checkpoint;"
```

## Network and Port Issues

### Port Conflicts

**Error**: Multiple services trying to use same port

**Solutions**:
```bash
# Check all port usage
netstat -tlnp | grep -E "(8000|8001|8002|5174|5175|5176)"

# Kill conflicting processes
sudo lsof -ti:8000 | xargs kill -9

# Use different environments
npm run start:staging  # Different ports
```

### Firewall Issues

**Error**: Cannot access services from other machines

**Solutions**:
```bash
# Check if services are binding to all interfaces
netstat -tlnp | grep 0.0.0.0

# Allow ports through firewall (Ubuntu/Debian)
sudo ufw allow 8000
sudo ufw allow 5174

# macOS firewall
sudo pfctl -f /etc/pf.conf
```

### Frontend-Backend Connection Issues

**Error**: Frontend cannot reach backend API

**Solutions**:
```bash
# Check if backend is accessible
curl http://localhost:8000/health

# Verify frontend API configuration
cd frontend
grep -r "VITE_API_BASE_URL" .

# Check CORS configuration in backend
# Ensure frontend URL is in allowed origins
```

## Development Workflow Issues

### Hot Reload Not Working

**Backend hot reload issues**:
```bash
# Ensure --reload flag is used
# Check if uvicorn is detecting file changes
# Verify virtual environment is activated
cd backend
source venv/bin/activate
uvicorn src.main:app --reload
```

**Frontend hot reload issues**:
```bash
# Clear Vite cache
cd frontend
rm -rf node_modules/.vite

# Check if file watching is working
npm run dev -- --force
```

### Test Execution Issues

**Error**: Tests fail in development but pass in CI

**Solutions**:
```bash
# Ensure test isolation
cd backend
pytest --verbose --tb=short

# Check test database isolation
# Tests should use in-memory database, not dev database

# Clear test caches
rm -rf .pytest_cache __pycache__
```

**Error**: Frontend tests fail with module resolution

**Solutions**:
```bash
cd frontend

# Clear Jest/Vitest cache
rm -rf node_modules/.cache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Run tests with verbose output
npm test -- --reporter=verbose
```

## Production Deployment Issues

### SSL/TLS Certificate Issues

**Error**: `SSL certificate verification failed`

**Solutions**:
```bash
# Check certificate validity
openssl x509 -in certificate.crt -text -noout

# Test SSL configuration
curl -I https://your-domain.com

# Renew Let's Encrypt certificates
certbot renew --dry-run
```

### Reverse Proxy Issues

**Error**: nginx configuration problems

**Solutions**:
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx error logs
sudo tail -f /var/log/nginx/error.log

# Restart nginx
sudo systemctl restart nginx
```

### Database Connection in Production

**Error**: PostgreSQL connection issues

**Solutions**:
```bash
# Test database connection
psql -h localhost -U orchestrator_user -d orchestrator

# Check PostgreSQL service
sudo systemctl status postgresql

# Verify connection string
echo $DATABASE_URL
```

## Advanced Diagnostics

### Debug Mode

Enable detailed logging:

```bash
# Backend debug mode
export LOG_LEVEL=DEBUG
export DEBUG=true
npm run backend:dev

# Frontend debug mode
export VITE_DEBUG=true
npm run frontend:dev
```

### Health Check Debugging

```bash
# Detailed health check
curl "http://localhost:8000/health?detailed=true"

# Check individual components
python -c "
from backend.src.orchestration.health_service import HealthService
health = HealthService()
result = health.check_health(detailed=True)
print(result)
"
```

### Log Analysis

```bash
# Backend logs
tail -f backend/logs/app.log

# System logs
journalctl -u orchestrator-backend -f

# Error pattern analysis
grep -E "(ERROR|CRITICAL)" backend/logs/app.log | tail -20
```

### Performance Profiling

```bash
# Database query profiling
sqlite3 orchestrator_dev.db "PRAGMA wal_checkpoint; PRAGMA optimize;"

# Memory profiling
pip install memory-profiler
python -m memory_profiler backend/src/main.py

# CPU profiling
pip install py-spy
py-spy top --pid $(pgrep uvicorn)
```

## Getting Help

### Before Reporting Issues

1. **Run validation**: `python scripts/validate_environment.py --json`
2. **Collect logs**: Save output from failing commands
3. **Document steps**: List exact steps to reproduce
4. **Include environment**: OS, Python/Node versions, environment type

### Support Channels

1. **Documentation**: Check [deployment guide](guide.md) and [quick start](quick-start.md)
2. **Validation**: Always run environment validation first
3. **GitHub Issues**: Create issue with validation output and error details
4. **Stack Traces**: Include full error messages and stack traces

### Useful Information to Include

```bash
# System information
uname -a
python --version
node --version
npm --version

# Project validation
python scripts/validate_environment.py --json

# Service status
ps aux | grep -E "(uvicorn|vite)"
netstat -tlnp | grep -E "(8000|5174)"

# Recent logs
tail -20 backend/logs/app.log
```

---

*This troubleshooting guide covers the most common issues with the npm script-based deployment system. For additional help, see the [deployment guide](guide.md) or create a GitHub issue with validation output.*