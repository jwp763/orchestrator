# Contributing to Orchestrator

Thank you for your interest in contributing to Orchestrator! This guide will help you get started with contributing to the project.

## 🚀 Getting Started

1. **Fork the Repository**
   - Click the "Fork" button on GitHub
   - Clone your fork locally: `git clone <your-fork-url>`

2. **Set Up Development Environment**
   - Follow the [Development Setup Guide](docs/development/setup.md)
   - Ensure all tests pass before making changes

3. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/issue-description
   ```

## 📝 Development Process

### Code Standards

#### Python (Backend)
- Follow PEP 8 style guide
- Use type hints for all functions
- Format with Black: `black .`
- Type check with mypy: `mypy .`
- Write docstrings for public methods

#### TypeScript (Frontend)
- Follow ESLint configuration
- Use strict TypeScript settings
- Format with Prettier: `npm run format`
- Ensure no lint errors: `npm run lint`

### Testing Requirements

- **Write tests for all new features**
- **Maintain or improve code coverage**
- **Follow existing test patterns**
  - Backend: See [Backend Testing Guide](docs/testing/backend-guide.md)
  - Frontend: See [Frontend Testing Guide](docs/testing/frontend-guide.md)

### Commit Messages

Follow conventional commit format:
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Test additions or modifications
- `chore`: Build process or auxiliary tool changes

Example:
```
feat(api): add task filtering by status

- Add status parameter to task listing endpoint
- Update storage layer to support status filtering
- Add tests for new functionality

Closes #123
```

## 🔄 Pull Request Process

1. **Before Creating PR**
   - Ensure all tests pass
   - Update documentation if needed
   - Add/update tests for your changes
   - Run linters and formatters

2. **PR Description**
   - Clearly describe what changes you made
   - Reference any related issues
   - Include screenshots for UI changes
   - List any breaking changes

3. **PR Checklist**
   - [ ] Tests pass locally
   - [ ] Code follows style guidelines
   - [ ] Documentation updated
   - [ ] Commits are clean and well-described
   - [ ] No merge conflicts

## 🧪 Running Tests

### Backend Tests
```bash
cd backend
pytest                    # Run all tests
pytest --cov=src         # With coverage
pytest -x                # Stop on first failure
```

### Frontend Tests
```bash
cd frontend
npm test                 # Run all tests
npm run test:watch       # Watch mode
npm run test:coverage    # With coverage
```

## 📂 Project Structure

When adding new features, follow the existing structure:

### Backend
- API routes: `backend/src/api/`
- Data models: `backend/src/models/`
- Business logic: `backend/src/orchestration/`
- Storage layer: `backend/src/storage/`
- Tests: `backend/tests/`

### Frontend
- Components: `frontend/src/components/`
- Hooks: `frontend/src/hooks/`
- Services: `frontend/src/services/`
- Types: `frontend/src/types/`
- Tests: Next to the files they test

## 🐛 Reporting Issues

### Bug Reports
Include:
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python/Node version)
- Error messages/stack traces

### Feature Requests
Include:
- Clear description of the feature
- Use cases and benefits
- Potential implementation approach
- Any mockups or examples

## 💡 Development Tips

1. **Use the AI Instructions**
   - See [AI Instructions](docs/development/ai-instructions.md)
   - Follow the patterns established in the codebase

2. **Database Changes**
   - Update SQLAlchemy models
   - Create migration if needed
   - Update tests

3. **API Changes**
   - Update FastAPI routes
   - Update Pydantic models
   - Update TypeScript types
   - Update API documentation

4. **UI Changes**
   - Follow existing component patterns
   - Ensure responsive design
   - Test across browsers
   - Update Storybook if applicable

## 🤝 Code Review

Your PR will be reviewed for:
- Code quality and style
- Test coverage
- Documentation
- Performance implications
- Security considerations
- Architecture alignment

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/handbook/intro.html)
- [Testing Best Practices](docs/testing.md)

## ❓ Questions?

- Check existing [issues](https://github.com/your-repo/issues)
- Join [discussions](https://github.com/your-repo/discussions)
- Review the [documentation](docs/)

Thank you for contributing to Orchestrator! 🎉