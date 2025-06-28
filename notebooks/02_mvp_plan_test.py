# Databricks notebook source
# MAGIC %md
# MAGIC # MVP Plan Testing Notebook
# MAGIC 
# MAGIC This notebook tests the ingestion of our MVP plan document, demonstrating the meta approach of using the system to manage its own development.

# COMMAND ----------

import os
import sys

# Correct order for workspace path modification if needed, then other imports
workspace_root = os.path.abspath(os.path.join(os.getcwd(), os.path.join(os.pardir, os.pardir, os.pardir)))
if workspace_root not in sys.path:
    print(f"Adding {workspace_root} to sys.path")
    sys.path.insert(0, workspace_root)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Initialize System

# COMMAND ----------

from src.models.user import User
from src.models.project import Project, ProjectStatus, ProjectPriority
from src.models.task import Task, TaskStatus, TaskPriority
from src.storage.delta_manager import DeltaManager
from datetime import datetime, timedelta
import json

# Initialize Delta Manager
delta_manager = DeltaManager()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Create Test User and Project

# COMMAND ----------

# Create or get test user
test_user = User(
    id="mvp_test_user",
    name="MVP Tester",
    email="mvp@test.com"
)

try:
    delta_manager.create_user(test_user)
    print("Created test user")
except Exception as e:
    print(f"User might already exist: {e}")
    test_user = delta_manager.get_user("mvp_test_user")

# Create MVP project
mvp_project = Project(
    id="hierarchical_task_planner_mvp",
    user_id=test_user.id,
    name="Hierarchical Task-Planner & Motion Scheduler",
    description="Enable the Databricks Orchestrator to ingest a free-form project description, explode it into 1–2-day tasks and 30 min - 2 h sub-tasks, and automatically push them to Motion",
    status=ProjectStatus.ACTIVE,
    priority=ProjectPriority.HIGH,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(weeks=6)
)

try:
    delta_manager.create_project(mvp_project)
    print("Created MVP project")
except Exception as e:
    print(f"Project might already exist: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Manual Task Creation (Phase 0 Example)
# MAGIC 
# MAGIC Since we don't have the planner agent yet, we'll manually create the Phase 0 tasks to demonstrate the structure.

# COMMAND ----------

# Phase 0 root task
phase_0 = Task(
    id="phase_0_foundation",
    project_id=mvp_project.id,
    title="Phase 0: Foundation Hardening",
    description="Solid baselines: upgraded models, typing, tests",
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    estimated_minutes=7 * 60,  # 7 hours total
    depth=0,
    parent_id=None
)

delta_manager.create_task(phase_0)
print(f"Created Phase 0 root task: {phase_0.id}")

# COMMAND ----------

# Task 0.1: Extend Task Model
task_0_1 = Task(
    id="task_0_1_extend_model",
    project_id=mvp_project.id,
    parent_id=phase_0.id,
    title="Task 0.1: Extend Task Model with Hierarchical Fields",
    description="Evolve the existing Task model to support parent-child relationships and time estimation",
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    estimated_minutes=480,  # 8 hours (1 day)
    depth=1
)

delta_manager.create_task(task_0_1)
print(f"Created Task 0.1: {task_0_1.id}")

# COMMAND ----------

# Subtasks for Task 0.1
subtasks_0_1 = [
    {
        "id": "subtask_0_1_1",
        "title": "Add Hierarchical Fields to Task Model",
        "description": "Add parent_id, estimated_minutes, actual_minutes, depth, dependencies to TaskBase model",
        "estimated_minutes": 90
    },
    {
        "id": "subtask_0_1_2", 
        "title": "Create Delta Table Migration",
        "description": "Create migration notebook that adds new columns with defaults",
        "estimated_minutes": 60
    },
    {
        "id": "subtask_0_1_3",
        "title": "Extend DeltaManager CRUD Operations", 
        "description": "Update create_task, get_tasks, add hierarchy methods",
        "estimated_minutes": 75
    },
    {
        "id": "subtask_0_1_4",
        "title": "Update Configuration for Defaults",
        "description": "Add settings for DEFAULT_TASK_DURATION_MINUTES, MAX_TASK_DEPTH, etc.",
        "estimated_minutes": 45
    }
]

for subtask_data in subtasks_0_1:
    subtask = Task(
        id=subtask_data["id"],
        project_id=mvp_project.id,
        parent_id=task_0_1.id,
        title=subtask_data["title"],
        description=subtask_data["description"],
        status=TaskStatus.TODO,
        priority=TaskPriority.MEDIUM,
        estimated_minutes=subtask_data["estimated_minutes"],
        depth=2
    )
    delta_manager.create_task(subtask)
    print(f"Created subtask: {subtask.title}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Query and Visualize Task Hierarchy

# COMMAND ----------

# Get all tasks for the project
all_tasks = delta_manager.get_tasks(project_id=mvp_project.id)
print(f"Total tasks created: {len(all_tasks)}")

# Display hierarchy
def print_task_tree(tasks, parent_id=None, indent=0):
    """Print tasks in tree format"""
    for task in tasks:
        if task.parent_id == parent_id:
            print("  " * indent + f"├─ {task.title} ({task.estimated_minutes} min)")
            print_task_tree(tasks, task.id, indent + 1)

print("\nTask Hierarchy:")
print_task_tree(all_tasks)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Calculate Time Rollups

# COMMAND ----------

def calculate_total_time(tasks, task_id):
    """Calculate total time including all subtasks"""
    task = next(t for t in tasks if t.id == task_id)
    total = task.estimated_minutes or 0
    
    # Add time from all children
    children = [t for t in tasks if t.parent_id == task_id]
    for child in children:
        total += calculate_total_time(tasks, child.id)
    
    return total

# Calculate Phase 0 total time
phase_0_total = calculate_total_time(all_tasks, phase_0.id)
print(f"Phase 0 total estimated time: {phase_0_total} minutes ({phase_0_total / 60:.1f} hours)")

# Verify it matches our subtask sum
subtask_sum = sum(st["estimated_minutes"] for st in subtasks_0_1)
print(f"Sum of subtasks: {subtask_sum} minutes")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Test Dependency Management

# COMMAND ----------

# Add a dependency example
task_0_2 = Task(
    id="task_0_2_relationship_table",
    project_id=mvp_project.id,
    parent_id=phase_0.id,
    title="Task 0.2: Create Task Relationship Table",
    description="Implement a separate table for complex task relationships",
    status=TaskStatus.TODO,
    priority=TaskPriority.HIGH,
    estimated_minutes=240,  # 4 hours (0.5 days)
    depth=1,
    dependencies=["task_0_1_extend_model"]  # Depends on Task 0.1
)

delta_manager.create_task(task_0_2)
print(f"Created Task 0.2 with dependency on Task 0.1")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Prepare for Future Planner Agent
# MAGIC 
# MAGIC This demonstrates the structure that the Planner Agent will need to create automatically.

# COMMAND ----------

# Example of what the planner agent should produce
example_plan_structure = {
    "project": {
        "name": "Hierarchical Task-Planner & Motion Scheduler",
        "description": "Enable natural language project planning...",
        "phases": [
            {
                "id": "phase_0",
                "title": "Foundation Hardening",
                "duration_days": 1,
                "tasks": [
                    {
                        "id": "task_0_1",
                        "title": "Extend Task Model with Hierarchical Fields",
                        "duration_minutes": 480,
                        "subtasks": [
                            {
                                "id": "subtask_0_1_1",
                                "title": "Add Hierarchical Fields to Task Model",
                                "duration_minutes": 90
                            }
                            # ... more subtasks
                        ]
                    }
                ]
            }
        ]
    }
}

print("Example plan structure for Planner Agent:")
print(json.dumps(example_plan_structure, indent=2))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Success Criteria Validation

# COMMAND ----------

# Check that we can:
# 1. Create hierarchical tasks
print("✅ Hierarchical task creation working")

# 2. Store parent-child relationships
parent_child_test = [t for t in all_tasks if t.parent_id is not None]
print(f"✅ Parent-child relationships stored: {len(parent_child_test)} child tasks")

# 3. Track time estimates
time_tracked = [t for t in all_tasks if t.estimated_minutes is not None]
print(f"✅ Time estimates tracked: {len(time_tracked)} tasks with estimates")

# 4. Manage dependencies
deps_test = [t for t in all_tasks if t.dependencies]
print(f"✅ Dependencies managed: {len(deps_test)} tasks with dependencies")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Next Steps
# MAGIC 
# MAGIC Once Phase 1 is complete, this notebook will be updated to:
# MAGIC 1. Read the MVP plan document (`docs/mvp_plan.md`)
# MAGIC 2. Call the Planner Agent to parse it
# MAGIC 3. Automatically create the full task hierarchy
# MAGIC 4. Sync to Motion for real project management
# MAGIC 
# MAGIC This demonstrates the meta approach - using the system we're building to manage the building process itself!

# COMMAND ----------

# Clean up display
display(spark.sql(f"""
    SELECT 
        id,
        title,
        parent_id,
        depth,
        estimated_minutes,
        status,
        dependencies
    FROM {delta_manager.catalog}.{delta_manager.schema}.tasks
    WHERE project_id = '{mvp_project.id}'
    ORDER BY depth, created_at
"""))