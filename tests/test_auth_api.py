import pytest
from fastapi.testclient import TestClient
from api.app.auth import app

def test_health_check():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_login_success():
    client = TestClient(app)
    response = client.post("/login", data={"username": "user", "password": "password"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_failure():
    client = TestClient(app)
    response = client.post("/login", data={"username": "user", "password": "wrongpass"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"

def test_protected_route():
    client = TestClient(app)
    # Get token
    login = client.post("/login", data={"username": "user", "password": "password"})
    token = login.json()["access_token"]
    # Access protected
    response = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "Hello, user!" in response.json()["message"]

def test_protected_route_unauthorized():
    client = TestClient(app)
    response = client.get("/protected", headers={"Authorization": "Bearer invalidtoken"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token"
