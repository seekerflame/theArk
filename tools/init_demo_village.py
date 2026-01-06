#!/usr/bin/env python3
"""
Quick Demo Village Setup
Creates demo users and quests directly in the ledger JSON
"""
import json
import time
import hashlib

def hash_seed(seed):
    return hashlib.sha256(seed.encode()).hexdigest()

def create_demo_data():
    """Generate demo village data"""
    print("🌍 Creating Demo Village Data...")
    print("=" * 60)
    
    demo_users = [
        ("alice_builder", "hammer nails wood construct build", ["BUILDER"], 1.5),
        ("bob_farmer", "soil seeds harvest greenhouse organic", ["FARMER"], 1.8),
        ("carol_energy", "solar panels battery grid renewable", ["ENERGY_TECH"], 2.0),
        ("dave_dev", "python javascript api code software", ["DEVELOPER"], 2.5),
        ("eve_oracle", "wisdom justice fairness validation governance", ["ORACLE"], 1.8),
        ("frank_hearth", "kitchen meals nutrition wellness hospitality", ["HEARTH_KEEPER"], 1.6),
        ("grace_chronicler", "documentation knowledge history records archive", ["CHRONICLER"], 1.4),
        ("henry_educator", "teaching learning curriculum mentorship education", ["EDUCATOR"], 1.7),
        ("iris_hardware", "electronics sensors microcontroller iot", ["HARDWARE_ENGINEER"], 2.2),
        ("jules_ai", "automation workflows machine learning ai", ["AI_STEWARD", "DEVELOPER"], 2.5),
        ("kate_federation", "networking mesh coordination logistics", ["FEDERATION_COORDINATOR"], 1.9),
        ("leo_economist", "treasury finance economics tokenomics", ["ECONOMIST"], 2.0),
        ("maria_worker", "willing helpful eager learn contribute", ["WORKER"], 1.0),
    ]
    
    blocks = []
    timestamp = int(time.time())
    
    # Create user registrations and role certifications
    credentials = []
    for username, seed, roles, multiplier in demo_users:
        # User registration
        user_block = {
            "hash": hashlib.sha256(f"{username}{timestamp}".encode()).hexdigest()[:16],
            "type": "USER_REGISTRATION",
            "timestamp": timestamp,
            "data": {
                "username": username,
                "seed_phrase_hash": hash_seed(seed),
                "registered_at": timestamp
            }
        }
        blocks.append(user_block)
        
        # Role certification
        for role in roles:
            cert_block = {
                "hash": hashlib.sha256(f"{username}{role}{timestamp}".encode()).hexdigest()[:16],
                "type": "ROLE_CERTIFICATION",
                "timestamp": timestamp + 1,
                "data": {
                    "username": username,
                    "role": role,
                    "certified_by": "system",
                    "multiplier": multiplier,
                    "certified_at": timestamp + 1
                }
            }
            blocks.append(cert_block)
        
        credentials.append({
            "username": username,
            "seed_phrase": seed,
            "roles": roles,
            "multiplier": multiplier
        })
        
        timestamp += 2
        print(f"✓ {username:20} [{', '.join(roles)}] x{multiplier}")
    
    # Create sample quests
    print("\n📋 Creating Sample Quests...")
    quests = [
        ("Build New Greenhouse Frame", "BUILDER", 40, ["construction", "greenhouse"]),
        ("Harvest Winter Vegetables", "FARMER", 15, ["agriculture", "harvest"]),
        ("Install Solar Panel Array", "ENERGY_TECH", 60, ["solar", "energy"]),
        ("Implement Lightning Bridge", "DEVELOPER", 80, ["code", "api"]),
        ("Validate Yesterday's Labor", "ORACLE", 20, ["validation", "governance"]),
        ("Prepare Community Dinner", "HEARTH_KEEPER", 12, ["meals", "wellness"]),
        ("Document Hardware Setup", "CHRONICLER", 18, ["documentation", "wiki"]),
        ("Teach Welding Basics", "EDUCATOR", 25, ["education", "training"]),
        ("Build IoT Soil Sensors", "HARDWARE_ENGINEER", 35, ["hardware", "iot"]),
        ("Automate Daily Backups", "AI_STEWARD", 30, ["automation", "n8n"]),
        ("Connect to Neighbor Village", "FEDERATION_COORDINATOR", 45, ["federation", "mesh"]),
        ("Analyze Token Velocity", "ECONOMIST", 28, ["economy", "tokenomics"]),
        ("Help with Wood Splitting", "WORKER", 8, ["general", "labor"]),
    ]
    
    for title, role, base_at, tags in quests:
        quest_id = f"quest_demo_{role.lower()}_{timestamp}"
        quest_block = {
            "hash": hashlib.sha256(f"{quest_id}{timestamp}".encode()).hexdigest()[:16],
            "type": "QUEST",
            "timestamp": timestamp,
            "data": {
                "quest_id": quest_id,
                "title": title,
                "offer_type": "ROLE_MULTIPLIED",
                "base_at": base_at,
                "required_role": role,
                "tags": tags,
                "owner": "system",
                "status": "OPEN",
                "created_at": timestamp
            }
        }
        blocks.append(quest_block)
        timestamp += 1
        print(f"✓ {title:30} ({base_at} AT)")
    
    print("\n" + "=" * 60)
    print(f"✅ Generated {len(blocks)} blocks")
    print(f"👥 Created {len(credentials)} demo users")
    print(f"📋 Created {len(quests)} sample quests")
    
    # Save to JSON files
    with open('ledger/demo_village_blocks.json', 'w') as f:
        json.dump(blocks, f, indent=2)
    
    with open('demo_credentials.json', 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print("\n📝 Files created:")
    print("   • ledger/demo_village_blocks.json (import to ledger)")
    print("   • demo_credentials.json (login information)")
    
    print("\n🚀 To activate:")
    print("   1. Merge demo blocks into your ledger")
    print("   2. Restart The Ark")
    print("   3. Login as any demo user")
    print("\n💡 Try logging in as:")
    print(f"   Username: {credentials[0]['username']}")
    print(f"   Seed: {credentials[0]['seed_phrase']}")
    print("=" * 60)

if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
