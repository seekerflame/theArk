
import requests
import os

BASE_URL = "http://localhost:3006"

def get_token():
    # Login as Lead_Architect
    r = requests.post(f"{BASE_URL}/api/login", json={
        "username": os.environ.get("ARK_ADMIN_USER", "Lead_Architect"),
        "password": os.environ.get("ARK_ADMIN_PASS", "queen_password")
    })
    return r.json()['data']['token']

def test_trade_flow():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Propose Trade
    trade_request = {
        "target_node": "node_002",
        "offer": {"type": "AT", "amount": 50},
        "request": {"type": "RESOURCE", "item": "Seed Potatoes"}
    }
    
    print("💎 Proposing Trade: AT for Seed Potatoes...")
    r = requests.post(f"{BASE_URL}/api/trade/propose", json=trade_request, headers=headers)
    assert r.status_code == 200
    trade_id = r.json()['data']['trade']['id']
    print(f"✅ Trade Proposed. ID: {trade_id}")
    
    # 2. Accept Trade
    print(f"🤝 Accepting Trade {trade_id}...")
    r = requests.post(f"{BASE_URL}/api/trade/accept", json={"trade_id": trade_id}, headers=headers)
    assert r.status_code == 200
    print("✅ Trade Accepted successfully.")

if __name__ == "__main__":
    test_trade_flow()
