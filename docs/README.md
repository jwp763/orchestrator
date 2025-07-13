# Orchestrator Documentation

Welcome to the comprehensive documentation for the Databricks Orchestrator project. This guide will help you navigate all available documentation based on your role and needs.

*Last Updated: 2025-01-11*

## 📚 Documentation by Role

### For Developers

| Category | Description | Links |
|----------|-------------|-------|
| **Getting Started** | Setup and development workflow | • [Development Setup](development/setup.md)<br>• [Contributing Guide](../CONTRIBUTING.md) |
| **Architecture** | System design and patterns | • [Architecture Overview](architecture/overview.md)<br>• [Testing Architecture](testing.md)<br>• [API Design](api/README.md) |
| **Testing** | Testing strategies and guides | • [Testing Overview](testing/overview.md)<br>• [Backend Testing](testing/backend-guide.md)<br>• [Frontend Testing](testing/frontend-guide.md) |
| **Reference** | Quick references and lookups | • [Data Models](reference/data-models.md)<br>• [CLI Commands](reference/commands.md)<br>• [Error Codes](reference/error-codes.md) |

### For AI Assistants

| Category | Description | Links |
|----------|-------------|-------|
| **Instructions** | AI-specific guidelines | • [AI Instructions](../.ai/ai-instructions.md)<br>• [Quick Reference](../.ai/ai-quick-reference.md) |
| **Context** | Project context and plans | • [Project Overview](../PROJECT.md)<br>• [MVP Plan](planning/mvp-overview.md)<br>• [Current Tasks](../.ai/tasks/current.yaml) |
| **Patterns** | Code patterns and examples | • [Testing Patterns](testing/patterns.md)<br>• [API Examples](api/examples.md) |

### For Project Managers

| Category | Description | Links |
|----------|-------------|-------|
| **Planning** | Project roadmap and status | • [MVP Overview](planning/mvp-overview.md)<br>• [Implementation Status](planning/implementation-status.md)<br>• [Future Phases](planning/future-phases.md) |
| **Decisions** | Architecture decisions | • [Decision Records](decisions/) |

## 📖 Documentation by Topic

### 🏗️ Architecture & Design

- [System Architecture Overview](architecture/overview.md) - High-level system design
- [Testing Architecture](testing.md) - Comprehensive testing infrastructure
- [Data Models Reference](reference/data-models.md) - Pydantic schemas and database models
- [API Design](api/README.md) - RESTful API patterns and conventions

### 🔧 Development

- [Development Setup](development/setup.md) - Complete environment setup
- [AI Instructions](../.ai/ai-instructions.md) - Guidelines for AI-assisted development
- [Contributing](../CONTRIBUTING.md) - How to contribute to the project

### 🧪 Testing

- [Testing Overview](testing/overview.md) - Test statistics and strategy
- [Backend Testing Guide](testing/backend-guide.md) - Python/pytest patterns
- [Frontend Testing Guide](testing/frontend-guide.md) - React/Vitest patterns
- [Common Testing Patterns](testing/patterns.md) - Shared testing approaches
- [Troubleshooting](testing/troubleshooting.md) - Common issues and solutions

### 🚀 API & Integration

- [API Documentation](api/README.md) - Complete API reference
- [API Examples](api/examples.md) - Usage examples and patterns
- [Quick Reference](api/quick-ref.md) - API endpoint tables

### 📋 Planning & Management

- [MVP Overview](planning/mvp-overview.md) - Minimum Viable Product plan
- [Implementation Status](planning/implementation-status.md) - Current progress
- [Phase Documentation](planning/) - Detailed phase breakdowns
- [Future Roadmap](planning/future-phases.md) - Upcoming features

### 🚢 Deployment

- [Deployment Guide](deployment/guide.md) - Production deployment instructions

### 📚 Reference

- [Command Reference](reference/commands.md) - CLI commands and scripts
- [Error Codes](reference/error-codes.md) - Common errors and solutions
- [Data Models](reference/data-models.md) - Schema reference

### 🤔 Decisions

- [Architecture Decision Records](decisions/) - Important technical decisions

## 🔍 Quick Links

### Essential Files
- [README](../README.md) - Project introduction
- [PROJECT.md](../PROJECT.md) - Detailed project context
- [LICENSE](../LICENSE) - MIT License
- [CONTRIBUTING](../CONTRIBUTING.md) - Contribution guidelines

### Task Management
- [Current Tasks](../.ai/tasks/current.yaml) - Active development tasks with automatic datetime tracking
- [Task Template](../.ai/templates/task-template.yaml) - Template for creating new tasks
- [Task Board](../PROJECT.md#current-sprint-focus) - Sprint overview

**Task Management Notes**: 
- CRITICAL: AI agents must use `date -Iseconds` command for datetime (AI internal date is often wrong)
- All tasks use automatic system datetime generation for created_date, start_date, and completion_date fields
- ALL tasks must include comprehensive test requirements (unit, integration, performance, security)
- Tasks cannot be marked "completed" until all test requirements are implemented and passing

### External Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 📝 Documentation Standards

All documentation in this project follows these standards:

1. **Markdown Format** - All docs use GitHub-flavored Markdown
2. **Last Updated** - Each file includes update timestamp
3. **Clear Structure** - Consistent headers and sections
4. **Code Examples** - Practical examples where relevant
5. **Cross-References** - Links to related documentation

## 🆘 Need Help?

- Can't find what you're looking for? Check the [search function](https://github.com/your-repo/search)
- Have questions? Open a [discussion](https://github.com/your-repo/discussions)
- Found an issue? Report it in [issues](https://github.com/your-repo/issues)