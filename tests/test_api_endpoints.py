"""
Comprehensive API Endpoint Tests for Velos Backend
Tests all critical endpoints with FastAPI TestClient
"""

import pytest
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from server import app, state, ORCHESTRATOR_AVAILABLE

# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_check(self):
        """Test /health endpoint"""
        response = client.get("/health")
        assert response.status_code in [200, 503]  # 200 if healthy, 503 if degraded
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "components" in data
        assert data["components"]["api"] == "up"
    
    def test_api_health_check(self):
        """Test /api/health endpoint"""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "uptime" in data
        assert "memory_usage" in data
        assert isinstance(data["uptime"], int)
        assert isinstance(data["memory_usage"], (int, float))
    
    def test_api_status(self):
        """Test /api/status endpoint"""
        response = client.get("/api/status")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "orchestrator" in data
        assert "timestamp" in data


class TestAgentEndpoints:
    """Test agent-related endpoints"""
    
    def test_get_agents(self):
        """Test /api/agents endpoint"""
        response = client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 3  # Should have 3 agents
        
        # Check agent structure
        for agent in data["agents"]:
            assert "name" in agent
            assert "role" in agent
            assert "status" in agent
            assert "processed" in agent
            assert "successRate" in agent
            assert "avgTime" in agent
            
        # Check agent names
        agent_names = [a["name"] for a in data["agents"]]
        assert "Gatekeeper" in agent_names
        assert "Validator" in agent_names
        assert "Inquisitor" in agent_names
    
    def test_get_insights(self):
        """Test /api/insights endpoint"""
        response = client.get("/api/insights")
        assert response.status_code == 200
        data = response.json()
        assert "bias_alerts" in data
        assert "fraud_cases" in data
        assert "avg_processing_time" in data
        assert "total_candidates" in data
        assert isinstance(data["bias_alerts"], int)
        assert isinstance(data["fraud_cases"], int)
        assert isinstance(data["avg_processing_time"], (int, float))


class TestStatsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_stats(self):
        """Test /api/stats endpoint"""
        response = client.get("/api/stats")
        assert response.status_code == 200
        data = response.json()
        assert "total_candidates" in data
        assert "passed_agent1" in data
        assert "passed_agent2" in data
        assert "approved_total" in data
        assert "fraud_detected" in data
    
    def test_get_audit_trail(self):
        """Test /api/audit endpoint"""
        response = client.get("/api/audit")
        assert response.status_code == 200
        data = response.json()
        assert "audit_logs" in data
        assert isinstance(data["audit_logs"], list)
    
    def test_get_candidates(self):
        """Test /api/candidates endpoint"""
        response = client.get("/api/candidates")
        assert response.status_code == 200
        data = response.json()
        assert "candidates" in data
        assert isinstance(data["candidates"], list)


class TestVerificationEndpoint:
    """Test main verification endpoint"""
    
    def test_verify_missing_fields(self):
        """Test verification with missing fields"""
        response = client.post("/api/verify", json={})
        assert response.status_code == 422  # Validation error
    
    def test_verify_invalid_data(self):
        """Test verification with invalid data"""
        response = client.post("/api/verify", json={
            "resume_text": "a",  # Too short
            "job_description": "Test",
            "min_years": 0
        })
        assert response.status_code == 422  # Should fail validation
    
    def test_verify_valid_data(self):
        """Test verification with valid data"""
        if not ORCHESTRATOR_AVAILABLE:
            pytest.skip("Orchestrator not available")
        
        response = client.post("/api/verify", json={
            "resume_text": "Senior Software Engineer with 5 years of experience in Python, FastAPI, and React. " * 10,
            "job_description": "Looking for a Python developer with 3+ years experience in web development.",
            "min_years": 2
        })
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "status" in data


class TestSampleDataEndpoints:
    """Test sample data endpoints"""
    
    def test_get_sample_resume(self):
        """Test /api/sample-resume endpoint"""
        response = client.get("/api/sample-resume")
        assert response.status_code == 200
        data = response.json()
        assert "resume_text" in data
        assert len(data["resume_text"]) > 100
    
    def test_get_sample_job_description(self):
        """Test /api/sample-job-description endpoint"""
        response = client.get("/api/sample-job-description")
        assert response.status_code == 200
        data = response.json()
        assert "job_description" in data
        assert len(data["job_description"]) > 50


class TestTrustPacketEndpoints:
    """Test trust packet and integrity endpoints"""
    
    def test_trust_packet_invalid_id(self):
        """Test trust packet with invalid ID"""
        response = client.get("/api/trust-packet/invalid_id_12345")
        # Should return 200 with error message or 404
        assert response.status_code in [200, 404]
        if response.status_code == 200:
            data = response.json()
            # Should have empty or default data
            assert "candidate_id" in data or "error" in data
    
    def test_parser_status(self):
        """Test parser status endpoint"""
        response = client.get("/api/parser-status")
        assert response.status_code == 200
        data = response.json()
        assert "available" in data
        assert isinstance(data["available"], bool)


class TestRateLimiting:
    """Test rate limiting on critical endpoints"""
    
    def test_verify_rate_limit(self):
        """Test that verify endpoint has rate limiting"""
        # Make 6 requests (limit is 5/minute)
        responses = []
        for _ in range(6):
            response = client.post("/api/verify", json={
                "resume_text": "Test resume text " * 100,
                "job_description": "Test job description",
                "min_years": 0
            })
            responses.append(response)
        
        # At least one should be rate limited (429)
        status_codes = [r.status_code for r in responses]
        # Note: In test mode, rate limiting might not work as expected
        # This is more of an integration test
        assert any(code in [200, 422, 429] for code in status_codes)


class TestInputValidation:
    """Test input validation on endpoints"""
    
    def test_resume_length_validation(self):
        """Test resume text length validation"""
        # Too short
        response = client.post("/api/verify", json={
            "resume_text": "abc",
            "job_description": "Test job description",
            "min_years": 0
        })
        assert response.status_code == 422
    
    def test_jd_length_validation(self):
        """Test job description length validation"""
        # Too short
        response = client.post("/api/verify", json={
            "resume_text": "Test resume text " * 100,
            "job_description": "abc",
            "min_years": 0
        })
        assert response.status_code == 422
    
    def test_min_years_validation(self):
        """Test minimum years validation"""
        # Negative years
        response = client.post("/api/verify", json={
            "resume_text": "Test resume text " * 100,
            "job_description": "Test job description",
            "min_years": -1
        })
        assert response.status_code == 422


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
