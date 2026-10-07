"""
Unit tests for vehicle registration, multiple vehicle management, and privacy masking.
"""
from fastapi import status
from app.utils.vehicle_validation import normalize_vehicle_number, mask_vehicle_number, validate_vehicle_format
from app.core.redis import get_redis_client


def test_vehicle_plate_normalization():
    """Tests whitespace and hyphen stripping."""
    assert normalize_vehicle_number("dl 01 ab 1234") == "DL01AB1234"
    assert normalize_vehicle_number("mh-12-de-9999") == "MH12DE9999"
    assert normalize_vehicle_number("22 bh 1234 aa") == "22BH1234AA"


def test_vehicle_plate_validation():
    """Tests valid vs invalid Indian license plate formats."""
    assert validate_vehicle_format("DL01AB1234") is True
    assert validate_vehicle_format("MH12DE1433") is True
    assert validate_vehicle_format("22BH1234AA") is True
    assert validate_vehicle_format("INVALID_PLATE") is False
    assert validate_vehicle_format("123") is False


def test_vehicle_privacy_masking():
    """Tests that middle characters are masked while prefix and suffix remain for verification."""
    masked = mask_vehicle_number("DL01AB1234")
    assert "DL" in masked
    assert "1234" in masked
    assert "*" in masked or "•" in masked


def test_add_multiple_vehicles(client, token_user_a):
    """Tests adding a second vehicle to user account."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {
        "vehicleNumber": "DL02CD3333",
        "nickname": "Weekend Thar",
        "vehicleType": "SUV",
        "isPrimary": False
    }
    response = client.post("/api/v1/vehicle/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["vehicleNumber"] == "DL02CD3333"

    # List vehicles
    list_res = client.get("/api/v1/vehicle/", headers=headers)
    assert list_res.status_code == status.HTTP_200_OK
    assert len(list_res.json()) == 2


def test_vehicle_identify_registered(client, token_user_a, user_a, user_b):
    """Tests looking up User B's vehicle from User A's perspective."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    # Clear any residual cooldown
    get_redis_client().delete(f"cooldown:{str(user_a.id)}:MH12DE2222")

    payload = {"vehicleNumber": "MH12DE2222"}
    response = client.post("/api/v1/vehicle/identify", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["isRegistered"] is True
    assert data["canSendRequest"] is True
    assert "maskedVehicleNumber" in data


def test_vehicle_identify_own_vehicle(client, token_user_a):
    """Tests looking up caller's own vehicle."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {"vehicleNumber": "DL01AB1111"}
    response = client.post("/api/v1/vehicle/identify", json=payload, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["canSendRequest"] is False
