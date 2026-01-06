#!/usr/bin/env python3
"""
🎮 Ark Demo Walkthrough
========================
Interactive demo showing key system features.
Run this to see The Ark in action!

Usage:
    python3 tools/demo_walkthrough.py         # Interactive mode
    python3 tools/demo_walkthrough.py --auto  # Auto-run (no prompts)
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:3000"
AUTO_MODE = "--auto" in sys.argv

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🌌 {title}")
    print(f"{'='*60}\n")

def print_step(num, description):
    print(f"\n[{num}] {description}")
    print("-" * 40)

def pause():
    if AUTO_MODE:
        time.sleep(0.5)
    else:
        input("\n⏸️  Press Enter to continue...")

def main():
    print_header("THE ARK - DEMO WALKTHROUGH")
    print("This demo will show you the key features of the Civilization OS.")
    print("Make sure the server is running: python3 server.py")
    pause()

    # Step 1: Health Check
    print_step(1, "System Health Check")
    try:
        r = requests.get(f"{BASE_URL}/api/health", timeout=5)
        data = r.json()
        print(f"✅ Status: {data['data']['status']}")
        print(f"📡 Agent: {data['data']['agent']}")
    except Exception as e:
        print(f"❌ Server not responding. Start with: python3 server.py")
        sys.exit(1)
    pause()

    # Step 2: Village State
    print_step(2, "Village State")
    r = requests.get(f"{BASE_URL}/api/state")
    data = r.json()['data']
    print(f"👥 Total Users: {data.get('total_users', 'N/A')}")
    print(f"📦 Ledger Blocks: {data.get('total_blocks', 'N/A')}")
    print(f"💰 Verified Mints: {data.get('verified_mints', 'N/A')}")
    print(f"📜 Total Transactions: {data.get('total_transactions', 'N/A')}")
    pause()

    # Step 3: Kardashev Energy
    print_step(3, "Kardashev Energy Level")
    r = requests.get(f"{BASE_URL}/api/system/energy")
    data = r.json()['data']
    print(f"⚡ Kardashev Level: Type {data.get('kardashev_level', 0.73)}")
    print(f"🔋 Power Output: {data.get('power_watts', 'N/A')} watts")
    print(f"📊 Sources: {json.dumps(data.get('sources', {}), indent=2)}")
    pause()

    # Step 4: Active Quests
    print_step(4, "Quest Board (Sample)")
    try:
        r = requests.get(f"{BASE_URL}/api/quests")
        resp = r.json()
        # Handle different response formats
        if isinstance(resp, list):
            quests = resp[:3]
        elif isinstance(resp, dict):
            quests = resp.get('data', resp.get('quests', []))[:3]
        else:
            quests = []
        if quests:
            for q in quests:
                title = q.get('title', q.get('name', 'Untitled'))
                reward = q.get('reward_at', q.get('reward', '?'))
                print(f"  🎯 {title} - {reward} AT")
        else:
            print("  (No active quests - try: python3 tools/seed_bored_board.py)")
    except Exception as e:
        print(f"  ⚠️ Could not fetch quests: {e}")
    pause()

    # Step 5: Federation Status
    print_step(5, "Federation (Mesh Network)")
    r = requests.get(f"{BASE_URL}/api/federation/nodes")
    nodes = r.json().get('data', {}).get('nodes', [])
    print(f"🌐 Connected Nodes: {len(nodes)}")
    for node in nodes[:3]:
        print(f"  🔗 {node.get('node_id', 'unknown')} @ {node.get('endpoint', 'N/A')}")
    pause()

    # Step 6: Evolution API (AI System)
    print_step(6, "Evolution API (AI Context)")
    r = requests.get(f"{BASE_URL}/api/evolution")
    data = r.json().get('data', {})
    print(f"🧠 System Health: {data.get('system_health', 'N/A')}")
    print(f"📈 Active Missions: {len(data.get('active_missions', []))}")
    print(f"🔍 Recent Errors: {len(data.get('recent_errors', []))}")
    pause()

    # Summary
    print_header("DEMO COMPLETE!")
    print("You've seen the core systems:")
    print("  ✅ Health monitoring")
    print("  ✅ Village state tracking")
    print("  ✅ Kardashev energy levels")
    print("  ✅ Quest board")
    print("  ✅ Federation mesh")
    print("  ✅ AI evolution context")
    print("\n🔗 Next steps:")
    print("  1. Open http://localhost:3000 in your browser")
    print("  2. Register an account (Auth tab)")
    print("  3. Try minting some AT (Economy tab)")
    print("  4. Read docs/DEVELOPER_OVERVIEW.md for technical details")
    print("\n🌌 Welcome to the Civilization OS!")

if __name__ == "__main__":
    main()
