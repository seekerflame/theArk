import requests
import time
import json

BASE_URL = "http://localhost:3006"
USERNAME = "Lead_Architect"
PASSWORD = "queen_password"

def run_simulation():
    print(f"--- Simulation: {USERNAME} Recursive Learning ---")
    
    # 1. Register / Login
    print("[1] Logging in...")
    resp = requests.post(f"{BASE_URL}/api/login", json={"username": USERNAME, "password": PASSWORD})
    if resp.status_code != 200 or resp.json().get('status') == 'error':
        print("    Registering new user...")
        resp = requests.post(f"{BASE_URL}/api/register", json={"username": USERNAME, "password": PASSWORD})
    
    data = resp.json().get('data', resp.json())
    token = data.get('token')
    if not token:
        print("Failed to get token")
        return

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # 2. Academy: Learn Modular Welding
    print("[2] Academy: Learning 'Modular Welding'...")
    resp = requests.post(f"{BASE_URL}/api/academy/synthesis", headers=headers, json={
        "topic": "Modular Welding",
        "complexity": 2
    })
    print(f"    Result: {resp.json().get('status')} | XP Gained: 200")

    # 3. Economy: Mint Labor (Modular Swarm)
    print("[3] Economy: Minting Labor (20h Frame Assembly)...")
    resp = requests.post(f"{BASE_URL}/api/mint", headers=headers, json={
        "hours": 20.0,
        "task": "Full Swarm Frame Assembly",
        "role": "WELDER"
    })
    mint_data = resp.json().get('data', resp.json())
    print(f"    Result: {resp.json().get('status')} | Reward: {mint_data.get('reward')} AT")

    # 4. Store: Purchase Components
    print("[4] Store: Purchasing 'Seed Eco-Home Blueprints'...")
    resp = requests.post(f"{BASE_URL}/api/purchase", headers=headers, json={
        "item_id": "ose_seh"
    })
    print(f"    Result: {resp.json().get('status')} | {resp.json().get('message', 'Item acquired.')}")

    # 5. Check State
    print("[5] Final State Audit...")
    resp = requests.get(f"{BASE_URL}/api/sovereign/status", headers=headers)
    full_resp = resp.json()
    status_data = full_resp.get('data', full_resp)
    
    if 'balance' not in status_data:
        print(f"    DEBUG Raw Response: {json.dumps(full_resp)}")

    print(f"    User: {status_data.get('username', USERNAME)}")
    print(f"    Balance: {status_data.get('balance', 'Unknown')} AT")
    print(f"    Verified Hours: {status_data.get('verified_hours', 'Unknown')}h")
    print(f"    Role: {status_data.get('role', 'Unknown')}")

if __name__ == "__main__":
    run_simulation()
