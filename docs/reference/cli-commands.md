# CLI Commands Reference

## Orchestrator CLI

The orchestrator provides a command-line interface for managing projects and tasks.

### Installation

```bash
pip install databricks-orchestrator
```

### Global Options

| Option | Short | Description |
|--------|-------|-------------|
| `--help` | `-h` | Show help message |
| `--version` | `-v` | Show version |
| `--config` | `-c` | Config file path |
| `--verbose` | | Enable verbose output |

### Commands

#### Project Management

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator project create` | Create a new project | `orchestrator project create "My Project"` |
| `orchestrator project list` | List all projects | `orchestrator project list --status active` |
| `orchestrator project update` | Update project details | `orchestrator project update PROJECT_ID --name "New Name"` |
| `orchestrator project delete` | Delete a project | `orchestrator project delete PROJECT_ID` |

#### Task Management

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator task create` | Create a new task | `orchestrator task create --project PROJECT_ID "Task Title"` |
| `orchestrator task list` | List tasks | `orchestrator task list --project PROJECT_ID` |
| `orchestrator task update` | Update task | `orchestrator task update TASK_ID --status completed` |
| `orchestrator task assign` | Assign task to agent | `orchestrator task assign TASK_ID --agent planner` |

#### Agent Operations

| Command | Description | Example |
|---------|-------------|---------|
| `orchestrator agent list` | List available agents | `orchestrator agent list` |
| `orchestrator agent status` | Check agent status | `orchestrator agent status planner` |
| `orchestrator agent execute` | Execute agent on task | `orchestrator agent execute AGENT_ID TASK_ID` |

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ORCHESTRATOR_API_URL` | API endpoint URL | `http://localhost:8000` |
| `ORCHESTRATOR_CONFIG` | Config file path | `~/.orchestrator/config.yaml` |
| `ORCHESTRATOR_LOG_LEVEL` | Logging level | `INFO` |
| `ENVIRONMENT` | Environment name | `development` |
| `DATABASE_URL` | Database connection URL | `sqlite:///backend/orchestrator_dev.db` |
| `API_PORT` | Backend API port | `8000` |
| `FRONTEND_PORT` | Frontend dev server port | `5174` |
| `BACKUP_ENABLED` | Enable automated backups | `false` |

### Development Scripts

| Command | Description | Example |
|---------|-------------|---------|
| `npm run start:dev` | Start development environment | `npm run start:dev` |
| `npm run start:staging` | Start staging environment | `npm run start:staging` |
| `npm run start:prod` | Start production environment | `npm run start:prod` |
| `npm run db:backup` | Backup production database | `npm run db:backup` |
| `npm run db:copy-prod-to-staging` | Copy prod to staging | `npm run db:copy-prod-to-staging` |
| `npm run db:reset-dev` | Reset development database | `npm run db:reset-dev` |
| `npm run test:all` | Run all tests | `npm run test:all` |
| `npm run lint:all` | Lint all code | `npm run lint:all` |

