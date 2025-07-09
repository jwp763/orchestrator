"""Database setup utilities for Databricks orchestrator"""

import uuid
from datetime import datetime
from typing import Dict, Any, List
from pyspark.sql import SparkSession
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    BooleanType,
    IntegerType,
    TimestampType,
    MapType,
    ArrayType,
    DateType,
)


class DatabaseSetup:
    """Handles database initialization and sample data creation"""

    def __init__(self, spark: SparkSession, catalog: str, schema: str):
        self.spark = spark
        self.catalog = catalog
        self.schema = schema
        self.full_schema = f"{catalog}.{schema}"

    def create_schema(self) -> None:
        """Create the catalog schema"""
        print(f"Setting up catalog: {self.catalog}, schema: {self.schema}")
        self.spark.sql(f"CREATE SCHEMA IF NOT EXISTS {self.full_schema}")
        self.spark.sql(f"USE {self.full_schema}")
        print(f"Using schema: {self.full_schema}")

    def drop_all_tables(self) -> None:
        """Drop all tables in the schema (for testing)"""
        print(f"Dropping all tables in {self.full_schema}")

        # Get all tables
        try:
            tables_df = self.spark.sql(f"SHOW TABLES IN {self.full_schema}")
            tables = [row.tableName for row in tables_df.collect()]
        except:
            # Schema might not exist yet
            tables = []

        # Drop in reverse dependency order
        drop_order = [
            "sync_logs",
            "agent_logs",
            "agent_contexts",
            "planning_metrics",
            "task_links",
            "tasks",
            "integrations",
            "projects",
            "users",
        ]

        for table in drop_order:
            if table in tables:
                self.spark.sql(f"DROP TABLE IF EXISTS {self.full_schema}.{table}")
                print(f"✓ Dropped {table}")

    def create_users_table(self) -> None:
        """Create users table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.users (
            id STRING,
            name STRING,
            email STRING,
            preferences MAP<STRING, STRING>,
            is_active BOOLEAN,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Users table created")

    def create_projects_table(self) -> None:
        """Create projects table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.projects (
            id STRING,
            user_id STRING,
            name STRING,
            description STRING,
            status STRING,
            priority STRING,
            start_date DATE,
            end_date DATE,
            task_count INT,
            completed_task_count INT,
            metadata MAP<STRING, STRING>,
            integration_project_ids MAP<STRING, STRING>,
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Projects table created")

    def create_tasks_table(self) -> None:
        """Create hierarchical tasks table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.tasks (
            -- Core fields
            id STRING,
            project_id STRING,
            title STRING,
            description STRING,
            status STRING,
            priority STRING,
            
            -- Hierarchical fields
            parent_id STRING,              -- Self-reference for parent task
            estimated_minutes INT,         -- Time estimate in minutes
            actual_minutes INT,           -- Actual time spent
            depth INT,                    -- Tree depth (0 = root task)
            dependencies ARRAY<STRING>,   -- List of task IDs that must complete first
            
            -- Scheduling fields
            scheduled_start TIMESTAMP,
            scheduled_end TIMESTAMP,
            actual_start TIMESTAMP,
            actual_end TIMESTAMP,
            due_date DATE,
            days_until_due INT,
            is_overdue BOOLEAN,
            
            -- Assignment and metadata
            assigned_to STRING,
            labels ARRAY<STRING>,
            integration_task_ids MAP<STRING, STRING>,
            
            -- Audit fields
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP,
            completed_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Tasks table created with hierarchical support")

    def create_task_links_table(self) -> None:
        """Create task links table for dependencies"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.task_links (
            id STRING,
            from_task_id STRING,
            to_task_id STRING,
            link_type STRING,  -- 'blocks', 'related', 'duplicate'
            metadata MAP<STRING, STRING>,
            created_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Task links table created")

    def create_planning_metrics_table(self) -> None:
        """Create planning metrics table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.planning_metrics (
            id STRING,
            project_id STRING,
            input_length INT,
            tasks_generated INT,
            tree_depth INT,
            total_estimated_minutes INT,
            llm_provider STRING,
            tokens_used INT,
            generation_time_ms INT,
            created_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Planning metrics table created")

    def create_integrations_table(self) -> None:
        """Create integrations table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.integrations (
            id STRING,
            user_id STRING,
            type STRING,
            name STRING,
            enabled BOOLEAN,
            config_encrypted STRING,
            sync_enabled BOOLEAN,
            sync_interval_minutes INT,
            last_sync_at TIMESTAMP,
            sync_status STRING,
            created_by STRING,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Integrations table created")

    def create_agent_contexts_table(self) -> None:
        """Create agent contexts table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.agent_contexts (
            conversation_id STRING,
            user_id STRING,
            project_id STRING,
            task_id STRING,
            messages STRING,  -- JSON serialized messages
            active_task_ids ARRAY<STRING>,
            total_tokens_used INT,
            created_at TIMESTAMP,
            updated_at TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Agent contexts table created")

    def create_agent_logs_table(self) -> None:
        """Create agent logs table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.agent_logs (
            id STRING,
            conversation_id STRING,
            log_level STRING,
            message STRING,
            action STRING,
            provider STRING,
            tokens_used INT,
            response_time_ms INT,
            error_details STRING,
            timestamp TIMESTAMP
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Agent logs table created")

    def create_sync_logs_table(self) -> None:
        """Create sync logs table"""
        self.spark.sql(
            f"""
        CREATE TABLE IF NOT EXISTS {self.full_schema}.sync_logs (
            id STRING,
            integration_id STRING,
            sync_type STRING,
            status STRING,
            items_processed INT,
            items_created INT,
            items_updated INT,
            items_failed INT,
            error_message STRING,
            started_at TIMESTAMP,
            completed_at TIMESTAMP,
            duration_ms INT
        ) USING DELTA
        TBLPROPERTIES (
            'delta.autoOptimize.optimizeWrite' = 'true',
            'delta.autoOptimize.autoCompact' = 'true'
        )
        """
        )
        print("✓ Sync logs table created")

    def optimize_tables(self) -> None:
        """Optimize tables for performance"""
        # Optimize tasks table (most frequently queried)
        self.spark.sql(f"OPTIMIZE {self.full_schema}.tasks ZORDER BY (project_id, parent_id, status)")
        print("✓ Tasks table optimized")

        # Optimize task_links for dependency queries
        self.spark.sql(f"OPTIMIZE {self.full_schema}.task_links ZORDER BY (from_task_id, to_task_id)")
        print("✓ Task links table optimized")

    def create_all_tables(self) -> None:
        """Create all tables in dependency order"""
        print("Creating all tables...")
        self.create_users_table()
        self.create_projects_table()
        self.create_tasks_table()
        self.create_task_links_table()
        self.create_planning_metrics_table()
        self.create_integrations_table()
        self.create_agent_contexts_table()
        self.create_agent_logs_table()
        self.create_sync_logs_table()
        self.optimize_tables()
        print("✅ All tables created successfully")

    def create_sample_user(self) -> str:
        """Create and return sample user ID"""
        user_id = str(uuid.uuid4())
        user_data = {
            "id": user_id,
            "name": "Default User",
            "email": "user@example.com",
            "preferences": {"theme": "light", "notifications": "true"},
            "is_active": True,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Define explicit schema for users
        users_schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("email", StringType(), True),
                StructField("preferences", MapType(StringType(), StringType()), True),
                StructField("is_active", BooleanType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("updated_at", TimestampType(), True),
            ]
        )

        user_df = self.spark.createDataFrame([user_data], users_schema)
        user_df.write.mode("append").saveAsTable(f"{self.full_schema}.users")
        print(f"✓ Created default user: {user_id}")
        return user_id

    def create_sample_integrations(self, user_id: str) -> List[str]:
        """Create sample integrations and return IDs"""
        integrations_data = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "motion",
                "name": "Motion Integration",
                "enabled": False,
                "config_encrypted": "{}",
                "sync_enabled": True,
                "sync_interval_minutes": 30,
                "sync_status": "pending",
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "linear",
                "name": "Linear Integration",
                "enabled": False,
                "config_encrypted": "{}",
                "sync_enabled": True,
                "sync_interval_minutes": 60,
                "sync_status": "pending",
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "gitlab",
                "name": "GitLab Integration",
                "enabled": False,
                "config_encrypted": "{}",
                "sync_enabled": True,
                "sync_interval_minutes": 60,
                "sync_status": "pending",
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "notion",
                "name": "Notion Integration",
                "enabled": False,
                "config_encrypted": "{}",
                "sync_enabled": True,
                "sync_interval_minutes": 60,
                "sync_status": "pending",
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        # Define explicit schema to avoid type inference issues
        integrations_schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("user_id", StringType(), True),
                StructField("type", StringType(), True),
                StructField("name", StringType(), True),
                StructField("enabled", BooleanType(), True),
                StructField("config_encrypted", StringType(), True),
                StructField("sync_enabled", BooleanType(), True),
                StructField("sync_interval_minutes", IntegerType(), True),
                StructField("sync_status", StringType(), True),
                StructField("created_by", StringType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("updated_at", TimestampType(), True),
            ]
        )

        integrations_df = self.spark.createDataFrame(integrations_data, integrations_schema)
        integrations_df.write.mode("append").saveAsTable(f"{self.full_schema}.integrations")
        print(f"✓ Created {len(integrations_data)} sample integrations")
        return [integration["id"] for integration in integrations_data]

    def create_sample_project_and_tasks(self, user_id: str) -> Dict[str, Any]:
        """Create sample hierarchical project and tasks"""
        # Create project
        project_id = str(uuid.uuid4())
        project_data = {
            "id": project_id,
            "user_id": user_id,
            "name": "Sample Hierarchical Project",
            "description": "Demonstrates hierarchical task structure",
            "status": "active",
            "priority": "high",
            "task_count": 0,
            "completed_task_count": 0,
            "metadata": {"template": "standard"},
            "integration_project_ids": {},
            "created_by": user_id,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }

        # Define explicit schema for projects
        projects_schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("user_id", StringType(), True),
                StructField("name", StringType(), True),
                StructField("description", StringType(), True),
                StructField("status", StringType(), True),
                StructField("priority", StringType(), True),
                StructField("task_count", IntegerType(), True),
                StructField("completed_task_count", IntegerType(), True),
                StructField("metadata", MapType(StringType(), StringType()), True),
                StructField("integration_project_ids", MapType(StringType(), StringType()), True),
                StructField("created_by", StringType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("updated_at", TimestampType(), True),
            ]
        )

        project_df = self.spark.createDataFrame([project_data], projects_schema)
        project_df.write.mode("append").saveAsTable(f"{self.full_schema}.projects")
        print(f"✓ Created sample project: {project_id}")

        # Create hierarchical tasks
        root_task_id = str(uuid.uuid4())
        foundation_task_id = str(uuid.uuid4())
        planner_task_id = str(uuid.uuid4())

        sample_tasks = [
            # Root task
            {
                "id": root_task_id,
                "project_id": project_id,
                "parent_id": None,
                "title": "MVP Development",
                "description": "Complete MVP for hierarchical task planning",
                "status": "in_progress",
                "priority": "high",
                "estimated_minutes": 4800,  # 80 hours
                "actual_minutes": None,
                "depth": 0,
                "dependencies": [],
                "labels": ["epic", "mvp"],
                "integration_task_ids": {},
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            # Child tasks
            {
                "id": foundation_task_id,
                "project_id": project_id,
                "parent_id": root_task_id,
                "title": "Foundation Hardening",
                "description": "Extend task model with hierarchical fields",
                "status": "in_progress",
                "priority": "high",
                "estimated_minutes": 480,  # 8 hours
                "actual_minutes": 180,  # 3 hours done
                "depth": 1,
                "dependencies": [],
                "labels": ["backend", "data-model"],
                "integration_task_ids": {},
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
            {
                "id": planner_task_id,
                "project_id": project_id,
                "parent_id": root_task_id,
                "title": "Planner Implementation",
                "description": "Build AI-powered hierarchical task planner",
                "status": "todo",
                "priority": "high",
                "estimated_minutes": 1200,  # 20 hours
                "actual_minutes": None,
                "depth": 1,
                "dependencies": [foundation_task_id],  # Depends on Foundation
                "labels": ["ai", "planner"],
                "integration_task_ids": {},
                "created_by": user_id,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            },
        ]

        # Define explicit schema for tasks
        tasks_schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("project_id", StringType(), True),
                StructField("parent_id", StringType(), True),
                StructField("title", StringType(), True),
                StructField("description", StringType(), True),
                StructField("status", StringType(), True),
                StructField("priority", StringType(), True),
                StructField("estimated_minutes", IntegerType(), True),
                StructField("actual_minutes", IntegerType(), True),
                StructField("depth", IntegerType(), True),
                StructField("dependencies", ArrayType(StringType()), True),
                StructField("labels", ArrayType(StringType()), True),
                StructField("integration_task_ids", MapType(StringType(), StringType()), True),
                StructField("created_by", StringType(), True),
                StructField("created_at", TimestampType(), True),
                StructField("updated_at", TimestampType(), True),
            ]
        )

        tasks_df = self.spark.createDataFrame(sample_tasks, tasks_schema)
        tasks_df.write.mode("append").saveAsTable(f"{self.full_schema}.tasks")
        print(f"✓ Created {len(sample_tasks)} sample hierarchical tasks")

        # Create task dependency link
        task_link_data = {
            "id": str(uuid.uuid4()),
            "from_task_id": foundation_task_id,  # Foundation
            "to_task_id": planner_task_id,  # Planner
            "link_type": "blocks",
            "metadata": {"reason": "Planner requires foundation to be complete"},
            "created_at": datetime.now(),
        }

        # Define explicit schema for task links
        task_links_schema = StructType(
            [
                StructField("id", StringType(), True),
                StructField("from_task_id", StringType(), True),
                StructField("to_task_id", StringType(), True),
                StructField("link_type", StringType(), True),
                StructField("metadata", MapType(StringType(), StringType()), True),
                StructField("created_at", TimestampType(), True),
            ]
        )

        link_df = self.spark.createDataFrame([task_link_data], task_links_schema)
        link_df.write.mode("append").saveAsTable(f"{self.full_schema}.task_links")
        print("✓ Created sample task dependency link")

        return {
            "project_id": project_id,
            "task_ids": [root_task_id, foundation_task_id, planner_task_id],
            "link_id": task_link_data["id"],
        }

    def create_sample_data(self) -> Dict[str, Any]:
        """Create all sample data and return references"""
        print("Creating sample data...")
        user_id = self.create_sample_user()
        integration_ids = self.create_sample_integrations(user_id)
        project_data = self.create_sample_project_and_tasks(user_id)

        return {"user_id": user_id, "integration_ids": integration_ids, **project_data}

    def setup_database(self, include_sample_data: bool = True) -> Dict[str, Any]:
        """Complete database setup"""
        print(f"🚀 Starting database setup for {self.full_schema}")

        self.create_schema()
        self.create_all_tables()

        sample_data = {}
        if include_sample_data:
            sample_data = self.create_sample_data()

        print(f"\n✅ Database setup completed successfully!")
        print(f"Database: {self.full_schema}")
        print("Ready for hierarchical task planning and AI agent interactions.")

        return sample_data


def get_validation_queries(schema: str) -> List[Dict[str, str]]:
    """Get validation queries for testing"""
    return [
        {
            "name": "Table Row Counts",
            "query": f"""
            SELECT 'users' as table_name, COUNT(*) as row_count FROM {schema}.users
            UNION ALL
            SELECT 'projects', COUNT(*) FROM {schema}.projects
            UNION ALL
            SELECT 'tasks', COUNT(*) FROM {schema}.tasks
            UNION ALL
            SELECT 'task_links', COUNT(*) FROM {schema}.task_links
            UNION ALL
            SELECT 'integrations', COUNT(*) FROM {schema}.integrations
            UNION ALL
            SELECT 'planning_metrics', COUNT(*) FROM {schema}.planning_metrics
            UNION ALL
            SELECT 'agent_contexts', COUNT(*) FROM {schema}.agent_contexts
            ORDER BY table_name
            """,
        },
        {
            "name": "Hierarchical Task Structure",
            "query": f"""
            SELECT 
              t.title,
              t.depth,
              t.estimated_minutes,
              t.actual_minutes,
              t.status,
              CASE WHEN t.parent_id IS NULL THEN 'Root Task' ELSE 'Child Task' END as task_type
            FROM {schema}.tasks t
            ORDER BY t.depth, t.created_at
            """,
        },
        {
            "name": "Task Dependencies",
            "query": f"""
            SELECT 
              t1.title as dependent_task,
              t2.title as depends_on_task,
              tl.link_type,
              tl.metadata['reason'] as reason
            FROM {schema}.task_links tl
            JOIN {schema}.tasks t1 ON tl.to_task_id = t1.id
            JOIN {schema}.tasks t2 ON tl.from_task_id = t2.id
            """,
        },
    ]
