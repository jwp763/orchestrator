# PlannerAgent Documentation

## Overview

The PlannerAgent is a specialized AI agent that transforms high-level project ideas into structured project metadata. It extends the AgentBase class and provides intelligent project planning capabilities by analyzing natural language descriptions and generating comprehensive project structures.

## Key Features

- **Project Metadata Generation**: Creates structured project data with name, description, priority, status, and tags
- **Milestone Creation**: Optionally generates initial milestone tasks with time estimates
- **Context-Aware Planning**: Adapts project structure based on provided context
- **Multi-Provider Support**: Works with OpenAI, Anthropic, Gemini, and other AI providers
- **Validation & Enhancement**: Validates and enhances generated project data

## Usage

### Basic Usage

```python
from src.agent.planner_agent import PlannerAgent, create_planner_agent

# Create agent with default settings
agent = create_planner_agent()

# Generate project structure
result = await agent.get_diff("Build a web application for task management")
```

### Configuration Options

```python
# Configure milestone creation
agent = create_planner_agent(
    create_milestones=True,      # Enable milestone creation
    max_milestones=5,            # Maximum number of milestones
    provider="openai",           # AI provider
    model_name="gpt-4"           # Specific model
)

# Context-aware planning
context = {
    "team_size": "3 developers",
    "timeline": "6 months",
    "complexity": "medium"
}

result = await agent.get_diff("Create a CRM system", context=context)
```

### Context Override

The agent supports context-based configuration overrides:

```python
# Agent configured with milestones enabled
agent = create_planner_agent(create_milestones=True, max_milestones=4)

# Context can override milestone creation
context = {"create_milestones": False}  # Disables milestones for this request
result = await agent.get_diff("Simple blog website", context=context)
```

## Output Structure

The PlannerAgent returns a `Patch` object containing:

### Project Patches

- **op**: Always `Op.CREATE` for new projects
- **name**: Generated project name
- **description**: Detailed project description
- **priority**: Project priority (`ProjectPriority.MEDIUM` by default)
- **status**: Project status (`ProjectStatus.PLANNING` by default)
- **tags**: Relevant project tags (e.g., ["web", "frontend", "backend"])
- **estimated_total_minutes**: Optional time estimate

### Task Patches (when milestones enabled)

- **op**: Always `Op.CREATE` for new tasks
- **title**: Milestone task title
- **description**: Task description
- **priority**: Task priority
- **status**: Task status (`TaskStatus.TODO` by default)
- **estimated_minutes**: Time estimate in minutes

## Implementation Details

### Core Methods

#### `get_diff(user_input, context=None)`

Main method that processes project ideas:

- Analyzes user input and context
- Builds appropriate system prompt
- Calls LLM with retry logic
- Validates and enhances results
- Returns structured Patch object

#### `_build_system_prompt(include_milestones=True)`

Constructs the system prompt:

- Defines agent role and capabilities
- Includes JSON schema for response format
- Adds milestone creation instructions if enabled
- Ensures proper validation requirements

#### `_validate_and_enhance_result(result)`

Post-processes LLM results:

- Validates project and task data
- Sets default values for missing fields
- Ensures data consistency
- Handles edge cases

### Error Handling

The agent includes robust error handling:

- **JSONParsingError**: Invalid JSON responses from LLM
- **ValidationError**: Data that fails Pydantic validation
- **AgentError**: General agent failures
- Automatic retry with exponential backoff

## Testing

The PlannerAgent includes comprehensive test coverage:

### Unit Tests (`tests/test_planner_agent_simple.py`)

- Basic functionality tests
- Configuration validation
- Error handling scenarios
- Mock-based testing for isolation

### Integration Tests (`tests/test_planner_integration.py`)

- Real-world project scenarios
- Context-aware behavior
- End-to-end functionality

### Test Coverage

- **98% code coverage** on PlannerAgent implementation
- All major code paths tested
- Edge cases and error scenarios covered

## Best Practices

### 1. Provider Configuration

```python
# Ensure API keys are properly configured
agent = create_planner_agent(provider="openai")  # Requires OPENAI_API_KEY
```

### 2. Context Usage

```python
# Provide relevant context for better results
context = {
    "domain": "e-commerce",
    "team_size": "5 developers",
    "timeline": "3 months",
    "budget": "medium"
}
```

### 3. Error Handling

```python
try:
    result = await agent.get_diff(project_idea, context=context)
except JSONParsingError as e:
    # Handle JSON parsing failures
    logger.error(f"LLM returned invalid JSON: {e}")
except ValidationError as e:
    # Handle validation failures
    logger.error(f"Generated data failed validation: {e}")
```

### 4. Milestone Management

```python
# For simple projects, disable milestones
agent = create_planner_agent(create_milestones=False)

# For complex projects, increase milestone limit
agent = create_planner_agent(max_milestones=8)
```

## Performance Considerations

- **Model Caching**: Models are cached to avoid repeated initialization
- **Async Support**: Fully asynchronous for better performance
- **Retry Logic**: Intelligent retry with exponential backoff
- **Context Optimization**: Only includes relevant context in prompts

## Dependencies

- `pydantic-ai`: LLM integration framework
- `pydantic`: Data validation and serialization
- `AgentBase`: Base class providing common functionality
- Project and task models from the data layer

## Future Enhancements

1. **Smart Template Selection**: Choose templates based on project type
2. **Time Estimation Improvement**: Better effort estimation algorithms
3. **Dependency Analysis**: Identify task dependencies automatically
4. **Risk Assessment**: Include risk analysis in project planning
5. **Resource Planning**: Consider team skills and availability

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure proper environment variables are set
2. **Validation Failures**: Check that LLM responses match expected schema
3. **Context Conflicts**: Verify context doesn't contain conflicting information
4. **Rate Limiting**: Implement appropriate delays between requests

### Debug Mode

Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

agent = create_planner_agent()
result = await agent.get_diff("Debug this project")
```

## Related Components

- **AgentBase**: Base class providing LLM functionality
- **ProjectPatch/TaskPatch**: Data models for generated content
- **Settings**: Configuration management
- **Repository Pattern**: Data persistence layer

This documentation provides a comprehensive guide for using and maintaining the PlannerAgent in the orchestrator system.
