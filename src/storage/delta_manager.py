"""Delta table management for Databricks"""

import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
from delta.tables import DeltaTable

from ..models.schemas import ALL_SCHEMAS
from ..config import get_settings


logger = logging.getLogger(__name__)


class DeltaManager:
    """Manages Delta table operations"""
    
    def __init__(self, spark: SparkSession = None):
        self.spark = spark or SparkSession.builder.getOrCreate()
        self.settings = get_settings()
        self.database = self.settings.database_name
    
    def initialize_database(self):
        """Create database and all tables"""
        # Create catalog if needed (may require permissions)
        catalog = self.settings.catalog_name
        schema = self.settings.schema_name
        
        # Create schema in the catalog
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
        self.spark.sql(f"USE {catalog}.{schema}")
        
        # Create tables in order (respecting foreign keys)
        table_order = ["users", "projects", "tasks", "integrations", "agent_contexts", "agent_logs", "sync_logs"]
        
        for table_name in table_order:
            logger.info(f"Creating table: {table_name}")
            schema_sql = ALL_SCHEMAS[table_name]
            self.spark.sql(schema_sql)
    
    def _generate_id(self) -> str:
        """Generate a unique ID"""
        return str(uuid.uuid4())
    
    def _get_table_path(self, table_name: str) -> str:
        """Get the full table path"""
        return f"{self.database}.{table_name}"
    
    # User operations
    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        user_data["id"] = self._generate_id()
        user_data["created_at"] = datetime.now()
        user_data["updated_at"] = datetime.now()
        user_data["is_active"] = user_data.get("is_active", True)
        
        df = self.spark.createDataFrame([user_data])
        df.write.mode("append").saveAsTable(self._get_table_path("users"))
        
        return user_data
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user by ID"""
        df = self.spark.table(self._get_table_path("users")).filter(col("id") == user_id)
        rows = df.collect()
        return rows[0].asDict() if rows else None
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update a user"""
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("users"))
        
        # Build update expression
        update_expr = {k: lit(v) for k, v in updates.items() if k != "id"}
        update_expr["updated_at"] = current_timestamp()
        
        delta_table.update(
            condition=col("id") == user_id,
            set=update_expr
        )
        
        return True
    
    # Project operations
    def create_project(self, project_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new project"""
        project_data["id"] = self._generate_id()
        project_data["created_at"] = datetime.now()
        project_data["updated_at"] = datetime.now()
        project_data["created_by"] = created_by
        project_data["task_count"] = 0
        project_data["completed_task_count"] = 0
        
        df = self.spark.createDataFrame([project_data])
        df.write.mode("append").saveAsTable(self._get_table_path("projects"))
        
        return project_data
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get a project by ID"""
        df = self.spark.table(self._get_table_path("projects")).filter(col("id") == project_id)
        rows = df.collect()
        return rows[0].asDict() if rows else None
    
    def get_projects(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get projects with optional filters"""
        df = self.spark.table(self._get_table_path("projects"))
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    df = df.filter(col(key) == value)
        
        return [row.asDict() for row in df.collect()]
    
    def update_project(self, project_id: str, updates: Dict[str, Any]) -> bool:
        """Update a project"""
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("projects"))
        
        # Build update expression
        update_expr = {k: lit(v) for k, v in updates.items() if k != "id"}
        update_expr["updated_at"] = current_timestamp()
        
        delta_table.update(
            condition=col("id") == project_id,
            set=update_expr
        )
        
        return True
    
    # Task operations
    def create_task(self, task_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new task"""
        task_data["id"] = self._generate_id()
        task_data["created_at"] = datetime.now()
        task_data["updated_at"] = datetime.now()
        task_data["created_by"] = created_by
        task_data["is_overdue"] = False
        
        # Calculate days until due
        if task_data.get("due_date"):
            due_date = task_data["due_date"]
            if isinstance(due_date, str):
                due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
            days_until = (due_date - datetime.now().date()).days
            task_data["days_until_due"] = days_until
            task_data["is_overdue"] = days_until < 0
        
        df = self.spark.createDataFrame([task_data])
        df.write.mode("append").saveAsTable(self._get_table_path("tasks"))
        
        # Update project task count
        self._update_project_task_count(task_data["project_id"])
        
        return task_data
    
    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by ID"""
        df = self.spark.table(self._get_table_path("tasks")).filter(col("id") == task_id)
        rows = df.collect()
        return rows[0].asDict() if rows else None
    
    def get_tasks(self, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Get tasks with optional filters"""
        df = self.spark.table(self._get_table_path("tasks"))
        
        if filters:
            for key, value in filters.items():
                if value is not None:
                    df = df.filter(col(key) == value)
        
        return [row.asDict() for row in df.collect()]
    
    def update_task(self, task_id: str, updates: Dict[str, Any]) -> bool:
        """Update a task"""
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("tasks"))
        
        # Build update expression
        update_expr = {k: lit(v) for k, v in updates.items() if k != "id"}
        update_expr["updated_at"] = current_timestamp()
        
        # Handle completion
        if updates.get("status") == "completed":
            update_expr["completed_at"] = current_timestamp()
        
        delta_table.update(
            condition=col("id") == task_id,
            set=update_expr
        )
        
        # Update project task count if status changed
        if "status" in updates:
            task = self.get_task(task_id)
            if task:
                self._update_project_task_count(task["project_id"])
        
        return True
    
    def _update_project_task_count(self, project_id: str):
        """Update task counts for a project"""
        tasks_df = self.spark.table(self._get_table_path("tasks")).filter(col("project_id") == project_id)
        
        total_count = tasks_df.count()
        completed_count = tasks_df.filter(col("status") == "completed").count()
        
        self.update_project(project_id, {
            "task_count": total_count,
            "completed_task_count": completed_count
        })
    
    # Integration operations
    def create_integration(self, integration_data: Dict[str, Any], created_by: str) -> Dict[str, Any]:
        """Create a new integration"""
        integration_data["id"] = self._generate_id()
        integration_data["created_at"] = datetime.now()
        integration_data["updated_at"] = datetime.now()
        integration_data["created_by"] = created_by
        
        # Encrypt config if encryption key is available
        if self.settings.encryption_key and integration_data.get("config"):
            # In production, use proper encryption
            integration_data["config_encrypted"] = json.dumps(integration_data["config"])
            del integration_data["config"]
        
        df = self.spark.createDataFrame([integration_data])
        df.write.mode("append").saveAsTable(self._get_table_path("integrations"))
        
        return integration_data
    
    def get_integration(self, integration_type: str) -> Optional[Dict[str, Any]]:
        """Get an integration by type"""
        df = self.spark.table(self._get_table_path("integrations")).filter(col("type") == integration_type)
        rows = df.collect()
        
        if rows:
            integration = rows[0].asDict()
            # Decrypt config if needed
            if integration.get("config_encrypted"):
                integration["config"] = json.loads(integration["config_encrypted"])
            return integration
        
        return None
    
    # Agent context operations
    def create_agent_context(self, user_id: str) -> Dict[str, Any]:
        """Create a new agent context"""
        context_data = {
            "conversation_id": self._generate_id(),
            "user_id": user_id,
            "messages": json.dumps([]),
            "active_task_ids": [],
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "total_tokens_used": 0
        }
        
        df = self.spark.createDataFrame([context_data])
        df.write.mode("append").saveAsTable(self._get_table_path("agent_contexts"))
        
        return context_data
    
    def get_agent_context(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get an agent context"""
        df = self.spark.table(self._get_table_path("agent_contexts")).filter(col("conversation_id") == conversation_id)
        rows = df.collect()
        
        if rows:
            context = rows[0].asDict()
            context["messages"] = json.loads(context["messages"])
            return context
        
        return None
    
    def update_agent_context(self, conversation_id: str, updates: Dict[str, Any]) -> bool:
        """Update an agent context"""
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("agent_contexts"))
        
        # Handle messages serialization
        if "messages" in updates:
            updates["messages"] = json.dumps(updates["messages"])
        
        # Build update expression
        update_expr = {k: lit(v) for k, v in updates.items() if k != "conversation_id"}
        update_expr["updated_at"] = current_timestamp()
        
        delta_table.update(
            condition=col("conversation_id") == conversation_id,
            set=update_expr
        )
        
        return True
    
    # Agent log operations
    def create_agent_log(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an agent log entry"""
        log_data["id"] = self._generate_id()
        log_data["timestamp"] = datetime.now()
        
        df = self.spark.createDataFrame([log_data])
        df.write.mode("append").saveAsTable(self._get_table_path("agent_logs"))
        
        return log_data