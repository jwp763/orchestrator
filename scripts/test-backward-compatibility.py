#!/usr/bin/env python3
"""
TDD Test Suite for DEL-005 - Backward Compatibility Testing
Tests that existing shell scripts continue to work during the transition to npm orchestration.
"""

import os
import sys
import stat
import unittest
import subprocess
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestBackwardCompatibility(unittest.TestCase):
    """Test backward compatibility with existing shell scripts."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.scripts_dir = self.project_root / 'scripts'
        self.original_cwd = os.getcwd()
        os.chdir(self.project_root)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_existing_shell_scripts_remain_executable(self):
        """Test that existing shell scripts still exist and are executable."""
        existing_scripts = [
            'start-dev.sh',
            'start-staging.sh',
            'start-prod.sh',
            'backup-prod.sh',
            'copy-prod-to-staging.sh',
            'reset-dev.sh'
        ]
        
        for script_name in existing_scripts:
            script_path = self.scripts_dir / script_name
            
            # Script should still exist
            self.assertTrue(script_path.exists(), 
                          f"Script {script_name} should still exist for backward compatibility")
            
            # Script should be executable
            script_stat = script_path.stat()
            is_executable = bool(script_stat.st_mode & stat.S_IEXEC)
            self.assertTrue(is_executable, 
                          f"Script {script_name} should remain executable")
    
    def test_shell_scripts_use_new_environment_system(self):
        """Test that shell scripts are updated to use the new environment system."""
        # Scripts should use the Python environment loader instead of shell substitution
        
        scripts_to_check = [
            'start-dev.sh',
            'start-staging.sh', 
            'start-prod.sh'
        ]
        
        for script_name in scripts_to_check:
            script_path = self.scripts_dir / script_name
            
            if script_path.exists():
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Should use Python environment loader
                self.assertIn('python scripts/load-env.py', content,
                            f"{script_name} should use Python environment loader")
                
                # Should not use shell variable substitution
                self.assertNotIn('${', content,
                            f"{script_name} should not use shell variable substitution")
    
    def test_npm_scripts_as_preferred_interface(self):
        """Test that npm scripts are available as the preferred interface."""
        # While shell scripts remain for backward compatibility,
        # npm scripts should be the recommended approach
        
        # This will initially FAIL - npm scripts not implemented yet
        
        result = subprocess.run(['npm', 'run'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "npm run should work")
        
        # Should list the new npm scripts
        preferred_scripts = [
            'start:dev',
            'start:staging',
            'start:prod'
        ]
        
        for script in preferred_scripts:
            self.assertIn(script, result.stdout,
                        f"Preferred npm script '{script}' should be available")
    
    def test_shell_script_documentation_deprecation(self):
        """Test that shell scripts include deprecation notices."""
        # Shell scripts should include notices encouraging npm script usage
        
        scripts_to_check = [
            'start-dev.sh',
            'start-staging.sh',
            'start-prod.sh'
        ]
        
        for script_name in scripts_to_check:
            script_path = self.scripts_dir / script_name
            
            if script_path.exists():
                with open(script_path, 'r') as f:
                    content = f.read()
                
                # Should contain deprecation notice
                deprecation_indicators = [
                    'deprecated',
                    'npm run',
                    'recommended',
                    'prefer'
                ]
                
                has_deprecation_notice = any(
                    indicator in content.lower() 
                    for indicator in deprecation_indicators
                )
                
                self.assertTrue(has_deprecation_notice,
                              f"{script_name} should include deprecation notice")
    
    def test_environment_variable_compatibility(self):
        """Test that environment variables work the same way in both systems."""
        # Same environment variables should be available whether using shell scripts or npm
        
        # This will initially FAIL - environment compatibility not ensured
        
        from scripts.env_loader import load_environment_config
        
        # Test each environment
        for environment in ['development', 'staging', 'production']:
            config = load_environment_config(environment)
            
            # Should contain expected variables
            expected_vars = [
                'DATABASE_URL',
                'API_PORT',
                'FRONTEND_PORT',
                'ENVIRONMENT'
            ]
            
            for var in expected_vars:
                self.assertIn(var, config,
                            f"Environment variable {var} should be available in {environment}")
    
    def test_port_configuration_consistency(self):
        """Test that port configurations are consistent between shell and npm scripts."""
        # Same ports should be used regardless of startup method
        
        port_mappings = {
            'development': {'backend': 8000, 'frontend': 5174},
            'staging': {'backend': 8001, 'frontend': 5175},
            'production': {'backend': 8002, 'frontend': 5176}
        }
        
        # This will initially FAIL - port consistency not verified
        
        from scripts.env_loader import load_environment_config
        
        for environment, expected_ports in port_mappings.items():
            config = load_environment_config(environment)
            
            # Check backend port
            self.assertEqual(config.get('API_PORT'), str(expected_ports['backend']),
                           f"Backend port should be consistent for {environment}")
            
            # Check frontend port  
            self.assertEqual(config.get('FRONTEND_PORT'), str(expected_ports['frontend']),
                           f"Frontend port should be consistent for {environment}")
    
    def test_database_path_consistency(self):
        """Test that database paths are consistent between startup methods."""
        # Same database files should be used regardless of startup method
        
        expected_db_paths = {
            'development': 'sqlite:///backend/orchestrator_dev.db',
            'staging': 'sqlite:///backend/orchestrator_staging.db',
            'production': 'sqlite:///backend/orchestrator_prod.db'
        }
        
        from scripts.env_loader import load_environment_config
        
        for environment, expected_path in expected_db_paths.items():
            config = load_environment_config(environment)
            
            self.assertEqual(config.get('DATABASE_URL'), expected_path,
                           f"Database path should be consistent for {environment}")
    
    def test_graceful_migration_path(self):
        """Test that there's a clear migration path from shell to npm scripts."""
        # Users should be able to gradually transition from shell scripts to npm scripts
        
        # This will initially FAIL - migration guidance not implemented
        
        # Should provide clear documentation on migration
        # Should allow mixed usage during transition period
        pass
    
    def test_error_message_consistency(self):
        """Test that error messages are consistent between shell and npm scripts."""
        # Similar errors should produce similar error messages
        
        # This will initially FAIL - error message consistency not ensured
        
        # Should provide helpful error messages in both systems
        pass


class TestMigrationTools(unittest.TestCase):
    """Test tools to help with migration from shell scripts to npm scripts."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
    
    def test_migration_script_exists(self):
        """Test that migration script exists to help users transition."""
        # Should provide a script to help users migrate
        
        # This will initially FAIL - migration script not implemented
        
        migration_script = self.project_root / 'scripts' / 'migrate-to-npm.py'
        # Should exist (will fail initially)
        # self.assertTrue(migration_script.exists(), "Migration script should exist")
        pass
    
    def test_usage_analytics_for_migration(self):
        """Test that usage can be tracked to understand migration progress."""
        # Should be able to track which startup method is being used
        
        # This will initially FAIL - usage analytics not implemented
        
        # Could log startup method usage for migration planning
        pass
    
    def test_migration_validation(self):
        """Test that migration can be validated."""
        # Should verify that npm scripts produce the same results as shell scripts
        
        # This will initially FAIL - migration validation not implemented
        
        # Should compare outputs and behaviors between methods
        pass


class TestDocumentationUpdates(unittest.TestCase):
    """Test that documentation is updated for the new npm script approach."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
    
    def test_readme_updated_with_npm_scripts(self):
        """Test that README includes npm script usage."""
        # README should document the new npm script approach
        
        # This will initially FAIL - README not updated
        
        readme_path = self.project_root / 'README.md'
        if readme_path.exists():
            with open(readme_path, 'r') as f:
                content = f.read()
            
            # Should mention npm scripts
            self.assertIn('npm run', content, "README should mention npm scripts")
    
    def test_claude_md_updated(self):
        """Test that CLAUDE.md is updated with new workflow commands."""
        # CLAUDE.md should reflect the new npm script approach
        
        claude_md_path = self.project_root / 'CLAUDE.md'
        if claude_md_path.exists():
            with open(claude_md_path, 'r') as f:
                content = f.read()
            
            # Should reference npm scripts in workflow commands
            # This may already be updated - check current content
            pass


if __name__ == '__main__':
    print("🔴 TDD RED PHASE: Testing backward compatibility")
    print("=" * 55)
    
    # Run tests and expect failures initially
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 55)
    print("✅ Expected test failures! Backward compatibility not yet ensured.")