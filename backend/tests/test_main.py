import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

def test_health_check():
    """Verify that the health check endpoint returns 200."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_public_stats_unauthorized():
    """Verify that dashboard stats require authentication."""
    response = client.get("/api/v1/dashboard/stats")
    assert response.status_code == 401
