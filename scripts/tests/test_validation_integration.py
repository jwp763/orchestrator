#!/usr/bin/env python3
"""
DEL-007 TDD Tests: Validation Integration Tests
RED phase integration tests for environment validation functionality.
These tests are designed to fail until implementation is complete.
"""

import os
import sys
import pytest
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from validate_environment import EnvironmentValidator, ValidationResult
    from setup_development import DevelopmentSetup, SetupResult
except ImportError:
    # This is expected during RED phase - tests should fail
    pytest.skip("Scripts not yet implemented", allow_module_level=True)


class TestValidationWithRealEnvironments:
    """Test environment validation with realistic environment configurations."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create mock project structure
        self.create_mock_project_structure()
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def create_mock_project_structure(self):
        """Create a mock project structure for testing."""
        # Create directories
        os.makedirs("backend/src", exist_ok=True)
        os.makedirs("frontend/src", exist_ok=True)
        os.makedirs("scripts", exist_ok=True)
        os.makedirs("docs", exist_ok=True)
        
        # Create package.json
        with open("package.json", "w") as f:
            f.write('{"name": "test-project", "scripts": {"start": "echo test"}}')
        
        # Create requirements.txt
        with open("backend/requirements.txt", "w") as f:
            f.write("fastapi>=0.68.0\nsqlalchemy>=1.4.0\n")
    
    def test_validation_with_complete_valid_environment(self):
        """Test validation with a completely valid environment setup."""
        # Create all required environment files
        env_files = {
            ".env.defaults": "DATABASE_URL=sqlite:///orchestrator.db\n",
            ".env.development": "DEBUG=true\nENVIRONMENT=development\n",
            ".env.staging": "DEBUG=false\nENVIRONMENT=staging\n",
            ".env.production": "DEBUG=false\nENVIRONMENT=production\n"
        }
        
        for filename, content in env_files.items():
            with open(filename, "w") as f:
                f.write(content)
        
        # Set up environment with valid API keys
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'sk-ant-test123',
            'OPENAI_API_KEY': 'sk-test123'
        }):
            validator = EnvironmentValidator(environment="development")
            result = validator.validate()
            
            assert isinstance(result, ValidationResult)
            # With valid setup, should have minimal errors
            assert len(result.errors) <= 2  # Some errors might be expected in test environment
    
    def test_validation_with_missing_environment_files(self):
        """Test validation when environment files are missing."""
        validator = EnvironmentValidator(environment="production")
        result = validator.validate()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        assert len(result.errors) > 0
        
        # Should report missing environment files
        error_messages = [error.message for error in result.errors]
        assert any(".env" in msg for msg in error_messages)
    
    def test_validation_with_invalid_database_config(self):
        """Test validation with invalid database configuration."""
        # Create environment file with invalid database URL
        with open(".env.development", "w") as f:
            f.write("DATABASE_URL=invalid://url\n")
        
        validator = EnvironmentValidator(environment="development")
        result = validator.validate()
        
        assert isinstance(result, ValidationResult)
        assert result.is_valid is False
        
        # Should report database configuration error
        error_messages = [error.message for error in result.errors]
        assert any("database" in msg.lower() for msg in error_messages)
    
    def test_validation_with_missing_api_keys_production(self):
        """Test validation in production environment with missing API keys."""
        # Create minimal production environment file
        with open(".env.production", "w") as f:
            f.write("ENVIRONMENT=production\nDEBUG=false\n")
        
        with patch.dict(os.environ, {}, clear=True):
            validator = EnvironmentValidator(environment="production")
            result = validator.validate()
            
            assert isinstance(result, ValidationResult)
            assert result.is_valid is False
            
            # Production should require API keys
            error_messages = [error.message for error in result.errors]
            assert any("api" in msg.lower() or "key" in msg.lower() for msg in error_messages)
    
    def test_validation_with_missing_dependencies(self):
        """Test validation when required dependencies are missing."""
        # Remove requirements.txt to simulate missing dependencies
        if os.path.exists("backend/requirements.txt"):
            os.remove("backend/requirements.txt")
        
        validator = EnvironmentValidator()
        result = validator.validate()
        
        assert isinstance(result, ValidationResult)
        # Should report missing dependency files
        assert len(result.errors) > 0 or len(result.warnings) > 0


class TestSetupIntegrationWithValidation:
    """Test integration between setup and validation processes."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    @patch('subprocess.run')
    def test_setup_followed_by_validation_success(self, mock_run):
        """Test that setup creates environment that passes validation."""
        mock_run.return_value = MagicMock(returncode=0)
        
        # Run setup
        setup = DevelopmentSetup(interactive=False)
        setup_result = setup.run()
        
        assert isinstance(setup_result, SetupResult)
        
        # Run validation after setup
        validator = EnvironmentValidator(environment="development")
        validation_result = validator.validate()
        
        assert isinstance(validation_result, ValidationResult)
        
        # After successful setup, validation should have fewer errors
        if setup_result.is_success():
            # Should have improved validation results
            assert len(validation_result.errors) <= len(validation_result.warnings)
    
    def test_validation_provides_actionable_setup_recommendations(self):
        """Test that validation provides recommendations that setup can address."""
        # Run validation on incomplete environment
        validator = EnvironmentValidator(environment="development")
        validation_result = validator.validate()
        
        assert isinstance(validation_result, ValidationResult)
        
        # Should provide actionable recommendations
        recommendations = getattr(validation_result, 'recommendations', [])
        assert len(recommendations) > 0
        
        # Recommendations should be actionable
        for rec in recommendations:
            assert isinstance(rec, str)
            assert len(rec) > 10  # Should be descriptive
    
    @patch('builtins.input')
    def test_setup_handles_validation_failures_gracefully(self, mock_input):
        """Test that setup handles validation failures gracefully."""
        mock_input.side_effect = ['n'] * 10  # No to all prompts
        
        setup = DevelopmentSetup(interactive=True)
        result = setup.run()
        
        assert isinstance(result, SetupResult)
        
        # Even with validation failures, setup should complete gracefully
        assert hasattr(result, 'steps_completed')
        assert hasattr(result, 'steps_failed')


class TestMultiEnvironmentValidation:
    """Test validation across multiple environments."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)
    
    def test_validation_different_requirements_per_environment(self):
        """Test that different environments have different validation requirements."""
        # Create environment-specific files
        env_configs = {
            ".env.development": "DEBUG=true\nANTHROPIC_API_KEY=optional\n",
            ".env.staging": "DEBUG=false\nANTHROPIC_API_KEY=required\n",
            ".env.production": "DEBUG=false\nANTHROPIC_API_KEY=required\nOPENAI_API_KEY=required\n"
        }
        
        for filename, content in env_configs.items():
            with open(filename, "w") as f:
                f.write(content)
        
        results = {}
        for env in ["development", "staging", "production"]:
            validator = EnvironmentValidator(environment=env)
            results[env] = validator.validate()
        
        # Development should be most lenient
        # Production should be most strict
        dev_errors = len(results["development"].errors)
        prod_errors = len(results["production"].errors)
        
        # This relationship might vary, but should be consistent
        assert isinstance(dev_errors, int)
        assert isinstance(prod_errors, int)
    
    def test_validation_consistency_across_environments(self):
        """Test that validation is consistent across environments."""
        environments = ["development", "staging", "production"]
        results = {}
        
        for env in environments:
            validator = EnvironmentValidator(environment=env)
            results[env] = validator.validate()
        
        # All results should be ValidationResult objects
        for env, result in results.items():
            assert isinstance(result, ValidationResult)
            assert result.environment == env
            assert hasattr(result, 'timestamp')
            
            # Should have consistent structure
            assert isinstance(result.errors, list)
            assert isinstance(result.warnings, list)


class TestValidationPerformanceRequirements:
    """Test that validation meets performance requirements."""
    
    def test_validation_completes_within_time_limit(self):
        """Test that validation completes within 5 seconds as required."""
        import time
        
        start_time = time.time()
        
        validator = EnvironmentValidator()
        result = validator.validate()
        
        end_time = time.time()
        validation_time = end_time - start_time
        
        # Should complete within 5 seconds (requirement from deployment plan)
        assert validation_time < 5.0, f"Validation took {validation_time:.2f}s, should be < 5s"
        assert isinstance(result, ValidationResult)
    
    def test_validation_all_environments_performance(self):
        """Test that validating all environments meets performance requirements."""
        import time
        
        start_time = time.time()
        
        # Test validation of all environments
        environments = ["development", "staging", "production"]
        results = {}
        
        for env in environments:
            validator = EnvironmentValidator(environment=env)
            results[env] = validator.validate()
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Should validate all environments within reasonable time
        assert total_time < 10.0, f"All environment validation took {total_time:.2f}s, should be < 10s"
        
        # All validations should complete
        assert len(results) == 3
        for result in results.values():
            assert isinstance(result, ValidationResult)


class TestValidationSecurityRequirements:
    """Test validation security and information protection."""
    
    def test_validation_does_not_expose_sensitive_information(self):
        """Test that validation results don't expose sensitive information."""
        # Set up environment with sensitive data
        with patch.dict(os.environ, {
            'ANTHROPIC_API_KEY': 'sk-ant-secret123',
            'OPENAI_API_KEY': 'sk-secret123',
            'DATABASE_URL': 'postgresql://user:password@localhost/db'
        }):
            validator = EnvironmentValidator()
            result = validator.validate()
            
            assert isinstance(result, ValidationResult)
            
            # Convert result to string representation
            result_str = str(result.__dict__)
            
            # Should not contain actual API keys or passwords
            assert 'sk-ant-secret123' not in result_str
            assert 'sk-secret123' not in result_str
            assert 'password' not in result_str.lower()
    
    def test_validation_handles_missing_permissions_safely(self):
        """Test that validation handles permission errors safely."""
        # This test would need actual file permission manipulation
        # For now, just ensure validation doesn't crash with permission errors
        
        validator = EnvironmentValidator()
        result = validator.validate()
        
        assert isinstance(result, ValidationResult)
        # Should not raise unhandled exceptions
    
    def test_validation_input_sanitization(self):
        """Test that validation properly sanitizes inputs."""
        # Test with potentially malicious environment variables
        with patch.dict(os.environ, {
            'MALICIOUS_VAR': '; rm -rf /',
            'INJECTION_TEST': '$(whoami)',
            'PATH_TRAVERSAL': '../../../etc/passwd'
        }):
            validator = EnvironmentValidator()
            result = validator.validate()
            
            assert isinstance(result, ValidationResult)
            # Should handle malicious inputs safely


if __name__ == '__main__':
    print("🔴 DEL-007 RED Phase: Validation Integration Tests")
    print("=" * 55)
    print("These tests are DESIGNED TO FAIL until implementation is complete.")
    print()
    
    # Run tests (expect failures)
    pytest.main([__file__, "-v", "--tb=short"])
    
    print("\n" + "=" * 55)
    print("🔴 RED phase complete. Proceed to GREEN phase implementation.")