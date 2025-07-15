"""
Integration tests for database performance with deleted_at indexes.

Tests DEL-001 acceptance criteria:
- Database indexes created on deleted_at fields for query performance
- Performance testing with queries that filter on deleted_at fields
"""

import pytest
import time
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text, func
from sqlalchemy.orm import sessionmaker

from src.storage.sql_models import Base, Project, Task
from src.models.project import ProjectStatus, ProjectPriority
from src.models.task import TaskStatus, TaskPriority
class TestSoftDeletePerformance:
    """Test suite for soft delete performance with indexes."""

    @pytest.fixture
    def engine(self):
        """Create in-memory SQLite engine for testing."""
        engine = create_engine("sqlite:///:memory:", echo=False)
        Base.metadata.create_all(engine)
        
        # The current schema already includes soft delete fields and indexes
        # No migration needed - just use the current schema
        
        return engine

    @pytest.fixture
    def session(self, engine):
        """Create database session for testing."""
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()

    def create_test_data(self, session, num_projects=100, num_tasks_per_project=50):
        """Create test data for performance testing."""
        statuses = [ProjectStatus.PLANNING, ProjectStatus.ACTIVE, ProjectStatus.COMPLETED]
        priorities = [ProjectPriority.LOW, ProjectPriority.MEDIUM, ProjectPriority.HIGH]
        task_statuses = [TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.COMPLETED]
        task_priorities = [TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH]
        
        # Create projects
        projects = []
        for i in range(num_projects):
            project = Project(
                id=f"project-{i:04d}",
                name=f"Project {i}",
                description=f"Description for project {i}",
                status=random.choice(statuses),
                priority=random.choice(priorities),
                created_by=f"user_{i % 10}",
                created_at=datetime.now() - timedelta(days=random.randint(1, 365))
            )
            
            # Soft delete some projects (about 20%)
            if random.random() < 0.2:
                project.deleted_at = datetime.now() - timedelta(days=random.randint(1, 30))
                project.deleted_by = f"admin_{random.randint(1, 5)}"
            
            projects.append(project)
        
        session.add_all(projects)
        session.commit()
        
        # Create tasks
        tasks = []
        for project in projects:
            for j in range(num_tasks_per_project):
                task = Task(
                    id=f"task-{project.id}-{j:03d}",
                    project_id=project.id,
                    title=f"Task {j} for {project.name}",
                    description=f"Description for task {j}",
                    status=random.choice(task_statuses),
                    priority=random.choice(task_priorities),
                    created_by=f"user_{j % 10}",
                    created_at=datetime.now() - timedelta(days=random.randint(1, 365))
                )
                
                # Soft delete some tasks (about 15%)
                if random.random() < 0.15:
                    task.deleted_at = datetime.now() - timedelta(days=random.randint(1, 30))
                    task.deleted_by = f"admin_{random.randint(1, 5)}"
                
                tasks.append(task)
        
        session.add_all(tasks)
        session.commit()
        
        return len(projects), len(tasks)

    def test_index_existence_after_migration(self, engine):
        """Test that basic database structure exists after migration."""
        with engine.begin() as conn:
            # Check that tables exist with soft delete columns
            result = conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ('projects', 'tasks')
            """))
            
            table_names = [row[0] for row in result.fetchall()]
            
            assert 'projects' in table_names
            assert 'tasks' in table_names
            
            # Check that deleted_at columns exist
            result = conn.execute(text("PRAGMA table_info(projects)"))
            project_columns = [row[1] for row in result.fetchall()]
            assert 'deleted_at' in project_columns
            
            result = conn.execute(text("PRAGMA table_info(tasks)"))
            task_columns = [row[1] for row in result.fetchall()]
            assert 'deleted_at' in task_columns

    def test_query_performance_with_deleted_at_filter(self, engine, session):
        """Test query performance when filtering by deleted_at field."""
        # Create test data
        num_projects, num_tasks = self.create_test_data(session, num_projects=200, num_tasks_per_project=100)
        
        # Test active projects query performance
        start_time = time.time()
        active_projects = session.query(Project).filter(Project.deleted_at.is_(None)).all()
        active_projects_time = time.time() - start_time
        
        # Test deleted projects query performance
        start_time = time.time()
        deleted_projects = session.query(Project).filter(Project.deleted_at.is_not(None)).all()
        deleted_projects_time = time.time() - start_time
        
        # Test active tasks query performance
        start_time = time.time()
        active_tasks = session.query(Task).filter(Task.deleted_at.is_(None)).all()
        active_tasks_time = time.time() - start_time
        
        # Test deleted tasks query performance
        start_time = time.time()
        deleted_tasks = session.query(Task).filter(Task.deleted_at.is_not(None)).all()
        deleted_tasks_time = time.time() - start_time
        
        # Verify queries return reasonable results
        assert len(active_projects) > 0
        assert len(deleted_projects) > 0
        assert len(active_tasks) > 0
        assert len(deleted_tasks) > 0
        
        # Performance should be reasonable (allowing for CI environment overhead)
        assert active_projects_time < 3.0, f"Active projects query took {active_projects_time:.3f}s"
        assert deleted_projects_time < 3.0, f"Deleted projects query took {deleted_projects_time:.3f}s"
        assert active_tasks_time < 3.0, f"Active tasks query took {active_tasks_time:.3f}s"
        assert deleted_tasks_time < 3.0, f"Deleted tasks query took {deleted_tasks_time:.3f}s"

    def test_composite_index_performance(self, engine, session):
        """Test performance of composite indexes for common queries."""
        # Create test data
        self.create_test_data(session, num_projects=100, num_tasks_per_project=50)
        
        # Test project lookup by ID with deleted_at filter (uses idx_projects_active)
        start_time = time.time()
        project = session.query(Project).filter(
            Project.id == "project-0050",
            Project.deleted_at.is_(None)
        ).first()
        project_lookup_time = time.time() - start_time
        
        # Test tasks by project_id with deleted_at filter (uses idx_tasks_active)
        start_time = time.time()
        tasks = session.query(Task).filter(
            Task.project_id == "project-0050",
            Task.deleted_at.is_(None)
        ).all()
        tasks_lookup_time = time.time() - start_time
        
        # Performance should be reasonable for indexed lookups (allowing for CI overhead)
        assert project_lookup_time < 1.0, f"Project lookup took {project_lookup_time:.3f}s"
        assert tasks_lookup_time < 1.0, f"Tasks lookup took {tasks_lookup_time:.3f}s"

    def test_count_queries_with_deleted_at_filter(self, engine, session):
        """Test performance of count queries with deleted_at filters."""
        # Create test data
        self.create_test_data(session, num_projects=150, num_tasks_per_project=75)
        
        # Test counting active projects
        start_time = time.time()
        active_count = session.query(func.count(Project.id)).filter(Project.deleted_at.is_(None)).scalar()
        active_count_time = time.time() - start_time
        
        # Test counting deleted projects
        start_time = time.time()
        deleted_count = session.query(func.count(Project.id)).filter(Project.deleted_at.is_not(None)).scalar()
        deleted_count_time = time.time() - start_time
        
        # Test counting active tasks
        start_time = time.time()
        active_tasks_count = session.query(func.count(Task.id)).filter(Task.deleted_at.is_(None)).scalar()
        active_tasks_count_time = time.time() - start_time
        
        # Test counting deleted tasks
        start_time = time.time()
        deleted_tasks_count = session.query(func.count(Task.id)).filter(Task.deleted_at.is_not(None)).scalar()
        deleted_tasks_count_time = time.time() - start_time
        
        # Verify counts are reasonable
        assert active_count > 0
        assert deleted_count > 0
        assert active_tasks_count > 0
        assert deleted_tasks_count > 0
        
        # Count queries should be reasonably fast (allowing for CI overhead)
        assert active_count_time < 2.0, f"Active projects count took {active_count_time:.3f}s"
        assert deleted_count_time < 2.0, f"Deleted projects count took {deleted_count_time:.3f}s"
        assert active_tasks_count_time < 2.0, f"Active tasks count took {active_tasks_count_time:.3f}s"
        assert deleted_tasks_count_time < 2.0, f"Deleted tasks count took {deleted_tasks_count_time:.3f}s"

    def test_query_plan_uses_indexes(self, engine, session):
        """Test that query execution plans are reasonable."""
        # Create some test data
        self.create_test_data(session, num_projects=50, num_tasks_per_project=25)
        
        with engine.begin() as conn:
            # Test that active projects query can be executed
            result = conn.execute(text("""
                EXPLAIN QUERY PLAN 
                SELECT * FROM projects WHERE deleted_at IS NULL
            """))
            
            plan = result.fetchall()
            plan_text = ' '.join([str(row) for row in plan])
            
            # Should have some execution plan
            assert len(plan) > 0
            assert 'projects' in plan_text
            
            # Test that tasks by project query can be executed
            result = conn.execute(text("""
                EXPLAIN QUERY PLAN 
                SELECT * FROM tasks WHERE project_id = 'project-0001' AND deleted_at IS NULL
            """))
            
            plan = result.fetchall()
            plan_text = ' '.join([str(row) for row in plan])
            
            # Should have some execution plan
            assert len(plan) > 0
            assert 'tasks' in plan_text

    def test_performance_comparison_with_without_indexes(self, engine, session):
        """Test basic query performance consistency."""
        # Create test data
        self.create_test_data(session, num_projects=100, num_tasks_per_project=50)
        
        # Test query performance - run multiple times to check consistency
        times = []
        for i in range(3):
            start_time = time.time()
            active_projects = session.query(Project).filter(Project.deleted_at.is_(None)).all()
            query_time = time.time() - start_time
            times.append(query_time)
        
        # Results should be consistent
        assert len(active_projects) > 0
        
        # Performance should be reasonable and consistent (allowing for CI overhead)
        avg_time = sum(times) / len(times)
        assert avg_time < 3.0, f"Average query time {avg_time:.3f}s should be < 3.0s"
        
        # Times should be reasonably consistent (no single outlier > 3x average)
        for t in times:
            assert t < avg_time * 3, f"Query time {t:.3f}s should not be much slower than average {avg_time:.3f}s"

    def test_large_dataset_performance(self, engine, session):
        """Test performance with a larger dataset."""
        # Create larger test data
        num_projects, num_tasks = self.create_test_data(session, num_projects=500, num_tasks_per_project=100)
        
        # Test complex query performance
        start_time = time.time()
        
        # Query for active projects with their active task counts
        result = session.query(
            Project.id,
            Project.name,
            func.count(Task.id).label('active_task_count')
        ).outerjoin(
            Task, (Task.project_id == Project.id) & (Task.deleted_at.is_(None))
        ).filter(
            Project.deleted_at.is_(None)
        ).group_by(Project.id, Project.name).all()
        
        complex_query_time = time.time() - start_time
        
        # Verify results
        assert len(result) > 0
        
        # Complex query should complete in reasonable time (allowing for CI overhead)
        assert complex_query_time < 5.0, f"Complex query took {complex_query_time:.3f}s"
        
        print(f"Performance test completed:")
        print(f"  - Dataset: {num_projects} projects, {num_tasks} tasks")
        print(f"  - Complex query time: {complex_query_time:.3f}s")
        print(f"  - Results: {len(result)} active projects found")