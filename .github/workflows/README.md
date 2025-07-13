# GitHub Actions Workflows

This directory contains CI/CD workflows for the Databricks Orchestrator project.

## Workflows

### 🧪 [`tests.yml`](tests.yml)
**Comprehensive Test Suite**

- **Triggers**: Push/PR to `main`, `master`, `develop`
- **Jobs**:
  - **Backend Tests**: Python 3.8-3.12, pytest with coverage
  - **Frontend Tests**: Node.js 16-20, Vitest with coverage
  - **Integration Tests**: End-to-end API health checks
  - **Test Summary**: Aggregates results and reports

### 📚 [`docs-check.yml`](docs-check.yml)
**Documentation Quality Assurance**

- **Triggers**: Push/PR affecting documentation files
- **Jobs**:
  - **Link Validation**: Internal link checking with lychee
  - **Markdown Linting**: Style and format validation
  - **Documentation Standards**: Custom quality checks
  - **Spell Checking**: Automated spell verification

## Features

### 🎯 Matrix Testing
- **Backend**: Tests across Python 3.8-3.12
- **Frontend**: Tests across Node.js 16-20
- **Cross-platform**: Ubuntu, with optional Windows/macOS

### 📊 Coverage Reporting
- **Codecov Integration**: Automatic coverage uploads
- **Separate Flags**: Backend and frontend coverage tracked separately
- **Coverage Reports**: HTML and XML formats generated

### ⚡ Performance Optimizations
- **Dependency Caching**: pip and npm caches for faster builds
- **Parallel Execution**: Jobs run concurrently when possible
- **Path Filtering**: Documentation workflow only runs on doc changes

### 🛡️ Quality Gates
- **All Tests Must Pass**: No broken builds allowed
- **Documentation Standards**: Links and format must be valid
- **Integration Verification**: API endpoints must be accessible

## Workflow Status

You can view the status of all workflows in the repository's Actions tab:
- [GitHub Actions Dashboard](../../actions)

## Adding New Workflows

When adding new workflows:

1. **Follow naming convention**: `kebab-case.yml`
2. **Add documentation**: Update this README
3. **Use consistent triggers**: Follow existing patterns
4. **Include summary reporting**: Add job summaries for visibility
5. **Optimize performance**: Use caching and path filters where appropriate

## Troubleshooting

### Common Issues

1. **Tests fail locally but pass in CI**: Check Python/Node versions
2. **Cache issues**: Clear GitHub Actions cache in repository settings
3. **Documentation checks fail**: Run `./scripts/doc-check.sh` locally
4. **Integration tests timeout**: Backend may need more startup time

### Debug Steps

1. Check the Actions tab for detailed logs
2. Run tests locally with the same commands as CI
3. Verify dependencies are properly cached
4. Check for environment-specific issues (paths, permissions)

## Branch Protection

Consider setting up branch protection rules to require:
- ✅ All status checks passing
- ✅ Up-to-date branches
- ✅ No force pushes to main branches