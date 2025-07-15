#!/usr/bin/env python3
"""
DEL-006 Health Check Endpoints - Core Implementation Tests
Tests implemented health check endpoints with detailed status.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

from src.api.main import create_app
from src.config.settings import Settings


class TestHealthCheckEndpoints:
    """Test core health check endpoints functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        self.original_env = dict(os.environ)
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def teardown_method(self):
        """Clean up test environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_basic_health_check_endpoint(self):
        """Test basic health check endpoint returns expected format."""
        response = self.client.get("/health")
        
        # Health endpoint can return 200 (healthy) or 503 (unhealthy) based on validation
        assert response.status_code in [200, 503], f"Expected 200 or 503, got {response.status_code}"
        
        health_data = response.json()
        
        # Should include detailed health information
        required_fields = [
            "status",
            "timestamp",
            "version",
            "environment",
            "database",
            "api_providers",
            "startup_validation",
            "performance"
        ]
        
        for field in required_fields:
            assert field in health_data, f"Health check should include {field}"
        
        # Status should be one of the expected values
        assert health_data["status"] in ["healthy", "degraded", "unhealthy"]
        
        # Should have performance metrics
        assert "response_time" in health_data["performance"]
        assert "memory_usage" in health_data["performance"]
        assert "uptime" in health_data["performance"]
    
    def test_detailed_health_check_endpoint(self):
        """Test detailed health check endpoint with comprehensive status."""
        response = self.client.get("/health/detailed")
        assert response.status_code == 200
        
        health_data = response.json()
        
        # Should include all health information plus additional details
        detailed_fields = [
            "status",
            "components",
            "checks",
            "diagnostics",
            "recommendations"
        ]
        
        for field in detailed_fields:
            assert field in health_data, f"Detailed health check should include {field}"
        
        # Verify components structure
        components = health_data["components"]
        assert "database" in components
        assert "api_providers" in components
        assert "configuration" in components
        assert "performance" in components
        
        # Verify checks structure
        checks = health_data["checks"]
        assert isinstance(checks, list)
        assert len(checks) > 0
        
        # Each check should have name, status, and message
        for check in checks:
            assert "name" in check
            assert "status" in check
            assert "message" in check
            assert check["status"] in ["pass", "fail"]
    
    def test_health_check_response_time_requirement(self):
        """Test that health check meets response time requirements."""
        import time
        
        start_time = time.time()
        response = self.client.get("/health")
        end_time = time.time()
        
        assert response.status_code in [200, 503]
        
        response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Should respond in < 100ms (relaxed from 50ms for CI)
        assert response_time < 100, f"Health check took {response_time:.2f}ms, should be < 100ms"


class TestHealthCheckSecurity:
    """Test health check security and information disclosure prevention."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_health_check_authentication_not_required(self):
        """Test that health check doesn't require authentication."""
        # Health checks should be publicly accessible for monitoring
        
        response = self.client.get("/health")
        # Should not return 401 or 403
        assert response.status_code != 401
        assert response.status_code != 403
        
        # Should return either 200 (healthy) or 503 (unhealthy)
        assert response.status_code in [200, 503]


class TestHealthCheckIntegration:
    """Test health check integration with monitoring systems."""
    
    def setup_method(self):
        """Set up test environment."""
        self.app = create_app()
        self.client = TestClient(self.app)
    
    def test_health_check_prometheus_metrics_format(self):
        """Test that health check can provide Prometheus metrics format."""
        response = self.client.get("/metrics")
        assert response.status_code == 200
        
        # Should return Prometheus metrics format
        assert response.headers["content-type"] == "text/plain; version=0.0.4; charset=utf-8"
        
        metrics_text = response.text
        
        # Should include basic metrics
        expected_metrics = [
            "health_check_status",
            "database_connection_status",
            "api_provider_status",
            "response_time_seconds"
        ]
        
        for metric in expected_metrics:
            assert metric in metrics_text, f"Metrics should include {metric}"
        
        # Verify Prometheus format structure
        lines = metrics_text.strip().split('\n')
        assert len(lines) > 0, "Metrics should contain data"
        
        # Each line should be a valid metric
        for line in lines:
            if line.strip():  # Skip empty lines
                assert ' ' in line, f"Metric line should have format 'metric_name value': {line}"


if __name__ == '__main__':
    print("✅ DEL-006 Core Health Endpoints Tests")
    print("=" * 42)
    
    # Run tests
    pytest.main([__file__, "-v"])
    
    print("\n" + "=" * 42)
    print("✅ Core health endpoints tests completed.")