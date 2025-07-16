#!/usr/bin/env python3
"""
TDD tests for npm script validation and cross-env fixes.

These tests define the expected behavior for npm scripts after 
fixing cross-env issues in npm-run-all context.
"""

import unittest
import subprocess
import json
import time
from pathlib import Path


class TestNpmScriptValidation(unittest.TestCase):
    """Test npm script syntax and execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        self.package_json_path = self.project_root / "package.json"
        
    def test_package_json_has_required_scripts(self):
        """package.json should contain all required scripts."""
        with open(self.package_json_path) as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        
        # Environment loading scripts
        self.assertIn("env:load:dev", scripts)
        self.assertIn("env:load:staging", scripts)
        self.assertIn("env:load:prod", scripts)
        
        # Individual service scripts
        self.assertIn("backend:dev", scripts)
        self.assertIn("backend:staging", scripts)
        self.assertIn("backend:prod", scripts)
        self.assertIn("frontend:dev", scripts)
        self.assertIn("frontend:staging", scripts)
        self.assertIn("frontend:prod", scripts)
        
        # Full stack scripts
        self.assertIn("dev:full", scripts)
        self.assertIn("staging:full", scripts)
        self.assertIn("prod:full", scripts)
        
        # Health check scripts
        self.assertIn("services:health", scripts)
        self.assertIn("services:health:staging", scripts)
        self.assertIn("services:health:prod", scripts)
    
    def test_env_load_scripts_work(self):
        """Environment loading scripts should work correctly."""
        # Test development environment loading
        result = subprocess.run(
            ["npm", "run", "env:load:dev"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Environment 'development' loaded successfully!", result.stdout)
        
        # Test staging environment loading
        result = subprocess.run(
            ["npm", "run", "env:load:staging"],
            cwd=self.project_root,
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("Environment 'staging' loaded successfully!", result.stdout)
    
    def test_backend_scripts_can_be_parsed(self):
        """Backend scripts should have valid syntax that doesn't cause npm errors."""
        # Test that npm can find all referenced scripts without "Task not found" error
        # Start the script and check initial output for parsing errors
        process = subprocess.Popen(
            ["npm", "run", "backend:dev"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or show parsing errors
        time.sleep(1)
        
        # Terminate early to avoid long-running processes
        process.terminate()
        stdout, stderr = process.communicate()
        
        # Should not contain "Task not found: cross-env"
        self.assertNotIn("Task not found", stderr)
        self.assertNotIn("ERROR: Task not found", stderr)
    
    def test_frontend_scripts_can_be_parsed(self):
        """Frontend scripts should have valid syntax."""
        process = subprocess.Popen(
            ["npm", "run", "frontend:dev"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or show parsing errors
        time.sleep(1)
        
        # Terminate early
        process.terminate()
        stdout, stderr = process.communicate()
        
        # Should not fail with cross-env errors
        self.assertNotIn("Task not found", stderr)
    
    def test_full_stack_scripts_can_be_parsed(self):
        """Full stack scripts should have valid syntax."""
        process = subprocess.Popen(
            ["npm", "run", "dev:full"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or show parsing errors
        time.sleep(1)
        
        # Terminate early
        process.terminate()
        stdout, stderr = process.communicate()
        
        # Should not fail with cross-env errors
        self.assertNotIn("Task not found", stderr)


class TestNpmScriptExecution(unittest.TestCase):
    """Test actual npm script execution."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        # Kill any existing services
        subprocess.run(["pkill", "-f", "uvicorn|vite"], check=False)
        time.sleep(1)
    
    def tearDown(self):
        """Clean up after tests."""
        subprocess.run(["pkill", "-f", "uvicorn|vite"], check=False)
    
    def test_backend_dev_script_starts_without_cross_env_error(self):
        """Backend dev script should start without cross-env errors."""
        # Start backend script in background
        process = subprocess.Popen(
            ["npm", "run", "backend:dev"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or fail
        time.sleep(3)
        
        # Check if it's still running (not failed immediately)
        poll_result = process.poll()
        
        # Clean up
        process.terminate()
        
        if poll_result is not None:
            # Process exited, check why
            stdout, stderr = process.communicate()
            self.assertNotIn("Task not found: \"cross-env\"", stderr)
            self.assertNotIn("ERROR: Task not found", stderr)
    
    def test_frontend_dev_script_starts_without_cross_env_error(self):
        """Frontend dev script should start without cross-env errors."""
        process = subprocess.Popen(
            ["npm", "run", "frontend:dev"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or fail
        time.sleep(3)
        
        # Check if it's still running
        poll_result = process.poll()
        
        # Clean up
        process.terminate()
        
        if poll_result is not None:
            # Process exited, check why
            stdout, stderr = process.communicate()
            self.assertNotIn("Task not found: \"cross-env\"", stderr)
            self.assertNotIn("ERROR: Task not found", stderr)
    
    def test_dev_full_script_starts_without_cross_env_error(self):
        """Full dev script should start both services without cross-env errors."""
        process = subprocess.Popen(
            ["npm", "run", "dev:full"],
            cwd=self.project_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Give it a moment to start or fail
        time.sleep(5)
        
        # Check if it's still running
        poll_result = process.poll()
        
        # Clean up
        process.terminate()
        
        if poll_result is not None:
            # Process exited, check why
            stdout, stderr = process.communicate()
            self.assertNotIn("Task not found: \"cross-env\"", stderr)
            self.assertNotIn("ERROR: Task not found", stderr)


class TestNpmScriptCompatibility(unittest.TestCase):
    """Test npm script cross-platform compatibility."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent.parent
        self.package_json_path = self.project_root / "package.json"
    
    def test_scripts_avoid_shell_specific_syntax(self):
        """Scripts should avoid shell-specific syntax for cross-platform compatibility."""
        with open(self.package_json_path) as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        
        # Check that service startup scripts don't use shell-specific syntax
        # Note: Some scripts like health checks and tests can use && where appropriate
        service_scripts = [k for k in scripts.keys() if k.endswith(":dev") or k.endswith(":staging") or k.endswith(":prod")]
        for script_name in service_scripts:
            if script_name.startswith("services:health"):
                continue  # Health checks can use && for sequencing
            script_content = scripts[script_name]
            # Main service startup scripts should not use shell-specific &&
            if "npm-run-all" not in script_content:
                self.assertNotIn("&&", script_content, f"Script {script_name} uses shell-specific && without npm-run-all")
    
    def test_scripts_use_npm_run_all_for_sequencing(self):
        """Scripts should use npm-run-all for proper cross-platform sequencing."""
        with open(self.package_json_path) as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        
        # Backend scripts should use npm-run-all for sequencing
        backend_scripts = [k for k in scripts.keys() if k.startswith("backend:")]
        for script_name in backend_scripts:
            script_content = scripts[script_name]
            if "env:load" in script_content:
                self.assertIn("npm-run-all", script_content, 
                             f"Script {script_name} should use npm-run-all for sequencing")
    
    def test_cross_env_usage_is_compatible(self):
        """cross-env usage should be compatible with npm-run-all."""
        with open(self.package_json_path) as f:
            package_data = json.load(f)
        
        scripts = package_data.get("scripts", {})
        
        # Scripts using cross-env should not have quoting issues
        for script_name, script_content in scripts.items():
            if "cross-env" in script_content:
                # Should not have nested quotes that cause issues
                self.assertNotIn('\"cross-env', script_content, 
                                f"Script {script_name} has problematic cross-env quoting")


if __name__ == '__main__':
    unittest.main()