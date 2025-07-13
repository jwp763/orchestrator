# Detailed Development Setup Guide

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: 7 or higher
- **Git**: 2.0 or higher
- **Operating System**: Windows, macOS, or Linux

### Recommended Tools

- **IDE**: VS Code with Python and TypeScript extensions
- **API Testing**: Postman or curl
- **Database Browser**: SQLite Browser (optional)

## Backend Setup

### 1. Python Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### 3. Database Initialization

The project uses environment-specific databases:
- **Development**: `orchestrator_dev.db`
- **Staging**: `orchestrator_staging.db`
- **Production**: `orchestrator_prod.db`

Databases are automatically created when you start each environment for the first time.

### 4. Environment Configuration

The project includes pre-configured environment files:

```bash
# .env.dev - Development configuration
# - Ports: Backend 8000, Frontend 5174
# - Debug mode enabled, hot-reload active
# - Database: orchestrator_dev.db

# .env.staging - Staging configuration  
# - Ports: Backend 8001, Frontend 5175
# - Production-like settings for testing
# - Database: orchestrator_staging.db

# .env.prod - Production configuration
# - Ports: Backend 8002, Frontend 5176  
# - Minimal logging, no reload
# - Database: orchestrator_prod.db
```

To customize, edit the appropriate `.env.*` file:
```bash
# Add your AI provider API keys
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
# ... etc
```

### 5. Run Backend Server

#### Option 1: Using Environment Scripts (Recommended)
```bash
# From project root - starts both frontend and backend
npm run start:dev      # Development
npm run start:staging  # Staging
npm run start:prod     # Production

# Or use scripts directly
./scripts/start-dev.sh
```

#### Option 2: Manual Start
```bash
# Load environment variables
export $(cat .env.dev | grep -v '^#' | xargs)

# Start the FastAPI server
python -m uvicorn src.api.main:app --reload --port $API_PORT

# Alternative: Run with custom host
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port $API_PORT
```

### 6. Verify Backend

```bash
# Check health endpoint
curl http://localhost:8000/health

# View API documentation
open http://localhost:8000/api/docs
```

## Frontend Setup

### 1. Install Dependencies

```bash
# Navigate to frontend directory
cd frontend

# Install all dependencies
npm install

# Alternative: Use yarn
yarn install
```

### 2. Environment Configuration

```bash
# Create .env file for frontend (optional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

### 3. Run Development Server

```bash
# Default development server (port 5174)
npm run dev

# Environment-specific ports
npm run dev:staging   # Port 5175
npm run dev:prod      # Port 5176

# Alternative: Use yarn
yarn dev
```

### 4. Build for Production

```bash
# Create production build
npm run build

# Preview production build
npm run preview
```

## Multi-Environment Workflow

### Running Multiple Environments

You can run development, staging, and production environments simultaneously:

```bash
# Terminal 1: Development
npm run start:dev
# Backend: http://localhost:8000
# Frontend: http://localhost:5174

# Terminal 2: Staging (in new terminal)
npm run start:staging
# Backend: http://localhost:8001
# Frontend: http://localhost:5175

# Terminal 3: Production (in new terminal)
npm run start:prod
# Backend: http://localhost:8002
# Frontend: http://localhost:5176
```

### Environment Use Cases

- **Development**: Active development with hot-reload, debug logging
- **Staging**: Test production builds, verify deployment process
- **Production**: Real usage, stable data, minimal logging

## Development Workflow

### Code Quality Tools

#### Backend

```bash
# Format code with Black
black .

# Type checking with mypy
mypy .

# Linting with pylint
pylint src/

# Run pre-commit hooks
pre-commit run --all-files
```

#### Frontend

```bash
# Format code
npm run format

# Lint code
npm run lint

# Type checking
npm run type-check
```

### Testing

#### Backend Testing

```bash
# Run all tests
cd backend && pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_api/test_project_routes.py

# Run tests in watch mode
pytest-watch
```

#### Frontend Testing

```bash
# Run all tests
npm test

# Run in watch mode
npm run test:watch

# Run with coverage
npm run test:coverage

# Run with UI
npm run test:ui
```

### Database Management

#### Environment-Specific Commands

```bash
# Reset development database
npm run db:reset-dev
# Or: ./scripts/reset-dev.sh

# Backup production database
npm run db:backup
# Or: ./scripts/backup-prod.sh

# Copy production data to staging
npm run db:copy-prod-to-staging
# Or: ./scripts/copy-prod-to-staging.sh
```

#### Manual Database Reset

```bash
cd backend

# For development
rm orchestrator_dev.db
# Database will be recreated on next server start

# For staging
rm orchestrator_staging.db

# For production (be careful!)
# Always backup first: ./scripts/backup-prod.sh
rm orchestrator_prod.db
```

#### Database Migrations

```bash
# Run migrations (if using alembic)
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description of changes"
```

## Troubleshooting

### Common Backend Issues

1. **ModuleNotFoundError**
   - Ensure virtual environment is activated
   - Reinstall dependencies: `pip install -r requirements.txt`

2. **Database Connection Errors**
   - Check if database file exists
   - Recreate database if needed

3. **Port Already in Use**
   - Kill existing process: `lsof -i :8000` (macOS/Linux)
   - Use different port: `--port 8001`

### Common Frontend Issues

1. **Module Resolution Errors**
   - Clear node_modules: `rm -rf node_modules && npm install`
   - Clear npm cache: `npm cache clean --force`

2. **Build Errors**
   - Check Node.js version: `node --version`
   - Update dependencies: `npm update`

3. **API Connection Issues**
   - Verify backend is running on port 8000
   - Check CORS configuration
   - Verify API URL in frontend code

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
    "bradlc.vscode-tailwindcss",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense"
  ]
}
```

### VS Code Settings

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "[typescript]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  },
  "[typescriptreact]": {
    "editor.defaultFormatter": "esbenp.prettier-vscode"
  }
}
```

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)