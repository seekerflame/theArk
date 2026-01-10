import requests
import json
import time

BASE_URL = "http://localhost:3006"

def seed():
    print("🚀 Seeding Thrive Ecosystem...")
    
    # 1. Login as Lead_Architect
    username = os.environ.get("ARK_ADMIN_USER", "Lead_Architect")
    password = os.environ.get("ARK_ADMIN_PASS", "queen_password")
    
    print(f"🔑 Authenticating as {username}...")
    login_resp = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})
    
    if login_resp.status_code != 200:
        print("    Registering Lead_Architect...")
        reg_resp = requests.post(f"{BASE_URL}/api/register", json={"username": username, "password": password})
        if reg_resp.status_code != 200:
            print(f"❌ Registration failed: {reg_resp.text}")
            return
        login_resp = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})

    try:
        resp_json = login_resp.json()
        # The server wraps data in a 'data' field
        data = resp_json.get('data', resp_json)
        token = data.get('token')
        
        if not token:
            print(f"❌ Login failed: {resp_json}")
            return
    except Exception as e:
        print(f"❌ Error parsing login response: {e}")
        print(f"RAW: {login_resp.text}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # 2. Seed Board Bored Ads (Attention-to-Instruction)
    print("📺 Seeding Board Bored...")
    requests.post(f"{BASE_URL}/api/bored/create", headers=headers, json={
        "title": "Learn: Modular Chassis Assembly",
        "content": "Review the blueprint for the SEED-Home chassis. Mint 0.5 AT for your attention.",
        "budget": 50.0
    })
    requests.post(f"{BASE_URL}/api/bored/create", headers=headers, json={
        "title": "Safety Audit: Weld Points",
        "content": "Verify the weld point locations on the primary pillars. Crucial for structural integrity.",
        "budget": 20.0
    })

    # 3. Seed Swarm Projects (Modular Build)
    print("🐝 Seeding Swarm Engine...")
    requests.post(f"{BASE_URL}/api/swarm/seed_demo", headers=headers)

    # 4. Seed Care Tasks (Social Labor)
    print("💗 Seeding Care Circle...")
    requests.post(f"{BASE_URL}/api/care/seed_demo", headers=headers)

    # 5. Gaia Autonomy Trigger
    print("🧠 Triggering Gaia Pulse...")
    requests.get(f"{BASE_URL}/api/gaia/pulse")

    print("✅ Ecosystem Seeded. Node is now in THRIVE state.")

if __name__ == "__main__":
    seed()
