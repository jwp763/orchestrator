# AI Agents Documentation

This directory contains documentation for the AI agents in the orchestrator system.

## Available Agents

### PlannerAgent
- **Purpose**: Transforms project ideas into structured project metadata
- **Location**: `src/agent/planner_agent.py`
- **Documentation**: [planner_agent.md](planner_agent.md)
- **Status**: ✅ Implemented and tested (98% coverage)

### OrchestratorAgent
- **Purpose**: Main conversational agent for task management
- **Location**: `src/agent/orchestrator_agent.py`
- **Documentation**: Coming soon
- **Status**: 🔄 In development

## Agent Architecture

All agents extend the `AgentBase` class which provides:
- Multi-provider LLM support (OpenAI, Anthropic, Gemini, XAI)
- Automatic retry logic with exponential backoff
- JSON parsing and Pydantic validation
- Structured error handling
- Model caching for performance

## Common Usage Patterns

### Agent Creation
```python
from src.agent.planner_agent import create_planner_agent

# Create with default settings
agent = create_planner_agent()

# Create with custom configuration
agent = create_planner_agent(
    provider="openai",
    model_name="gpt-4",
    create_milestones=True,
    max_milestones=5
)
```

### Async Usage
```python
# Primary async interface
result = await agent.get_diff(user_input, context=context)

# Synchronous wrapper (creates new event loop)
result = agent.get_diff_sync(user_input, context=context)
```

### Error Handling
```python
from src.agent.base import AgentError, JSONParsingError, ValidationError

try:
    result = await agent.get_diff(user_input)
except JSONParsingError:
    # LLM returned invalid JSON
    pass
except ValidationError:
    # Data failed Pydantic validation
    pass
except AgentError:
    # General agent error
    pass
```

## Testing

Each agent includes comprehensive test coverage:
- Unit tests with mocking for isolation
- Integration tests with real scenarios
- Error handling and edge case testing
- Performance and retry logic testing

## Configuration

Agents are configured through:
- Environment variables (API keys)
- `configs/providers.yaml` (provider settings)
- Constructor parameters (agent-specific config)
- Runtime context (request-specific overrides)

## Development Guidelines

1. **Extend AgentBase**: All agents must inherit from `AgentBase`
2. **Implement get_diff**: Core method for processing user input
3. **Add Type Hints**: Full type annotations required
4. **Include Documentation**: Comprehensive docstrings
5. **Write Tests**: Minimum 90% test coverage
6. **Handle Errors**: Proper error handling and logging

## Performance Considerations

- Use model caching to avoid repeated initialization
- Implement proper retry logic with exponential backoff
- Consider rate limiting for API calls
- Use async/await for better concurrency
- Monitor token usage and costs

## Deployment Notes

- Ensure all required API keys are configured
- Monitor rate limits and quotas
- Set up proper logging and error tracking
- Consider using multiple providers for redundancy
- Test with various input scenarios before deployment