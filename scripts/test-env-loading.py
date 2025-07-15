#!/usr/bin/env python3
"""
TDD Test Suite for DEL-004 - Environment Loading System
Tests the layered environment configuration system that replaces shell variable substitution.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import time

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnvironmentLoading(unittest.TestCase):
    """Test suite for layered environment configuration system."""
    
    def setUp(self):
        """Set up test environment with temporary files."""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
        
        # Clear environment variables that might interfere
        self.original_env = dict(os.environ)
        for key in list(os.environ.keys()):
            if key.startswith(('ANTHROPIC_', 'OPENAI_', 'XAI_', 'GEMINI_', 'MOTION_', 'LINEAR_', 'GITLAB_', 'NOTION_')):
                del os.environ[key]
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.old_cwd)
        os.environ.clear()
        os.environ.update(self.original_env)
        
        # Clean up temp directory
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_env_defaults_loading(self):
        """Test that .env.defaults loads correctly with base configuration."""
        from scripts.env_loader import load_environment_config
        
        # Create .env.defaults in test directory
        self._create_test_env_file('.env.defaults', {
            'DATABASE_URL': 'sqlite:///default.db',
            'API_PORT': '8000',
            'LOG_LEVEL': 'INFO'
        })
        
        config = load_environment_config('development')
        
        # Should load defaults when no other files exist
        self.assertEqual(config['DATABASE_URL'], 'sqlite:///default.db')
        self.assertEqual(config['API_PORT'], '8000')
        self.assertEqual(config['LOG_LEVEL'], 'INFO')
    
    def test_env_file_precedence(self):
        """Test environment variable precedence: .env.local > .env.development > .env.defaults."""
        # Create test environment files
        self._create_test_env_file('.env.defaults', {
            'DATABASE_URL': 'sqlite:///default.db',
            'API_PORT': '8000',
            'LOG_LEVEL': 'INFO'
        })
        
        self._create_test_env_file('.env.development', {
            'DATABASE_URL': 'sqlite:///dev.db',
            'DEBUG': 'true'
        })
        
        self._create_test_env_file('.env.local', {
            'DATABASE_URL': 'sqlite:///local.db',
            'ANTHROPIC_API_KEY': 'local-secret-key'
        })
        
        from scripts.env_loader import load_environment_config
        config = load_environment_config('development')
        
        # Expected precedence:
        # DATABASE_URL should be from .env.local (highest precedence)
        # DEBUG should be from .env.development
        # API_PORT should be from .env.defaults
        # LOG_LEVEL should be from .env.defaults
        self.assertEqual(config['DATABASE_URL'], 'sqlite:///local.db')
        self.assertEqual(config['DEBUG'], 'true')
        self.assertEqual(config['API_PORT'], '8000')
        self.assertEqual(config['LOG_LEVEL'], 'INFO')
    
    def test_api_key_validation(self):
        """Test API key loading and validation."""
        self._create_test_env_file('.env.defaults', {
            'REQUIRED_API_KEYS': 'ANTHROPIC_API_KEY,OPENAI_API_KEY'
        })
        
        self._create_test_env_file('.env.local', {
            'ANTHROPIC_API_KEY': 'sk-ant-test-key',
            'OPENAI_API_KEY': 'sk-test-key'
        })
        
        from scripts.env_loader import validate_api_keys, load_environment_config
        
        config = load_environment_config('development')
        is_valid, missing_keys = validate_api_keys(config)
        self.assertTrue(is_valid)
        self.assertEqual(missing_keys, [])
    
    def test_environment_loading_performance(self):
        """Test that environment loading completes in < 100ms."""
        # Create realistic environment files
        self._create_test_env_file('.env.defaults', {
            'DATABASE_URL': 'sqlite:///default.db',
            'API_PORT': '8000',
            'FRONTEND_PORT': '5174',
            'ENVIRONMENT': 'development',
            'DEBUG': 'false',
            'LOG_LEVEL': 'INFO',
            'RELOAD': 'false',
            'BACKUP_ENABLED': 'false'
        })
        
        self._create_test_env_file('.env.development', {
            'DATABASE_URL': 'sqlite:///backend/orchestrator_dev.db',
            'DEBUG': 'true',
            'LOG_LEVEL': 'DEBUG',
            'RELOAD': 'true'
        })
        
        from scripts.env_loader import load_environment_config
        
        start_time = time.time()
        config = load_environment_config('development')
        end_time = time.time()
        
        load_time = (end_time - start_time) * 1000  # Convert to milliseconds
        self.assertLess(load_time, 100, f"Environment loading took {load_time:.2f}ms, should be < 100ms")
    
    def test_no_shell_substitution(self):
        """Test that the new system doesn't use shell variable substitution."""
        # Create environment file with what looks like shell substitution
        self._create_test_env_file('.env.local', {
            'API_KEY': '${SOME_VARIABLE}',  # This should be treated as literal value
            'NORMAL_KEY': 'normal-value'
        })
        
        from scripts.env_loader import load_environment_config
        
        config = load_environment_config('development')
        
        # Should treat ${SOME_VARIABLE} as literal value, not substitute
        self.assertEqual(config['API_KEY'], '${SOME_VARIABLE}')
        self.assertEqual(config['NORMAL_KEY'], 'normal-value')
    
    def test_missing_env_file_handling(self):
        """Test graceful handling when environment files are missing."""
        # Only create .env.defaults, missing .env.development
        self._create_test_env_file('.env.defaults', {
            'DATABASE_URL': 'sqlite:///default.db',
            'API_PORT': '8000'
        })
        
        from scripts.env_loader import load_environment_config
        
        # Should not raise exception, should fall back to defaults
        config = load_environment_config('development')
        self.assertEqual(config['DATABASE_URL'], 'sqlite:///default.db')
        self.assertEqual(config['API_PORT'], '8000')
    
    def test_env_example_template(self):
        """Test that .env.example serves as a proper template."""
        # Check that .env.example exists in project root (not test directory)
        project_root = Path(__file__).parent.parent
        env_example_path = project_root / '.env.example'
        self.assertTrue(env_example_path.exists(), ".env.example template should exist")
        
        # Should contain all required variables without real values
        with open(env_example_path, 'r') as f:
            content = f.read()
            self.assertIn('ANTHROPIC_API_KEY=your_anthropic_key_here', content)
            self.assertIn('OPENAI_API_KEY=your_openai_key_here', content)
    
    def _create_test_env_file(self, filename, variables):
        """Helper method to create test environment files."""
        with open(filename, 'w') as f:
            for key, value in variables.items():
                f.write(f"{key}={value}\n")


class TestEnvironmentSecurity(unittest.TestCase):
    """Test suite for environment security requirements."""
    
    def test_env_local_gitignored(self):
        """Test that .env.local is properly gitignored."""
        # This will FAIL - .gitignore doesn't include .env.local yet
        gitignore_path = Path(__file__).parent.parent / '.gitignore'
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
                self.assertIn('.env.local', content, ".env.local should be in .gitignore")
        else:
            self.fail(".gitignore file should exist")
    
    def test_no_secrets_in_committed_files(self):
        """Test that committed .env files don't contain real secrets."""
        # This will FAIL initially - current files have ${VAR} substitution
        committed_env_files = ['.env.defaults', '.env.development', '.env.staging', '.env.production']
        
        for env_file in committed_env_files:
            if os.path.exists(env_file):
                with open(env_file, 'r') as f:
                    content = f.read()
                    # Should not contain real API keys (should be placeholders or empty)
                    self.assertNotRegex(content, r'sk-[a-zA-Z0-9-_]{20,}', 
                                       f"{env_file} should not contain real API keys")
                    # Should not use shell substitution
                    self.assertNotIn('${', content, 
                                   f"{env_file} should not use shell variable substitution")


if __name__ == '__main__':
    print("🔴 TDD RED PHASE: Running failing tests for DEL-004 environment configuration")
    print("=" * 70)
    
    # Run tests and expect failures
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 70)
    print("✅ Expected test failures! Now implementing GREEN PHASE...")