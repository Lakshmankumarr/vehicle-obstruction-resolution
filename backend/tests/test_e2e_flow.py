"""
End-to-end integration tests for FreeWay Community:
1. User registration & login with vehicle plate & phone number
2. Vehicle identification and privacy masking
3. Sending obstruction requests
4. Receiving requests on target user dashboard/history
5. Responding to requests (MOVING, ETA)
6. Resolving requests
"""
import pytest
from fastapi.testclient import TestClient
from starlette import status

def test_complete_e2e_obstruction_flow(client: TestClient):
    import time
    ts = int(time.time()) % 9000 + 1000
    plate_a = f"KA01AB{ts}"
    phone_a = f"98111{ts}"
    plate_b = f"MH12CD{ts}"
    phone_b = f"98222{ts}"
    pwd = "Password123!"

    # 1. Register Sender A
    res_reg_a = client.post("/api/v1/auth/register", json={
        "vehicleNumber": plate_a,
        "password": pwd,
        "name": "Sender Alice",
        "phoneNumber": phone_a
    })
    assert res_reg_a.status_code == status.HTTP_201_CREATED
    data_reg_a = res_reg_a.json()
    assert "tokens" in data_reg_a
    assert data_reg_a["user"]["name"] == "Sender Alice"

    # 2. Register Receiver B
    res_reg_b = client.post("/api/v1/auth/register", json={
        "vehicleNumber": plate_b,
        "password": pwd,
        "name": "Receiver Bob",
        "phoneNumber": phone_b
    })
    assert res_reg_b.status_code == status.HTTP_201_CREATED

    # 3. Log in Sender A via plate
    res_log_a = client.post("/api/v1/auth/login", json={
        "vehicleNumber": plate_a,
        "password": pwd
    })
    assert res_log_a.status_code == status.HTTP_200_OK
    token_a = res_log_a.json()["tokens"]["accessToken"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 4. Log in Receiver B via phone
    res_log_b = client.post("/api/v1/auth/login", json={
        "vehicleNumber": phone_b,
        "password": pwd
    })
    assert res_log_b.status_code == status.HTTP_200_OK
    token_b = res_log_b.json()["tokens"]["accessToken"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 5. Sender A identifies Receiver B vehicle
    res_ident = client.post("/api/v1/vehicle/identify", json={"vehicleNumber": plate_b}, headers=headers_a)
    assert res_ident.status_code == status.HTTP_200_OK
    ident_data = res_ident.json()
    assert ident_data["isRegistered"] is True
    assert ident_data["canSendRequest"] is True
    assert "maskedVehicleNumber" in ident_data
    assert "masked_number" in ident_data

    # 6. Sender A creates obstruction request
    res_create = client.post("/api/v1/request/", json={
        "targetVehicle": plate_b,
        "message": "Car is blocking driveway, please move it!",
        "isEmergency": False
    }, headers=headers_a)
    assert res_create.status_code == status.HTTP_201_CREATED
    req_data = res_create.json()
    request_id = req_data["requestId"]
    assert req_data["id"] == request_id

    # 7. Receiver B gets history and finds the request
    res_hist_b = client.get("/api/v1/request/history", headers=headers_b)
    assert res_hist_b.status_code == status.HTTP_200_OK
    hist_b = res_hist_b.json()
    assert len(hist_b["received"]) >= 1
    assert "requests" in hist_b
    recv_req = next((r for r in hist_b["received"] if r["id"] == request_id), None)
    assert recv_req is not None
    assert recv_req["direction"] == "incoming"
    assert recv_req["status"] == "PENDING"
    assert recv_req["message"] == "Car is blocking driveway, please move it!"

    # 8. Receiver B responds: MOVING with ETA
    res_resp = client.post("/api/v1/request/respond", json={
        "requestId": request_id,
        "response": "MOVING",
        "responseMessage": "On my way down now!",
        "etaMinutes": 3
    }, headers=headers_b)
    assert res_resp.status_code == status.HTTP_200_OK
    assert res_resp.json()["status"] == "ON_MY_WAY"

    # 9. Sender A inspects live status
    res_status = client.get(f"/api/v1/request/{request_id}", headers=headers_a)
    assert res_status.status_code == status.HTTP_200_OK
    live_data = res_status.json()
    assert live_data["status"] == "ON_MY_WAY"
    assert live_data["etaMinutes"] == 3
    assert live_data["isRequester"] is True

    # 10. Sender A marks request as resolved
    res_res = client.post(f"/api/v1/request/{request_id}/resolve", headers=headers_a)
    assert res_res.status_code == status.HTTP_200_OK
    assert res_res.json()["status"] == "RESOLVED"
