#!/usr/bin/env python3
"""
TDD Tests for Database Backup Functionality (DEL-009)
Test-driven development for database backup features
"""

import unittest
import tempfile
import os
import shutil
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))

from database_manager import DatabaseManager


class TestDatabaseBackup(unittest.TestCase):
    """Test database backup functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db_path = os.path.join(self.temp_dir, "test.db")
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Create mock database file
        with open(self.test_db_path, 'w') as f:
            f.write("mock database content")
        
        self.db_manager = DatabaseManager(
            database_path=self.test_db_path,
            backup_directory=self.backup_dir
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_backup_database_creates_timestamped_file(self):
        """Test that backup creates a timestamped backup file"""
        # This test will fail initially (TDD red phase)
        with patch('database_manager.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 7, 15, 10, 30, 45)
            mock_datetime.strftime = datetime.strftime
            
            backup_path = self.db_manager.backup_database()
            
            expected_filename = "test_backup_20250715_103045.db"
            expected_path = os.path.join(self.backup_dir, expected_filename)
            
            self.assertEqual(backup_path, expected_path)
            self.assertTrue(os.path.exists(backup_path))

    def test_backup_database_copies_original_content(self):
        """Test that backup contains same content as original"""
        backup_path = self.db_manager.backup_database()
        
        with open(self.test_db_path, 'r') as original:
            original_content = original.read()
        
        with open(backup_path, 'r') as backup:
            backup_content = backup.read()
            
        self.assertEqual(original_content, backup_content)

    def test_backup_database_returns_backup_path(self):
        """Test that backup returns the path to the backup file"""
        backup_path = self.db_manager.backup_database()
        
        self.assertIsInstance(backup_path, str)
        self.assertTrue(backup_path.endswith('.db'))
        self.assertTrue(os.path.exists(backup_path))

    def test_backup_database_handles_missing_source(self):
        """Test backup handles missing source database gracefully"""
        os.remove(self.test_db_path)
        
        with self.assertRaises(FileNotFoundError):
            self.db_manager.backup_database()

    def test_backup_database_creates_backup_directory(self):
        """Test that backup creates backup directory if it doesn't exist"""
        shutil.rmtree(self.backup_dir)
        self.assertFalse(os.path.exists(self.backup_dir))
        
        self.db_manager.backup_database()
        
        self.assertTrue(os.path.exists(self.backup_dir))

    def test_backup_database_validates_file_integrity(self):
        """Test that backup validates file integrity"""
        backup_path = self.db_manager.backup_database()
        
        # Should return True for successful backup
        integrity_result = self.db_manager.validate_backup_integrity(backup_path)
        self.assertTrue(integrity_result)

    def test_backup_database_handles_insufficient_disk_space(self):
        """Test backup handles insufficient disk space"""
        with patch('shutil.copy2') as mock_copy:
            mock_copy.side_effect = OSError("No space left on device")
            
            with self.assertRaises(OSError):
                self.db_manager.backup_database()

    def test_backup_database_preserves_file_permissions(self):
        """Test that backup preserves file permissions"""
        # Set specific permissions on original
        os.chmod(self.test_db_path, 0o644)
        
        backup_path = self.db_manager.backup_database()
        
        original_perms = os.stat(self.test_db_path).st_mode & 0o777
        backup_perms = os.stat(backup_path).st_mode & 0o777
        
        self.assertEqual(original_perms, backup_perms)

    def test_backup_database_with_custom_name(self):
        """Test backup with custom backup name"""
        custom_name = "custom_backup_name"
        backup_path = self.db_manager.backup_database(backup_name=custom_name)
        
        self.assertIn(custom_name, backup_path)
        self.assertTrue(os.path.exists(backup_path))

    def test_backup_database_returns_metadata(self):
        """Test that backup returns metadata about the backup"""
        backup_result = self.db_manager.backup_database_with_metadata()
        
        self.assertIsInstance(backup_result, dict)
        self.assertIn('backup_path', backup_result)
        self.assertIn('original_size', backup_result)
        self.assertIn('backup_size', backup_result)
        self.assertIn('created_at', backup_result)
        self.assertIn('checksum', backup_result)


class TestDatabaseBackupCleanup(unittest.TestCase):
    """Test database backup cleanup functionality"""

    def setUp(self):
        """Set up test environment with multiple backups"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_dir = os.path.join(self.temp_dir, "backups")
        os.makedirs(self.backup_dir)
        
        # Create 15 mock backup files
        for i in range(15):
            backup_file = os.path.join(self.backup_dir, f"test_backup_2025071{i:02d}_120000.db")
            with open(backup_file, 'w') as f:
                f.write(f"backup content {i}")
        
        self.db_manager = DatabaseManager(
            database_path="/tmp/test.db",
            backup_directory=self.backup_dir
        )

    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir)

    def test_cleanup_old_backups_keeps_recent_ten(self):
        """Test that cleanup keeps only the 10 most recent backups"""
        # Should have 15 backups initially
        initial_backups = len(os.listdir(self.backup_dir))
        self.assertEqual(initial_backups, 15)
        
        self.db_manager.cleanup_old_backups(keep_count=10)
        
        remaining_backups = len(os.listdir(self.backup_dir))
        self.assertEqual(remaining_backups, 10)

    def test_cleanup_old_backups_keeps_newest_files(self):
        """Test that cleanup keeps the newest backup files"""
        # Get file modification times before cleanup
        backup_files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir)]
        backup_files.sort(key=os.path.getmtime, reverse=True)
        
        newest_10 = backup_files[:10]
        
        self.db_manager.cleanup_old_backups(keep_count=10)
        
        remaining_files = [os.path.join(self.backup_dir, f) for f in os.listdir(self.backup_dir)]
        remaining_files.sort(key=os.path.getmtime, reverse=True)
        
        for expected_file in newest_10:
            self.assertIn(expected_file, remaining_files)

    def test_cleanup_old_backups_with_custom_count(self):
        """Test cleanup with custom keep count"""
        self.db_manager.cleanup_old_backups(keep_count=5)
        
        remaining_backups = len(os.listdir(self.backup_dir))
        self.assertEqual(remaining_backups, 5)

    def test_cleanup_old_backups_handles_empty_directory(self):
        """Test cleanup handles empty backup directory"""
        # Remove all backups
        for f in os.listdir(self.backup_dir):
            os.remove(os.path.join(self.backup_dir, f))
        
        # Should not raise error
        self.db_manager.cleanup_old_backups(keep_count=10)
        
        remaining_backups = len(os.listdir(self.backup_dir))
        self.assertEqual(remaining_backups, 0)


if __name__ == '__main__':
    unittest.main()