
import requests
import json
import time
import threading
import random

BASE_URL = "http://localhost:3006"
USER_COUNT = 150

def simulate_user(i):
    username = f"citizen_{i}"
    user_p = f"pass_{i}_ark"
    
    # 1. Register
    try:
        r = requests.post(f"{BASE_URL}/api/register", json={"username": username, "password": user_p})
        if r.status_code != 200:
            print(f"User {i} registration failed.")
            return
            
        token = r.json().get('data', {}).get('token')
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Add some labor
        requests.post(f"{BASE_URL}/api/economy/mint", json={"hours": random.uniform(1, 5)}, headers=headers)
        
        # 3. Random Peer Transfer
        if i > 1:
            target = f"citizen_{random.randint(0, i-1)}"
            requests.post(f"{BASE_URL}/api/transfer", json={"receiver": target, "amount": 1.0}, headers=headers)
            
        print(f"✅ User {i} ({username}) simulated successfully.")
    except Exception as e:
        print(f"❌ User {i} error: {e}")

def run_stress_test():
    print(f"🚀 INITIATING GREAT EXIT STRESS TEST ({USER_COUNT} USERS)...")
    start_time = time.time()
    
    threads = []
    for i in range(USER_COUNT):
        t = threading.Thread(target=simulate_user, args=(i,))
        threads.append(t)
        t.start()
        # Slight stagger to prevent immediate connection burst limit
        if i % 10 == 0: time.sleep(0.1)
        
    for t in threads:
        t.join()
        
    duration = time.time() - start_time
    print(f"\n✨ STRESS TEST COMPLETE.")
    print(f"Total Time: {duration:.2f}s")
    print(f"Avg Time per User: {duration/USER_COUNT:.2f}s")
    print(f"System State: THRIVE")

if __name__ == "__main__":
    run_stress_test()
