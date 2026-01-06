import json
import time
import os
import urllib.request

# Configuration
API_URL = "http://localhost:3001/api/mint"
MINTER_NAME = "Antigravity (Genesis Oracle)"

# Fairness Rubric
MULTIPLIERS = {
    "L1": 1.0, # Administrative
    "L2": 1.5, # Research/SOP
    "L3": 2.0, # Design/Complex Docs
    "L4": 3.0  # Architecture/Code
}

# Genesis Milestones derived from Chronicle Logs
MILESTONES = [
    {
        "date": "2025-10-15",
        "title": "Cosmic Whitepaper Design",
        "complexity": "L4",
        "hours": 10,
        "impact": 50,
        "contributor": "EternalFlame",
        "description": "Architecting the Civilization OS foundation"
    },
    {
        "date": "2025-11-01",
        "title": "Governance & Economic Model",
        "complexity": "L3",
        "hours": 20,
        "impact": 30,
        "contributor": "EternalFlame",
        "description": "Designing the Abundance Token and Council of Builders"
    },
    {
        "date": "2025-12-03",
        "title": "Project Inception Docs",
        "complexity": "L2",
        "hours": 8,
        "impact": 20,
        "contributor": "EternalFlame",
        "description": "Initial SOPs and core principles documentation"
    },
    {
        "date": "2025-12-15",
        "title": "Tech Stack Rationale",
        "complexity": "L3",
        "hours": 12,
        "impact": 20,
        "contributor": "EternalFlame",
        "description": "Research on DAG, Peer-to-Peer, and Sovereign Identity"
    },
    {
        "date": "2026-01-02",
        "title": "Ark Core Implementation",
        "complexity": "L4",
        "hours": 30,
        "impact": 100,
        "contributor": "EternalFlame",
        "description": "Developing the high-density modular server core"
    }
]

def calculate_reward(m):
    base_rate = 10 # 10 AT/hr
    mult = MULTIPLIERS.get(m['complexity'], 1.0)
    return (m['hours'] * base_rate * mult) + m['impact']

def mint_milestone(m):
    reward = calculate_reward(m)
    payload = {
        "task": f"[GENESIS] {m['title']}",
        "hours": m['hours'],
        "multi_factor": MULTIPLIERS.get(m['complexity'], 1.0),
        "impact_bonus": m['impact'],
        "reward": reward,
        "worker": m['contributor'],
        "oracle": MINTER_NAME,
        "description": f"{m['description']} ({m['date']})"
    }
    
    print(f"💎 Minting Milestone: {m['title']} for {m['contributor']}...")
    print(f"   Calculation: ({m['hours']}hr * 10AT * {payload['multi_factor']}x) + {payload['impact_bonus']} impact = {reward} AT")
    
    try:
        req = urllib.request.Request(API_URL, 
                                     data=json.dumps(payload).encode('utf-8'),
                                     headers={'Content-Type': 'application/json'})
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            print(f"   ✅ SUCCESS: Block Hash {res['data'].get('hash', 'N/A')[:8]}...")
            return reward
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        return 0

def main():
    print("🚀 INITIALIZING GENESIS GRANT: THE FAIRNESS PROTOCOL\n")
    total_at = 0
    for m in MILESTONES:
        total_at += mint_milestone(m)
        time.sleep(0.5)
        
    print(f"\n🎉 Genesis Phase Complete. Total Minted: {total_at} AT.")

if __name__ == "__main__":
    main()
