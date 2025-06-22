# Databricks notebook source
# MAGIC %md
# MAGIC # Setup Notebook
# MAGIC This notebook initializes the orchestrator database and tables

# COMMAND ----------

# MAGIC %pip install pydantic pydantic-ai delta-spark pyyaml

# COMMAND ----------

import sys
sys.path.append("..")

from src.storage import DeltaManager
from src.config import get_settings

# COMMAND ----------

# Initialize settings
settings = get_settings()
print(f"Database name: {settings.database_name}")
print(f"Default provider: {settings.default_provider}")

# COMMAND ----------

# Initialize Delta manager
delta_manager = DeltaManager(spark)

# COMMAND ----------

# Create database and tables
delta_manager.initialize_database()
print("Database and tables created successfully!")

# COMMAND ----------

# MAGIC %sql
# MAGIC USE jwp763.orchestrator;
# MAGIC SHOW TABLES;

# COMMAND ----------

# Create default user
default_user = delta_manager.create_user({
    "name": "Default User",
    "email": "user@example.com"
})
print(f"Created default user: {default_user['id']}")

# COMMAND ----------

# Create sample integrations (disabled by default)
integrations = [
    {
        "type": "motion",
        "name": "Motion Integration",
        "enabled": False,
        "config_encrypted": "{}",
        "sync_enabled": True,
        "sync_interval_minutes": 30
    },
    {
        "type": "linear",
        "name": "Linear Integration",
        "enabled": False,
        "config_encrypted": "{}",
        "sync_enabled": True,
        "sync_interval_minutes": 60
    },
    {
        "type": "gitlab",
        "name": "GitLab Integration",
        "enabled": False,
        "config_encrypted": "{}",
        "sync_enabled": True,
        "sync_interval_minutes": 60
    },
    {
        "type": "notion",
        "name": "Notion Integration",
        "enabled": False,
        "config_encrypted": "{}",
        "sync_enabled": True,
        "sync_interval_minutes": 60
    }
]

for integration in integrations:
    created = delta_manager.create_integration(integration, default_user['id'])
    print(f"Created {integration['name']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup Complete!
# MAGIC 
# MAGIC The orchestrator database has been initialized with:
# MAGIC - Users table
# MAGIC - Projects table
# MAGIC - Tasks table
# MAGIC - Integrations table
# MAGIC - Agent contexts table
# MAGIC - Agent logs table
# MAGIC - Sync logs table
# MAGIC 
# MAGIC Next steps:
# MAGIC 1. Configure your API keys in the environment
# MAGIC 2. Run the agent interface notebook to start interacting
# MAGIC 3. Enable integrations as needed