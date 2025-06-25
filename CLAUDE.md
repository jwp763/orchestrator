# Claude Code Configuration

This file contains configuration and context for Claude Code to help with development tasks.

## Project Overview
This is a Databricks orchestrator project for personal task and project management with AI agent capabilities.

## Database Configuration
- Catalog: `jwp763`
- Schema: `orchestrator`
- Full database path: `jwp763.orchestrator`

## Key Features
- Provider-agnostic AI agent using PydanticAI
- Integrations with Motion, Linear, GitLab, and Notion
- Delta table storage for projects, tasks, and user data
- Multi-model support (Anthropic, OpenAI, xAI, Gemini)

## Development Commands
- Build: (to be added)
- Test: (to be added)
- Lint: (to be added)
- Typecheck: (to be added)

## Notebooks
- `00_setup.py` - Initialize database and tables
- `01_agent_interface.py` - Interactive agent chat interface

### Databricks Notebook Path Setup
All Databricks notebooks that reference other files in the repo must include this path setup code at the top:

```python
import os
import sys

# Correct order for workspace path modification if needed, then other imports
workspace_root = os.path.abspath(os.path.join(os.getcwd(), os.path.join(os.pardir, os.pardir, os.pardir)))
if workspace_root not in sys.path:
    print(f"Adding {workspace_root} to sys.path")
    sys.path.insert(0, workspace_root)
```

This ensures proper module imports from the src/ directory when running in Databricks workspace.

## Documentation Structure
- Main docs located in `/docs/` directory
- See `docs/DOCUMENTATION_MAINTENANCE.md` for maintenance rules
- **IMPORTANT**: Documentation changes only during planning mode with user approval

## Notes
- Working directory: /Users/johnpope/databricks_orchestrator
- This is not currently a git repository