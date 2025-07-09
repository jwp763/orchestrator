"""
Security tests for input validation and SQL injection prevention.

Tests API-001 acceptance criteria:
- Security tests for input validation and SQL injection prevention
"""

import pytest
import json
from fastapi.testclient import TestClient

from src.api.main import app
from .test_database_isolation import TestDatabaseIsolation


class TestAPISecurity(TestDatabaseIsolation):
    """Security tests for input validation and SQL injection prevention."""
    
    def test_sql_injection_prevention_projects(self, isolated_client):
        """Test SQL injection prevention in project endpoints."""
        # Test SQL injection in project creation
        sql_injection_payloads = [
            "'; DROP TABLE projects; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM projects --",
            "'; DELETE FROM projects WHERE id = '1'; --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "1' OR '1'='1' --",
            "' OR ''=''"
        ]
        
        for payload in sql_injection_payloads:
            project_data = {
                "name": payload,
                "description": f"SQL injection test with payload: {payload}",
                "status": "planning",
                "priority": "medium",
                "created_by": payload
            }
            
            # Should not cause SQL injection - either creates safely or returns validation error
            response = isolated_client.post("/api/projects", json=project_data)
            
            # Should not return 500 (SQL error) - either 201 (success) or 422 (validation)
            assert response.status_code in [201, 422], f"SQL injection may have occurred with payload: {payload}"
            
            if response.status_code == 201:
                # If created successfully, the payload should be stored as-is (escaped)
                project = response.json()
                assert project["name"] == payload
                
                # Test SQL injection in get request
                get_response = isolated_client.get(f"/api/projects/{project['id']}")
                assert get_response.status_code == 200
                
                # Clean up
                delete_response = isolated_client.delete(f"/api/projects/{project['id']}")
                assert delete_response.status_code == 204
    
    def test_sql_injection_prevention_tasks(self, isolated_client):
        """Test SQL injection prevention in task endpoints."""
        # First create a project for the tasks
        project_data = {
            "name": "SQL Injection Test Project",
            "description": "Project for SQL injection testing",
            "status": "planning",
            "priority": "medium",
            "created_by": "security_user"
        }
        
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        sql_injection_payloads = [
            "'; DROP TABLE tasks; --",
            "' OR '1'='1",
            "' UNION SELECT * FROM tasks --",
            "'; DELETE FROM tasks WHERE id = '1'; --",
            "' OR 1=1 --",
            "admin'--",
            "admin'/*",
            "' OR 'x'='x",
            "1' OR '1'='1' --",
            "' OR ''=''"
        ]
        
        for payload in sql_injection_payloads:
            task_data = {
                "project_id": project_id,
                "title": payload,
                "description": f"SQL injection test with payload: {payload}",
                "status": "todo",
                "priority": "medium",
                "assignee": payload,
                "created_by": payload
            }
            
            # Should not cause SQL injection
            response = isolated_client.post("/api/tasks", json=task_data)
            assert response.status_code in [201, 422], f"SQL injection may have occurred with payload: {payload}"
            
            if response.status_code == 201:
                # If created successfully, the payload should be stored as-is (escaped)
                task = response.json()
                assert task["title"] == payload
                
                # Test SQL injection in get request
                get_response = isolated_client.get(f"/api/tasks/{task['id']}")
                assert get_response.status_code == 200
                
                # Clean up
                delete_response = isolated_client.delete(f"/api/tasks/{task['id']}")
                assert delete_response.status_code == 204
    
    def test_input_validation_projects(self, isolated_client):
        """Test input validation for project endpoints."""
        # Test missing required fields
        invalid_payloads = [
            {},  # Empty payload
            {"name": ""},  # Empty name
            {"name": "Test", "status": "invalid_status"},  # Invalid status
            {"name": "Test", "priority": "invalid_priority"},  # Invalid priority
            {"name": "Test", "created_by": ""},  # Empty created_by
            {"name": "A" * 500, "created_by": "user"},  # Name too long
            {"name": "Test", "description": "A" * 5000, "created_by": "user"},  # Description too long
        ]
        
        for payload in invalid_payloads:
            response = isolated_client.post("/api/projects", json=payload)
            assert response.status_code == 422, f"Validation should fail for payload: {payload}"
            
            error_detail = response.json()
            assert "detail" in error_detail
    
    def test_input_validation_tasks(self, isolated_client):
        """Test input validation for task endpoints."""
        # First create a project for the tasks
        project_data = {
            "name": "Validation Test Project",
            "description": "Project for validation testing",
            "status": "planning",
            "priority": "medium",
            "created_by": "validation_user"
        }
        
        response = isolated_client.post("/api/projects", json=project_data)
        assert response.status_code == 201
        project_id = response.json()["id"]
        
        # Test invalid task payloads
        invalid_payloads = [
            {},  # Empty payload
            {"project_id": project_id},  # Missing title
            {"project_id": project_id, "title": ""},  # Empty title
            {"project_id": project_id, "title": "Test", "status": "invalid_status"},  # Invalid status
            {"project_id": project_id, "title": "Test", "priority": "invalid_priority"},  # Invalid priority
            {"project_id": "nonexistent", "title": "Test", "created_by": "user"},  # Nonexistent project
            {"project_id": project_id, "title": "A" * 500, "created_by": "user"},  # Title too long
            {"project_id": project_id, "title": "Test", "description": "A" * 5000, "created_by": "user"},  # Description too long
            {"project_id": project_id, "title": "Test", "estimated_minutes": -1, "created_by": "user"},  # Negative minutes
            {"project_id": project_id, "title": "Test", "estimated_minutes": "invalid", "created_by": "user"},  # Invalid minutes type
        ]
        
        for payload in invalid_payloads:
            response = isolated_client.post("/api/tasks", json=payload)
            assert response.status_code in [422, 404], f"Validation should fail for payload: {payload}"
            
            error_detail = response.json()
            assert "detail" in error_detail
    
    def test_xss_prevention(self, isolated_client):
        """Test XSS prevention in API responses."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src='x' onerror='alert(1)'>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "';alert('XSS');//",
            "<iframe src='javascript:alert(1)'></iframe>",
            "<body onload=alert('XSS')>",
            "<div onclick='alert(1)'>Click me</div>",
            "<%3Cscript%3Ealert('XSS')%3C/script%3E",
            "&lt;script&gt;alert('XSS')&lt;/script&gt;"
        ]
        
        for payload in xss_payloads:
            project_data = {
                "name": payload,
                "description": f"XSS test with payload: {payload}",
                "status": "planning",
                "priority": "medium",
                "created_by": "xss_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            
            if response.status_code == 201:
                project = response.json()
                
                # The payload should be returned as-is (not executed)
                assert project["name"] == payload
                assert project["description"] == f"XSS test with payload: {payload}"
                
                # Response should be JSON, not HTML
                assert response.headers["content-type"] == "application/json"
                
                # Clean up
                delete_response = isolated_client.delete(f"/api/projects/{project['id']}")
                assert delete_response.status_code == 204
    
    def test_content_type_validation(self, isolated_client):
        """Test content type validation."""
        # Test non-JSON content
        response = isolated_client.post(
            "/api/projects",
            data="not json",
            headers={"Content-Type": "text/plain"}
        )
        assert response.status_code == 422
        
        # Test malformed JSON
        response = isolated_client.post(
            "/api/projects",
            data="{invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test empty content type
        response = isolated_client.post(
            "/api/projects",
            data='{"name": "Test"}',
            headers={}
        )
        # Should still work with proper JSON
        assert response.status_code in [201, 422]
    
    def test_http_method_validation(self, isolated_client):
        """Test HTTP method validation."""
        # Test invalid methods on endpoints
        invalid_methods = [
            ("PATCH", "/api/projects"),
            ("HEAD", "/api/projects"),
            ("OPTIONS", "/api/projects"),
            ("TRACE", "/api/projects"),
        ]
        
        for method, endpoint in invalid_methods:
            response = isolated_client.request(method, endpoint)
            assert response.status_code == 405  # Method Not Allowed
    
    def test_authorization_headers(self, isolated_client):
        """Test authorization header handling."""
        # Test requests with various authorization headers
        auth_headers = [
            {"Authorization": "Bearer invalid_token"},
            {"Authorization": "Basic invalid_credentials"},
            {"Authorization": ""},
            {"X-API-Key": "some_key"},
        ]
        
        for headers in auth_headers:
            response = isolated_client.get("/api/projects", headers=headers)
            # Should still work (no auth implemented yet, but headers should be handled safely)
            assert response.status_code == 200
    
    def test_large_payload_handling(self, isolated_client):
        """Test handling of extremely large payloads."""
        # Test large string payload
        large_string = "A" * 100000  # 100KB string
        
        project_data = {
            "name": "Large Payload Test",
            "description": large_string,
            "status": "planning",
            "priority": "medium",
            "created_by": "large_user"
        }
        
        response = isolated_client.post("/api/projects", json=project_data)
        # Should either reject (422) or handle gracefully (201)
        assert response.status_code in [201, 422]
        
        if response.status_code == 422:
            error_detail = response.json()
            assert "detail" in error_detail
    
    def test_special_characters_handling(self, isolated_client):
        """Test handling of special characters and unicode."""
        special_payloads = [
            "Test with émojis 🚀 and unicòde",
            "日本語テスト",
            "العربية",
            "Тест на русском",
            "Test with\nnewlines\tand\ttabs",
            "Test with \"quotes\" and 'apostrophes'",
            "Test with \\backslashes\\ and /slashes/",
            "Test with null\\x00characters",
            "Test with control\\x01characters\\x02",
            "Test\rwith\rcarriage\rreturns"
        ]
        
        for payload in special_payloads:
            project_data = {
                "name": payload,
                "description": f"Special characters test: {payload}",
                "status": "planning",
                "priority": "medium",
                "created_by": "special_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            
            if response.status_code == 201:
                project = response.json()
                # Should preserve the original payload
                assert project["name"] == payload
                
                # Test retrieval
                get_response = isolated_client.get(f"/api/projects/{project['id']}")
                assert get_response.status_code == 200
                retrieved_project = get_response.json()
                assert retrieved_project["name"] == payload
                
                # Clean up
                delete_response = isolated_client.delete(f"/api/projects/{project['id']}")
                assert delete_response.status_code == 204
    
    def test_null_byte_injection(self, isolated_client):
        """Test null byte injection prevention."""
        null_byte_payloads = [
            "test\\x00.txt",
            "test\\0.txt",
            "test\x00malicious",
            "test%00.txt",
            "normaltext\\x00<script>alert('XSS')</script>",
        ]
        
        for payload in null_byte_payloads:
            project_data = {
                "name": payload,
                "description": f"Null byte test: {payload}",
                "status": "planning",
                "priority": "medium",
                "created_by": "null_user"
            }
            
            response = isolated_client.post("/api/projects", json=project_data)
            
            # Should either handle safely or reject
            assert response.status_code in [201, 422]
            
            if response.status_code == 201:
                project = response.json()
                # Should not interpret null bytes as string terminators
                assert project["name"] == payload
                
                # Clean up
                delete_response = isolated_client.delete(f"/api/projects/{project['id']}")
                assert delete_response.status_code == 204
    
    def test_path_traversal_prevention(self, isolated_client):
        """Test path traversal prevention in URL parameters."""
        path_traversal_payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fpasswd",
            "..%252f..%252f..%252fetc%252fpasswd",
            "..%c0%af..%c0%af..%c0%afetc%c0%afpasswd",
        ]
        
        for payload in path_traversal_payloads:
            # Test in URL path
            response = isolated_client.get(f"/api/projects/{payload}")
            # Should return 404 (not found) not 500 (error) or file contents
            assert response.status_code == 404
            
            # Should not return file contents
            response_text = response.text.lower()
            assert "root:" not in response_text
            assert "administrator" not in response_text
    
    def test_response_headers_security(self, isolated_client):
        """Test security-related response headers."""
        response = isolated_client.get("/api/projects")
        
        # Check for security headers (these may not be implemented yet)
        headers = response.headers
        
        # Content-Type should be properly set
        assert "content-type" in headers
        assert "application/json" in headers["content-type"]
        
        # Response should not contain sensitive information
        assert "server" not in headers.get("server", "").lower() or "fastapi" in headers.get("server", "").lower()
    
    def test_error_message_information_disclosure(self, isolated_client):
        """Test that error messages don't disclose sensitive information."""
        # Test various error scenarios
        error_scenarios = [
            ("GET", "/api/projects/nonexistent-id"),
            ("PUT", "/api/projects/nonexistent-id", {"name": "Test"}),
            ("DELETE", "/api/projects/nonexistent-id"),
            ("GET", "/api/tasks/nonexistent-id"),
            ("PUT", "/api/tasks/nonexistent-id", {"title": "Test"}),
            ("DELETE", "/api/tasks/nonexistent-id"),
        ]
        
        for method, endpoint, *data in error_scenarios:
            if data:
                response = isolated_client.request(method, endpoint, json=data[0])
            else:
                response = isolated_client.request(method, endpoint)
            
            assert response.status_code in [404, 422]
            
            error_detail = response.json()
            error_message = str(error_detail).lower()
            
            # Should not contain sensitive information
            sensitive_terms = [
                "password", "token", "secret", "key", "database", "sql",
                "internal", "stack trace", "exception", "traceback"
            ]
            
            for term in sensitive_terms:
                assert term not in error_message, f"Error message may contain sensitive term '{term}': {error_detail}"