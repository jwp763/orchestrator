# Databricks notebook source
# MAGIC %md
# MAGIC # Database Setup Notebook
# MAGIC
# MAGIC This notebook performs the complete setup of the Databricks orchestrator database with:
# MAGIC - All Delta tables with proper schemas
# MAGIC - Hierarchical task model support
# MAGIC - Task dependency tracking
# MAGIC - Planning metrics collection
# MAGIC - Sample data for testing
# MAGIC
# MAGIC **Database**: `jwp763.orchestrator`

# COMMAND ----------

import os
import sys

from pyspark.sql import SparkSession

# Correct order for workspace path modification if needed, then other imports
workspace_root = os.path.abspath(os.path.join(os.getcwd(), os.path.join(os.pardir)))
if workspace_root not in sys.path:
    print(f"Adding {workspace_root} to sys.path")
    sys.path.insert(0, workspace_root)

from src.config import get_settings  # noqa: E402
from src.setup import DatabaseSetup, get_validation_queries  # noqa: E402

# COMMAND ----------

# Initialize settings and Spark
settings = get_settings()
spark = SparkSession.builder.appName("00-setup").getOrCreate()

print(f"Database name: {settings.database_name}")
print(f"Default provider: {settings.default_provider}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Initialize Database Setup
# MAGIC Create the setup manager and run complete database initialization

# COMMAND ----------

# Initialize database setup
db_setup = DatabaseSetup(spark=spark, catalog=settings.catalog_name, schema=settings.schema_name)

# Run complete setup with sample data
sample_data = db_setup.setup_database(include_sample_data=True)

print(f"\n📊 Sample data created:")
print(f"  User ID: {sample_data['user_id']}")
print(f"  Project ID: {sample_data['project_id']}")
print(f"  Task IDs: {len(sample_data['task_ids'])} tasks")
print(f"  Integration IDs: {len(sample_data['integration_ids'])} integrations")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Validation Queries
# MAGIC Run validation queries to verify everything is working correctly

# COMMAND ----------

# Run validation queries
validation_queries = get_validation_queries(f"{settings.catalog_name}.{settings.schema_name}")

for query_info in validation_queries:
    print(f"\n📋 {query_info['name']}:")
    print("=" * 50)
    result_df = spark.sql(query_info["query"])
    result_df.show(truncate=False)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🎉 Setup Complete!
# MAGIC
# MAGIC The orchestrator database has been initialized with:
# MAGIC
# MAGIC ### Core Tables ✅
# MAGIC - **Users** - User management and preferences
# MAGIC - **Projects** - Project organization with task counting
# MAGIC - **Tasks** - Enhanced hierarchical task model with time tracking
# MAGIC - **Task Links** - Explicit dependency relationships
# MAGIC - **Planning Metrics** - AI planning performance analytics
# MAGIC
# MAGIC ### Integration & Agent Tables ✅
# MAGIC - **Integrations** - External service connections (Motion, Linear, GitLab, Notion)
# MAGIC - **Agent Contexts** - AI conversation tracking
# MAGIC - **Agent Logs** - Detailed agent operation logs
# MAGIC - **Sync Logs** - Integration synchronization tracking
# MAGIC
# MAGIC ### Sample Data Created ✅
# MAGIC - 👤 Default user account
# MAGIC - 🔗 4 integration templates (disabled)
# MAGIC - 📋 Sample hierarchical project with tasks
# MAGIC - 🔗 Task dependency example
# MAGIC
# MAGIC ### Performance Optimizations ✅
# MAGIC - 📊 Z-ordering applied to tasks and task_links tables
# MAGIC - 🗓️ Date partitioning on high-volume tables
# MAGIC - ⚡ Auto-optimization enabled
# MAGIC
# MAGIC ## Next Steps
# MAGIC 1. 🔑 Configure your API keys in the environment
# MAGIC 2. 📓 Run `01_agent_interface.py` to start interacting with the AI agent
# MAGIC 3. 🔌 Enable and configure integrations as needed
# MAGIC 4. 📝 Create your first hierarchical project plan
