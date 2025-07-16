#!/usr/bin/env python3
"""
TDD tests for workflow_utils.py npm script integration.

These tests define the expected behavior when workflow_utils.py
integrates with npm scripts instead of shell scripts.
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import subprocess
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from workflow_utils import EnvironmentSwitcher, WorkflowOrchestrator


class TestWorkflowNpmIntegration(unittest.TestCase):
    """Test npm script integration in workflow utilities."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.environment_switcher = EnvironmentSwitcher()
        self.orchestrator = WorkflowOrchestrator()
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_uses_npm_scripts_not_shell_scripts(self, mock_popen):
        """
        CRITICAL TEST: _execute_switch should use npm scripts, not shell scripts.
        
        This is the core requirement of DEL-012.
        """
        # Arrange
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Mock the port checking to return False (not in use) then True (started)
        with patch.object(self.environment_switcher, '_is_port_in_use', side_effect=[False, True]):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    result = self.environment_switcher._execute_switch('development')
                    
                    # Assert
                    self.assertTrue(result)
                    mock_popen.assert_called_once()
                    
                    # CRITICAL: Should call npm script, not shell script
                    call_args = mock_popen.call_args
                    command = call_args[0][0]  # First positional argument
                    
                    # Should be npm command
                    self.assertIn('npm', command)
                    self.assertIn('run', command)
                    self.assertIn('dev:full', command)
                    
                    # Should NOT be shell script
                    self.assertNotIn('start-dev.sh', str(command))
                    self.assertNotIn('.sh', str(command))
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_development_calls_npm_dev_full(self, mock_popen):
        """Development environment should call 'npm run dev:full'."""
        # Arrange
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        with patch.object(self.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    self.environment_switcher._execute_switch('development')
                    
                    # Assert
                    mock_popen.assert_called_once()
                    call_args = mock_popen.call_args[0][0]
                    
                    self.assertEqual(call_args, ['npm', 'run', 'dev:full'])
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_staging_calls_npm_staging_full(self, mock_popen):
        """Staging environment should call 'npm run staging:full'."""
        # Arrange
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        with patch.object(self.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    self.environment_switcher._execute_switch('staging')
                    
                    # Assert
                    call_args = mock_popen.call_args[0][0]
                    self.assertEqual(call_args, ['npm', 'run', 'staging:full'])
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_production_calls_npm_prod_full(self, mock_popen):
        """Production environment should call 'npm run prod:full'."""
        # Arrange
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        with patch.object(self.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    self.environment_switcher._execute_switch('production')
                    
                    # Assert
                    call_args = mock_popen.call_args[0][0]
                    self.assertEqual(call_args, ['npm', 'run', 'prod:full'])
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_runs_from_project_root(self, mock_popen):
        """npm scripts should be executed from project root directory."""
        # Arrange
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        with patch.object(self.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    self.environment_switcher._execute_switch('development')
                    
                    # Assert
                    call_kwargs = mock_popen.call_args[1]
                    self.assertEqual(call_kwargs['cwd'], self.environment_switcher.project_root)
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_handles_npm_command_not_found(self, mock_popen):
        """Should handle gracefully when npm command is not found."""
        # Arrange
        mock_popen.side_effect = FileNotFoundError("npm command not found")
        
        # Act
        result = self.environment_switcher._execute_switch('development')
        
        # Assert
        self.assertFalse(result)
    
    @patch('workflow_utils.subprocess.Popen')
    def test_execute_switch_handles_npm_script_failure(self, mock_popen):
        """Should handle gracefully when npm script fails to start services."""
        # Arrange
        mock_process = Mock()
        mock_process.pid = 12345
        mock_popen.return_value = mock_process
        
        # Service never starts (port never becomes active)
        with patch.object(self.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.environment_switcher, '_wait_for_service', return_value=False):
                with patch.object(self.environment_switcher, '_store_process_info'):
                    
                    # Act
                    result = self.environment_switcher._execute_switch('development')
                    
                    # Assert
                    self.assertFalse(result)
    
    @patch('workflow_utils.subprocess.Popen')
    def test_workflow_orchestrator_uses_npm_integration(self, mock_popen):
        """WorkflowOrchestrator.quick_switch should use npm script integration."""
        # Arrange
        mock_process = Mock()
        mock_popen.return_value = mock_process
        
        with patch.object(self.orchestrator.environment_switcher, '_is_port_in_use', return_value=False):
            with patch.object(self.orchestrator.environment_switcher, '_wait_for_service', return_value=True):
                with patch.object(self.orchestrator.environment_switcher, '_store_process_info'):
                    with patch.object(self.orchestrator.proxy_manager, 'setup_proxy', return_value=True):
                        
                        # Act
                        result = self.orchestrator.quick_switch('development')
                        
                        # Assert
                        self.assertTrue(result)
                        call_args = mock_popen.call_args[0][0]
                        self.assertEqual(call_args, ['npm', 'run', 'dev:full'])


class TestWorkflowErrorHandling(unittest.TestCase):
    """Test error handling for npm script integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.environment_switcher = EnvironmentSwitcher()
    
    @patch('workflow_utils.subprocess.Popen')
    def test_graceful_failure_with_missing_package_json(self, mock_popen):
        """Should fail gracefully when package.json is missing."""
        # Arrange - npm run will fail if package.json doesn't exist
        mock_popen.side_effect = subprocess.CalledProcessError(1, 'npm run dev:full')
        
        # Act
        result = self.environment_switcher._execute_switch('development')
        
        # Assert
        self.assertFalse(result)
    
    @patch('workflow_utils.subprocess.Popen')
    def test_graceful_failure_with_missing_npm_script(self, mock_popen):
        """Should fail gracefully when npm script doesn't exist."""
        # Arrange - npm will return error code when script doesn't exist
        mock_process = Mock()
        mock_process.returncode = 1
        mock_popen.return_value = mock_process
        
        with patch.object(self.environment_switcher, '_wait_for_service', return_value=False):
            
            # Act
            result = self.environment_switcher._execute_switch('development')
            
            # Assert
            self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()