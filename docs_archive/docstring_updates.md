# Docstring Updates for DeltaManager

## User Operations

### create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
```python
"""
Create a new user account in the system.

Automatically generates a unique ID and timestamps for the user record.
Sets default active status if not provided.

Args:
    user_data (Dict[str, Any]): User information containing:
        - name (str): User's display name
        - email (str): User's email address
        - preferences (Dict, optional): User preferences dictionary
        - is_active (bool, optional): Whether user is active (default: True)

Returns:
    Dict[str, Any]: Created user record with generated ID and timestamps

Raises:
    SparkException: If user creation fails due to database constraints
    ValueError: If required fields (name, email) are missing

Example:
    >>> user = manager.create_user({
    ...     "name": "John Doe",
    ...     "email": "john@example.com",
    ...     "preferences": {"theme": "dark"}
    ... })
    >>> print(user["id"])  # Generated UUID
"""
```

### get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
```python
"""
Retrieve a user by their unique ID.

Args:
    user_id (str): Unique identifier for the user

Returns:
    Optional[Dict[str, Any]]: User record if found, None otherwise.
        Contains all user fields: id, name, email, preferences, is_active,
        created_at, updated_at

Example:
    >>> user = manager.get_user("12345-67890-abcdef")
    >>> if user:
    ...     print(f"User: {user['name']} ({user['email']})")
"""
```

## Project Operations

### create_project(self, project_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
```python
"""
Create a new project with automatic task counting initialization.

Generates unique ID, timestamps, and initializes task counters to zero.

Args:
    project_data (Dict[str, Any]): Project information containing:
        - user_id (str): ID of the project owner
        - name (str): Project name
        - description (str, optional): Project description
        - status (str, optional): Project status
        - priority (str, optional): Project priority
        - metadata (Dict, optional): Additional project metadata
        - integration_project_ids (Dict, optional): External project IDs
    created_by (str): ID or name of the user creating the project

Returns:
    Dict[str, Any]: Created project record with generated fields

Raises:
    ValueError: If required fields are missing
    SparkException: If project creation fails

Example:
    >>> project = manager.create_project({
    ...     "user_id": "user-123",
    ...     "name": "Website Redesign",
    ...     "description": "Complete UI overhaul",
    ...     "status": "active"
    ... }, created_by="user-123")
"""
```

## Task Operations

### create_task(self, task_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
```python
"""
Create a new task with hierarchical support and validation.

Automatically handles:
- ID generation and timestamps
- Parent-child relationship validation
- Depth calculation and limits
- Default duration assignment
- Due date calculations
- Project task count updates

Args:
    task_data (Dict[str, Any]): Task information containing:
        - project_id (str): Parent project ID
        - title (str): Task title
        - description (str, optional): Task description
        - parent_id (str, optional): Parent task ID for hierarchy
        - estimated_minutes (int, optional): Time estimate in minutes
        - dependencies (List[str], optional): Dependent task IDs
        - status (str, optional): Task status
        - priority (str, optional): Task priority
        - assigned_to (str, optional): Assignee ID
        - due_date (str/date, optional): Due date
        - labels (List[str], optional): Task labels
    created_by (str): ID or name of the user creating the task

Returns:
    Dict[str, Any]: Created task record with computed fields

Raises:
    ValueError: If parent task doesn't exist or depth exceeds limits
    SparkException: If task creation fails

Example:
    >>> task = manager.create_task({
    ...     "project_id": "proj-123",
    ...     "title": "Design mockups",
    ...     "parent_id": "task-456",
    ...     "estimated_minutes": 120,
    ...     "dependencies": ["task-789"]
    ... }, created_by="user-123")
"""
```

### get_task_tree(self, root_id: str) -> Dict[str, Any]:
```python
"""
Retrieve a task with all its descendants in a nested tree structure.

Recursively builds a hierarchical representation with children nested
under their parents. Calculates total estimated time across all
descendants.

Args:
    root_id (str): ID of the root task to build tree from

Returns:
    Dict[str, Any]: Task tree with nested children. Each task includes:
        - All original task fields
        - children (List[Dict]): List of child task trees
        - child_count (int): Number of direct children
        - total_estimated_minutes (int): Sum of self + all descendants

    Returns None if root task doesn't exist.

Example:
    >>> tree = manager.get_task_tree("task-123")
    >>> print(f"Task: {tree['title']}")
    >>> print(f"Total time: {tree['total_estimated_minutes']} minutes")
    >>> for child in tree['children']:
    ...     print(f"  Child: {child['title']}")
"""
```

### move_task(self, task_id: str, new_parent_id: Optional[str]) -> bool:
```python
"""
Move a task to a new position in the hierarchy.

Validates the move operation to prevent circular references and
depth limit violations. Updates the depth of the moved task and
all its descendants.

Args:
    task_id (str): ID of task to move
    new_parent_id (Optional[str]): ID of new parent task, or None for root

Returns:
    bool: True if move was successful

Raises:
    ValueError: If:
        - Task or new parent doesn't exist
        - Move would create circular dependency
        - Move would exceed maximum depth limits
        - Task would become its own parent

Example:
    >>> # Move task to be a child of another task
    >>> success = manager.move_task("task-123", "new-parent-456")
    >>> 
    >>> # Move task to root level
    >>> success = manager.move_task("task-123", None)
"""
```

## Integration Operations

### create_integration(self, integration_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
```python
"""
Create a new integration configuration for external services.

Stores encrypted configuration data for services like Motion, Linear,
GitLab, and Notion. Handles secure credential storage.

Args:
    integration_data (Dict[str, Any]): Integration configuration:
        - user_id (str): Owner user ID
        - provider_type (str): Service type (motion, linear, gitlab, notion)
        - encrypted_config (str): Encrypted configuration JSON
        - is_active (bool, optional): Whether integration is active
        - metadata (Dict, optional): Additional metadata
    created_by (str): ID of user creating the integration

Returns:
    Dict[str, Any]: Created integration record

Raises:
    ValueError: If required fields are missing or provider type invalid
    SparkException: If integration creation fails

Example:
    >>> integration = manager.create_integration({
    ...     "user_id": "user-123",
    ...     "provider_type": "motion",
    ...     "encrypted_config": encrypted_credentials,
    ...     "is_active": True
    ... }, created_by="user-123")
"""
```

## Agent Operations

### create_agent_context(self, context_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
```python
"""
Create a new agent conversation context.

Stores conversation state, project/task focus, and message history
for AI agent interactions. Manages token usage tracking.

Args:
    context_data (Dict[str, Any]): Context information:
        - user_id (str): User ID for the conversation
        - project_id (str, optional): Active project context
        - task_id (str, optional): Active task context
        - messages (List[Dict], optional): Conversation messages
        - metadata (Dict, optional): Additional context metadata
    created_by (str): ID of user creating the context

Returns:
    Dict[str, Any]: Created context record with token tracking

Example:
    >>> context = manager.create_agent_context({
    ...     "user_id": "user-123",
    ...     "project_id": "proj-456",
    ...     "messages": [{"role": "user", "content": "Hello"}]
    ... }, created_by="user-123")
"""
```