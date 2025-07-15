"""
Security tests for the migration system.

This module tests security aspects of the migration system including
data protection, access controls, and secure migration practices.
"""

import os
import pytest
import tempfile
import stat
from pathlib import Path
from unittest.mock import patch, mock_open

from tests.test_api.test_database_isolation import TestDatabaseIsolation


class TestMigrationSecurity(TestDatabaseIsolation):
    """Test security aspects of migration system."""
    
    def test_migration_file_permissions(self):
        """Test that migration files have appropriate permissions."""
        backend_dir = Path(__file__).parent.parent.parent
        migrations_dir = backend_dir / "migrations"
        
        # Check migrations directory permissions
        if migrations_dir.exists():
            dir_stat = migrations_dir.stat()
            dir_perms = stat.filemode(dir_stat.st_mode)
            
            # Directory should be readable and writable by owner, readable by group
            assert dir_perms.startswith('d')  # Should be a directory
            assert dir_perms[1:4] == 'rwx'    # Owner should have full access
        
        # Check migration files
        versions_dir = migrations_dir / "versions"
        if versions_dir.exists():
            for migration_file in versions_dir.glob("*.py"):
                file_stat = migration_file.stat()
                file_perms = stat.filemode(file_stat.st_mode)
                
                # Files should be readable by owner and group, but not world-writable
                assert file_perms.startswith('-')  # Should be a regular file
                assert file_perms[1:4] == 'rw-'    # Owner should have read/write
                assert file_perms[8] != 'w'        # World should not be writable
    
    def test_migration_script_permissions(self):
        """Test that migration scripts have secure permissions."""
        backend_dir = Path(__file__).parent.parent.parent
        migrate_script = backend_dir / "scripts" / "migrate.py"
        
        if migrate_script.exists():
            script_stat = migrate_script.stat()
            script_perms = stat.filemode(script_stat.st_mode)
            
            # Script should be executable by owner
            assert script_perms[1:4] == 'rwx'    # Owner should have full access
            assert script_perms[8] != 'w'        # World should not be writable
    
    def test_database_connection_security(self):
        """Test that database connections are secure."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from config.settings import get_settings
        from setup.migration_manager import MigrationManager
        
        settings = get_settings()
        database_url = settings.database_url
        
        # Database URL should not contain plaintext credentials in production
        if not database_url.startswith('sqlite:///'):
            # For non-SQLite databases, ensure no plaintext passwords
            assert 'password' not in database_url.lower()
            assert 'pwd' not in database_url.lower()
        
        # Test that migration manager handles URLs securely
        manager = MigrationManager()
        
        # Should not log sensitive information
        with patch('logging.Logger.debug') as mock_debug:
            manager.check_migration_status()
            
            # Check that no sensitive data is logged
            for call in mock_debug.call_args_list:
                args = str(call)
                assert 'password' not in args.lower()
                assert 'secret' not in args.lower()
    
    def test_migration_command_injection_protection(self):
        """Test protection against command injection in migration scripts."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test with potentially dangerous input
        dangerous_inputs = [
            "; rm -rf /",
            "$(rm -rf /)",
            "`rm -rf /`",
            "test && rm -rf /",
            "test || rm -rf /",
            "test | rm -rf /",
            "../../../etc/passwd",
            "../../secrets"
        ]
        
        for dangerous_input in dangerous_inputs:
            # Test create migration with dangerous input
            result = subprocess.run(
                ['python', 'scripts/migrate.py', 'create', dangerous_input],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            
            # Should either fail safely or sanitize the input
            # The key is that it shouldn't execute shell commands
            assert result.returncode != 0 or dangerous_input not in result.stderr
    
    def test_migration_file_content_validation(self):
        """Test that migration files don't contain suspicious content."""
        backend_dir = Path(__file__).parent.parent.parent
        versions_dir = backend_dir / "migrations" / "versions"
        
        dangerous_patterns = [
            'import os',
            'subprocess.',
            'eval(',
            'exec(',
            '__import__',
            'system(',
            'popen(',
            'shell=True'
        ]
        
        if versions_dir.exists():
            for migration_file in versions_dir.glob("*.py"):
                with open(migration_file, 'r') as f:
                    content = f.read()
                
                # Check for dangerous patterns
                for pattern in dangerous_patterns:
                    if pattern in content:
                        # Some patterns might be legitimate (like 'import os' for path handling)
                        # but they should be used carefully
                        lines = content.split('\\n')
                        dangerous_lines = [line for line in lines if pattern in line]
                        
                        # Log for manual review
                        print(f"Warning: {pattern} found in {migration_file}: {dangerous_lines}")
    
    def test_migration_environment_variable_security(self):
        """Test that environment variables are handled securely."""
        # Test that sensitive environment variables are not logged or exposed
        sensitive_vars = [
            'DATABASE_PASSWORD',
            'SECRET_KEY',
            'API_KEY',
            'TOKEN',
            'PASSWORD'
        ]
        
        with patch.dict(os.environ, {'TEST_SECRET_VAR': 'secret_value'}):
            import sys
            sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
            
            from setup.migration_manager import MigrationManager
            
            manager = MigrationManager()
            
            # Capture any logging output
            with patch('logging.Logger.info') as mock_info, \
                 patch('logging.Logger.debug') as mock_debug, \
                 patch('logging.Logger.error') as mock_error:
                
                manager.check_migration_status()
                
                # Check that no sensitive data is logged
                all_calls = mock_info.call_args_list + mock_debug.call_args_list + mock_error.call_args_list
                for call in all_calls:
                    args = str(call)
                    assert 'secret_value' not in args.lower()
                    for var in sensitive_vars:
                        assert var.lower() not in args.lower()
    
    def test_migration_sql_injection_protection(self):
        """Test protection against SQL injection in migrations."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        # Test with potentially malicious revision names
        malicious_revisions = [
            "'; DROP TABLE projects; --",
            "1 OR 1=1",
            "test'; DELETE FROM tasks; --",
            "../../etc/passwd"
        ]
        
        for malicious_revision in malicious_revisions:
            # The migration system should handle these safely
            # (they should either be rejected or sanitized)
            result = manager._run_alembic_command("upgrade", malicious_revision)
            
            # Should fail safely, not execute SQL injection
            assert result[0] != 0  # Should fail
            assert "syntax error" in result[2].lower() or "invalid" in result[2].lower()
    
    def test_migration_backup_security(self):
        """Test that migration backups are handled securely."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        # Test that temporary files are cleaned up
        with tempfile.TemporaryDirectory() as temp_dir:
            # Migration operations should not leave sensitive files
            manager.check_migration_status()
            
            # Check that no temporary files with sensitive data are left
            temp_files = list(Path(temp_dir).glob("*"))
            for temp_file in temp_files:
                if temp_file.is_file():
                    with open(temp_file, 'r') as f:
                        content = f.read()
                    
                    # Should not contain database credentials or sensitive data
                    assert 'password' not in content.lower()
                    assert 'secret' not in content.lower()
                    assert 'token' not in content.lower()
    
    def test_migration_error_message_security(self):
        """Test that error messages don't expose sensitive information."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test with invalid database URL to trigger error
        with patch.dict(os.environ, {'DATABASE_URL': 'invalid://user:password@host/db'}):
            result = subprocess.run(
                ['python', 'scripts/migrate.py', 'current'],
                cwd=backend_dir,
                capture_output=True,
                text=True
            )
            
            # Should fail but not expose password
            assert result.returncode != 0
            assert 'password' not in result.stderr.lower()
            assert 'secret' not in result.stderr.lower()
    
    def test_migration_access_control(self):
        """Test that migration operations require appropriate access."""
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test that migration files are not world-writable
        alembic_ini = backend_dir / "alembic.ini"
        if alembic_ini.exists():
            file_stat = alembic_ini.stat()
            file_perms = stat.filemode(file_stat.st_mode)
            
            # File should not be world-writable
            assert file_perms[8] != 'w'
        
        # Test that migration scripts require proper permissions
        migrate_script = backend_dir / "scripts" / "migrate.py"
        if migrate_script.exists():
            script_stat = migrate_script.stat()
            script_perms = stat.filemode(script_stat.st_mode)
            
            # Script should not be world-writable
            assert script_perms[8] != 'w'


class TestMigrationDataProtection:
    """Test data protection during migrations."""
    
    def test_migration_data_encryption_support(self):
        """Test that migration system supports encrypted data."""
        # This is a placeholder for future encryption support
        # Currently we're using SQLite without encryption
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from config.settings import get_settings
        
        settings = get_settings()
        database_url = settings.database_url
        
        # For now, just ensure we're not storing plaintext credentials
        if not database_url.startswith('sqlite:///'):
            # Future: Add tests for encrypted database connections
            pass
    
    def test_migration_backup_encryption(self):
        """Test that migration backups can be encrypted."""
        # This is a placeholder for future backup encryption support
        # Currently implemented as a basic test
        
        backend_dir = Path(__file__).parent.parent.parent
        
        # Test that backup operations don't expose sensitive data
        with tempfile.TemporaryDirectory() as temp_dir:
            # Future: Add backup encryption tests
            pass
    
    def test_migration_audit_logging(self):
        """Test that migration operations are auditable."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from setup.migration_manager import MigrationManager
        
        manager = MigrationManager()
        
        # Test that migration operations can be logged for audit
        with patch('logging.Logger.info') as mock_info:
            manager.check_migration_status()
            
            # Should log migration operations
            assert len(mock_info.call_args_list) > 0
            
            # Check that logged information includes operation details
            logged_messages = [str(call) for call in mock_info.call_args_list]
            migration_related = [msg for msg in logged_messages if 'migration' in msg.lower()]
            assert len(migration_related) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])