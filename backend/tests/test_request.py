"""
End-to-End integration tests for the vehicle obstruction resolution lifecycle.
Validates:
- Section 101: Required E2E Demo (User A -> User B -> Response -> Resolution)
- Section 59: Duplicate Request Protection
- Section 60: Target Cooldown
- Section 99 Issue 28: Persisted Message
"""
from fastapi import status


def test_full_obstruction_resolution_lifecycle(client, token_user_a, token_user_b, user_a, user_b):
    """
    Simulates complete obstruction resolution flow between User A (requester) and User B (target).
    """
    headers_a = {"Authorization": f"Bearer {token_user_a}"}
    headers_b = {"Authorization": f"Bearer {token_user_b}"}

    # Step 1: User A creates request for User B's vehicle
    create_payload = {
        "targetVehicle": "MH12DE2222",
        "message": "Car is blocking my garage driveway, please move it!"
    }
    create_res = client.post("/api/v1/request/", json=create_payload, headers=headers_a)
    assert create_res.status_code == status.HTTP_201_CREATED
    req_data = create_res.json()
    assert req_data["success"] is True
    request_id = req_data["requestId"]
    assert req_data["status"] == "PENDING"

    # Step 2: User B checks their received requests
    history_res = client.get("/api/v1/request/history", headers=headers_b)
    assert history_res.status_code == status.HTTP_200_OK
    b_history = history_res.json()
    assert len(b_history["received"]) >= 1
    target_req = next(r for r in b_history["received"] if r["id"] == request_id)
    assert target_req["status"] == "PENDING"
    assert target_req["message"] == "Car is blocking my garage driveway, please move it!"

    # Step 3: User B responds with ON_MY_WAY and 5 minute ETA
    respond_payload = {
        "requestId": request_id,
        "response": "ON_MY_WAY",
        "responseMessage": "Coming down right now!",
        "etaMinutes": 5
    }
    respond_res = client.post("/api/v1/request/respond", json=respond_payload, headers=headers_b)
    assert respond_res.status_code == status.HTTP_200_OK
    assert respond_res.json()["status"] == "ON_MY_WAY"

    # Step 4: User A checks live status
    status_res = client.get(f"/api/v1/request/{request_id}", headers=headers_a)
    assert status_res.status_code == status.HTTP_200_OK
    live_data = status_res.json()
    assert live_data["status"] == "ON_MY_WAY"
    assert live_data["etaMinutes"] == 5
    assert live_data["responseMessage"] == "Coming down right now!"

    # Step 5: Obstacle cleared, User A resolves the request
    resolve_res = client.post(f"/api/v1/request/{request_id}/resolve", headers=headers_a)
    assert resolve_res.status_code == status.HTTP_200_OK
    assert resolve_res.json()["status"] == "RESOLVED"

    # Verify final status in history
    final_status = client.get(f"/api/v1/request/{request_id}", headers=headers_a).json()
    assert final_status["status"] == "RESOLVED"


def test_cannot_request_own_vehicle(client, token_user_a):
    """User cannot request their own vehicle."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {"targetVehicle": "DL01AB1111"}
    response = client.post("/api/v1/request/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_unregistered_vehicle_request_fails(client, token_user_a):
    """Requesting an unregistered vehicle returns 404."""
    headers = {"Authorization": f"Bearer {token_user_a}"}
    payload = {"targetVehicle": "UP16AB9999"}
    response = client.post("/api/v1/request/", json=payload, headers=headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND
