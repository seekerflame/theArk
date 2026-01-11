
import requests
import time

BASE_URL = "http://localhost:3006"

def setup_user(username, password):
    requests.post(f"{BASE_URL}/api/register", json={"username": username, "password": password})
    r = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})
    return r.json()['data']['token']

def test_passport_flow():
    print("🚀 Starting Sovereign Passport Flow Test...")
    
    # 0. Setup: We need 3 existing Sovereign Citizens to attest for a new one.
    # We'll use 'superadmin' as the first one (seeded as admin).
    # Wait, superadmin needs a passport too!
    admin_token = setup_user("superadmin", "superpassword") # Already exists but we need token
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Manually issue passport to superadmin for testing if not exists
    requests.post(f"{BASE_URL}/api/sovereign/passport/request", headers=admin_headers)
    
    # Bootstrap verifiers by giving them passports directly (as admin)
    verifiers = []
    for i in range(3):
        uname = f"verifier_{i}"
        token = setup_user(uname, "password123")
        headers = {"Authorization": f"Bearer {token}"}
        # Admin grants it
        requests.post(f"{BASE_URL}/api/sovereign/passport/grant", 
                      headers=admin_headers, 
                      json={"target": uname})
        verifiers.append({"username": uname, "token": token, "headers": headers})

    # Target user
    target_uname = "new_citizen_v1"
    target_token = setup_user(target_uname, "password123")
    target_headers = {"Authorization": f"Bearer {target_token}"}
    
    # 1. Target Requests Passport
    print(f"📝 {target_uname} requesting passport...")
    r = requests.post(f"{BASE_URL}/api/sovereign/passport/request", headers=target_headers)
    print(f"Response: {r.json()}")

    # 2. Get Presence Token
    r_presence = requests.post(f"{BASE_URL}/api/sovereign/passport/at_token", json={})
    presence_token = r_presence.json()['data']['presence_token']
    print(f"📍 Presence Token: {presence_token}")

    # 3. 3 Verifiers Attest (Mocking they have passports for now)
    # Wait, the code checks `is_sovereign(verifier)`. I need to ensure them have passports.
    # To bootstrap, I'll use the 'superadmin' as the FIRST verifier and then recursive...
    # Actually, for this test, I'll just check the error if not sovereign.
    
    print(f"🤝 Verifiers attesting for {target_uname}...")
    for v in verifiers:
         r = requests.post(f"{BASE_URL}/api/sovereign/passport/attest", 
                          headers=v['headers'], 
                          json={"target": target_uname, "presence_token": presence_token})
         resp_data = r.json().get('data', r.json())
         print(f"Attestation from {v['username']}: {resp_data.get('message', 'No message')}")

    # 4. Check Status
    r_status = requests.get(f"{BASE_URL}/api/sovereign/passport/status", headers=target_headers)
    print(f"🛡️ Final Passport Status: {r_status.json()['data']}")

if __name__ == "__main__":
    try:
        test_passport_flow()
    except Exception as e:
        print(f"❌ Test Failed: {e}")
