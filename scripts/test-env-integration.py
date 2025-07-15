#!/usr/bin/env python3
"""
Integration tests for DEL-004 - Complete environment system testing
Tests the integration of environment loading with deployment scripts.
"""

import os
import sys
import tempfile
import unittest
import subprocess
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnvironmentIntegration(unittest.TestCase):
    """Integration tests for complete environment system."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.original_cwd = os.getcwd()
        os.chdir(self.project_root)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_development_environment_loading(self):
        """Test loading development environment configuration."""
        result = subprocess.run([
            'python', 'scripts/load-env.py', 'development'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Environment loading failed: {result.stderr}")
        
        # Check that output contains expected information
        self.assertIn('Environment: development', result.stdout)
        self.assertIn('DATABASE_URL="sqlite:///backend/orchestrator_dev.db"', result.stdout)
        self.assertIn('API_PORT="8000"', result.stdout)
        self.assertIn('DEBUG="true"', result.stdout)
    
    def test_staging_environment_loading(self):
        """Test loading staging environment configuration."""
        result = subprocess.run([
            'python', 'scripts/load-env.py', 'staging'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Environment loading failed: {result.stderr}")
        
        # Check staging-specific configuration
        self.assertIn('Environment: staging', result.stdout)
        self.assertIn('DATABASE_URL="sqlite:///backend/orchestrator_staging.db"', result.stdout)
        self.assertIn('API_PORT="8001"', result.stdout)
        self.assertIn('DEBUG="false"', result.stdout)
    
    def test_production_environment_loading(self):
        """Test loading production environment configuration."""
        result = subprocess.run([
            'python', 'scripts/load-env.py', 'production'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Environment loading failed: {result.stderr}")
        
        # Check production-specific configuration
        self.assertIn('Environment: production', result.stdout)
        self.assertIn('DATABASE_URL="sqlite:///backend/orchestrator_prod.db"', result.stdout)
        self.assertIn('API_PORT="8002"', result.stdout)
        self.assertIn('DEBUG="false"', result.stdout)
    
    def test_env_loader_direct_usage(self):
        """Test direct usage of env_loader module."""
        result = subprocess.run([
            'python', 'scripts/env_loader.py', 'development'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, f"Direct env_loader failed: {result.stderr}")
        
        # Should show configuration summary
        self.assertIn('Loading environment configuration for: development', result.stdout)
        self.assertIn('Shell substitution detected: False', result.stdout)
        self.assertIn('API key validation:', result.stdout)
    
    def test_no_shell_substitution_in_loaded_config(self):
        """Test that loaded configuration doesn't contain shell substitution patterns."""
        from scripts.env_loader import load_environment_config
        
        for env in ['development', 'staging', 'production']:
            config = load_environment_config(env)
            
            # Check no values contain ${...} patterns
            for key, value in config.items():
                self.assertNotIn('${', str(value), 
                               f"Shell substitution found in {env} environment: {key}={value}")
    
    def test_environment_file_validation(self):
        """Test that all environment files are properly structured."""
        env_files = [
            '.env.defaults',
            '.env.development', 
            '.env.staging',
            '.env.production',
            '.env.example'
        ]
        
        for env_file in env_files:
            file_path = self.project_root / env_file
            self.assertTrue(file_path.exists(), f"{env_file} should exist")
            
            # Check file format
            with open(file_path, 'r') as f:
                content = f.read()
                
                # Should not contain shell substitution (except .env.example for documentation)
                if env_file != '.env.example':
                    self.assertNotIn('${', content, 
                                   f"{env_file} should not contain shell substitution")
                
                # Should contain key=value format
                lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
                for line in lines:
                    if line:  # Skip empty lines
                        self.assertIn('=', line, f"Invalid format in {env_file}: {line}")
    
    def test_gitignore_protection(self):
        """Test that .env.local is properly gitignored."""
        gitignore_path = self.project_root / '.gitignore'
        self.assertTrue(gitignore_path.exists(), ".gitignore should exist")
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
            self.assertIn('.env.local', content, ".env.local should be in .gitignore")
    
    def test_migration_helper(self):
        """Test the migration helper for old shell substitution format."""
        from scripts.env_loader import migrate_from_shell_substitution
        
        # Create a test file with shell substitution
        test_file = '.env.test_migration'
        with open(test_file, 'w') as f:
            f.write("""# Test environment
DATABASE_URL=sqlite:///test.db
API_KEY=${API_KEY}
SECRET_TOKEN=${SECRET_TOKEN}
NORMAL_VAR=normal_value
""")
        
        try:
            # Test migration
            result = migrate_from_shell_substitution('test_migration')
            self.assertTrue(result, "Migration should succeed")
            
            # Check migration file was created
            migration_file = '.env.test_migration.new'
            self.assertTrue(os.path.exists(migration_file), "Migration file should be created")
            
            # Check migration content
            with open(migration_file, 'r') as f:
                migrated_content = f.read()
                self.assertIn('# TODO: Set API_KEY in .env.local', migrated_content)
                self.assertIn('# TODO: Set SECRET_TOKEN in .env.local', migrated_content)
                self.assertIn('NORMAL_VAR=normal_value', migrated_content)
            
        finally:
            # Clean up test files
            for test_cleanup_file in [test_file, '.env.test_migration.new']:
                if os.path.exists(test_cleanup_file):
                    os.remove(test_cleanup_file)


class TestEnvironmentPerformance(unittest.TestCase):
    """Performance tests for environment loading."""
    
    def test_loading_performance(self):
        """Test that environment loading meets performance requirements."""
        import time
        from scripts.env_loader import load_environment_config
        
        # Test each environment
        for environment in ['development', 'staging', 'production']:
            start_time = time.time()
            config = load_environment_config(environment)
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            self.assertLess(load_time, 100, 
                          f"Environment loading for {environment} took {load_time:.2f}ms, should be < 100ms")
            self.assertGreater(len(config), 0, f"Should load configuration for {environment}")


if __name__ == '__main__':
    print("🧪 Running DEL-004 Integration Tests")
    print("=" * 40)
    
    # Run tests
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 40)
    print("✅ Integration tests completed!")