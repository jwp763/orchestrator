"""Delta Table Schemas for Databricks"""

USERS_SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id STRING NOT NULL,
    name STRING NOT NULL,
    email STRING,

    -- Integration user IDs
    motion_user_id STRING,
    linear_user_id STRING,
    notion_user_id STRING,
    gitlab_user_id STRING,

    -- Metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,

    PRIMARY KEY (id)
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

PROJECTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS projects (
    id STRING NOT NULL,
    name STRING NOT NULL,
    description STRING,
    status STRING NOT NULL,
    priority INT NOT NULL,
    tags ARRAY<STRING>,

    -- Scheduling
    due_date DATE,
    start_date DATE,

    -- Integration IDs
    motion_project_id STRING,
    linear_project_id STRING,
    notion_page_id STRING,
    gitlab_project_id STRING,

    -- Metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,

    -- Computed fields
    task_count INT DEFAULT 0,
    completed_task_count INT DEFAULT 0,

    PRIMARY KEY (id),
    FOREIGN KEY (created_by) REFERENCES users(id)
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

TASKS_SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id STRING NOT NULL,
    project_id STRING NOT NULL,
    title STRING NOT NULL,
    description STRING,
    status STRING NOT NULL,
    priority STRING NOT NULL,
    
    -- Scheduling
    due_date DATE,
    estimated_hours DOUBLE,
    actual_hours DOUBLE,
    
    -- Assignment
    assignee STRING,
    tags ARRAY<STRING>,
    labels ARRAY<STRING>,
    
    -- Integration IDs
    motion_task_id STRING,
    linear_issue_id STRING,
    notion_task_id STRING,
    gitlab_issue_id STRING,
    
    -- Dependencies
    depends_on ARRAY<STRING>,
    blocks ARRAY<STRING>,
    
    -- Metadata
    metadata MAP<STRING, STRING>,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    created_by STRING NOT NULL,
    
    -- Computed fields
    is_overdue BOOLEAN DEFAULT FALSE,
    days_until_due INT,
    
    PRIMARY KEY (id),
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assignee) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

INTEGRATIONS_SCHEMA = """
CREATE TABLE IF NOT EXISTS integrations (
    id STRING NOT NULL,
    type STRING NOT NULL,
    name STRING NOT NULL,
    enabled BOOLEAN DEFAULT TRUE,
    
    -- Configuration (stored as encrypted JSON)
    config_encrypted STRING NOT NULL,
    
    -- Sync settings
    sync_enabled BOOLEAN DEFAULT TRUE,
    sync_interval_minutes INT DEFAULT 60,
    last_sync_at TIMESTAMP,
    last_sync_status STRING,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    created_by STRING NOT NULL,
    
    PRIMARY KEY (id)
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

AGENT_CONTEXTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_contexts (
    conversation_id STRING NOT NULL,
    user_id STRING NOT NULL,

    -- Conversation data (stored as JSON)
    messages STRING NOT NULL,

    -- Current context
    active_project_id STRING,
    active_task_ids ARRAY<STRING>,

    -- Preferences
    default_provider STRING,
    default_integration STRING,

    -- Metadata
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    total_tokens_used BIGINT DEFAULT 0,

    PRIMARY KEY (conversation_id),
    FOREIGN KEY (user_id) REFERENCES users(id)
)
USING DELTA
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

AGENT_LOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS agent_logs (
    id STRING NOT NULL,
    conversation_id STRING NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    
    -- Request/Response
    request STRING NOT NULL,
    response STRING NOT NULL,
    
    -- Model info
    provider_used STRING NOT NULL,
    model_used STRING NOT NULL,
    tokens_used INT,
    response_time_ms INT,
    
    -- Execution
    actions_executed ARRAY<STRING>,
    errors ARRAY<STRING>,
    
    PRIMARY KEY (id),
    FOREIGN KEY (conversation_id) REFERENCES agent_contexts(conversation_id)
)
USING DELTA
PARTITIONED BY (DATE(timestamp))
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

SYNC_LOGS_SCHEMA = """
CREATE TABLE IF NOT EXISTS sync_logs (
    id STRING NOT NULL,
    integration_id STRING NOT NULL,
    sync_type STRING NOT NULL,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    
    -- Results
    status STRING NOT NULL,
    items_synced INT DEFAULT 0,
    errors_count INT DEFAULT 0,
    error_details ARRAY<STRING>,
    
    PRIMARY KEY (id),
    FOREIGN KEY (integration_id) REFERENCES integrations(id)
)
USING DELTA
PARTITIONED BY (DATE(started_at))
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
)
"""

# All schemas for easy iteration
ALL_SCHEMAS = {
    "users": USERS_SCHEMA,
    "projects": PROJECTS_SCHEMA,
    "tasks": TASKS_SCHEMA,
    "integrations": INTEGRATIONS_SCHEMA,
    "agent_contexts": AGENT_CONTEXTS_SCHEMA,
    "agent_logs": AGENT_LOGS_SCHEMA,
    "sync_logs": SYNC_LOGS_SCHEMA
}