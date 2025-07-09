import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
import json
import logging

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, current_timestamp
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    BooleanType,
    IntegerType,
    TimestampType,
    MapType,
    ArrayType,
)
from delta.tables import DeltaTable

from src.models.project import Project
from src.models.task import Task
from src.models.schemas import ALL_SCHEMAS
from src.config import get_settings
from src.storage.repositories.base import BaseStorageRepository

logger = logging.getLogger(__name__)


class DeltaStorageRepository(BaseStorageRepository):
    def initialize(self, config: Dict[str, Any]) -> None:
        self.spark = SparkSession.builder.getOrCreate()
        self.settings = get_settings()
        self.database = self.settings.database_name

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
        return str(uuid.uuid4())

    def _get_table_path(self, table_name: str) -> str:
        return f"{self.database}.{table_name}"

    def create_project(self, project: Project) -> Project:
        project.id = self._generate_id()
        project.created_at = datetime.now()
        project.updated_at = datetime.now()

        project_dict = project.model_dump()

        df = self.spark.createDataFrame([project_dict])
        df.write.mode("append").saveAsTable(self._get_table_path("projects"))

        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        df = self.spark.table(self._get_table_path("projects")).filter(col("id") == project_id)
        rows = df.collect()
        if not rows:
            return None
        return Project.model_validate(rows[0].asDict())

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[Project]:
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("projects"))

        update_expr = {k: lit(v) for k, v in updates.items() if k != "id"}
        update_expr["updated_at"] = current_timestamp()

        delta_table.update(condition=col("id") == project_id, set=update_expr)

        return self.get_project(project_id)

    def create_task(self, task: Task) -> Task:
        task.id = self._generate_id()
        task.created_at = datetime.now()
        task.updated_at = datetime.now()

        task_dict = task.model_dump()

        df = self.spark.createDataFrame([task_dict])
        df.write.mode("append").saveAsTable(self._get_table_path("tasks"))

        self._update_project_task_count(task.project_id)

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        df = self.spark.table(self._get_table_path("tasks")).filter(col("id") == task_id)
        rows = df.collect()
        if not rows:
            return None
        return Task.model_validate(rows[0].asDict())

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        delta_table = DeltaTable.forName(self.spark, self._get_table_path("tasks"))

        update_expr = {k: lit(v) for k, v in updates.items() if k != "id"}
        update_expr["updated_at"] = current_timestamp()

        if updates.get("status") == "completed":
            update_expr["completed_at"] = current_timestamp()

        delta_table.update(condition=col("id") == task_id, set=update_expr)

        task = self.get_task(task_id)
        if task and "status" in updates:
            self._update_project_task_count(task.project_id)

        return task

    def get_tasks_by_project(self, project_id: str) -> List[Task]:
        df = self.spark.table(self._get_table_path("tasks")).filter(col("project_id") == project_id)
        return [Task.model_validate(row.asDict()) for row in df.collect()]

    def _update_project_task_count(self, project_id: str):
        tasks_df = self.spark.table(self._get_table_path("tasks")).filter(col("project_id") == project_id)

        total_count = tasks_df.count()
        completed_count = tasks_df.filter(col("status") == "completed").count()

        self.update_project(project_id, {"task_count": total_count, "completed_task_count": completed_count})
