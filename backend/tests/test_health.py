"""
Tests for system health and readiness check endpoint.
Fixes:
- Section 99 Issue 30: Health check validates DB and cache dependencies
"""
from fastapi import status


def test_health_check_endpoint(client):
    """Test health check returns 200 and component statuses."""
    response = client.get("/api/v1/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data
    assert data["services"]["database"]["status"] == "up"
    assert data["services"]["redis"]["status"] in ["up", "degraded"]
    assert data["services"]["alpr"]["status"] == "ready"
