"""
First Customer Quest: Rudy's Hot Dog Stand
FIXED: Scalable economics - AT only minted for LABOR

Economic Rules:
1. AT is ONLY minted when LABOR is performed and VERIFIED
2. "Promotional" quests are funded by the POSTER (not minted)
3. Purchases TRANSFER AT (customer → merchant), no minting
"""

# === LABOR QUESTS (AT IS MINTED - Scalable) ===

RUDY_LABOR_QUESTS = [
    {
        "id": "rudy_setup_001",
        "title": "Help Rudy Set Up His Stand",
        "description": "Arrive at 7am, help Rudy unload equipment and set up his hot dog stand. Takes about 30 minutes.",
        "reward": 1.5,  # AT minted for real labor
        "funding_source": "SYSTEM_MINT",  # Labor-backed, system mints
        "category": "labor",get
        "verification": {
            "type": "triple_verification",
            "witnesses_required": 1,  # Rudy + 1 bystander
            "method": "Rudy confirms work completed"
        },
        "estimated_time_minutes": 30,
        "scalable": True,
        "replicable": True,
        "why_it_works": "Real labor performed. AT is backed by 30 min of work."
    },
    {
        "id": "rudy_photos_001",
        "title": "Take Menu Photos for Rudy",
        "description": "Photograph Rudy's hot dogs for his new digital menu. 5-10 good shots.",
        "reward": 2.0,  # AT minted for real labor
        "funding_source": "SYSTEM_MINT",
        "category": "labor",
        "verification": {
            "type": "triple_verification",
            "witnesses_required": 1,
            "method": "Rudy approves photos"
        },
        "estimated_time_minutes": 45,
        "scalable": True,
        "replicable": True,
        "why_it_works": "Real skilled labor. Photos have market value (~$50-100). AT is backed."
    },
    {
        "id": "rudy_flyering_001",
        "title": "Distribute Rudy's Flyers",
        "description": "Hand out 50 flyers for Rudy's stand in downtown area.",
        "reward": 1.0,
        "funding_source": "SYSTEM_MINT",
        "category": "labor",
        "verification": {
            "type": "gps_verified",
            "method": "GPS confirms you walked the route"
        },
        "estimated_time_minutes": 30,
        "scalable": True,
        "replicable": True,
        "why_it_works": "Real labor. Measurable. Rudy would pay for this."
    }
]

# === PROMOTIONAL QUESTS (Funded by Poster - Scalable) ===

RUDY_PROMO_QUEST = {
    "id": "rudy_visit_001",
    "title": "Visit Rudy's Stand",
    "description": "Visit Rudy's hot dog stand and say 'I'm from the Ark!' Get a stamp for your first visit.",
    "reward": 0.25,  # Small reward
    "funding_source": "POSTER_WALLET",  # Rudy (or you) funds this from existing AT
    "funder_wallet_id": "rudy_merchant_001",  # Debited from Rudy's wallet
    "category": "promotional",
    "verification": {
        "type": "merchant_stamp",
        "method": "Rudy scans your QR code"
    },
    "scalable": True,
    "replicable": True,
    "why_it_works": "Rudy PAYS 0.25 AT per customer. It's his marketing budget. He earns it back when they buy."
}

# === PURCHASE TRANSACTIONS (Transfer, No Minting) ===

PURCHASE_FLOW = """
Customer has 5 AT in wallet
Customer buys hot dog for 3 AT
→ Customer wallet: 5 - 3 = 2 AT
→ Rudy wallet: 0 + 3 = 3 AT
→ NO NEW AT MINTED
→ This scales infinitely because it's just transfers
"""

# === THRIFT WALK (Scalable Version) ===

THRIFT_WALK_QUEST = {
    "id": "thrift_walk_helper_001", 
    "title": "Thrift Walk Setup Crew",
    "description": "Help 3 vendors set up their tables at Thrift Walk. Takes about 1 hour total.",
    "reward": 3.0,  # AT minted for real labor
    "funding_source": "SYSTEM_MINT",
    "category": "labor",
    "quest_type": "party",
    "max_participants": 4,
    "bonus_multiplier": 1.2,  # Teamwork bonus
    "verification": {
        "type": "multi_stamp",
        "required_stamps": 3,
        "method": "Each vendor stamps you after setup"
    },
    "scalable": True,
    "replicable": True,
    "why_it_works": "3 vendors get free setup help. 3 people get paid in AT. Real labor, real value."
}

# === SCALABILITY PROOF ===

ECONOMIC_RULES = """
SCALABILITY FORMULA:

1. LABOR → MINT
   - Every human has time
   - Infinite supply of labor
   - AT supply grows WITH productive capacity
   - No central treasury needed

2. PROMO → TRANSFER
   - Merchants fund their own marketing
   - Self-sustaining flywheel
   - Rich merchants can spend more, poor ones less
   - No central subsidy

3. PURCHASE → TRANSFER
   - Pure peer-to-peer
   - No fees, no middlemen
   - Infinite scalability

WHAT DOESN'T SCALE:
- "Free money" quests (who pays?)
- Central treasury subsidies (runs out)
- Ponzi referral bonuses (collapses)

WHAT SCALES:
- Labor-for-AT (infinite human time)
- Merchant-funded promos (self-sustaining)
- Peer-to-peer transfers (no bottleneck)
"""

if __name__ == "__main__":
    import json
    print("=== LABOR QUESTS (Scalable) ===")
    for q in RUDY_LABOR_QUESTS:
        print(f"- {q['title']}: {q['reward']} AT ({q['funding_source']})")
    print("\n=== PROMO QUEST (Funded by Poster) ===")
    print(f"- {RUDY_PROMO_QUEST['title']}: {RUDY_PROMO_QUEST['reward']} AT (funded by merchant)")
    print("\n=== ECONOMIC RULES ===")
    print(ECONOMIC_RULES)
