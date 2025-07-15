#!/usr/bin/env python3
"""
TDD Tests for Data Seeding Functionality (DEL-009)
Test-driven development for data seeding features
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from database_manager import DatabaseManager


class TestDataSeeding(unittest.TestCase):
    """Test data seeding functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create mock database
        with open(self.test_db_path, 'w') as f:
            f.write("empty database")
        
        self.db_manager = DatabaseManager(
            database_path=self.test_db_path,
            backup_directory=os.path.join(self.temp_dir, "backups")
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_seed_development_data(self):
        """Test seeding development environment with test data"""
        # This test will fail initially (TDD red phase)
        seed_result = self.db_manager.seed_development_data()
        
        self.assertIsInstance(seed_result, dict)
        self.assertIn('projects_created', seed_result)
        self.assertIn('tasks_created', seed_result)
        self.assertIn('users_created', seed_result)
        
        # Should create some test data
        self.assertGreater(seed_result['projects_created'], 0)
        self.assertGreater(seed_result['tasks_created'], 0)

    def test_seed_dogfooding_data(self):
        """Test seeding realistic dogfooding data"""
        seed_result = self.db_manager.seed_dogfooding_data()
        
        self.assertIsInstance(seed_result, dict)
        self.assertIn('projects_created', seed_result)
        self.assertIn('tasks_created', seed_result)
        
        # Dogfooding should have more realistic data
        self.assertGreater(seed_result['projects_created'], 3)
        self.assertGreater(seed_result['tasks_created'], 10)

    def test_seed_performance_testing_data(self):
        """Test seeding large dataset for performance testing"""
        seed_result = self.db_manager.seed_performance_testing_data(
            project_count=100,
            tasks_per_project=50
        )
        
        self.assertIsInstance(seed_result, dict)
        self.assertEqual(seed_result['projects_created'], 100)
        self.assertEqual(seed_result['tasks_created'], 5000)

    def test_clear_all_data(self):
        """Test clearing all data from database"""
        # First seed some data
        self.db_manager.seed_development_data()
        
        # Then clear it
        clear_result = self.db_manager.clear_all_data()
        
        self.assertIsInstance(clear_result, dict)
        self.assertIn('projects_deleted', clear_result)
        self.assertIn('tasks_deleted', clear_result)
        
        # Verify data is cleared
        self.assertGreater(clear_result['projects_deleted'], 0)
        self.assertGreater(clear_result['tasks_deleted'], 0)

    def test_seed_with_custom_user(self):
        """Test seeding data with custom user"""
        custom_user = "test_user@example.com"
        
        seed_result = self.db_manager.seed_development_data(created_by=custom_user)
        
        self.assertIn('created_by', seed_result)
        self.assertEqual(seed_result['created_by'], custom_user)

    def test_seed_hierarchical_tasks(self):
        """Test seeding hierarchical task structures"""
        seed_result = self.db_manager.seed_hierarchical_tasks(
            project_id="test_project",
            max_depth=3,
            tasks_per_level=5
        )
        
        self.assertIsInstance(seed_result, dict)
        self.assertIn('tasks_created', seed_result)
        self.assertIn('max_depth_created', seed_result)
        
        self.assertEqual(seed_result['max_depth_created'], 3)
        self.assertGreater(seed_result['tasks_created'], 15)  # 5 + 25 + 125

    def test_seed_with_dependencies(self):
        """Test seeding tasks with dependencies"""
        seed_result = self.db_manager.seed_tasks_with_dependencies(
            project_id="test_project",
            task_count=10,
            dependency_probability=0.3
        )
        
        self.assertIsInstance(seed_result, dict)
        self.assertIn('tasks_created', seed_result)
        self.assertIn('dependencies_created', seed_result)
        
        self.assertEqual(seed_result['tasks_created'], 10)
        self.assertGreater(seed_result['dependencies_created'], 0)

    def test_seed_environment_specific_data(self):
        """Test seeding environment-specific data"""
        # Development should have simple test data
        dev_result = self.db_manager.seed_environment_data('development')
        
        # Staging should have more realistic data
        staging_result = self.db_manager.seed_environment_data('staging')
        
        # Production should have minimal seed data
        prod_result = self.db_manager.seed_environment_data('production')
        
        # Verify different amounts of data for each environment
        self.assertLess(dev_result['projects_created'], staging_result['projects_created'])
        self.assertLess(prod_result['projects_created'], dev_result['projects_created'])

    def test_seed_validates_database_connection(self):
        """Test that seeding validates database connection first"""
        # Mock a connection failure
        with patch.object(self.db_manager, 'validate_database_connection', return_value=False):
            with self.assertRaises(ConnectionError):
                self.db_manager.seed_development_data()

    def test_seed_respects_existing_data(self):
        """Test that seeding respects existing data and doesn't duplicate"""
        # Seed initial data
        first_seed = self.db_manager.seed_development_data()
        
        # Seed again - should not duplicate
        second_seed = self.db_manager.seed_development_data(skip_existing=True)
        
        self.assertEqual(second_seed['projects_created'], 0)
        self.assertEqual(second_seed['tasks_created'], 0)

    def test_seed_with_custom_templates(self):
        """Test seeding with custom data templates"""
        custom_template = {
            'project_template': {
                'name': 'Template Project {}',
                'description': 'A template project for testing',
                'status': 'active',
                'priority': 'medium'
            },
            'task_template': {
                'title': 'Template Task {}',
                'description': 'A template task for testing',
                'status': 'todo',
                'priority': 'medium'
            }
        }
        
        seed_result = self.db_manager.seed_with_template(
            template=custom_template,
            project_count=3,
            tasks_per_project=5
        )
        
        self.assertEqual(seed_result['projects_created'], 3)
        self.assertEqual(seed_result['tasks_created'], 15)


class TestDataSeedingIntegration(unittest.TestCase):
    """Test data seeding integration with real database"""

    def setUp(self):
        """Set up test environment with real database connection"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
        
        # Create mock database file
        with open(self.test_db_path, 'w') as f:
            f.write("mock database content")
        
        # This would use real SQLAlchemy setup
        self.db_manager = DatabaseManager(
            database_path=self.test_db_path,
            backup_directory=os.path.join(self.temp_dir, "backups")
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_seed_creates_valid_database_records(self):
        """Test that seeding creates valid database records"""
        # This test would validate actual database records
        seed_result = self.db_manager.seed_development_data()
        
        # Verify records exist in database
        projects = self.db_manager.get_all_projects()
        tasks = self.db_manager.get_all_tasks()
        
        self.assertEqual(len(projects), seed_result['projects_created'])
        self.assertEqual(len(tasks), seed_result['tasks_created'])
        
        # Verify record integrity
        for project in projects:
            self.assertIsNotNone(project['id'])
            self.assertIsNotNone(project['name'])
            self.assertIsNotNone(project['created_at'])

    def test_seed_maintains_referential_integrity(self):
        """Test that seeding maintains referential integrity"""
        self.db_manager.seed_development_data()
        
        # Verify all tasks have valid project references
        tasks = self.db_manager.get_all_tasks()
        projects = self.db_manager.get_all_projects()
        project_ids = {p['id'] for p in projects}
        
        for task in tasks:
            self.assertIn(task['project_id'], project_ids)

    def test_seed_respects_foreign_key_constraints(self):
        """Test that seeding respects foreign key constraints"""
        # This should not raise any constraint violations
        try:
            self.db_manager.seed_development_data()
            self.db_manager.seed_hierarchical_tasks(
                project_id="non_existent_project",
                max_depth=2,
                tasks_per_level=3
            )
        except Exception as e:
            # Should handle foreign key constraint appropriately
            self.assertIn("foreign key", str(e).lower())


if __name__ == '__main__':
    unittest.main()