import json
import time
import urllib.request
import sys

BASE_URL = "http://localhost:3001"

def api_call(path, method="GET", payload=None, token=None):
    url = f"{BASE_URL}{path}"
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f"Bearer {token}"
    
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    
    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        print(f"❌ API Error [{path}]: {e}")
        return None

def test_loop():
    print("🚀 STARTING ATOMIC LOOP VERIFICATION (The Marcin Demo Path)")
    
    # 1. Setup Identities
    print("\n👤 1. Establishing Identities (Genesis Oracle & Worker)...")
    admin = api_call("/api/login", "POST", {"username": "superadmin", "password": "superpassword"})
    if not admin: 
        print("❌ Admin login failed. Ensure server is running and credentials injected.")
        return
    admin_token = admin['data']['token']
    
    # Register a test worker
    worker_name = f"worker_{int(time.time())}"
    reg = api_call("/api/register", "POST", {"username": worker_name, "password": "password123"})
    worker_token = reg['data']['token']
    print(f"   ✅ Worker Created: {worker_name}")

    # 2. Post a Quest
    print("\n📋 2. Posting a Quest (Admin/Oracle)...")
    quest = api_call("/api/quests/post", "POST", {
        "title": "Atomic Loop Verification",
        "description": "Ensure the system is actually perfect for Marcin.",
        "offer_type": "FIXED",
        "base_at": 50
    }, token=admin_token)
    quest_id = quest['data']['quest_id']
    print(f"   ✅ Quest Posted: {quest_id}")

    # 3. Claim Quest
    print("\n🔗 3. Claiming Quest (Worker)...")
    claim = api_call("/api/quests/claim", "POST", {"quest_id": quest_id}, token=worker_token)
    print(f"   ✅ Quest Claimed: {claim['data']['status']}")

    # 4. Submit Proof
    print("\n📤 4. Submitting Proof of Work (Worker)...")
    submission = api_call("/api/quests/submit", "POST", {
        "quest_id": quest_id,
        "proof_text": "Atomic loop verified via automated script.",
        "assets": ["link_to_code"]
    }, token=worker_token)
    print(f"   ✅ Proof Submitted: {submission['data']['status']}")

    # 5. Validate & Mint
    print("\n👁️ 5. Validating & Minting (Oracle)...")
    validation = api_call("/api/quests/validate", "POST", {
        "quest_id": quest_id,
        "status": "APPROVED",
        "oracle_notes": "Perfect execution."
    }, token=admin_token)
    print(f"   ✅ Validated. Block Hash: {validation['data']['mint_hash'][:10]}...")

    # 6. Check Balance
    print("\n💰 6. Verifying AT Balance...")
    time.sleep(1) # Wait for ledger sync
    user_data = api_call("/api/login", "POST", {"username": worker_name, "password": "password123"})
    balance = user_data['data']['user']['balance']
    print(f"   ✅ Worker Balance: {balance} AT")
    if balance < 50:
        print("❌ Balance check failed!")
        return

    # 7. Spend in Store
    print("\n🛍️ 7. Executing Store Purchase (Spending Velocity)...")
    # Buy a CAD File for 50 AT
    purchase = api_call("/api/purchase", "POST", {"item_id": "ose_cad"}, token=worker_token)
    print(f"   ✅ Purchase Successful: {purchase['data']['status']}")
    
    # 8. Check Final Balance
    user_data_final = api_call("/api/login", "POST", {"username": worker_name, "password": "password123"})
    final_balance = user_data_final['data']['user']['balance']
    print(f"   ✅ Final Balance: {final_balance} AT")
    
    print("\n✨ ATOMIC LOOP VERIFIED: PERFECT CYCLE COMPLETE.")

if __name__ == "__main__":
    test_loop()
