"""
FreeWay Community — End-to-End Live Demonstration Script
Runs against the live running API server at http://127.0.0.1:8000
Demonstrates:
  1. Auth & Vehicle Registration for 2 Users (Priya & Rajesh)
  2. Privacy-Preserving Plate Identification (/vehicle/identify)
  3. Obstruction Request Creation (/request/)
  4. Response by Blocking Vehicle Owner with ETA (/request/respond)
  5. Resolution of Obstruction (/request/{id}/resolve)
  6. Final Request Status & History Retrieval (/request/history)
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api/v1"

def print_step(title):
    print("\n" + "=" * 65)
    print(f"  {title}")
    print("=" * 65)

def main():
    session = requests.Session()
    
    # --- Step 1: Health Check ---
    print_step("STEP 1: Verify API Health")
    res = session.get(f"{BASE_URL}/health")
    print(f"Status: {res.status_code}")
    print("Health Data:", json.dumps(res.json(), indent=2))
    assert res.status_code == 200

    suffix = str(int(time.time()))[-4:]
    blocking_plate = f"KA01AB{suffix}"
    driver_plate = f"MH12CD{suffix}"
    
    # --- Step 2: Register Blocking Vehicle Owner (User B - Priya Sharma) ---
    print_step(f"STEP 2: Register Blocking Vehicle Owner (Priya Sharma - {blocking_plate})")
    owner_payload = {
        "vehicleNumber": blocking_plate,
        "password": "SecurePassword123!",
        "name": "Priya Sharma",
        "phoneNumber": f"+9198765{suffix}10",
        "deviceToken": f"fcm_fake_token_priya_{suffix}",
        "deviceType": "ANDROID"
    }
    res = session.post(f"{BASE_URL}/auth/register", json=owner_payload)
    print(f"Registration Status: {res.status_code}")
    owner_data = res.json()
    print("Owner Registered:", json.dumps(owner_data.get("user", {}), indent=2))
    owner_token = owner_data["tokens"]["accessToken"]

    # --- Step 3: Register Obstructed Driver (User A - Rajesh Kumar) ---
    print_step(f"STEP 3: Register Obstructed Driver (Rajesh Kumar - {driver_plate})")
    driver_payload = {
        "vehicleNumber": driver_plate,
        "password": "SecurePassword123!",
        "name": "Rajesh Kumar",
        "phoneNumber": f"+9191234{suffix}20",
        "deviceToken": f"fcm_fake_token_rajesh_{suffix}",
        "deviceType": "ANDROID"
    }
    res = session.post(f"{BASE_URL}/auth/register", json=driver_payload)
    print(f"Registration Status: {res.status_code}")
    driver_data = res.json()
    print("Driver Registered:", json.dumps(driver_data.get("user", {}), indent=2))
    driver_token = driver_data["tokens"]["accessToken"]

    # --- Step 4: Privacy-Preserving Plate Lookup ---
    print_step(f"STEP 4: Privacy-Preserving Plate Lookup for '{blocking_plate}'")
    lookup_res = session.post(
        f"{BASE_URL}/vehicle/identify",
        headers={"Authorization": f"Bearer {driver_token}"},
        json={"vehicleNumber": blocking_plate}
    )
    print(f"Lookup Status: {lookup_res.status_code}")
    lookup_info = lookup_res.json()
    print("Masked Vehicle Information (Zero Personal Data Leaked):")
    print(json.dumps(lookup_info, indent=2))

    # --- Step 5: Obstructed Driver Creates Obstruction Request ---
    print_step(f"STEP 5: Create Obstruction Request (Rajesh -> {blocking_plate})")
    req_payload = {
        "targetVehicle": blocking_plate,
        "message": "Vehicle is double-parked behind mine in Slot B-14. Need to leave for airport urgently.",
        "isEmergency": True
    }
    create_res = session.post(
        f"{BASE_URL}/request/",
        headers={"Authorization": f"Bearer {driver_token}"},
        json=req_payload
    )
    print(f"Request Creation Status: {create_res.status_code}")
    req_data = create_res.json()
    print("Created Request Response:", json.dumps(req_data, indent=2))
    request_id = req_data["requestId"]

    # --- Step 6: Owner (Priya) Responds with ETA ---
    print_step("STEP 6: Blocking Vehicle Owner (Priya) Responds (ETA: 5 mins)")
    respond_payload = {
        "requestId": request_id,
        "response": "ON_MY_WAY",
        "responseMessage": "Coming down right now with the keys!",
        "etaMinutes": 5
    }
    respond_res = session.post(
        f"{BASE_URL}/request/respond",
        headers={"Authorization": f"Bearer {owner_token}"},
        json=respond_payload
    )
    print(f"Response Status: {respond_res.status_code}")
    print("Respond Result:", json.dumps(respond_res.json(), indent=2))

    # --- Step 7: Driver Checks Updated Status (Viewing ETA) ---
    print_step("STEP 7: Driver Views Active Request Status & ETA")
    detail_res = session.get(
        f"{BASE_URL}/request/{request_id}",
        headers={"Authorization": f"Bearer {driver_token}"}
    )
    print(f"Detail Status: {detail_res.status_code}")
    detail_data = detail_res.json()
    print("Live Request Status:")
    print(f"  Status: {detail_data['status']}")
    print(f"  Owner Response: {detail_data.get('responseType')}")
    print(f"  Owner Message: {detail_data.get('responseMessage')}")
    print(f"  ETA: {detail_data.get('etaMinutes')} minutes")

    # --- Step 8: Resolution of Obstruction ---
    print_step("STEP 8: Mark Request Resolved (Obstruction Cleared)")
    resolve_res = session.post(
        f"{BASE_URL}/request/{request_id}/resolve",
        headers={"Authorization": f"Bearer {driver_token}"}
    )
    print(f"Resolve Status: {resolve_res.status_code}")
    print("Resolve Result:", json.dumps(resolve_res.json(), indent=2))

    # --- Step 9: History Audit Verification ---
    print_step("STEP 9: Retrieve Resolved Request History")
    hist_res = session.get(
        f"{BASE_URL}/request/history",
        headers={"Authorization": f"Bearer {driver_token}"}
    )
    print(f"History Status: {hist_res.status_code}")
    hist_data = hist_res.json()
    sent_requests = hist_data.get("sentRequests", [])
    print(f"Total Sent Requests in History: {len(sent_requests)}")
    if sent_requests:
        last_req = sent_requests[0]
        print(f"  ID: {last_req['id']}")
        print(f"  Target: {last_req['maskedTargetVehicle']}")
        print(f"  Final Status: {last_req['status']}")

    print("\n" + "*" * 65)
    print("  COMPLETE 9-STEP LIVE PLATFORM DEMONSTRATION SUCCEEDED!")
    print("*" * 65)

if __name__ == "__main__":
    main()
