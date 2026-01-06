"""
Seed Irresistible Offer - Strategic concepts for Evolution Engine
"What is the irresistible offer to the WORLD?"
"""

import requests
import time

API_URL = "http://localhost:3000/api/evolution/propose"

CONCEPTS = [
    {
        "title": "Zero-Fee Payment Network",
        "description": "AT transactions have 0% processing fees vs 2.9% for credit cards. This alone saves merchants $3,000/year on $100k revenue. The irresistible offer: 'Keep what you earn.'",
        "type": "economic",
        "impact": 10,
        "logic_proof": "Visa/MC fees are pure extraction. Time banks have no transaction costs. AT inherits this property. Merchants will switch when USD conversion is seamless.",
        "estimated_labor": 80
    },
    {
        "title": "Direct-to-Producer Supply Chain",
        "description": "Connect shopkeepers directly to local farmers/makers via Harvest Marketplace. Cut out Sysco, Amazon, and distributors. 'Buy from your neighbor, not a warehouse.'",
        "type": "economic",
        "impact": 9,
        "logic_proof": "Sysco markup is 20-40%. Direct connection = lower prices for buyer, higher prices for seller. Both win. Middlemen evaporate.",
        "estimated_labor": 120
    },
    {
        "title": "The Hub Effect (First Mover Advantage)",
        "description": "First merchant in an area becomes the 'hub' where AT circulates. They get network effect benefits: more customers, referral bonuses, community prestige.",
        "type": "social",
        "impact": 8,
        "logic_proof": "Early adopters in network effects win disproportionately. FOMO for merchants: 'Your competitor is already on this.'",
        "estimated_labor": 40
    },
    {
        "title": "Anti-Yelp: Proof-of-Visit Reviews",
        "description": "Reviews can only be left by users who completed a quest at the location. No fake reviews, no extortion. 'Real reviews from real visitors.'",
        "type": "social",
        "impact": 7,
        "logic_proof": "Yelp is extortion. Google reviews are gamed. Proof-of-visit via quest completion = verified authenticity.",
        "estimated_labor": 60
    },
    {
        "title": "The Landlord Play (Long-Term)",
        "description": "If AT becomes the dominant local currency, landlords will have to accept it for rent. This breaks the biggest extraction point in capitalism.",
        "type": "economic",
        "impact": 10,
        "logic_proof": "Rent is the ultimate extraction. If tenants can only pay in AT, landlords must accept AT. Requires critical mass. 5-year goal.",
        "estimated_labor": 500
    }
]

def seed_concepts():
    print("🌟 Seeding Irresistible Offer Concepts...")
    
    for concept in CONCEPTS:
        try:
            payload = {
                "source": "irresistible_offer_brainstorm",
                **concept
            }
            response = requests.post(API_URL, json=payload, timeout=5)
            
            if response.status_code == 200:
                print(f"✅ Seeded: {concept['title']}")
            else:
                print(f"❌ Failed: {concept['title']}: {response.text}")
                
            time.sleep(0.5)
            
        except Exception as e:
            print(f"⚠️ Error seeding {concept['title']}: {e}")

if __name__ == "__main__":
    seed_concepts()
