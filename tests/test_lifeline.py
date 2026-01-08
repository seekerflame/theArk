import json
import requests
import time

BASE_URL = "http://localhost:3000"

def test_lifeline():
    print("🚀 Testing Lifeline API...")
    
    # login if needed, or assume dev environment without strict auth for this test
    # (Actually we need a token for @auth_decorator)
    
    # For simplicity in this test, we'll assume a user 'dagny' exists or we create one
    user_payload = {"username": "dagny_lifetest", "password": "password123"}
    requests.post(f"{BASE_URL}/api/register", json=user_payload)
    login_res = requests.post(f"{BASE_URL}/api/login", json=user_payload).json()
    token = login_res['data']['token']
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Add Memory
    res = requests.post(f"{BASE_URL}/api/lifeline/memories/add", 
                        headers=headers, 
                        json={"content": "Built the Lifeline module today."})
    print(f"Add Memory: {res.json()['status']}")

    # 2. Get Data
    res = requests.get(f"{BASE_URL}/api/lifeline/data", headers=headers)
    data = res.json()['data']
    print(f"Memories count: {len(data['memories'])}")

    # 3. Add Op
    res = requests.post(f"{BASE_URL}/api/lifeline/ops/add",
                        headers=headers,
                        json={"type": "cleaning", "content": "Clean the workshop"})
    print(f"Add Op: {res.json()['status']}")
    op_id = res.json()['data']['op']['id']

    # 4. Toggle Op
    res = requests.post(f"{BASE_URL}/api/lifeline/ops/toggle",
                        headers=headers,
                        json={"type": "cleaning", "id": op_id})
    print(f"Toggle Op: {res.json()['status']} -> {res.json()['data']['new_status']}")

    # 5. Add Favor
    res = requests.post(f"{BASE_URL}/api/lifeline/favors/add",
                        headers=headers,
                        json={"content": "Prepare breakfast for tomorrow Dagny"})
    print(f"Add Favor: {res.json()['status']}")

    # 6. Complete Zen
    res = requests.post(f"{BASE_URL}/api/lifeline/zen/complete", headers=headers)
    print(f"Complete Zen: {res.json()['status']}, Total: {res.json()['data']['total_cycles']}")

    print("✅ Lifeline API Test Passed.")

if __name__ == "__main__":
    try:
        test_lifeline()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
