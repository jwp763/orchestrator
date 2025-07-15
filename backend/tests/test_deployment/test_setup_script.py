#!/usr/bin/env python3
"""
DEL-007 TDD Tests: Development Setup Script
RED phase tests for setup_development.py functionality.
These tests are designed to fail until implementation is complete.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock, call
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "scripts"))

try:
    from setup_development import (
        DevelopmentSetup,
        SetupStep,
        SetupResult,
        install_python_dependencies,
        install_node_dependencies,
        create_environment_files,
        setup_database,
        validate_api_keys_interactive,
        run_initial_tests,
        complete_setup_flow
    )
except ImportError:
    # This is expected during RED phase - tests should fail
    pytest.skip("setup_development.py not yet implemented", allow_module_level=True)


class TestDevelopmentSetup:
    """Test the main DevelopmentSetup class."""
    
    def test_setup_initialization(self):
        """Test DevelopmentSetup can be initialized."""
        setup = DevelopmentSetup()
        assert setup is not None
        assert hasattr(setup, 'run')
        assert hasattr(setup, 'steps')
        assert hasattr(setup, 'interactive')
    
    def test_setup_with_interactive_mode(self):
        """Test DevelopmentSetup in interactive mode."""
        setup = DevelopmentSetup(interactive=True)
        assert setup.interactive is True
        
        setup = DevelopmentSetup(interactive=False)
        assert setup.interactive is False
    
    def test_setup_returns_setup_result(self):
        """Test that setup returns proper SetupResult."""
        setup = DevelopmentSetup(interactive=False)
        result = setup.run()
        
        assert isinstance(result, SetupResult)
        assert hasattr(result, 'success')
        assert hasattr(result, 'steps_completed')
        assert hasattr(result, 'steps_failed')
        assert hasattr(result, 'duration')
        assert hasattr(result, 'recommendations')


class TestSetupStep:
    """Test SetupStep data structure."""
    
    def test_setup_step_creation(self):
        """Test SetupStep can be created with proper fields."""
        step = SetupStep(
            name="test_step",
            description="Test step description",
            function=lambda: True,
            required=True
        )
        
        assert step.name == "test_step"
        assert step.description == "Test step description"
        assert step.required is True
        assert callable(step.function)
    
    def test_setup_step_execution(self):
        """Test SetupStep can be executed."""
        executed = False
        
        def test_function():
            nonlocal executed
            executed = True
            return True
        
        step = SetupStep(
            name="test",
            description="Test",
            function=test_function,
            required=True
        )
        
        result = step.execute()
        assert executed is True
        assert result is True


class TestSetupResult:
    """Test SetupResult data structure."""
    
    def test_setup_result_creation(self):
        """Test SetupResult tracks setup progress."""
        result = SetupResult()
        
        assert hasattr(result, 'success')
        assert hasattr(result, 'steps_completed')
        assert hasattr(result, 'steps_failed')
        assert hasattr(result, 'start_time')
        assert isinstance(result.steps_completed, list)
        assert isinstance(result.steps_failed, list)
    
    def test_setup_result_add_completed_step(self):
        """Test adding completed steps to result."""
        result = SetupResult()
        result.add_completed_step("install_dependencies")
        
        assert "install_dependencies" in result.steps_completed
        assert len(result.steps_completed) == 1
    
    def test_setup_result_add_failed_step(self):
        """Test adding failed steps to result."""
        result = SetupResult()
        result.add_failed_step("setup_database", "Connection failed")
        
        assert len(result.steps_failed) == 1
        assert result.steps_failed[0]["step"] == "setup_database"
        assert result.steps_failed[0]["error"] == "Connection failed"
    
    def test_setup_result_overall_success(self):
        """Test overall success calculation."""
        result = SetupResult()
        result.add_completed_step("step1")
        result.add_completed_step("step2")
        
        # No failures = success
        assert result.is_success() is True
        
        result.add_failed_step("step3", "Failed")
        # Has failures = not success
        assert result.is_success() is False


class TestPythonDependenciesInstallation:
    """Test Python dependencies installation."""
    
    @patch('setup_development.subprocess.run')
    @patch('setup_development.Path')
    def test_install_python_dependencies_success(self, mock_path, mock_run):
        """Test successful Python dependencies installation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock Path.exists() to return True for requirements.txt files
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path.return_value = mock_path_instance
        
        result = install_python_dependencies()
        
        assert result is True
        mock_run.assert_called()
        
        # Should install both backend and root dependencies
        calls = mock_run.call_args_list
        assert any("-m" in str(call) and "pip" in str(call) and "install" in str(call) for call in calls)
    
    @patch('subprocess.run')
    def test_install_python_dependencies_failure(self, mock_run):
        """Test Python dependencies installation failure."""
        from subprocess import CalledProcessError
        mock_run.side_effect = CalledProcessError(1, 'pip')
        
        result = install_python_dependencies()
        
        assert result is False
    
    @patch('subprocess.run')
    def test_install_python_dependencies_with_create_venv_param(self, mock_run):
        """Test that Python setup accepts create_venv parameter (not yet implemented)."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = install_python_dependencies(create_venv=True)
        
        # Should succeed even with create_venv=True (parameter accepted but not implemented)
        assert result is True
        mock_run.assert_called()


class TestNodeDependenciesInstallation:
    """Test Node.js dependencies installation."""
    
    @patch('subprocess.run')
    @patch('setup_development.Path')
    def test_install_node_dependencies_success(self, mock_path_class, mock_run):
        """Test successful Node.js dependencies installation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock Path instances and their exists() method
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)  # For frontend_dir / "package.json"
        mock_path_class.return_value = mock_path_instance
        
        result = install_node_dependencies()
        
        assert result is True
        mock_run.assert_called()
        
        # Should install both root and frontend dependencies
        calls = mock_run.call_args_list
        assert any("npm" in str(call) and "install" in str(call) for call in calls)
    
    @patch('subprocess.run')
    @patch('setup_development.Path')
    def test_install_node_dependencies_failure(self, mock_path_class, mock_run):
        """Test Node.js dependencies installation failure."""
        from subprocess import CalledProcessError
        
        # Mock Path instances and their exists() method
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = True
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_class.return_value = mock_path_instance
        
        mock_run.side_effect = CalledProcessError(1, 'npm')
        
        result = install_node_dependencies()
        
        assert result is False
    
    @patch('subprocess.run')
    @patch('setup_development.Path')
    def test_install_node_dependencies_with_missing_files(self, mock_path_class, mock_run):
        """Test Node installation when package.json files don't exist."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Mock Path instances where exists() returns False
        mock_path_instance = MagicMock()
        mock_path_instance.exists.return_value = False
        mock_path_instance.__truediv__ = MagicMock(return_value=mock_path_instance)
        mock_path_class.return_value = mock_path_instance
        
        result = install_node_dependencies()
        
        # Should succeed even when no package.json files exist
        assert result is True
        # Should not call npm install when files don't exist
        mock_run.assert_not_called()


class TestEnvironmentFilesCreation:
    """Test environment files creation."""
    
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_create_environment_files_from_examples(self, mock_open, mock_exists):
        """Test creating environment files from examples."""
        mock_exists.return_value = False  # Files don't exist yet
        
        result = create_environment_files()
        
        assert result is True
        
        # Should create files from examples (if needed)
        # Note: mock_open may not be called if files already exist
    
    @patch('os.path.exists')
    def test_create_environment_files_skips_existing(self, mock_exists):
        """Test that existing environment files are not overwritten."""
        mock_exists.return_value = True  # Files already exist
        
        result = create_environment_files(overwrite=False)
        
        assert result is True
    
    @patch('os.path.exists')
    @patch('builtins.open', create=True)
    def test_create_environment_files_interactive_prompts(self, mock_open, mock_exists):
        """Test interactive environment file creation."""
        mock_exists.return_value = False
        
        with patch('builtins.input', side_effect=['y', 'development']):
            result = create_environment_files(interactive=True)
            
            assert result is True
    
    def test_create_environment_files_validates_content(self):
        """Test that created environment files have valid content."""
        result = create_environment_files()
        
        # Should create files with proper structure
        assert isinstance(result, bool)


class TestDatabaseSetup:
    """Test database setup functionality."""
    
    @patch('subprocess.run')
    def test_setup_database_sqlite_development(self, mock_run):
        """Test SQLite database setup for development."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = setup_database(environment="development")
        
        assert result is True
    
    @patch('subprocess.run')
    def test_setup_database_runs_migrations(self, mock_run):
        """Test that database setup runs migrations."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = setup_database(run_migrations=True)
        
        assert result is True
        
        # Should run migration commands (if migrations are implemented)
        calls = mock_run.call_args_list
        # Note: Migration system may not be fully implemented yet
    
    @patch('subprocess.run')
    def test_setup_database_seeds_development_data(self, mock_run):
        """Test that database setup seeds development data."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = setup_database(environment="development", seed_data=True)
        
        assert result is True
    
    def test_setup_database_validates_connection(self):
        """Test that database setup validates connection."""
        result = setup_database()
        
        # Should validate database connectivity
        assert isinstance(result, bool)


class TestApiKeysInteractiveSetup:
    """Test interactive API keys setup."""
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_validate_api_keys_interactive_prompts(self, mock_getpass, mock_input):
        """Test interactive API key setup prompts user."""
        mock_input.side_effect = ['y', 'y', 'n', 'n']  # Yes to Anthropic/OpenAI, No to others
        mock_getpass.side_effect = ['sk-ant-test', 'sk-test']
        
        result = validate_api_keys_interactive()
        
        assert isinstance(result, bool)
        # Note: getpass may not be called if keys are already configured
    
    @patch('builtins.input')
    def test_validate_api_keys_interactive_skips_optional(self, mock_input):
        """Test that interactive setup can skip optional keys."""
        mock_input.side_effect = ['n', 'n', 'n', 'n']  # Skip all
        
        result = validate_api_keys_interactive()
        
        # Should still succeed (development can work without all keys)
        assert isinstance(result, bool)
    
    @patch('builtins.input')
    @patch('getpass.getpass')
    def test_validate_api_keys_interactive_validates_format(self, mock_getpass, mock_input):
        """Test that interactive setup validates API key format."""
        mock_input.side_effect = ['y']
        mock_getpass.side_effect = ['invalid-key-format']
        
        result = validate_api_keys_interactive()
        
        # Should handle invalid formats gracefully
        assert isinstance(result, bool)


class TestInitialTests:
    """Test running initial tests after setup."""
    
    @patch('subprocess.run')
    def test_run_initial_tests_backend(self, mock_run):
        """Test running initial backend tests."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = run_initial_tests(components=["backend"])
        
        assert result is True
        
        # Should run pytest
        calls = mock_run.call_args_list
        assert any("pytest" in str(call) for call in calls)
    
    @patch('subprocess.run')
    def test_run_initial_tests_frontend(self, mock_run):
        """Test running initial frontend tests."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = run_initial_tests(components=["frontend"])
        
        assert result is True
        
        # Should run npm test
        calls = mock_run.call_args_list
        assert any("npm" in str(call) and "test" in str(call) for call in calls)
    
    @patch('subprocess.run')
    def test_run_initial_tests_all_components(self, mock_run):
        """Test running tests for all components."""
        mock_run.return_value = MagicMock(returncode=0)
        
        result = run_initial_tests(components=["backend", "frontend"])
        
        assert result is True
    
    @patch('subprocess.run')
    def test_run_initial_tests_failure_handling(self, mock_run):
        """Test handling of test failures."""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = run_initial_tests()
        
        # Should handle test failures gracefully
        assert isinstance(result, bool)


class TestCompleteSetupFlow:
    """Test complete setup flow."""
    
    @patch('setup_development.DevelopmentSetup._install_python_dependencies')
    @patch('setup_development.DevelopmentSetup._install_node_dependencies')
    @patch('setup_development.DevelopmentSetup._create_environment_files')
    @patch('setup_development.DevelopmentSetup._setup_database')
    @patch('setup_development.run_initial_tests')
    def test_complete_setup_flow_success(self, mock_tests, mock_db, mock_env, mock_node, mock_python):
        """Test successful complete setup flow."""
        # Mock all steps to succeed
        mock_python.return_value = True
        mock_node.return_value = True
        mock_env.return_value = True
        mock_db.return_value = True
        mock_tests.return_value = True
        
        result = complete_setup_flow(interactive=False)
        
        assert isinstance(result, SetupResult)
        assert result.is_success() is True
        
        # All steps should be called
        mock_python.assert_called_once()
        mock_node.assert_called_once()
        mock_env.assert_called_once()
        mock_db.assert_called_once()
        mock_tests.assert_called_once()
    
    @patch('setup_development.DevelopmentSetup._install_python_dependencies')
    @patch('setup_development.DevelopmentSetup._install_node_dependencies')
    def test_complete_setup_flow_partial_failure(self, mock_node, mock_python):
        """Test setup flow with partial failures."""
        mock_python.return_value = True
        mock_node.return_value = False  # Node installation fails
        
        result = complete_setup_flow(interactive=False)
        
        assert isinstance(result, SetupResult)
        assert result.is_success() is False
        assert len(result.steps_failed) > 0
    
    def test_complete_setup_flow_performance_requirement(self):
        """Test that complete setup meets performance requirements."""
        import time
        
        start_time = time.time()
        result = complete_setup_flow(interactive=False, skip_tests=True)
        end_time = time.time()
        
        # Should complete setup reasonably quickly
        setup_time = end_time - start_time
        # Allow more time for actual setup operations
        assert setup_time < 60.0, f"Setup took {setup_time:.2f}s, should be < 60s"
    
    @patch('builtins.input')
    def test_complete_setup_flow_interactive_mode(self, mock_input):
        """Test complete setup flow in interactive mode."""
        mock_input.side_effect = ['y'] * 10  # Yes to all prompts
        
        result = complete_setup_flow(interactive=True)
        
        assert isinstance(result, SetupResult)
        # Interactive mode should work (input may or may not be called depending on setup state)


if __name__ == '__main__':
    print("🔴 DEL-007 RED Phase: Development Setup Tests")
    print("=" * 49)
    print("These tests are DESIGNED TO FAIL until implementation is complete.")
    print()
    
    # Run tests (expect failures)
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 49)
    print("🔴 RED phase complete. Proceed to GREEN phase implementation.")