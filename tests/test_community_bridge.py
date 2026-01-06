"""
Test the Community Bridge verification and quest system.
Tests:
1. Quest posting
2. Quest claiming
3. Verification request with 3 witnesses
4. Witness approvals
5. Reward distribution
"""

import requests
import time
import json

BASE_URL = "http://localhost:3000"

# Test users (assuming these exist from the demo credentials)
POSTER = {"username": "demo1", "password": "password"}
DOER = {"username": "demo2", "password": "password"}
WITNESS1 = {"username": "demo3", "password": "password"}
WITNESS2 = {"username": "demo4", "password": "password"}
WITNESS3 = {"username": "demo5", "password": "password"}

def login(username, password):
    """Login and get JWT token."""
    response = requests.post(f"{BASE_URL}/api/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        data = response.json()
        return data["data"]["token"]
    else:
        print(f"Login failed for {username}: {response.text}")
        return None

def test_quest_posting():
    """Test posting a community quest."""
    print("\n=== TEST 1: Quest Posting ===")
    
    token = login(POSTER["username"], POSTER["password"])
    if not token:
        return None
    
    quest_data = {
        "title": "Help organize the shop",
        "description": "Organize stockroom and clean display cases",
        "reward": 2.0,
        "tier": "physical",
        "duration": 120
    }
    
    response = requests.post(
        f"{BASE_URL}/api/quests/post",
        json=quest_data,
        headers={"Authorization": f"Bearer {token}"}
   )
    
    if response.status_code == 200:
        data = response.json()
        quest_id = data["data"]["quest_id"]
        print(f"✅ Quest posted successfully: {quest_id}")
        return quest_id
    else:
        print(f"❌ Quest posting failed: {response.text}")
        return None

def test_quest_claiming(quest_id):
    """Test claiming a quest."""
    print("\n=== TEST 2: Quest Claiming ===")
    
    token = login(DOER["username"], DOER["password"])
    if not token:
        return False
    
    response = requests.post(
        f"{BASE_URL}/api/quests/claim",
        json={"quest_id": quest_id},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        print(f"✅ Quest claimed successfully")
        return True
    else:
        print(f"❌ Quest claiming failed: {response.text}")
        return False

def test_verification_request(quest_id):
    """Test requesting verification with 3 witnesses."""
    print("\n=== TEST 3: Verification Request ===")
    
    token = login(DOER["username"], DOER["password"])
    if not token:
        return None
    
    verification_data = {
        "quest_id": quest_id,
        "witnesses": [
            WITNESS1["username"],
            WITNESS2["username"],
            WITNESS3["username"]
        ],
        "proof": {
            "photos": ["photo1.jpg", "photo2.jpg"],
            "notes": "Organized all shelves alphabetically, cleaned display cases",
            "timestamp": time.time()
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/verification/request",
        json=verification_data,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        verification_id = data["data"]["verification_id"]
        print(f"✅ Verification requested: {verification_id}")
        return verification_id
    else:
        print(f"❌ Verification request failed: {response.text}")
        return None

def test_witness_approvals(verification_id):
    """Test all 3 witnesses approving the work."""
    print("\n=== TEST 4: Witness Approvals ===")
    
    witnesses = [WITNESS1, WITNESS2, WITNESS3]
    
    for i, witness in enumerate(witnesses, 1):
        token = login(witness["username"], witness["password"])
        if not token:
            continue
        
        response = requests.post(
            f"{BASE_URL}/api/verification/submit",
            json={
                "verification_id": verification_id,
                "approved": True,
                "note": f"Verified by {witness['username']}, looks good!"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Witness {i}/3 approved: {witness['username']}")
            print(f"   Status: {data['data']['message']}")
        else:
            print(f"❌ Witness {i} approval failed: {response.text}")

def test_get_pending_verifications():
    """Test getting pending verifications for a witness."""
    print("\n=== TEST 5: Pending Verifications ===")
    
    token = login(WITNESS1["username"], WITNESS1["password"])
    if not token:
        return
    
    response = requests.get(
        f"{BASE_URL}/api/verification/pending",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    if response.status_code == 200:
        data = response.json()
        count = data["data"]["count"]
        print(f"✅ Retrieved pending verifications: {count} pending")
        for v in data["data"]["verifications"]:
            print(f"   - Quest: {v['quest_id']}, Doer: {v['doer']}, Expires in: {int(v['expires_in']/3600)}h")
    else:
        print(f"❌ Failed to get pending verifications: {response.text}")

def test_quest_templates():
    """Test getting quest templates."""
    print("\n=== TEST 6: Quest Templates ===")
    
    response = requests.get(f"{BASE_URL}/api/quests/templates")
    
    if response.status_code == 200:
        data = response.json()
        templates = data["data"]["templates"]
        print(f"✅ Retrieved {len(templates)} quest templates:")
        for name, template in templates.items():
            print(f"   - {template['title']} ({template['tier']}, {template['reward']} AT)")
    else:
        print(f"❌ Failed to get templates: {response.text}")

if __name__ == "__main__":
    print("🚀 Community Bridge Integration Test")
    print("="*50)
    
    # Run tests
    quest_id = test_quest_posting()
    if quest_id:
        if test_quest_claiming(quest_id):
            verification_id = test_verification_request(quest_id)
            if verification_id:
                test_witness_approvals(verification_id)
    
    test_get_pending_verifications()
    test_quest_templates()
    
    print("\n" + "="*50)
    print("✅ Test suite complete!")
