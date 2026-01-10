import requests
import json
import time

BASE_URL = "http://localhost:3006"
USER_TOKEN = "dev_token_user" # Assuming dev token works or we need to login

def login():
    username = os.environ.get("ARK_ADMIN_USER", "Lead_Architect")
    password = os.environ.get("ARK_ADMIN_PASS", "queen_password")
    
    try:
        # Try login first
        r = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})
        
        # Register if login fails
        if r.status_code != 200:
            print("    Registering user...")
            requests.post(f"{BASE_URL}/api/register", json={"username": username, "password": password})
            r = requests.post(f"{BASE_URL}/api/login", json={"username": username, "password": password})
            
        if r.status_code == 200:
            resp_json = r.json()
            # Handle potential data wrapper
            data = resp_json.get('data', resp_json)
            return data.get('token')
            
    except Exception as e:
        print(f"Login failed: {e}")
    return None

def test_governance():
    print("🚀 Starting Governance System Test...")
    
    token = login()
    if not token:
        print("❌ Login failed. Aborting.")
        return

    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Create Proposal
    print("\n1. Creating Proposal...")
    proposal_data = {
        "title": "Build a Community Greenhouse",
        "description": "allocate funds for a hydroponic setup",
        "requested_amount": 500,
        "recipient": "node_treasury"
    }
    
    r = requests.post(f"{BASE_URL}/api/steward/propose", json=proposal_data, headers=headers)
    print(f"Response: {r.status_code} - {r.text}")
    
    if r.status_code != 200:
        print("❌ Proposal creation failed")
        return

    proposal_id = r.json()['data']['id']
    print(f"✅ Proposal Created: {proposal_id}")
    
    # 2. List Proposals to verify
    print("\n2. Listing Proposals...")
    r = requests.get(f"{BASE_URL}/api/steward/proposals", headers=headers)
    proposals = r.json()['data']
    found = False
    for p in proposals:
        if p['id'] == proposal_id:
            found = True
            print(f"✅ Found proposal in list: {p['title']} (Status: {p['status']})")
            break
            
    if not found:
        print("❌ Proposal not found in list")
        return

    # 3. Vote on Proposal
    print("\n3. Voting on Proposal...")
    vote_data = {
        "id": proposal_id,
        "vote": "YES"
    }
    r = requests.post(f"{BASE_URL}/api/steward/vote", json=vote_data, headers=headers)
    print(f"Response: {r.status_code} - {r.text}")
    
    if r.status_code == 200:
        print("✅ Vote recorded successfully")
    else:
        print("❌ Voting failed")
        
    # 4. Check Status Update (might not change immediately depending on logic, but checking vote count)
    print("\n4. Verifying Vote Count...")
    r = requests.get(f"{BASE_URL}/api/steward/proposals", headers=headers)
    proposals = r.json()['data']
    for p in proposals:
        if p['id'] == proposal_id:
             # Assuming structure has votes or we check status
            print(f"Current Proposal State: {json.dumps(p, indent=2)}")
            # If logic auto-approves or just counts votes, we see it here
            
    print("\n✨ Governance Test Complete.")

if __name__ == "__main__":
    test_governance()
