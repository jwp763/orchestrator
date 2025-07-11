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

```bash
# Initialize SQLite database
python -c "
from src.storage.sql_models import Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///orchestrator.db')
Base.metadata.create_all(engine)
print('Database initialized successfully')
"
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your configuration
# Add your AI provider API keys (optional)
```

### 5. Run Backend Server

```bash
# Start the FastAPI server with auto-reload
python -m uvicorn src.api.main:app --reload --port 8000

# Alternative: Run with custom host
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
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
# Start Vite development server
npm run dev

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

#### Reset Database

```bash
cd backend
rm orchestrator.db
python -c "from src.storage.sql_models import Base; from sqlalchemy import create_engine; engine = create_engine('sqlite:///orchestrator.db'); Base.metadata.create_all(engine)"
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