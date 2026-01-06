"""
First Customer Quest: Rudy's Hot Dog Stand
"The first AT transaction in the wild."
"""

RUDY_QUEST = {
    "id": "rudy_hotdog_001",
    "title": "Buy a Hot Dog from Rudy",
    "description": "Support local! Buy a hot dog from Rudy's stand and earn AT for supporting a local vendor. Show Rudy this screen to verify.",
    "reward": 0.5,
    "category": "local_support",
    "verification": {
        "type": "merchant_stamp",
        "method": "Rudy scans your QR code after purchase"
    },
    "merchant": {
        "name": "Rudy's Hot Dogs",
        "location": "Bakersfield, CA",
        "story": "Rudy got burned by Square when the SSN breach happened. He's the first merchant on Ark OS - proving you don't need a bank account to run a business."
    },
    "created_by": "genesis_architect",
    "tags": ["food", "local", "first_customer", "genesis"]
}

THRIFT_WALK_QUEST = {
    "id": "thrift_walk_001", 
    "title": "Thrift Walk Explorer",
    "description": "Visit 3 vendors at the Thrift Walk and collect a stamp from each. Support local makers and earn AT!",
    "reward": 1.0,
    "category": "social",
    "verification": {
        "type": "multi_stamp",
        "required_stamps": 3
    },
    "quest_type": "party",
    "max_participants": 4,
    "bonus_multiplier": 1.2,
    "tags": ["thrift", "local", "social", "exploration"]
}

# QR Code template for merchants
MERCHANT_QR_CONFIG = {
    "base_url": "https://ark.local/m/",  # or localhost for testing
    "format": "SVG",
    "error_correction": "H",
    "instructions": """
    1. Print this QR code
    2. Laminate it (weather protection)
    3. Display at your stand/table
    4. When customer completes quest, they show you their phone
    5. You scan their code to verify → They get AT, you get credit
    """
}

if __name__ == "__main__":
    import json
    print("=== RUDY'S QUEST ===")
    print(json.dumps(RUDY_QUEST, indent=2))
    print("\n=== THRIFT WALK QUEST ===")
    print(json.dumps(THRIFT_WALK_QUEST, indent=2))
