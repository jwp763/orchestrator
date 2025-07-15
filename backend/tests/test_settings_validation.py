#!/usr/bin/env python3
"""
DEL-006 Settings Validation - Core Implementation Tests
Tests implemented Pydantic settings validation functionality.
"""

import os
import pytest
import tempfile
from unittest.mock import patch, MagicMock
from pathlib import Path

from src.config.settings import Settings, get_settings, ProvidersConfig


class TestSettingsValidation:
    """Test core settings validation functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Clear LRU cache between tests
        get_settings.cache_clear()
        self.original_env = dict(os.environ)
    
    def teardown_method(self):
        """Clean up test environment."""
        # Restore original environment
        os.environ.clear()
        os.environ.update(self.original_env)
        get_settings.cache_clear()
    
    def test_environment_detection_validation(self):
        """Test that environment is properly detected and validated."""
        # Test development environment
        with patch.dict(os.environ, {"ENVIRONMENT": "development"}):
            settings = Settings()
            assert settings.environment == "development"
            
        # Test production environment
        with patch.dict(os.environ, {"ENVIRONMENT": "production"}):
            settings = Settings()
            assert settings.environment == "production"
    
    def test_required_api_keys_validation(self):
        """Test that required API keys are validated on startup."""
        # Test missing required API keys
        with patch.dict(os.environ, {}, clear=True):
            settings = Settings()
            
            # Should have validation method for required keys
            is_valid, missing_keys = settings.validate_required_api_keys()
            assert not is_valid
            assert "ANTHROPIC_API_KEY" in missing_keys
            assert "OPENAI_API_KEY" in missing_keys
    
    def test_database_connection_validation(self):
        """Test that database connection is validated on startup."""
        settings = Settings()
        
        # Should validate database connection
        is_valid, error_message = settings.validate_database_connection()
        
        # Should return validation result
        assert isinstance(is_valid, bool)
        if not is_valid:
            assert error_message is not None
    
    def test_startup_validation_comprehensive(self):
        """Test comprehensive startup validation that combines all checks."""
        settings = Settings()
        
        # Should perform all validation checks
        validation_result = settings.validate_startup_configuration()
        
        assert hasattr(validation_result, 'is_valid')
        assert hasattr(validation_result, 'errors')
        assert hasattr(validation_result, 'warnings')
    
    def test_validation_performance_requirements(self):
        """Test that validation completes within performance requirements."""
        import time
        
        settings = Settings()
        
        start_time = time.time()
        validation_result = settings.validate_startup_configuration()
        end_time = time.time()
        
        validation_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should complete validation in < 50ms
        assert validation_time < 50, f"Validation took {validation_time:.2f}ms, should be < 50ms"


if __name__ == '__main__':
    print("✅ DEL-006 Core Settings Validation Tests")
    print("=" * 45)
    
    # Run tests
    pytest.main([__file__, "-v"])
    
    print("\n" + "=" * 45)
    print("✅ Core settings validation tests completed.")