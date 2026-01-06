"""
Seed Bored Board - Ingests User's Raw Vision into the Evolution Engine
"We need to think about how to expand your capabilities with every single push."
"""

import requests
import time

API_URL = "http://localhost:3000/api/evolution/propose"

RAW_CONCEPTS = [
    {
        "title": "The Mirror Interface (Bored Board Kiosk)",
        "description": "Physical Raspberry Pi + Touchscreen nodes in local businesses. Serves as a 'Mirror' into the digital economy. 'Are you Bored?' button triggers Quest discovery.",
        "type": "hardware",
        "impact": 9,
        "logic_proof": "Digital-only apps fail to build local community. Physical presence in 'Third Spaces' (coffee shops) creates a bridge. Replaces 'ads' with 'quests' to drive foot traffic.",
        "estimated_labor": 100
    },
    {
        "title": "Stake-to-Post Content Defense",
        "description": "Prevent vandalism/spam on public boards by requiring AT stake to post. Bad content results in slashed stake (community moderation).",
        "type": "economic",
        "impact": 8,
        "logic_proof": "Public screens are vulnerable to griefing. Economic friction (staking) aligns incentives better than centralized moderation.",
        "estimated_labor": 40
    },
    {
        "title": "Merchant 'Free Labor' Market",
        "description": "Business value prop shift: Instead of buying ads, merchants utilize the board to post micro-tasks (clean windows, move boxes) paid in AT/Store Credit.",
        "type": "economic",
        "impact": 10,
        "logic_proof": "Solves 'Why accept AT?' - It buys them labor/service. Solves 'Merchant ROI' - tangible help immediately.",
        "estimated_labor": 50
    },
    {
        "title": "Community Voting / Governance Layer",
        "description": "Use the boards for local polling. 'We believe that humans should have access to community voting.'",
        "type": "social",
        "impact": 7,
        "logic_proof": "Decentralized governance needs an interface. Boards provide a verifiable, localized voting booth for non-critical community sentiment.",
        "estimated_labor": 60
    }
]

def seed_concepts():
    print("🌱 Seeding Bored Board Concepts into Evolution Engine...")
    
    for concept in RAW_CONCEPTS:
        try:
            payload = {
                "source": "user_archives_bored_board",
                **concept
            }
            response = requests.post(API_URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Injested: {concept['title']}")
            else:
                print(f"❌ Failed to seed {concept['title']}: {response.text}")
                
            time.sleep(0.5) # Be gentle
            
        except Exception as e:
            print(f"⚠️ Error seeding {concept['title']}: {e}")

if __name__ == "__main__":
    seed_concepts()
