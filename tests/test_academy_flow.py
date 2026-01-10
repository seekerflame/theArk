import requests
import json
import time

BASE_URL = "http://localhost:3006"

def login():
    username = os.environ.get("ARK_ADMIN_USER", "Lead_Architect")
    password = os.environ.get("ARK_ADMIN_PASS", "queen_password")
    try:
        r = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})
        if r.status_code == 200:
            resp_json = r.json()
            data = resp_json.get('data', resp_json)
            return data.get('token')
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def test_academy():
    print("🚀 Starting Academy Flow Test...")
    token = login()
    if not token:
        print("❌ Login failed")
        return
        
    headers = {"Authorization": f"Bearer {token}"}

    # 1. List Missions
    print("\n1. Listing Missions...")
    r = requests.get(f"{BASE_URL}/api/academy/missions", headers=headers)
    if r.status_code != 200:
        print(f"❌ Failed to list missions: {r.text}")
        return
        
    data = r.json().get('data', {})
    missions = data.get('missions', [])
    print(f"✅ Found {len(missions)} missions")
    
    if not missions:
        print("⚠️ No missions available to test further")
        return
        
    mission_id = missions[0]['id']
    print(f"👉 Selecting Mission: {mission_id}")

    # 2. Claim Mission
    print("\n2. Claiming Mission...")
    r = requests.post(f"{BASE_URL}/api/academy/claim", json={"mission_id": mission_id}, headers=headers)
    print(f"Response: {r.status_code} - {r.text}")
    
    # 3. Verify Physical Action (if applicable)
    print("\n3. Simulating Physical Verification...")
    # Using self as student for test purposes, effectively verifying self (or need a second user)
    # The API expects 'student_id', using the logged in user's ID which we need to get from token or assumptions
    # Decoded token would have 'sub', let's assume 'Lead_Architect' 
    verify_data = {
        "mission_id": mission_id,
        "student_id": "Lead_Architect",
        "proof_type": "qr_scan", 
        "data": "valid_qr_code_mock"
    }
    r = requests.post(f"{BASE_URL}/api/academy/verify_physical", json=verify_data, headers=headers)
    print(f"Response: {r.status_code} - {r.text}")
    
    print("\n✨ Academy Test Complete.")

if __name__ == "__main__":
    test_academy()
