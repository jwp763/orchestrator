# Personal Project & Task Manager with AI Orchestration

## Overview

This is a Databricks-based personal project and task management system that uses AI agents to intelligently orchestrate work across multiple platforms. The system provides a unified interface to manage projects and tasks while automatically syncing with external tools like Motion, Linear, GitLab, and Notion.

## Key Features

- **Provider-Agnostic AI Agent**: Uses PydanticAI to seamlessly switch between LLM providers (Anthropic, OpenAI, xAI, Gemini) based on task complexity and cost optimization
- **Multi-Platform Integration**: Bidirectional sync with Motion (scheduling), Linear (tickets), GitLab (code), and Notion (docs)
- **Delta Lake Storage**: Robust data storage using Databricks Delta tables with proper schemas and relationships
- **Interactive Notebooks**: Databricks notebooks for setup, agent interaction, and automation
- **Flexible Architecture**: Modular design allowing easy extension of integrations and capabilities

## Architecture

```
databricks_orchestrator/
├── src/
│   ├── agent/           # PydanticAI agent with multi-provider support
│   ├── models/          # Pydantic data models and Delta schemas
│   ├── integrations/    # External service integrations (Motion, Linear, etc.)
│   ├── orchestration/   # Task routing and workflow management
│   ├── storage/         # Delta table operations and state management
│   └── config/          # Settings and provider configurations
├── notebooks/           # Interactive Databricks notebooks
├── configs/            # Configuration files
└── docs/               # Project documentation
```

## Database Structure

- **Catalog**: `jwp763`
- **Schema**: `orchestrator`
- **Tables**: users, projects, tasks, integrations, agent_contexts, agent_logs, sync_logs

## Getting Started

1. Run `notebooks/00_setup.py` to initialize the database
2. Configure API keys for your integrations
3. Use `notebooks/01_agent_interface.py` to interact with the system
4. Enable integrations as needed in the admin interface

## Documentation Structure

- [What's Been Done](./PROGRESS.md) - Detailed status of completed work
- [Short Term Plan](./SHORT_TERM_PLAN.md) - Next 2-4 weeks of work
- [Mid Term Plan](./MID_TERM_PLAN.md) - 2-6 month roadmap
- [Long Term Vision](./LONG_TERM_VISION.md) - Future possibilities
- [Documentation Maintenance](./DOCUMENTATION_MAINTENANCE.md) - How to keep docs updated

## Quick Start

```python
# In Databricks notebook
from src.agent import get_agent
from src.models import AgentRequest

agent = get_agent()
response = agent.process_request_sync(AgentRequest(
    message="Create a project for building a mobile app with a 3-month deadline"
))
print(response.message)
```