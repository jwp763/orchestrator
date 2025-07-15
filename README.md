# Orchestrator

A modern AI-powered project planning and task management system that intelligently orchestrates work across multiple platforms.

## 🚀 Features

- **AI-Powered Planning**: Intelligent project breakdown using multiple AI providers (OpenAI, Anthropic, Gemini, xAI)
- **Project Management**: Complete CRUD operations for projects and tasks with hierarchical support
- **Real-time Sync**: Frontend-backend integration with optimistic updates
- **Multi-Platform**: Support for Motion, Linear, Notion, and GitLab integrations
- **Modern Stack**: FastAPI backend + React TypeScript frontend
- **Comprehensive Testing**: 672+ tests with 99%+ coverage

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### Installation

#### Automated Setup (Recommended)

```bash
# Clone repository
git clone <repository-url>
cd databricks_orchestrator

# Run automated setup (installs dependencies, creates environment files)
python scripts/setup_development.py

# Validate environment
python scripts/validate_environment.py
```

#### Manual Setup

```bash
# Install all dependencies
npm run install:all  # Installs both backend and frontend dependencies

# Or manually:
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Frontend setup (new terminal)
cd frontend
npm install
```

### Running the Application

#### Quick Start (Development)
```bash
# From project root - starts both frontend and backend
npm run start:dev
```

#### Multi-Environment Support
The project supports three isolated environments:

| Environment | Backend Port | Frontend Port | Database |
|-------------|--------------|---------------|----------|
| Development | 8000 | 5174 | orchestrator_dev.db |
| Staging | 8001 | 5175 | orchestrator_staging.db |
| Production | 8002 | 5176 | orchestrator_prod.db |

```bash
# Start specific environments
npm run start:dev      # Development with hot-reload
npm run start:staging  # Staging with production builds
npm run start:prod     # Production without reload

# Or use scripts directly
./scripts/start-dev.sh
./scripts/start-staging.sh
./scripts/start-prod.sh
```

- **Frontend**: http://localhost:5174 (dev) / 5175 (staging) / 5176 (prod)
- **API Docs**: http://localhost:8000/api/docs (adjust port per environment)
- **Health Check**: http://localhost:8000/health (adjust port per environment)

## 📖 Documentation

### Deployment
- [Quick Start Guide (5 min)](docs/deployment/quick-start.md) - Get running in 5 minutes
- [Complete Deployment Guide](docs/deployment/guide.md) - Comprehensive deployment documentation
- [Troubleshooting Guide](docs/deployment/troubleshooting.md) - Common issues and solutions

### Development
- [Development Setup Guide](docs/deployment/setup-guide.md) - Complete setup instructions
- [AI Instructions](.ai/ai-instructions.md) - Guidelines for AI assistants
- [Architecture Overview](docs/architecture/overview.md) - System architecture

### Testing
- [Testing Overview](docs/testing.md) - Comprehensive testing documentation
- [Backend Testing](docs/testing/backend-guide.md) - Backend test patterns
- [Frontend Testing](docs/testing/frontend-guide.md) - Frontend test patterns
- [Troubleshooting](docs/testing/troubleshooting.md) - Common issues and solutions

### Project Management
- [Current Tasks](PROJECT.md) - Active development tasks and sprint focus
- [MVP Overview](docs/planning/mvp-overview.md) - Product roadmap and vision
- [Task Details](.ai/tasks/current.yaml) - Machine-readable task tracking

## 🧪 Testing

```bash
# Run all tests (backend + frontend)
npm run test:all

# Backend tests
cd backend && pytest              # Run all tests
cd backend && pytest --cov=src    # With coverage

# Frontend tests  
cd frontend && npm test           # Run all tests
cd frontend && npm run test:coverage  # With coverage
```

**Current Status**: 672 tests (Backend: 516, Frontend: 156) with 99.6% success rate

**Note**: Tests use in-memory databases and are isolated from development/staging/production databases.

## 🏗️ Project Structure

```
databricks_orchestrator/
├── backend/              # FastAPI backend
│   ├── src/             # Application code
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/             # React components
│   └── tests/           # Frontend tests
├── scripts/             # Environment management scripts
│   ├── start-*.sh      # Environment startup scripts
│   ├── backup-prod.sh  # Production backup script
│   └── reset-dev.sh    # Development reset script
├── docs/                # Documentation
├── notebooks/           # Databricks notebooks
├── .ai/                # AI configurations
├── .env.defaults       # Shared environment defaults  
├── .env.development    # Development environment config
├── .env.staging        # Staging environment config
├── .env.production     # Production environment config
└── .env.local          # Personal API keys (git-ignored)
```

## 🔧 Development

### Common Commands

```bash
# Database Management
npm run db:backup               # Backup production database
npm run db:copy-prod-to-staging # Copy prod data to staging
npm run db:reset-dev            # Reset development database

# Code Quality (from root)
npm run lint:all                # Lint all code
npm run lint:backend            # Python linting
npm run lint:frontend           # TypeScript linting

# Backend (from backend/)
black .                         # Format Python code
mypy .                          # Type checking

# Frontend (from frontend/)
npm run format                  # Format TypeScript code
npm run lint                    # Lint code
```

### Making Changes

1. Backend changes auto-reload with `--reload` flag in development
2. Frontend has hot module replacement via Vite
3. See [Development Setup Guide](docs/deployment/setup-guide.md) for detailed workflow
4. Use [Troubleshooting Guide](docs/deployment/troubleshooting.md) for common issues

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push branch: `git push origin feature/amazing-feature`
5. Open Pull Request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) for details.

## 🆘 Support

- **Documentation**: Check our comprehensive [docs](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

Built with ❤️ using AI-assisted development

<!-- CI Test: $(date) -->