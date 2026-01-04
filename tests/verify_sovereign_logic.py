import sys
import os
import time

# Add core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ledger import VillageLedger
from core.identity import IdentityManager
from core.justice import JusticeSteward

def test_sovereign_flow():
    print("--- 🛠️ TESTING SOVEREIGN LOGIC ---")
    
    # 1. Setup
    ledger_file = "tests/test_ledger_sovereign_v3.db"
    users_file = "tests/test_users_sovereign.json"
    
    if os.path.exists(ledger_file): os.remove(ledger_file)
    if os.path.exists(users_file): os.remove(users_file)

    ledger = VillageLedger(ledger_file)
    identity = IdentityManager(users_file, jwt_secret="test_secret")
    justice = JusticeSteward(ledger, identity)
    
    # 2. Register & Certify
    username = "test_welder"
    identity.register(username, "pass")
    identity.users[username]['roles'] = ["WORKER"] # Default
    
    print(f"User {username} registered. Roles: {identity.users[username]['roles']}")
    
    # Certify as WELDER (1.5x)
    identity.users[username]['roles'].append("WELDER")
    identity.save()
    print(f"User {username} certified as WELDER. Roles: {identity.users[username]['roles']}")
    
    # 3. Mint Labor (Simulate API logic)
    hours = 10
    multiplier = 1.5 # Welder
    reward = hours * 10 * multiplier
    
    # Use VillageLedger.add_block
    block_hash = ledger.add_block("LABOR", {
        "worker": username,
        "hours": hours,
        "at_reward": reward,
        "multiplier": multiplier,
        "role": "WELDER"
    })
    print(f"Minted {reward} AT for {hours}h labor. Block: {block_hash}")
    
    assert reward == 150.0
    
    # 4. Justice - Flag as Dispute
    success, msg = justice.dispute_block(block_hash, "oracle_admin", "Suspiciously high reward")
    print(f"Dispute status: {success} - {msg}")
    
    # Find dispute block to get its hash
    dispute_block = ledger.blocks[-1]
    dispute_hash = dispute_block['hash']
    
    # 5. Resolve - Resolve as MISTAKE
    success, msg = justice.resolve_dispute(dispute_hash, "MISTAKE", "oracle_admin", "Incorrect multiplier applied")
    print(f"Resolution status: {success} - {msg}")
    
    # 6. Verify Grade
    grade_str = justice.get_safety_grade(username)
    grade_val = identity.users[username].get('safety_grade', 100.0)
    print(f"Final Safety Grade for {username}: {grade_str} ({grade_val})")
    
    assert grade_val == 95.0 # 100 - 5 (Mistake)
    
    print("--- ✅ SOVEREIGN LOGIC VERIFIED ---")
    
    # Cleanup
    if os.path.exists(ledger_file): os.remove(ledger_file)
    if os.path.exists(users_file): os.remove(users_file)

if __name__ == "__main__":
    test_sovereign_flow()
