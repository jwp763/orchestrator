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

```bash
# Clone repository
git clone <repository-url>
cd databricks_orchestrator

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python -c "from src.storage.sql_models import Base; from sqlalchemy import create_engine; engine = create_engine('sqlite:///orchestrator.db'); Base.metadata.create_all(engine)"

# Frontend setup (new terminal)
cd frontend
npm install
```

### Running the Application

```bash
# Terminal 1 - Backend
cd backend
python -m uvicorn src.api.main:app --reload --port 8000

# Terminal 2 - Frontend
cd frontend
npm run dev
```

- **Frontend**: http://localhost:5173
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

## 📖 Documentation

### Development
- [Detailed Setup Guide](docs/development/setup.md) - Complete setup instructions
- [AI Instructions](docs/development/ai-instructions.md) - Guidelines for AI assistants
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
# Backend tests
cd backend && pytest              # Run all tests
cd backend && pytest --cov=src    # With coverage

# Frontend tests  
npm test                          # Run all tests
npm run test:coverage             # With coverage
```

**Current Status**: 672 tests (Backend: 516, Frontend: 156) with 99.6% success rate

## 🏗️ Project Structure

```
databricks_orchestrator/
├── backend/              # FastAPI backend
│   ├── src/             # Application code
│   └── tests/           # Backend tests
├── frontend/            # React frontend
│   ├── src/             # React components
│   └── tests/           # Frontend tests
├── docs/                # Documentation
├── notebooks/           # Databricks notebooks
└── .ai/                # AI configurations
```

## 🔧 Development

### Common Commands

```bash
# Backend
black .                  # Format Python code
mypy .                   # Type checking

# Frontend
npm run format           # Format TypeScript code
npm run lint            # Lint code
```

### Making Changes

1. Backend changes auto-reload with `--reload` flag
2. Frontend has hot module replacement via Vite
3. See [Development Guide](docs/development/setup.md) for detailed workflow

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