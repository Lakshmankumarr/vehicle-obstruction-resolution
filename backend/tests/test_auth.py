"""
Unit and integration tests for authentication endpoints.
"""
import pytest
from fastapi import status


def test_user_registration_success(client):
    """Test successful user registration with vehicle plate."""
    payload = {
        "vehicleNumber": "KA05MB9999",
        "password": "SecurePassword123!",
        "phoneNumber": "+919988776655",
        "name": "Karthik"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["success"] is True
    assert "tokens" in data
    assert "accessToken" in data["tokens"]
    assert "refreshToken" in data["tokens"]
    assert data["user"]["primaryVehicle"] == "KA05MB9999"


def test_user_registration_duplicate_vehicle_rejected(client, user_a):
    """Test that attempting to register an already-registered plate returns 409 Conflict."""
    payload = {
        "vehicleNumber": "DL01AB1111",  # Already owned by user_a
        "password": "AnotherPassword123!",
        "phoneNumber": "+919900000000"
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == status.HTTP_409_CONFLICT


def test_user_login_success(client, user_a):
    """Test login with registered vehicle number and valid password."""
    payload = {
        "vehicleNumber": "DL01AB1111",
        "password": "Password123!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["success"] is True
    assert data["tokens"]["accessToken"] is not None


def test_user_login_wrong_password_rejected(client, user_a):
    """Test login with invalid password returns 401 Unauthorized."""
    payload = {
        "vehicleNumber": "DL01AB1111",
        "password": "WrongPassword!"
    }
    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_refresh_token_endpoint(client, user_a):
    """Test token refresh using valid refresh token."""
    login_res = client.post("/api/v1/auth/login", json={
        "vehicleNumber": "DL01AB1111",
        "password": "Password123!"
    }).json()

    refresh_tok = login_res["tokens"]["refreshToken"]
    refresh_res = client.post("/api/v1/auth/refresh", json={"refreshToken": refresh_tok})
    assert refresh_res.status_code == status.HTTP_200_OK
    assert "accessToken" in refresh_res.json()


def test_get_current_user_profile(client, token_user_a):
    """Test /me endpoint returns user profile."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["primaryVehicle"] == "DL01AB1111"
    assert data["reputationScore"] == 100.0
