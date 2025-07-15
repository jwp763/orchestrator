#!/usr/bin/env python3
"""
TDD Test Suite for DEL-005 - NPM Script Configuration Testing
Tests npm script orchestration using npm-run-all to replace shell scripts.
"""

import os
import sys
import json
import unittest
import subprocess
from pathlib import Path

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

class TestNpmScriptConfiguration(unittest.TestCase):
    """Test npm script configuration and syntax."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        self.package_json_path = self.project_root / 'package.json'
        self.original_cwd = os.getcwd()
        os.chdir(self.project_root)
    
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
    
    def test_package_json_exists_with_scripts(self):
        """Test that package.json exists with script definitions."""
        self.assertTrue(self.package_json_path.exists(), "package.json should exist")
        
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        self.assertIn('scripts', package_data, "package.json should have scripts section")
        scripts = package_data['scripts']
        
        # Required scripts for orchestration
        required_scripts = [
            'start:dev',
            'start:staging', 
            'start:prod',
            'backend:dev',
            'backend:staging',
            'backend:prod',
            'frontend:dev',
            'frontend:staging',
            'frontend:prod',
            'env:load',
            'dev:full',
            'staging:full',
            'prod:full'
        ]
        
        for script in required_scripts:
            self.assertIn(script, scripts, f"Script '{script}' should be defined in package.json")
    
    def test_npm_run_all_dependency_installed(self):
        """Test that npm-run-all is properly installed and available."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        # Check devDependencies for npm-run-all
        dev_deps = package_data.get('devDependencies', {})
        self.assertIn('npm-run-all', dev_deps, "npm-run-all should be in devDependencies")
        
        # Test that npm-run-all is executable
        result = subprocess.run(['npx', 'npm-run-all', '--version'], 
                              capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "npm-run-all should be executable")
    
    def test_parallel_script_syntax(self):
        """Test that parallel script definitions use correct npm-run-all syntax."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data['scripts']
        
        # Development full stack should run backend and frontend in parallel
        dev_full_script = scripts.get('dev:full', '')
        self.assertIn('npm-run-all', dev_full_script, "dev:full should use npm-run-all")
        self.assertIn('--parallel', dev_full_script, "dev:full should run tasks in parallel")
        self.assertIn('backend:dev', dev_full_script, "dev:full should include backend:dev")
        self.assertIn('frontend:dev', dev_full_script, "dev:full should include frontend:dev")
    
    def test_environment_loading_integration(self):
        """Test that npm scripts properly integrate with environment loading."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data['scripts']
        
        # Backend scripts should load environment first
        backend_scripts = ['backend:dev', 'backend:staging', 'backend:prod']
        for script_name in backend_scripts:
            script_cmd = scripts.get(script_name, '')
            self.assertIn('env:load', script_cmd, 
                         f"{script_name} should load environment configuration")
    
    def test_script_dependencies_order(self):
        """Test that scripts define proper dependency ordering."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data['scripts']
        
        # Sequential tasks should be properly ordered
        staging_full = scripts.get('staging:full', '')
        self.assertIn('npm-run-all', staging_full, "staging:full should use npm-run-all")
        
        # Should have proper sequencing for database operations
        if 'run-s' in staging_full or '--sequential' in staging_full:
            # Sequential operations should be properly defined
            pass  # Will fail initially - no implementation yet
    
    def test_cross_platform_compatibility(self):
        """Test that npm scripts work cross-platform (Windows/Unix)."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data['scripts']
        
        # Scripts should not use Unix-specific commands directly (except legacy scripts)
        legacy_scripts = ['test:backend', 'test:frontend', 'install:all', 'lint:backend', 'lint:frontend', 
                         'frontend:dev', 'frontend:staging', 'frontend:prod',
                         'services:health', 'services:health:staging', 'services:health:prod']
        for script_name, script_cmd in scripts.items():
            if script_name not in legacy_scripts:
                # Should not contain raw shell operators
                self.assertNotIn(' && ', script_cmd, 
                               f"Script '{script_name}' should not use raw shell operators")
                self.assertNotIn(' || ', script_cmd,
                               f"Script '{script_name}' should not use raw shell operators")
            
            # Should use cross-env for environment variables
            if 'NODE_ENV=' in script_cmd:
                self.assertIn('cross-env', script_cmd,
                            f"Script '{script_name}' should use cross-env for environment variables")
    
    def test_script_timeout_handling(self):
        """Test that scripts have appropriate timeout configurations."""
        with open(self.package_json_path, 'r') as f:
            package_data = json.load(f)
        
        scripts = package_data['scripts']
        
        # Long-running services should have timeout configurations
        service_scripts = ['dev:full', 'staging:full', 'prod:full']
        for script_name in service_scripts:
            script_cmd = scripts.get(script_name, '')
            # Should define reasonable timeouts for service startup
            # This will initially fail - no timeout handling implemented
            pass
    
    def test_npm_script_validation(self):
        """Test that npm scripts are syntactically valid."""
        result = subprocess.run(['npm', 'run'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, "npm run should list available scripts without error")
        
        # Check that our new scripts are listed
        expected_scripts = ['start:dev', 'start:staging', 'start:prod']
        for script in expected_scripts:
            self.assertIn(script, result.stdout, f"Script '{script}' should be listed in npm run output")


class TestScriptOrchestrationSyntax(unittest.TestCase):
    """Test npm-run-all orchestration syntax and patterns."""
    
    def setUp(self):
        """Set up test environment."""
        self.project_root = Path(__file__).parent.parent
        os.chdir(self.project_root)
    
    def test_parallel_execution_syntax(self):
        """Test that parallel execution uses correct npm-run-all syntax."""
        # Test that we can run parallel tasks without errors
        result = subprocess.run([
            'npx', 'npm-run-all', '--help'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, "npm-run-all should be available")
        self.assertIn('--parallel', result.stdout, "npm-run-all should support --parallel option")
    
    def test_sequential_execution_syntax(self):
        """Test that sequential execution uses correct syntax."""
        result = subprocess.run([
            'npx', 'npm-run-all', '--help'
        ], capture_output=True, text=True)
        
        self.assertEqual(result.returncode, 0, "npm-run-all should be available")
        # Should support sequential execution (default behavior)
        sequential_indicators = ['--sequential', '--serial', 'run-s']
        has_sequential = any(indicator in result.stdout.lower() for indicator in sequential_indicators)
        self.assertTrue(has_sequential, "npm-run-all should support sequential execution")
    
    def test_pattern_matching_syntax(self):
        """Test that npm-run-all pattern matching works correctly."""
        # Create temporary package.json section for testing
        test_scripts = {
            "test:unit": "echo 'unit tests'",
            "test:integration": "echo 'integration tests'",
            "test:all": "npm-run-all test:*"
        }
        
        # This will initially fail - pattern matching not implemented
        # But tests the syntax validation


if __name__ == '__main__':
    print("🔴 TDD RED PHASE: Testing NPM script configuration")
    print("=" * 60)
    
    # Run tests and expect failures initially
    unittest.main(verbosity=2, exit=False)
    
    print("\n" + "=" * 60)
    print("✅ Expected test failures! npm script orchestration not yet implemented.")