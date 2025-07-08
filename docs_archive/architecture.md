# System Architecture

## Overview

The Databricks Orchestrator is a hierarchical task-planning system that transforms natural language project descriptions into structured, time-bounded tasks synchronized with external task management systems.

## Core Components

### 1. Data Layer

#### Delta Lake Storage
- **Projects Table**: Stores project metadata and integration references
- **Tasks Table**: Hierarchical task storage with parent-child relationships
- **Task Links Table**: Directed acyclic graph (DAG) for complex dependencies
- **Users Table**: User profiles and preferences
- **Integrations Table**: Provider configurations with encrypted credentials
- **Agent Logs Table**: Conversation history and metrics

#### Hierarchical Task Model
```
Task
├── id: str (UUID)
├── parent_id: Optional[str]  # References parent task
├── project_id: str
├── title: str
├── description: Optional[str]
├── status: TaskStatus
├── priority: TaskPriority
├── estimated_minutes: Optional[int]
├── actual_minutes: Optional[int]
├── depth: int  # Tree depth (0 = root)
├── dependencies: List[str]  # Task IDs that must complete first
└── integration_ids: Dict[str, str]  # Provider-specific IDs
```

### 2. Agent Layer

#### Orchestrator Agent
- **Purpose**: Central AI agent for task management
- **Framework**: PydanticAI with multi-model support
- **Capabilities**:
  - Natural language understanding
  - Tool calling for CRUD operations
  - Context-aware responses
  - State management

#### Planner Agent
- **Purpose**: Transform natural language into hierarchical task plans
- **Process**:
  1. Parse project description
  2. Identify major phases
  3. Decompose into 1-2 day tasks
  4. Create 30min-2hr subtasks
  5. Establish dependencies
  6. Estimate durations

#### Splitter Agent
- **Purpose**: Dynamic task granularity adjustment
- **Triggers**:
  - Tasks exceeding duration threshold
  - Vague task descriptions
  - User requests
- **Strategies**: By phase, component, or time chunk

### 3. Integration Layer

#### Provider Interface
```python
class TaskProvider(ABC):
    async def create_task(self, task: Task) -> str
    async def update_task(self, provider_id: str, updates: Dict)
    async def create_subtask(self, parent_id: str, task: Task) -> str
    async def sync_status(self) -> List[StatusUpdate]
```

#### Supported Providers
- **Motion**: Full bidirectional sync with hierarchies
- **Linear**: Issue tracking integration
- **GitLab**: Development task management
- **Notion**: Documentation and planning

#### Sync Engine
- **Bidirectional Sync**: Delta ↔ Provider
- **Conflict Resolution**: Last-write-wins with manual flags
- **Webhook Support**: Real-time updates
- **Batch Operations**: Efficient bulk syncing

### 4. API Layer

#### Task Operations
- **Split**: Decompose tasks into subtasks
- **Merge**: Combine related tasks
- **Move**: Reposition in hierarchy
- **Schedule**: Dependency-aware scheduling

#### Planning Pipeline
```
Natural Language → Planner Agent → Structured Plan → Delta Storage → Provider Sync
```

### 5. UI Layer

#### Databricks Notebooks
- **Project Planner**: Natural language input interface
- **Task Visualizer**: Interactive tree and Gantt views
- **Sync Monitor**: Integration health dashboard
- **Analytics**: Planning accuracy and velocity metrics

## Data Flow

### Planning Flow
1. User enters project description in notebook
2. Planner Agent generates hierarchical task structure
3. Tasks persisted to Delta with relationships
4. Sync engine pushes to configured providers
5. Webhook listener maintains bidirectional sync

### Task Management Flow
1. User or agent modifies task (status, estimate, etc.)
2. Change persisted to Delta
3. Sync engine propagates to providers
4. Conflicts resolved per configuration
5. Analytics updated for accuracy tracking

## Scalability Considerations

### Performance Optimizations
- **Z-ordering**: On frequently queried columns
- **Batch Operations**: For bulk task creation
- **Caching Layer**: LRU + Redis + Delta cache tables
- **Async Processing**: Non-blocking sync operations

### Limits
- **Max Task Depth**: 5 levels (configurable)
- **Tasks per Project**: 10,000 (tested)
- **Concurrent Users**: 100+ (with caching)
- **Sync Frequency**: Real-time to 5-minute intervals

## Security

### Data Protection
- **Encryption**: Integration credentials encrypted at rest
- **Authentication**: OAuth2 for provider connections
- **Authorization**: User-based access control
- **Audit Trail**: All operations logged

### API Security
- **Rate Limiting**: Per-user quotas
- **Input Validation**: Schema enforcement
- **Injection Prevention**: Parameterized queries

## Deployment

### Databricks Environment
- **Compute**: Shared cluster for notebooks
- **Storage**: Unity Catalog for governance
- **Secrets**: Databricks secret scope
- **Monitoring**: Built-in metrics and logs

### Development Workflow
1. Local development with Databricks Connect
2. Notebook-based testing
3. Delta table migrations
4. Integration testing
5. Production deployment

## Future Architecture Considerations

### Planned Enhancements
- **GraphQL API**: For external clients
- **Event Streaming**: Kafka/EventHubs integration
- **ML Pipeline**: Task duration prediction
- **Multi-tenant**: Workspace isolation

### Extension Points
- **Custom Providers**: Plugin architecture
- **Planning Strategies**: Configurable algorithms
- **Visualization Plugins**: D3.js extensions
- **Export Formats**: PDF, Excel, API