
import requests
import time

BASE_URL = "http://localhost:3006"

def test_fishery_digital_threat():
    print("🚀 Starting Fishery Digital Threat Test...")
    
    # 1. Get Admin Token FIRST (before triggering shields)
    r_auth = requests.post(f"{BASE_URL}/api/login", json={"username": "superadmin", "password": "superpassword"})
    token = r_auth.json()['data']['token']
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Trigger SHIELDED state (10 failures)
    print("⚔️  Simulating Brute Force (Auth Failures)...")
    for i in range(12):
        r = requests.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "wrong_password"})
        time.sleep(0.05)
        if i == 10:
            print(f"📊 Checkpoint at 10 failures: Status {r.status_code}")

    # 3. Verify SHIELDED state
    status_r = requests.get(f"{BASE_URL}/api/fishery/status", headers=headers)
    print(f"📡 Status Request: {status_r.status_code} - {status_r.text}")
    resp = status_r.json()
    if resp.get('status') == 'error':
        print(f"❌ API Error: {resp.get('message')}")
        return
    status = resp.get('data', {})
    print(f"🛡️ Current Fishery State: {status.get('state')}")
    assert status.get('state') == "SHIELDED"
    print("✅ SHIELDED state confirmed.")

    # 3. Trigger LOCKDOWN (50 failures)
    print("🔥 Scaling attack to trigger LOCKDOWN...")
    for i in range(40):
        requests.post(f"{BASE_URL}/api/login", json={"username": "admin", "password": "wrong_password"})
        time.sleep(0.05)
    
    # 4. Verify LOCKDOWN
    # Any request should now return 503
    r_lockdown = requests.get(f"{BASE_URL}/api/state")
    print(f"🛑 Lockdown response: {r_lockdown.status_code}")
    assert r_lockdown.status_code == 503
    assert "NODE IN LOCKDOWN" in r_lockdown.text
    print("✅ LOCKDOWN state confirmed. Node is secured.")

if __name__ == "__main__":
    try:
        test_fishery_digital_threat()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
