
import requests
import json
import os
import sys
import subprocess
import time

BASE_URL = os.environ.get('ARK_API_URL', 'http://localhost:3006')
USERNAME = "antigravity_ai"
PASSWORD = "sovereign_intelligence_password_123"

def register_and_login():
    print(f"🤖 Bootstrapping AI Agent on {BASE_URL}...")
    
    # 1. Try Login
    token = None
    try:
        r = requests.post(f"{BASE_URL}/api/login", json={"username": USERNAME, "password": PASSWORD})
        if r.status_code == 200:
            data = r.json()
            # Handle potential data wrapper
            if 'data' in data:
                token = data['data'].get('token')
            else:
                token = data.get('token')
            print("✅ AI Agent Logged In.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return None

    # 2. Register if login failed
    if not token:
        print("🆕 Registering AI Agent...")
        try:
            r = requests.post(f"{BASE_URL}/api/register", json={"username": USERNAME, "password": PASSWORD})
            if r.status_code == 200:
                print("✅ AI Agent Registered.")
                return register_and_login() # Recurse once
            elif r.status_code == 400 and "exists" in r.text:
                # Should have logged in then?
                print("⚠️ User exists but login failed?")
            else:
                print(f"❌ Registration Failed: {r.text}")
                return None
        except Exception as e:
            print(f"❌ Registration Error: {e}")
            return None
            
    return token

def start_orchestrator(token):
    print("🚀 Launching AI Orchestrator...")
    
    env = os.environ.copy()
    env['ARK_API_URL'] = BASE_URL
    env['AI_AGENT_TOKEN'] = token
    
    # Run in background or foreground? For this script, run once to verify.
    cmd = [sys.executable, "ai_orchestrator.py"]
    
    p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Stream output for a bit
    start = time.time()
    while time.time() - start < 10:
        line = p.stdout.readline()
        if line:
            print(f"[ORCHESTRATOR] {line.strip()}")
        if p.poll() is not None:
            break
            
    print("✨ Orchestrator Bootstrap Complete.")

if __name__ == "__main__":
    token = register_and_login()
    if token:
        start_orchestrator(token)
    else:
        print("❌ Failed to bootstrap.")
