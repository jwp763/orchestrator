# Databricks notebook source
# MAGIC %md
# MAGIC # Database Integration Test
# MAGIC
# MAGIC This notebook provides comprehensive integration testing for the database setup:
# MAGIC - ❌ **Drops all tables** in the test schema
# MAGIC - 🔧 **Recreates everything** from scratch
# MAGIC - ✅ **Validates** all functionality works correctly
# MAGIC - 📊 **Reports** on test results
# MAGIC
# MAGIC **Test Database**: `jwp763.orchestrator_test`
# MAGIC
# MAGIC ⚠️ **WARNING**: This will delete all data in the test schema!

# COMMAND ----------


import os
import sys
from datetime import datetime

from pyspark.sql import SparkSession

# Correct order for workspace path modification if needed, then other imports
workspace_root = os.path.abspath(os.path.join(os.getcwd(), os.path.join(os.pardir)))
if workspace_root not in sys.path:
    print(f"Adding {workspace_root} to sys.path")
    sys.path.insert(0, workspace_root)

from src.config import get_settings  # noqa: E402
from src.setup import DatabaseSetup, get_validation_queries  # noqa: E402
from src.storage.delta_manager import DeltaManager  # noqa: E402

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Configuration
# MAGIC Set up test environment with separate schema

# COMMAND ----------

# Initialize test environment
settings = get_settings()
spark = SparkSession.builder.appName("database-integration-test").getOrCreate()

# Override schema for testing
TEST_CATALOG = settings.catalog_name
TEST_SCHEMA = "orchestrator_test"
TEST_FULL_SCHEMA = f"{TEST_CATALOG}.{TEST_SCHEMA}"

print(f"🧪 Test Configuration:")
print(f"  Catalog: {TEST_CATALOG}")
print(f"  Schema: {TEST_SCHEMA}")
print(f"  Full schema: {TEST_FULL_SCHEMA}")
print(f"  Timestamp: {datetime.now()}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Test Setup Class
# MAGIC Enhanced setup class with comprehensive testing capabilities

# COMMAND ----------


class DatabaseIntegrationTest:
    """Comprehensive database integration testing"""

    def __init__(self, spark: SparkSession, catalog: str, schema: str):
        self.spark = spark
        self.db_setup = DatabaseSetup(spark, catalog, schema)
        self.delta_manager = DeltaManager(spark)
        self.test_results = []
        self.start_time = datetime.now()
        self.test_user_id = None
        self.test_project_id = None

    def log_test_result(self, test_name: str, passed: bool, message: str = ""):
        """Log a test result"""
        self.test_results.append({"test": test_name, "passed": passed, "message": message, "timestamp": datetime.now()})
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name} - {message}")

    def test_schema_creation(self):
        """Test schema creation"""
        try:
            self.db_setup.create_schema()

            # Verify schema exists
            schemas_df = self.spark.sql(f"SHOW SCHEMAS IN {self.db_setup.catalog}")
            schema_names = [row.databaseName for row in schemas_df.collect()]

            if self.db_setup.schema in schema_names:
                self.log_test_result(
                    "Schema Creation", True, f"Schema {self.db_setup.full_schema} created successfully"
                )
            else:
                self.log_test_result("Schema Creation", False, f"Schema {self.db_setup.full_schema} not found")

        except Exception as e:
            self.log_test_result("Schema Creation", False, f"Error: {str(e)}")

    def test_table_creation(self):
        """Test all table creation"""
        expected_tables = [
            "users",
            "projects",
            "tasks",
            "task_links",
            "planning_metrics",
            "integrations",
            "agent_contexts",
            "agent_logs",
            "sync_logs",
        ]

        try:
            self.db_setup.create_all_tables()

            # Verify all tables exist
            tables_df = self.spark.sql(f"SHOW TABLES IN {self.db_setup.full_schema}")
            table_names = [row.tableName for row in tables_df.collect()]

            missing_tables = [table for table in expected_tables if table not in table_names]

            if not missing_tables:
                self.log_test_result("Table Creation", True, f"All {len(expected_tables)} tables created successfully")
            else:
                self.log_test_result("Table Creation", False, f"Missing tables: {missing_tables}")

        except Exception as e:
            self.log_test_result("Table Creation", False, f"Error: {str(e)}")

    def test_sample_data_creation(self):
        """Test sample data creation"""
        try:
            sample_data = self.db_setup.create_sample_data()

            # Verify user was created
            users_count = (
                self.spark.sql(f"SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.users").collect()[0]["count"]
            )

            # Verify projects were created
            projects_count = (
                self.spark.sql(f"SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.projects").collect()[0]["count"]
            )

            # Verify tasks were created
            tasks_count = (
                self.spark.sql(f"SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.tasks").collect()[0]["count"]
            )

            # Verify integrations were created
            integrations_count = (
                self.spark.sql(f"SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.integrations")
                .collect()[0]["count"]
            )

            if users_count > 0 and projects_count > 0 and tasks_count > 0 and integrations_count > 0:
                self.log_test_result(
                    "Sample Data Creation",
                    True,
                    f"Created {users_count} users, {projects_count} projects, {tasks_count} tasks, {integrations_count} integrations",
                )
            else:
                self.log_test_result(
                    "Sample Data Creation",
                    False,
                    f"Insufficient data: {users_count} users, {projects_count} projects, {tasks_count} tasks, {integrations_count} integrations",
                )

        except Exception as e:
            self.log_test_result("Sample Data Creation", False, f"Error: {str(e)}")

    def test_hierarchical_structure(self):
        """Test hierarchical task structure"""
        try:
            # Query for hierarchical structure
            hierarchy_df = self.spark.sql(
                f"""
            SELECT
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN parent_id IS NULL THEN 1 END) as root_tasks,
                COUNT(CASE WHEN parent_id IS NOT NULL THEN 1 END) as child_tasks,
                MAX(depth) as max_depth
            FROM {self.db_setup.full_schema}.tasks
            """
            )

            result = hierarchy_df.collect()[0]

            if result.total_tasks > 0 and result.root_tasks > 0 and result.child_tasks > 0:
                self.log_test_result(
                    "Hierarchical Structure",
                    True,
                    f"{result.total_tasks} total tasks, {result.root_tasks} root, {result.child_tasks} children, max depth {result.max_depth}",
                )
            else:
                self.log_test_result(
                    "Hierarchical Structure",
                    False,
                    f"Invalid hierarchy: {result.total_tasks} total, {result.root_tasks} root, {result.child_tasks} children",
                )

        except Exception as e:
            self.log_test_result("Hierarchical Structure", False, f"Error: {str(e)}")

    def test_task_dependencies(self):
        """Test task dependency links"""
        try:
            # Query for task links
            links_df = self.spark.sql(
                f"""
            SELECT
                COUNT(*) as total_links,
                COUNT(DISTINCT link_type) as link_types,
                COUNT(DISTINCT from_task_id) as from_tasks,
                COUNT(DISTINCT to_task_id) as to_tasks
            FROM {self.db_setup.full_schema}.task_links
            """
            )

            result = links_df.collect()[0]

            if result.total_links > 0:
                self.log_test_result(
                    "Task Dependencies",
                    True,
                    f"{result.total_links} links, {result.link_types} types, {result.from_tasks} from tasks, {result.to_tasks} to tasks",
                )
            else:
                self.log_test_result("Task Dependencies", False, "No task links found")

        except Exception as e:
            self.log_test_result("Task Dependencies", False, f"Error: {str(e)}")

    def test_data_integrity(self):
        """Test data integrity constraints"""
        try:
            # Test foreign key relationships
            orphaned_projects = (
                self.spark.sql(
                    f"""
            SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.projects p
            LEFT JOIN {self.db_setup.full_schema}.users u ON p.user_id = u.id
            WHERE u.id IS NULL
            """
                )
                .collect()[0]["count"]
            )

            orphaned_tasks = (
                self.spark.sql(
                    f"""
            SELECT COUNT(*) as count FROM {self.db_setup.full_schema}.tasks t
            LEFT JOIN {self.db_setup.full_schema}.projects p ON t.project_id = p.id
            WHERE p.id IS NULL
            """
                )
                .collect()[0]["count"]
            )

            if orphaned_projects == 0 and orphaned_tasks == 0:
                self.log_test_result("Data Integrity", True, "No orphaned records found")
            else:
                self.log_test_result(
                    "Data Integrity", False, f"{orphaned_projects} orphaned projects, {orphaned_tasks} orphaned tasks"
                )

        except Exception as e:
            self.log_test_result("Data Integrity", False, f"Error: {str(e)}")

    def test_validation_queries(self):
        """Test all validation queries"""
        try:
            validation_queries = get_validation_queries(self.db_setup.full_schema)

            successful_queries = 0
            for query_info in validation_queries:
                try:
                    result_df = self.spark.sql(query_info["query"])
                    row_count = result_df.count()
                    successful_queries += 1
                    print(f"  ✓ {query_info['name']}: {row_count} rows")
                except Exception as e:
                    print(f"  ✗ {query_info['name']}: {str(e)}")

            if successful_queries == len(validation_queries):
                self.log_test_result(
                    "Validation Queries", True, f"All {len(validation_queries)} queries executed successfully"
                )
            else:
                self.log_test_result(
                    "Validation Queries",
                    False,
                    f"Only {successful_queries}/{len(validation_queries)} queries succeeded",
                )

        except Exception as e:
            self.log_test_result("Validation Queries", False, f"Error: {str(e)}")

    def test_hierarchical_crud_operations(self):
        """Test enhanced DeltaManager CRUD operations for hierarchical tasks"""
        try:
            # Setup test data - ensure DeltaManager uses test schema
            self.delta_manager.database = self.db_setup.full_schema
            
            # Create test user and project for our CRUD tests
            user_data = {
                "name": "CRUD Test User",
                "email": "crud@test.com",
                "preferences": {"theme": "dark"},
                "is_active": True
            }
            user = self.delta_manager.create_user(user_data)
            self.test_user_id = user["id"]
            
            project_data = {
                "name": "CRUD Test Project",
                "description": "Test project for hierarchical CRUD operations",
                "status": "active",
                "priority": "high",
                "user_id": self.test_user_id,
                "task_count": 0,  # Explicitly set to avoid schema conflicts
                "completed_task_count": 0,  # Explicitly set to avoid schema conflicts
                "metadata": {},
                "integration_project_ids": {}
            }
            project = self.delta_manager.create_project(project_data, self.test_user_id)
            self.test_project_id = project["id"]
            
            self.log_test_result("CRUD Setup", True, f"Created test user and project")
            
        except Exception as e:
            self.log_test_result("CRUD Setup", False, f"Error: {str(e)}")
            return
    
    def test_create_task_with_hierarchy(self):
        """Test creating tasks with parent-child relationships"""
        try:
            if not self.test_project_id:
                self.log_test_result("Create Hierarchical Task", False, "No test project available")
                return
            
            # Create root task
            root_task_data = {
                "project_id": self.test_project_id,
                "title": "Root Task - Feature Development",
                "description": "Main feature development task",
                "status": "todo",
                "priority": "high",
                "estimated_minutes": 480  # 8 hours
            }
            root_task = self.delta_manager.create_task(root_task_data, self.test_user_id)
            
            # Verify root task has depth 0
            if root_task["depth"] != 0:
                self.log_test_result("Create Hierarchical Task", False, f"Root task depth should be 0, got {root_task['depth']}")
                return
            
            # Create child task
            child_task_data = {
                "project_id": self.test_project_id,
                "parent_id": root_task["id"],
                "title": "Child Task - Design Phase",
                "description": "Design the feature interface",
                "status": "todo",
                "priority": "medium",
                "estimated_minutes": 120  # 2 hours
            }
            child_task = self.delta_manager.create_task(child_task_data, self.test_user_id)
            
            # Verify child task has depth 1
            if child_task["depth"] != 1:
                self.log_test_result("Create Hierarchical Task", False, f"Child task depth should be 1, got {child_task['depth']}")
                return
            
            # Create grandchild task
            grandchild_task_data = {
                "project_id": self.test_project_id,
                "parent_id": child_task["id"],
                "title": "Grandchild Task - UI Mockups",
                "description": "Create detailed UI mockups",
                "status": "todo",
                "priority": "low",
                "estimated_minutes": 60  # 1 hour
            }
            grandchild_task = self.delta_manager.create_task(grandchild_task_data, self.test_user_id)
            
            # Verify grandchild task has depth 2
            if grandchild_task["depth"] != 2:
                self.log_test_result("Create Hierarchical Task", False, f"Grandchild task depth should be 2, got {grandchild_task['depth']}")
                return
            
            # Test depth limit (should fail at depth > 5)
            try:
                deep_task_data = {
                    "project_id": self.test_project_id,
                    "parent_id": grandchild_task["id"],
                    "title": "Deep Task Level 3",
                    "status": "todo"
                }
                # Create tasks until we hit the depth limit
                current_parent = grandchild_task["id"]
                for i in range(4):  # This should eventually fail
                    deep_task_data["parent_id"] = current_parent
                    deep_task_data["title"] = f"Deep Task Level {3+i}"
                    deep_task = self.delta_manager.create_task(deep_task_data.copy(), self.test_user_id)
                    current_parent = deep_task["id"]
                
                # If we get here, the depth limit isn't working
                self.log_test_result("Create Hierarchical Task", False, "Depth limit not enforced")
                return
                
            except ValueError as ve:
                if "exceeds maximum" not in str(ve):
                    self.log_test_result("Create Hierarchical Task", False, f"Unexpected error: {str(ve)}")
                    return
            
            self.log_test_result("Create Hierarchical Task", True, "Successfully created hierarchical tasks with depth validation")
            
        except Exception as e:
            self.log_test_result("Create Hierarchical Task", False, f"Error: {str(e)}")
    
    def test_get_tasks_with_hierarchy(self):
        """Test retrieving tasks with hierarchical filters"""
        try:
            if not self.test_project_id:
                self.log_test_result("Get Tasks with Hierarchy", False, "No test project available")
                return
            
            # Test get_tasks with parent_id filter
            root_tasks = self.delta_manager.get_tasks(parent_id=None, filters={"project_id": self.test_project_id})
            if len(root_tasks) == 0:
                self.log_test_result("Get Tasks with Hierarchy", False, "No root tasks found")
                return
            
            root_task = root_tasks[0]
            
            # Test getting children of root task
            child_tasks = self.delta_manager.get_tasks(parent_id=root_task["id"])
            if len(child_tasks) == 0:
                self.log_test_result("Get Tasks with Hierarchy", False, "No child tasks found")
                return
            
            # Test include_children parameter
            all_project_tasks = self.delta_manager.get_tasks(
                filters={"project_id": self.test_project_id}, 
                include_children=True
            )
            
            # Should be ordered by depth, then created_at
            depths = [task["depth"] for task in all_project_tasks]
            if depths != sorted(depths):
                self.log_test_result("Get Tasks with Hierarchy", False, f"Tasks not properly ordered by depth: {depths}")
                return
            
            self.log_test_result("Get Tasks with Hierarchy", True, f"Successfully retrieved {len(all_project_tasks)} tasks with proper hierarchy")
            
        except Exception as e:
            self.log_test_result("Get Tasks with Hierarchy", False, f"Error: {str(e)}")
    
    def test_get_task_tree(self):
        """Test get_task_tree method for nested structure"""
        try:
            if not self.test_project_id:
                self.log_test_result("Get Task Tree", False, "No test project available")
                return
            
            # Get root task
            root_tasks = self.delta_manager.get_tasks(parent_id=None, filters={"project_id": self.test_project_id})
            if len(root_tasks) == 0:
                self.log_test_result("Get Task Tree", False, "No root tasks found")
                return
            
            root_task_id = root_tasks[0]["id"]
            
            # Get task tree
            task_tree = self.delta_manager.get_task_tree(root_task_id)
            if not task_tree:
                self.log_test_result("Get Task Tree", False, "Task tree not found")
                return
            
            # Verify tree structure
            if "children" not in task_tree:
                self.log_test_result("Get Task Tree", False, "Task tree missing children property")
                return
            
            if "total_estimated_minutes" not in task_tree:
                self.log_test_result("Get Task Tree", False, "Task tree missing total_estimated_minutes")
                return
            
            # Verify total time calculation includes descendants
            if task_tree["total_estimated_minutes"] <= task_tree.get("estimated_minutes", 0):
                self.log_test_result("Get Task Tree", False, "Total estimated minutes should include descendants")
                return
            
            self.log_test_result("Get Task Tree", True, f"Successfully retrieved task tree with {task_tree['child_count']} direct children")
            
        except Exception as e:
            self.log_test_result("Get Task Tree", False, f"Error: {str(e)}")
    
    def test_get_task_ancestors(self):
        """Test get_task_ancestors method"""
        try:
            if not self.test_project_id:
                self.log_test_result("Get Task Ancestors", False, "No test project available")
                return
            
            # Find a deep task (depth > 0)
            deep_tasks = self.delta_manager.get_tasks(filters={"project_id": self.test_project_id})
            deep_task = None
            for task in deep_tasks:
                if task.get("depth", 0) > 1:
                    deep_task = task
                    break
            
            if not deep_task:
                self.log_test_result("Get Task Ancestors", False, "No deep tasks found for ancestor testing")
                return
            
            # Get ancestors
            ancestors = self.delta_manager.get_task_ancestors(deep_task["id"])
            
            # Verify ancestor count matches depth
            expected_ancestor_count = deep_task["depth"]
            if len(ancestors) != expected_ancestor_count:
                self.log_test_result("Get Task Ancestors", False, f"Expected {expected_ancestor_count} ancestors, got {len(ancestors)}")
                return
            
            # Verify ancestor chain (each ancestor's depth should be one less than the next)
            for i, ancestor in enumerate(ancestors):
                expected_depth = i
                if ancestor.get("depth", -1) != expected_depth:
                    self.log_test_result("Get Task Ancestors", False, f"Ancestor {i} has wrong depth: {ancestor.get('depth')} vs {expected_depth}")
                    return
            
            self.log_test_result("Get Task Ancestors", True, f"Successfully retrieved {len(ancestors)} ancestors")
            
        except Exception as e:
            self.log_test_result("Get Task Ancestors", False, f"Error: {str(e)}")
    
    def test_move_task(self):
        """Test move_task method for repositioning in hierarchy"""
        try:
            if not self.test_project_id:
                self.log_test_result("Move Task", False, "No test project available")
                return
            
            # Create a separate branch to test moving
            branch_task_data = {
                "project_id": self.test_project_id,
                "title": "Branch Task - Testing Feature",
                "description": "Separate branch for testing",
                "status": "todo",
                "priority": "medium",
                "estimated_minutes": 180
            }
            branch_task = self.delta_manager.create_task(branch_task_data, self.test_user_id)
            
            # Find a child task to move
            child_tasks = self.delta_manager.get_tasks(filters={"project_id": self.test_project_id})
            child_task = None
            for task in child_tasks:
                if task.get("depth", 0) == 1 and task.get("parent_id"):
                    child_task = task
                    break
            
            if not child_task:
                self.log_test_result("Move Task", False, "No suitable child task found for moving")
                return
            
            # Move task to new parent (branch task)
            success = self.delta_manager.move_task(child_task["id"], branch_task["id"])
            if not success:
                self.log_test_result("Move Task", False, "Move task returned False")
                return
            
            # Verify task was moved
            moved_task = self.delta_manager.get_task(child_task["id"])
            if moved_task["parent_id"] != branch_task["id"]:
                self.log_test_result("Move Task", False, f"Task parent not updated: {moved_task['parent_id']} vs {branch_task['id']}")
                return
            
            # Verify depth was updated
            expected_new_depth = branch_task["depth"] + 1
            if moved_task["depth"] != expected_new_depth:
                self.log_test_result("Move Task", False, f"Task depth not updated: {moved_task['depth']} vs {expected_new_depth}")
                return
            
            # Test circular reference prevention
            try:
                # Try to move parent under child (should fail)
                self.delta_manager.move_task(branch_task["id"], moved_task["id"])
                self.log_test_result("Move Task", False, "Circular reference not prevented")
                return
            except ValueError as ve:
                if "descendant" not in str(ve):
                    self.log_test_result("Move Task", False, f"Wrong error for circular reference: {str(ve)}")
                    return
            
            self.log_test_result("Move Task", True, "Successfully moved task and prevented circular reference")
            
        except Exception as e:
            self.log_test_result("Move Task", False, f"Error: {str(e)}")

    def run_full_test_suite(self):
        """Run complete integration test suite"""
        print(f"🚀 Starting integration test suite for {self.db_setup.full_schema}")
        print(f"Started at: {self.start_time}")
        print("=" * 80)

        # 1. Clean slate - drop existing tables
        print("\n🧹 Phase 1: Cleanup")
        try:
            self.db_setup.drop_all_tables()
            self.log_test_result("Table Cleanup", True, "All tables dropped successfully")
        except Exception as e:
            self.log_test_result("Table Cleanup", False, f"Error: {str(e)}")

        # 2. Test schema creation
        print("\n🏗️ Phase 2: Schema Creation")
        self.test_schema_creation()

        # 3. Test table creation
        print("\n📋 Phase 3: Table Creation")
        self.test_table_creation()

        # 4. Test sample data creation
        print("\n📊 Phase 4: Sample Data")
        self.test_sample_data_creation()

        # 5. Test hierarchical structure
        print("\n🌳 Phase 5: Hierarchical Structure")
        self.test_hierarchical_structure()

        # 6. Test dependencies
        print("\n🔗 Phase 6: Task Dependencies")
        self.test_task_dependencies()

        # 7. Test data integrity
        print("\n🔍 Phase 7: Data Integrity")
        self.test_data_integrity()

        # 8. Test validation queries
        print("\n✅ Phase 8: Validation Queries")
        self.test_validation_queries()

        # 9. Test hierarchical CRUD operations
        print("\n🔧 Phase 9: Hierarchical CRUD Operations")
        self.test_hierarchical_crud_operations()
        self.test_create_task_with_hierarchy()
        self.test_get_tasks_with_hierarchy()
        self.test_get_task_tree()
        self.test_get_task_ancestors()
        self.test_move_task()

        # Generate final report
        self.generate_test_report()

    def generate_test_report(self):
        """Generate comprehensive test report"""
        end_time = datetime.now()
        duration = end_time - self.start_time

        passed_tests = [r for r in self.test_results if r["passed"]]
        failed_tests = [r for r in self.test_results if not r["passed"]]

        print("\n" + "=" * 80)
        print("🏁 INTEGRATION TEST REPORT")
        print("=" * 80)
        print(f"Test Suite: Database Integration Test")
        print(f"Schema: {self.db_setup.full_schema}")
        print(f"Started: {self.start_time}")
        print(f"Completed: {end_time}")
        print(f"Duration: {duration}")
        print(f"Total Tests: {len(self.test_results)}")
        print(f"Passed: {len(passed_tests)} ✅")
        print(f"Failed: {len(failed_tests)} ❌")
        print(f"Success Rate: {len(passed_tests)/len(self.test_results)*100:.1f}%")

        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  • {test['test']}: {test['message']}")

        if len(failed_tests) == 0:
            print("\n🎉 ALL TESTS PASSED! Database setup is working correctly.")
        else:
            print(f"\n⚠️ {len(failed_tests)} tests failed. Please review and fix issues.")

        print("=" * 80)


# COMMAND ----------

# MAGIC %md
# MAGIC ## ⚠️ DESTRUCTIVE TEST EXECUTION
# MAGIC This will drop all tables and recreate everything in the test schema

# COMMAND ----------

# Initialize and run integration tests
test_runner = DatabaseIntegrationTest(spark, TEST_CATALOG, TEST_SCHEMA)

print("⚠️  WARNING: About to run destructive tests!")
print(f"   This will DROP ALL TABLES in {TEST_FULL_SCHEMA}")
print("   and recreate everything from scratch.")
print()

# Run the full test suite
test_runner.run_full_test_suite()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 📊 Detailed Validation Results
# MAGIC Review the actual data created during testing

# COMMAND ----------

# Show table contents for manual verification
print("📋 Table Contents Summary:")
print("=" * 50)

tables_to_check = ["users", "projects", "tasks", "task_links", "integrations"]

for table in tables_to_check:
    try:
        count_df = spark.sql(f"SELECT COUNT(*) as count FROM {TEST_FULL_SCHEMA}.{table}")
        count = count_df.collect()[0].count
        print(f"{table:20} {count:>5} rows")

        if count > 0 and count <= 10:  # Show data for small tables
            print(f"  Sample data from {table}:")
            sample_df = spark.sql(f"SELECT * FROM {TEST_FULL_SCHEMA}.{table} LIMIT 3")
            sample_df.show(truncate=False)
    except Exception as e:
        print(f"{table:20} ERROR: {str(e)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🔍 Advanced Validation Queries
# MAGIC Run complex queries to verify hierarchical functionality

# COMMAND ----------

print("🔍 Advanced Validation:")
print("=" * 50)

# Test hierarchical task query
print("\n1. Hierarchical Task Tree:")
hierarchy_result = spark.sql(
    f"""
WITH RECURSIVE task_tree AS (
    -- Root tasks
    SELECT id, title, parent_id, depth, 0 as level
    FROM {TEST_FULL_SCHEMA}.tasks
    WHERE parent_id IS NULL

    UNION ALL

    -- Child tasks
    SELECT t.id, t.title, t.parent_id, t.depth, tt.level + 1
    FROM {TEST_FULL_SCHEMA}.tasks t
    INNER JOIN task_tree tt ON t.parent_id = tt.id
    WHERE tt.level < 5  -- Prevent infinite recursion
)
SELECT
    CONCAT(REPEAT('  ', level), title) as task_hierarchy,
    depth,
    level
FROM task_tree
ORDER BY level, title
"""
)
hierarchy_result.show(truncate=False)

# Test dependency resolution
print("\n2. Task Dependencies:")
deps_result = spark.sql(
    f"""
SELECT
    t1.title as task,
    t2.title as blocks_task,
    tl.link_type,
    tl.metadata['reason'] as reason
FROM {TEST_FULL_SCHEMA}.task_links tl
JOIN {TEST_FULL_SCHEMA}.tasks t1 ON tl.from_task_id = t1.id
JOIN {TEST_FULL_SCHEMA}.tasks t2 ON tl.to_task_id = t2.id
"""
)
deps_result.show(truncate=False)

# Test time estimates rollup
print("\n3. Time Estimates by Project:")
time_result = spark.sql(
    f"""
SELECT
    p.name as project,
    COUNT(t.id) as total_tasks,
    SUM(COALESCE(t.estimated_minutes, 0)) as total_estimated_minutes,
    SUM(COALESCE(t.actual_minutes, 0)) as total_actual_minutes,
    ROUND(SUM(COALESCE(t.estimated_minutes, 0)) / 60.0, 1) as estimated_hours,
    ROUND(SUM(COALESCE(t.actual_minutes, 0)) / 60.0, 1) as actual_hours
FROM {TEST_FULL_SCHEMA}.projects p
LEFT JOIN {TEST_FULL_SCHEMA}.tasks t ON p.id = t.project_id
GROUP BY p.id, p.name
"""
)
time_result.show(truncate=False)

print("\n✅ Integration test completed!")
print(f"Test schema: {TEST_FULL_SCHEMA}")
print("Ready for production deployment!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 🧹 Cleanup (Optional)
# MAGIC Uncomment and run to clean up test data

# COMMAND ----------

# Uncomment to clean up test schema after testing
# print("🧹 Cleaning up test data...")
# test_runner.db_setup.drop_all_tables()
# spark.sql(f"DROP SCHEMA IF EXISTS {TEST_FULL_SCHEMA}")
# print(f"✅ Test schema {TEST_FULL_SCHEMA} cleaned up")

# COMMAND ----------

print("🏁 Database Integration Test Complete!")
print(f"Tested schema: {TEST_FULL_SCHEMA}")
print("Run this notebook after major code changes to ensure everything works correctly.")
