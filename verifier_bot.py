#!/usr/bin/env python3
"""
Verifier Bot: Autonomous Labor Validator
Scans the ledger for unverified blocks and signs those that meet "Abundance" safety criteria.
"""

import time
import urllib.request
import json
import os

BASE_URL = "http://localhost:3000"
CHECK_INTERVAL = 15 # Check every 15 seconds
AUTO_VERIFY_THRESHOLD_AT = 5.0 # Auto-verify tasks under 5 AT
TRUSTED_MINTERS = ["Sentinel_AI", "INFRASTRUCTURE", "System"]

def get_ledger():
    try:
        with urllib.request.urlopen(f"{BASE_URL}/api/graph") as r:
            return json.loads(r.read().decode())
    except:
        return []

def verify_block(block_hash):
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/api/verify",
            data=json.dumps({"hash": block_hash}).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode())
            if res.get('status') == 'success':
                print(f"[BOT] ✅ Auto-Verified Block: {block_hash[:8]}")
                return True
    except Exception as e:
        print(f"[BOT] ❌ Verification failed for {block_hash[:8]}: {e}")
    return False

def batch_verify():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/verify_all", method='POST')
        with urllib.request.urlopen(req) as r:
            res = json.loads(r.read().decode())
            if res.get('status') == 'success':
                print(f"[BOT] ✨ Batch Verified: {res.get('message')}")
                return True
    except Exception as e:
        print(f"[BOT] ❌ Batch verification failed: {e}")
    return False

def run_bot():
    print("🤖 Verifier Bot Active. Scanning for Abundance...")
    
    # Initial Batch Sweep
    batch_verify()
    
    while True:
        blocks = get_ledger()
        unverified = [b for b in blocks if b.get('data', {}).get('verified') is False or b.get('data', {}).get('verified') == 0]
        
        if not unverified:
            time.sleep(CHECK_INTERVAL)
            continue

        for b in unverified:
            data = b.get('data', {})
            minter = data.get('minter')
            task_desc = data.get('task', data.get('title', ''))
            
            # Use data.get('hours') or data.get('amount') safely
            try:
                hours = float(data.get('hours', 0))
                amount = float(data.get('amount', 0)) or (hours * 20)
            except:
                amount = 0

            # CRITERIA 1: Trusted System Minters
            should_verify = False
            if minter in TRUSTED_MINTERS:
                should_verify = True
            
            # CRITERIA 2: Low-Risk Automation Proofs
            elif data.get('block_type') == 'HARDWARE_PROOF' and amount < AUTO_VERIFY_THRESHOLD_AT:
                should_verify = True
                
            # CRITERIA 3: Mission Heartbeats
            elif "Heartbeat" in task_desc:
                should_verify = True

            if should_verify:
                verify_block(b['hash'])
                time.sleep(0.5) # Anti-spam delay

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    # Wait for server to be likely up
    time.sleep(3)
    run_bot()
