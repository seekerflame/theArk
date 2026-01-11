import requests
import json
import time
import os

BASE_URL = "http://localhost:3000"

def test_thrival():
    print("🩺 STARTING THRIVAL ECONOMY VERIFICATION...")
    
    # 1. Login as Superadmin
    r = requests.post(f"{BASE_URL}/api/login", json={"username": "superadmin", "password": "superpassword"})
    
    if r.status_code != 200:
        print(f"❌ Login failed: {r.text}")
        return
        
    token = r.json().get('data', {}).get('token')
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login Successful.")
    
    # 2. Test Infrastructure Dividend (Node Host)
    print("\n[1/3] Testing Infrastructure Dividends...")
    # Add NODE_HOST role to superadmin for test
    requests.get(f"{BASE_URL}/api/roles/certify", params={"user_id": "superadmin", "role": "NODE_HOST"}, headers=headers)
    
    # Check version and blocks
    r = requests.get(f"{BASE_URL}/api/state")
    data = r.json().get('data', {})
    print(f"    Server Version: {data.get('version')}")
    print(f"    Total Blocks: {data.get('blocks')}")
    
    # 3. Test Production Bonus (Harvest)
    print("\n[2/3] Testing Production Bonuses...")
    # List a strawberry harvest
    list_data = {
        "title": "Verified Strawberries",
        "category": "fruits",
        "quantity": "1 basket",
        "price_at": 1.0,
        "grown_by": "pilot_user_001"
    }
    r = requests.post(f"{BASE_URL}/api/harvest/list", json=list_data, headers=headers)
    if r.status_code == 200:
        # Corrected: listing_id is inside 'data'
        listing_id = r.json().get('data', {}).get('listing_id')
        print(f"    Harvest Listing Created: {listing_id}")
    else:
        print(f"    Harvest Listing Failed: {r.text}")
    
    # 4. Test Mission Escrow Minting
    print("\n[3/3] Testing Mission Escrow Minting...")
    escrow_data = {
        "title": "Clean Community Well",
        "amount": 50.0,
        "target_role": "WORKER"
    }
    r = requests.post(f"{BASE_URL}/api/economy/mission/escrow", json=escrow_data, headers=headers)
    if r.status_code == 200:
        print(f"    Response: {r.json().get('data', {}).get('status')} - TX: {r.json().get('data', {}).get('tx')}")
        print("✅ MISSION_ESCROW block successfully minted.")
    else:
        print(f"    Response Status: {r.status_code}")
        print(f"    Response Body: {r.text}")
        print("❌ MISSION_ESCROW minting failed.")

    print("\n✨ THRIVAL VERIFICATION COMPLETE.")

if __name__ == "__main__":
    test_thrival()
