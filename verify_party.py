import urllib.request
import urllib.error
import json
import time

BASE_URL = "http://localhost:3000"

def post(endpoint, data, token=None):
    req = urllib.request.Request(
        f"{BASE_URL}{endpoint}",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    
    try:
        with urllib.request.urlopen(req) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode()}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def run_test():
    print("1. Registering Users...")
    u1 = f"party_leader_{int(time.time())}"
    u2 = f"party_member_{int(time.time())}"
    
    t1 = post("/api/register", {"username": u1, "password": "password"})['token']
    t2 = post("/api/register", {"username": u2, "password": "password"})['token']
    print(f"Registered: {u1}, {u2}")

    print("2. Setting up Quest...")
    # Just pick a quest ID e.g. 'q1' (assuming simple ID check or existing ID)
    # Server logic just logs block with quest_id, doesn't strictly validate existence in Python yet (validation is frontend-heavy).
    # But let's use a dummy ID safely.
    quest_id = "quest_verify_party"

    print("3. User 1 Joins Party...")
    res = post("/api/party/join", {"quest_id": quest_id}, t1)
    if res and res['status'] == 'success':
         print("✅ User 1 Joined Party")
    else:
         print(f"❌ User 1 Join Failed: {res}")

    print("4. User 2 Joins Party...")
    res = post("/api/party/join", {"quest_id": quest_id}, t2)
    if res and res['status'] == 'success':
         print("✅ User 2 Joined Party")
    else:
         print(f"❌ User 2 Join Failed: {res}")

    print("5. Verifying Ledger...")
    # Fetch graph, look for PARTY_JOIN blocks
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/graph") as r:
            blocks = json.loads(r.read().decode())
            
        joins = [b for b in blocks if b['data'].get('block_type') == 'PARTY_JOIN' and b['data'].get('quest_id') == quest_id]
        
        users_in_party = [b['data']['username'] for b in joins]
        
        if u1 in users_in_party and u2 in users_in_party:
             print(f"✅ Both users found in ledger party: {users_in_party}")
        else:
             print(f"❌ Missing users in party ledger: {users_in_party}")

    except Exception as e:
        print(f"Ledger Verify Error: {e}")

if __name__ == "__main__":
    run_test()
