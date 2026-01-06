#!/usr/bin/env python3
"""
Comprehensive System Test Suite
Tests all role system functionality
"""
import requests
import json
import sys

BASE_URL = "http://localhost:3000"

def test_server_health():
    """Test 1: Server Health Check"""
    print("=" * 60)
    print("TEST 1: Server Health")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        if r.status_code == 200:
            data = r.json()
            print(f"✅ Server is healthy")
            print(f"   Status: {data.get('data', {}).get('status')}")
            return True
        else:
            print(f"❌ Server returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False

def test_role_api():
    """Test 2: Role API Endpoints"""
    print("\n" + "=" * 60)
    print("TEST 2: Role API")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE_URL}/api/roles", timeout=5)
        if r.status_code == 200:
            data = r.json().get('data', [])
            print(f"✅ Role API working")
            print(f"   Total Roles: {len(data)}")
            if len(data) >= 13:
                print(f"   ✅ All 13 roles present")
                # Show first 3 roles
                for role in data[:3]:
                    print(f"   - {role['role']:20} ({role['title']}) x{role['base_multiplier']}")
                return True
            else:
                print(f"   ❌ Expected 13 roles, got {len(data)}")
                return False
        else:
            print(f"❌ API returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_demo_users():
    """Test 3: Demo Users in Ledger"""
    print("\n" + "=" * 60)
    print("TEST 3: Demo Users")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE_URL}/api/state", timeout=5)
        if r.status_code == 200:
            print(f"✅ Ledger accessible")
            # Check demo credentials file
            try:
                with open('demo_credentials.json', 'r') as f:
                    creds = json.load(f)
                print(f"   Demo users configured: {len(creds)}")
                print(f"   Sample users:")
                for user in creds[:3]:
                    print(f"   - {user['username']:20} [{', '.join(user['roles'])}]")
                return True
            except:
                print(f"   ⚠️  demo_credentials.json not found")
                return False
        else:
            print(f"❌ State API returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_quest_system():
    """Test 4: Quest System"""
    print("\n" + "=" * 60)
    print("TEST 4: Quest System")
    print("=" * 60)
    try:
        r = requests.get(f"{BASE_URL}/api/quests", timeout=5)
        if r.status_code == 200:
            data = r.json().get('data', [])
            print(f"✅ Quest API working")
            print(f"   Total Quests: {len(data)}")
            
            # Count by status
            open_quests = [q for q in data if q.get('status') == 'OPEN']
            print(f"   Open Quests: {len(open_quests)}")
            
            # Show sample quests
            if open_quests:
                print(f"   Sample open quests:")
                for quest in open_quests[:3]:
                    print(f"   - {quest.get('title', 'Untitled'):40} ({quest.get('base_at', 0)} AT)")
                return True
            else:
                print(f"   ⚠️  No open quests found")
                return False
        else:
            print(f"❌ Quest API returned {r.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n🧪 COMPREHENSIVE SYSTEM TEST SUITE")
    print("=" * 60)
    
    results = {
        "Server Health": test_server_health(),
        "Role API": test_role_api(),
        "Demo Users": test_demo_users(),
        "Quest System": test_quest_system()
    }
    
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test:20} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - System is fully operational!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed - Review above for details")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)
