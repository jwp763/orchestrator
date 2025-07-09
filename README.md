# Databricks Orchestrator

A modern AI-powered project planning and task management system that intelligently orchestrates work across multiple platforms. The system combines a FastAPI backend with a React frontend to provide a comprehensive solution for project management with AI assistance.

## 🚀 Features

- **AI-Powered Planning**: Intelligent project breakdown using multiple AI providers (OpenAI, Anthropic, Gemini, xAI)
- **Project Management**: Complete CRUD operations for projects and tasks
- **Task Hierarchies**: Support for subtasks and task dependencies
- **Real-time Sync**: Frontend-backend integration with optimistic updates
- **Multi-Platform Integration**: Support for Motion, Linear, Notion, and GitLab
- **Modern UI**: Responsive React interface with Tailwind CSS
- **Type Safety**: Full TypeScript coverage with Pydantic models

## 🏗️ Architecture

### Backend (FastAPI)
- **API Layer**: RESTful endpoints with automatic documentation
- **Storage Layer**: SQLAlchemy ORM with SQLite database
- **AI Integration**: Pluggable AI agents for project planning
- **Service Layer**: Business logic for orchestration and coordination

### Frontend (React)
- **UI Components**: Modern React components with TypeScript
- **State Management**: Custom hooks for API integration
- **Routing**: Simple router for different views
- **API Client**: Robust HTTP client with retry logic and error handling

## 📋 Prerequisites

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **npm**: 7 or higher

## 🛠️ Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd databricks_orchestrator
```

### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your AI provider API keys

# Initialize database
python -c "
from src.storage.sql_models import Base
from sqlalchemy import create_engine
engine = create_engine('sqlite:///orchestrator.db')
Base.metadata.create_all(engine)
print('Database initialized successfully')
"
```

### 3. Frontend Setup

```bash
# Navigate to frontend directory (from project root)
cd frontend

# Install dependencies
npm install

# Build for development
npm run dev
```

## 🚀 Running the Application

### Start the Backend Server

```bash
cd backend
python -m uvicorn src.api.main:app --reload --port 8000
```

The backend API will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

### Start the Frontend Application

```bash
cd frontend
npm run dev
```

The frontend will be available at:
- **Application**: http://localhost:5173 (or next available port)
- **API Test Interface**: Click "API Test" button in the navigation

## 🔧 API Usage

### Project Operations

```bash
# List all projects
curl -X GET "http://localhost:8000/api/projects"

# Create a new project
curl -X POST "http://localhost:8000/api/projects" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Project",
    "description": "Project description",
    "created_by": "user-id"
  }'

# Get project with tasks
curl -X GET "http://localhost:8000/api/projects/{project_id}"

# Update project
curl -X PUT "http://localhost:8000/api/projects/{project_id}" \
  -H "Content-Type: application/json" \
  -d '{"name": "Updated Project Name"}'

# Delete project
curl -X DELETE "http://localhost:8000/api/projects/{project_id}"
```

### Task Operations

```bash
# List all tasks
curl -X GET "http://localhost:8000/api/tasks"

# Create a new task
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": "project-id",
    "title": "My Task",
    "description": "Task description",
    "created_by": "user-id"
  }'

# Get task with subtasks
curl -X GET "http://localhost:8000/api/tasks/{task_id}"

# Update task
curl -X PUT "http://localhost:8000/api/tasks/{task_id}" \
  -H "Content-Type: application/json" \
  -d '{"status": "completed"}'

# Delete task
curl -X DELETE "http://localhost:8000/api/tasks/{task_id}"
```

### AI Planning

```bash
# Generate project plan
curl -X POST "http://localhost:8000/api/planner/plan" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Build a web application for task management",
    "config": {
      "provider": "openai",
      "create_milestones": true,
      "max_milestones": 5
    }
  }'
```

## 🧪 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_api/test_project_routes.py

# Run with coverage
pytest --cov=src
```

### Frontend Testing

The frontend includes an API test interface accessible through the web application:

1. Start both backend and frontend servers
2. Open the frontend in your browser
3. Click the "API Test" button in the navigation
4. Use the interface to test CRUD operations

## 📁 Project Structure

```
databricks_orchestrator/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   ├── api/               # API routes and models
│   │   ├── models/            # Pydantic data models
│   │   ├── storage/           # Database layer
│   │   ├── orchestration/     # Service layer
│   │   └── agent/             # AI agents
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── services/         # API client services
│   │   └── types/            # TypeScript definitions
│   ├── public/               # Static assets
│   └── package.json          # Node.js dependencies
├── docs/                     # Documentation
├── .ai/                      # AI configuration and tasks
└── README.md                 # This file
```

## 🔑 Environment Variables

Create a `.env` file in the backend directory with the following optional variables:

```env
# AI Provider API Keys (optional)
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
GEMINI_API_KEY=your_gemini_key
XAI_API_KEY=your_xai_key

# Database URL (optional, defaults to SQLite)
DATABASE_URL=sqlite:///orchestrator.db

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
```

## 🔄 Development Workflow

### Making Changes

1. **Backend Changes**: The server runs with `--reload` flag, so changes are automatically reflected
2. **Frontend Changes**: Vite provides hot module replacement for instant updates
3. **Database Changes**: Recreate the database if you modify the schema:
   ```bash
   cd backend
   rm orchestrator.db
   python -c "from src.storage.sql_models import Base; from sqlalchemy import create_engine; engine = create_engine('sqlite:///orchestrator.db'); Base.metadata.create_all(engine)"
   ```

### Adding New Features

1. **Backend**: Add routes in `src/api/`, models in `src/models/`, and services in `src/orchestration/`
2. **Frontend**: Add components in `src/components/`, hooks in `src/hooks/`, and services in `src/services/`
3. **Types**: Update TypeScript interfaces in `src/types/` to match backend models

## 🐛 Troubleshooting

### Common Issues

1. **Port Already in Use**: The application will automatically find the next available port
2. **Database Errors**: Recreate the database using the command above
3. **API Connection Issues**: Ensure the backend is running on port 8000
4. **CORS Issues**: The backend is configured to allow all origins in development

### Logs

- **Backend Logs**: Displayed in the terminal where you started the backend
- **Frontend Logs**: Check the browser console for client-side issues

## 📖 API Documentation

When the backend is running, visit http://localhost:8000/api/docs for interactive API documentation powered by Swagger UI.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Commit your changes: `git commit -am 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
- Check the troubleshooting section above
- Review the API documentation at http://localhost:8000/api/docs
- Check existing issues in the repository
- Create a new issue with detailed information about your problem

---

**Happy orchestrating!** 🎯