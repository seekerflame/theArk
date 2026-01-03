import threading
import urllib.request
import urllib.error
import json
import time
import random

BASE_URL = "http://localhost:3000"
NUM_USERS = 20
OPS_PER_USER = 10

def api_call(endpoint, data=None, token=None, method='POST'):
    try:
        url = f"{BASE_URL}{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        body = None
        if data:
            body = json.dumps(data).encode('utf-8')
        
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read().decode())
    except Exception as e:
        # print(f"Error {endpoint}: {e}")
        return None

def user_behavior(user_id):
    username = f"stress_user_{user_id}_{int(time.time())}"
    password = "password"
    
    # 1. Register
    reg = api_call("/api/register", {"username": username, "password": password})
    if not reg or 'token' not in reg:
        print(f"[{username}] Failed to register (Server might be overloaded)")
        return
    token = reg['token']
    
    # 2. Ops
    for i in range(OPS_PER_USER):
        op = random.choice(['transfer', 'party', 'store_check', 'mining'])
        
        if op == 'transfer':
            target = f"user_{random.randint(0, 100)}"
            api_call("/api/transfer", {
                "sender": username,
                "receiver": target,
                "amount": random.randint(1, 5)
            }, token)
            
        elif op == 'party':
            api_call("/api/party/join", {"quest_id": f"quest_{random.randint(1,3)}"}, token)
            
        elif op == 'store_check':
             api_call("/api/store", method='GET', token=token)

        elif op == 'mining':
             # Simulate small mining effort
             api_call("/api/mint", {
                 "minter": username,
                 "task": "Stress Test Mining",
                 "hours": 0.1,
                 "category": "LABOR"
             }, token)
        
        time.sleep(random.uniform(0.05, 0.2)) # Fast fire
    
    # print(f"[{username}] Finished.")

def run_stress_test():
    print(f"🚀 Starting Stress Test: {NUM_USERS} users, {OPS_PER_USER} ops each...")
    threads = []
    start_time = time.time()
    
    for i in range(NUM_USERS):
        t = threading.Thread(target=user_behavior, args=(i,))
        threads.append(t)
        t.start()
        time.sleep(0.05) # Slight stagger to allow connections
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    print(f"✅ Stress Test Completed in {duration:.2f} seconds.")
    
    # Check Server Health
    print("Checking Server Health...")
    health = api_call("/api/store", method='GET')
    if health:
        print("✅ Server remains responsive.")
    else:
        print("❌ Server unresponsive after stress test.")

if __name__ == "__main__":
    run_stress_test()
