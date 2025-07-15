#!/usr/bin/env python3
"""
TDD Test Suite for DEL-004 - Environment Variable Precedence Testing
Tests the specific precedence rules: .env.local > .env.{environment} > .env.defaults
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestEnvironmentPrecedence(unittest.TestCase):
    """Test environment variable precedence rules."""
    
    def setUp(self):
        """Set up test environment with temporary files."""
        self.test_dir = tempfile.mkdtemp()
        self.old_cwd = os.getcwd()
        os.chdir(self.test_dir)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.old_cwd)
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
    
    def test_three_layer_precedence(self):
        """Test precedence across all three layers."""
        # Create layered configuration
        self._create_env_file('.env.defaults', {
            'SHARED_VAR': 'default_value',
            'DEFAULT_ONLY': 'default_only',
            'OVERRIDDEN_VAR': 'default_override'
        })
        
        self._create_env_file('.env.development', {
            'SHARED_VAR': 'dev_value',
            'DEV_ONLY': 'dev_only',
            'OVERRIDDEN_VAR': 'dev_override'
        })
        
        self._create_env_file('.env.local', {
            'SHARED_VAR': 'local_value',
            'LOCAL_ONLY': 'local_only',
            'SECRET_KEY': 'local_secret'
        })
        
        from scripts.env_loader import load_environment_config
        
        config = load_environment_config('development')
        
        # Test precedence rules
        self.assertEqual(config['SHARED_VAR'], 'local_value')  # .env.local wins
        self.assertEqual(config['OVERRIDDEN_VAR'], 'dev_override')  # .env.development wins over defaults
        self.assertEqual(config['DEFAULT_ONLY'], 'default_only')  # Only in defaults
        self.assertEqual(config['DEV_ONLY'], 'dev_only')  # Only in development
        self.assertEqual(config['LOCAL_ONLY'], 'local_only')  # Only in local
        self.assertEqual(config['SECRET_KEY'], 'local_secret')  # Secret from local
    
    def test_missing_intermediate_layer(self):
        """Test precedence when intermediate layer (.env.development) is missing."""
        self._create_env_file('.env.defaults', {
            'VAR1': 'default1',
            'VAR2': 'default2'
        })
        
        self._create_env_file('.env.local', {
            'VAR1': 'local1'
        })
        
        # Missing .env.development
        
        from scripts.env_loader import load_environment_config
        
        config = load_environment_config('development')
        
        # Should still work with defaults + local
        self.assertEqual(config['VAR1'], 'local1')  # local overrides default
        self.assertEqual(config['VAR2'], 'default2')  # from defaults
    
    def test_environment_specific_precedence(self):
        """Test that correct environment file is loaded based on environment parameter."""
        self._create_env_file('.env.defaults', {
            'ENV_VAR': 'default'
        })
        
        self._create_env_file('.env.development', {
            'ENV_VAR': 'development'
        })
        
        self._create_env_file('.env.staging', {
            'ENV_VAR': 'staging'
        })
        
        self._create_env_file('.env.production', {
            'ENV_VAR': 'production'
        })
        
        from scripts.env_loader import load_environment_config
        
        # Test each environment loads correct file
        dev_config = load_environment_config('development')
        staging_config = load_environment_config('staging')
        prod_config = load_environment_config('production')
        
        self.assertEqual(dev_config['ENV_VAR'], 'development')
        self.assertEqual(staging_config['ENV_VAR'], 'staging')
        self.assertEqual(prod_config['ENV_VAR'], 'production')
    
    def test_empty_values_override(self):
        """Test that empty values in higher precedence files override non-empty values."""
        self._create_env_file('.env.defaults', {
            'NON_EMPTY_VAR': 'default_value'
        })
        
        self._create_env_file('.env.development', {
            'NON_EMPTY_VAR': ''  # Explicitly empty
        })
        
        from scripts.env_loader import load_environment_config
        
        config = load_environment_config('development')
        
        # Empty value should override non-empty default
        self.assertEqual(config['NON_EMPTY_VAR'], '')
    
    def test_boolean_and_numeric_precedence(self):
        """Test precedence with boolean and numeric values."""
        self._create_env_file('.env.defaults', {
            'DEBUG': 'false',
            'PORT': '8000',
            'TIMEOUT': '30'
        })
        
        self._create_env_file('.env.development', {
            'DEBUG': 'true',
            'PORT': '8080'
        })
        
        from scripts.env_loader import load_environment_config
        
        config = load_environment_config('development')
        
        # Development should override defaults
        self.assertEqual(config['DEBUG'], 'true')
        self.assertEqual(config['PORT'], '8080')
        # Timeout should come from defaults
        self.assertEqual(config['TIMEOUT'], '30')
    
    def _create_env_file(self, filename, variables):
        """Helper method to create environment files."""
        with open(filename, 'w') as f:
            for key, value in variables.items():
                f.write(f"{key}={value}\n")


if __name__ == '__main__':
    print("🔴 TDD RED PHASE: Testing environment variable precedence")
    print("=" * 60)
    
    unittest.main(verbosity=2, exit=False)
    
    print("\n✅ Expected test failures for precedence logic!")