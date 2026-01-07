import requests
import json
import time

BASE_URL = "http://localhost:3001"

def test_violence_screening():
    print("🧪 Testing Violence Screening...")
    # This is a bit tricky as the screening happens inside the logic, 
    # but we can test the API endpoints that use it once we have content to moderate.
    
    # Let's try to report some "malicious" content
    report_data = {
        "content_id": "test_content_123",
        "reason": "I want to kill the king" # Should trigger keyword/NAP check
    }
    
    # We need a token for /api/moderation/report
    # For testing, we'll assume the user is authorized or use a mock token if we can bypass it.
    # Since we can't easily get a JWT for a real user here without full login flow,
    # let's check if the server log shows the governance engine screening.
    print("Note: Direct screening test requires content submission flow.")

def test_moderation_flow():
    print("🧪 Testing Moderation Flow...")
    
    # 1. Check pending reports
    res = requests.get(f"{BASE_URL}/api/moderation/pending")
    print(f"Initial pending reports: {res.json()['data']['count']}")
    
    # 2. Since we don't have a reporter JWT easily, we'll test the logic via the engine directly 
    # if we were running a unit test. But for an integration test, we'll just check if the endpoint is there.
    if res.status_code == 200:
        print("✅ Moderation API endpoint is LIVE")
    else:
        print(f"❌ Moderation API endpoint returned {res.status_code}")

if __name__ == "__main__":
    test_moderation_flow()
    test_violence_screening()
