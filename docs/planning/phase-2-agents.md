# Phase 2: The Conversational Diff Agent

*Last Updated: 2025-01-11*

**Status**: ✅ 85% Complete  
**Estimated Time**: 3-4 hours  
**Actual Progress**: Core agents implemented

## Goal

Create the AI "brain" that powers the conversational interaction, enabling users to create and modify projects through natural language.

## Completed Tasks

### Task 2.1: Implement the Diff Agent ✅

**Base Agent Implementation**

**Location**: `src/agent/base.py`

**AgentBase Class Features**:
```python
class AgentBase(ABC):
    - Multi-provider LLM support
    - Configurable retry logic (max 3 attempts)
    - Exponential backoff for rate limits
    - JSON parsing and validation
    - Pydantic model integration
    - Response caching
    - Error handling and logging
```

**Supported Providers**:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini 1.5 Pro, Flash)
- xAI (Grok Beta)

**Key Methods**:
```python
def get_llm_client(provider: str, api_key: str)
    # Factory method for LLM clients

def _execute_with_retry(
    messages: List[Dict],
    model: str,
    response_model: Type[BaseModel]
) -> BaseModel
    # Handles retries and parsing
```

### Task 2.2: Project Mode Implementation ✅

**PlannerAgent - FULLY IMPLEMENTED**

**Location**: `src/agent/planner_agent.py`

**Test Coverage**: 98% (36 comprehensive tests)

**Core Functionality**:
```python
class PlannerAgent(AgentBase):
    def get_diff(
        self,
        user_request: str,
        current_state: Optional[CurrentProjectState] = None
    ) -> PatchSet:
        # Generates project scaffolding from natural language
```

**Key Features**:
- Breaks requests into maximum 6 high-level tasks
- Generates meaningful project metadata
- Estimates effort in person-days
- Creates hierarchical milestone structure
- Returns only patch operations (diff-first)

**Prompt Engineering**:
```python
PROJECT_PLANNER_PROMPT = """
You are an expert project planner AI assistant.

Your task is to help users break down their project ideas into 
structured, actionable plans with clear milestones.

Key Instructions:
- Create a maximum of {max_milestones} high-level milestone tasks
- Each milestone should represent 1-2 weeks of work
- Focus on deliverables, not granular steps
- Return ONLY valid JSON matching the PatchSet schema
- All operations should be 'create' for new projects
"""
```

**Production Ready**:
- Comprehensive test suite
- Full documentation
- Error handling
- Performance optimized
- Multi-provider support

### Task 2.3: Task Mode Implementation ✅

**DecomposerAgent**

**Location**: `src/agent/decomposer_agent.py`

**Core Functionality**:
```python
class DecomposerAgent(AgentBase):
    def get_diff(
        self,
        task_id: str,
        user_request: str,
        context: TaskContext
    ) -> PatchSet:
        # Breaks down tasks into subtasks
```

**Key Features**:
- Decomposes tasks into 3-7 subtasks
- Maintains context awareness
- Generates technical implementation steps
- Preserves time estimates
- Creates acceptance criteria

**Task Decomposition Prompt**:
```python
TASK_DECOMPOSER_PROMPT = """
You are a technical task decomposition specialist.

Given a parent task, break it down into smaller, actionable subtasks.

Key Instructions:
- Create 3-7 subtasks for the parent task
- Each subtask should be independently completable
- Include technical details and acceptance criteria
- Maintain logical sequencing
- All subtasks are children of task_id: {task_id}
"""
```

### Additional Agent Implementations

**EditorAgent** ✅

**Location**: `src/agent/editor_agent.py`

**Purpose**: Natural language editing of existing projects/tasks

**Features**:
- Interprets edit requests ("change priority to high")
- Generates update patches
- Handles bulk operations
- Maintains data integrity

**OrchestratorAgent** ✅

**Location**: `src/agent/orchestrator_agent.py`

**Purpose**: High-level conversation management

**Features**:
- Routes requests to appropriate agents
- Manages conversation context
- Handles multi-step workflows
- Provides unified interface

## Agent System Architecture

### Tool System

**Location**: `src/agent/tools.py`

**Implemented Tools**:
```python
TOOLS = [
    create_project_tool,
    update_project_tool,
    delete_project_tool,
    create_task_tool,
    update_task_tool,
    delete_task_tool,
    list_projects_tool,
    list_tasks_tool,
    search_tool
]
```

**Benefits**:
- Structured agent capabilities
- Type-safe operations
- Clear action boundaries
- Easy to extend

### Prompt Management

**Location**: `src/agent/prompts.py`

**Prompt Categories**:
- Project planning prompts
- Task decomposition prompts
- Editing instruction prompts
- Context formatting prompts

**Best Practices**:
- Clear role definition
- Structured output requirements
- Example-driven instructions
- Schema validation emphasis

## Testing

**Test Coverage by Agent**:
- PlannerAgent: 98% (36 tests)
- DecomposerAgent: 85% (24 tests)
- EditorAgent: 80% (18 tests)
- OrchestratorAgent: 75% (15 tests)

**Key Test Scenarios**:
- Natural language understanding
- Edge case handling
- Multi-provider compatibility
- Error recovery
- Performance benchmarks

## Configuration

**Location**: `src/config/providers.yaml`

```yaml
providers:
  openai:
    default_model: gpt-4-turbo-preview
    planning_model: gpt-4-turbo-preview
    decomposition_model: gpt-3.5-turbo
    
  anthropic:
    default_model: claude-3-opus-20240229
    planning_model: claude-3-opus-20240229
    decomposition_model: claude-3-sonnet-20240229
```

**Model Selection Logic**:
- Planning: Highest capability models
- Decomposition: Balance of speed/quality
- Editing: Fast, focused models

## Performance Metrics

### Response Times
- Project planning: 2-4 seconds
- Task decomposition: 1-2 seconds
- Editing operations: < 1 second

### Token Usage
- Planning: ~1000-2000 tokens
- Decomposition: ~500-1000 tokens
- Editing: ~200-500 tokens

## Lessons Learned

1. **Structured outputs** critical for reliability
2. **Provider failover** improves availability
3. **Response caching** reduces costs
4. **Clear prompts** improve consistency
5. **Retry logic** handles transient failures

## Remaining Work

1. **Advanced Context Management**
   - Long conversation memory
   - Cross-project learning
   - User preference tracking

2. **Enhanced Capabilities**
   - Multi-language support
   - Domain-specific planning
   - Team collaboration features

3. **Optimization**
   - Response streaming
   - Batch operations
   - Cost optimization

## Next Phase

With the AI agents operational, Phase 3 focuses on exposing these capabilities through a REST API.

## Related Documentation

- [Phase 3: API Layer](phase-3-api.md)
- [Architecture Overview](../architecture/overview.md)
- [PlannerAgent Documentation](../agents/planner_agent.md)