"""
Merchant Profiles: Launch Network
YOU + Rudy = first 2-merchant closed loop
"""

YOUR_DETAILING = {
    "merchant_id": "detail_001",
    "name": "Eternal Detailing",  # Replace with your biz name
    "owner": "eternalflame",  # Your wallet ID
    "category": "auto_services",
    "description": "Professional car detailing. Interior, exterior, full service. Pay in AT or cash.",
    "services": [
        {
            "name": "Basic Interior Clean",
            "price_at": 5.0,
            "price_usd": 50,  # For reference
            "duration_minutes": 60,
            "description": "Vacuum, wipe down, air freshener"
        },
        {
            "name": "Full Detail",
            "price_at": 15.0,
            "price_usd": 150,
            "duration_minutes": 180,
            "description": "Interior + exterior, wax, polish, tire shine"
        },
        {
            "name": "Quick Wash",
            "price_at": 2.0,
            "price_usd": 20,
            "duration_minutes": 30,
            "description": "Exterior wash, dry"
        }
    ],
    "location": {
        "address": "Bakersfield, CA",  # Update with real location
        "mobile": True,  # You come to them
        "service_radius_miles": 10
    },
    "accepts_at": True,
    "accepts_usd": True,
    "qr_code": "detail_001_qr.png",
    "story": "First merchant on Ark OS. Proving you don't need banks to run a business.",
    "first_friday_offer": "Scan QR, book a detail, pay in AT. First 5 customers get 10% bonus AT back."
}

RUDY_HOT_DOGS = {
    "merchant_id": "rudy_hotdogs_001",
    "name": "Rudy's Hot Dogs",
    "owner": "rudy",
    "category": "food",
    "description": "Best hot dogs in Bakersfield. Cash, card, or AT accepted.",
    "services": [
        {
            "name": "Classic Hot Dog",
            "price_at": 0.3,
            "price_usd": 3,
            "description": "All beef, grilled"
        },
        {
            "name": "Deluxe Dog",
            "price_at": 0.5,
            "price_usd": 5,
            "description": "Bacon-wrapped, loaded toppings"
        },
        {
            "name": "Combo (Dog + Drink)",
            "price_at": 0.7,
            "price_usd": 7,
            "description": "Hot dog + soda"
        }
    ],
    "location": {
        "address": "Downtown Bakersfield, CA",
        "mobile": False,
        "coordinates": None  # Add GPS later
    },
    "accepts_at": True,
    "accepts_usd": True,
    "qr_code": "rudy_qr.png",
    "story": "Rudy got burned by Square during the SSN breach. He's the first vendor to say 'no more banks.' Now he accepts AT.",
    "first_friday_offer": "Visit Rudy's stand, show this app, get a stamp. Collect 3 stamps = 1 free hot dog."
}

DAGNYS_PLACEHOLDER = {
    "merchant_id": "dagnys_001",
    "name": "Dagny's Coffee",
    "owner": "TBD",
    "category": "food",
    "description": "Local coffee shop. Accepting AT starting Week 2.",
    "services": [
        {
            "name": "Coffee",
            "price_at": 0.3,
            "price_usd": 3
        }
    ],
    "location": {
        "address": "Bakersfield, CA"
    },
    "accepts_at": False,  # Not yet
    "status": "pending_onboarding"
}

# For API integration
MERCHANTS = [YOUR_DETAILING, RUDY_HOT_DOGS]

if __name__ == "__main__":
    import json
    print("=== LAUNCH NETWORK ===\n")
    for m in MERCHANTS:
        print(f"{m['name']} ({m['category']})")
        print(f"  Services: {len(m['services'])}")
        print(f"  Accepts AT: {m['accepts_at']}")
        print(f"  Story: {m['story']}\n")
