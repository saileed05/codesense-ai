"""Simple tests for API endpoints"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from main import app

# Fix: Don't create client globally, create it in each test
# OR use the correct import

def test_root_endpoint():
    """Test root endpoint"""
    client = TestClient(app=app)
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_health_check():
    """Test health check"""
    client = TestClient(app=app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data


def test_visualize_array():
    """Test visualization endpoint"""
    client = TestClient(app=app)
    payload = {
        "code": "arr = [1, 2, 3]",
        "language": "python"
    }
    response = client.post("/visualize", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "steps" in data


def test_visualize_requires_python():
    """Test that non-Python is rejected"""
    client = TestClient(app=app)
    payload = {
        "code": "console.log('test')",
        "language": "javascript"
    }
    response = client.post("/visualize", json=payload)
    assert response.status_code == 400


def test_explain_validation():
    """Test explain endpoint validation"""
    client = TestClient(app=app)
    payload = {
        "code": "   ",  # Empty whitespace
        "language": "python",
        "level": "beginner"
    }
    response = client.post("/explain", json=payload)
    assert response.status_code == 422  # Validation error