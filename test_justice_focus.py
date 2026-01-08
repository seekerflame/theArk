import requests
import time

BASE_URL = "http://localhost:8000"

# Mock login (requires server to be running with dev secret)
def test_justice_flow():
    print("Testing Justice Flow...")
    # 1. Check Transparency Log
    r = requests.get(f"{BASE_URL}/api/moderation/log")
    print(f"Initial Logs: {r.status_code}")
    
    # 2. Check Moderation Queue
    # Note: Auth required, so we might need to skip full E2E in this script 
    # and just check if endpoints exist and return 401/403 (basic health check)
    r = requests.get(f"{BASE_URL}/api/moderation/queue")
    print(f"Mod Queue (no auth): {r.status_code}")

def test_focus_economy():
    print("\nTesting Focus Economy...")
    r = requests.post(f"{BASE_URL}/api/economy/focus/start")
    print(f"Focus Start (no auth): {r.status_code}")

if __name__ == "__main__":
    try:
        test_justice_flow()
        test_focus_economy()
    except Exception as e:
        print(f"Error connecting to server: {e}")
