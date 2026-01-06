import sys
import os
import time

# Add core to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.ledger import VillageLedger
from core.identity import IdentityManager
from core.justice import JusticeSteward

def test_integrated_human_path():
    print("--- 🛠️ TESTING INTEGRATED HUMAN PATH ---")
    
    # 1. Setup
    ledger_file = "tests/test_ledger_path.db"
    users_file = "tests/test_users_path.json"
    
    if os.path.exists(ledger_file): os.remove(ledger_file)
    if os.path.exists(users_file): os.remove(users_file)

    ledger = VillageLedger(ledger_file)
    identity = IdentityManager(users_file, jwt_secret="test_secret")
    
    username = "integrated_citizen"
    identity.register(username, "pass")
    
    # 2. Define New Role via Ledger
    # Simulated Oracle Action
    ledger.add_block('ROLE_DEFINITION', {
        "role": "MECHANIC",
        "multiplier": 1.4,
        "defined_by": "oracle_admin"
    })
    print("Minted ROLE_DEFINITION: MECHANIC (1.4x)")
    
    # 3. Certify User
    identity.users[username]['roles'].append("MECHANIC")
    identity.save()
    
    # 4. Check HM - Apprentice Stage
    hm_apprentice = identity.get_holistic_multiplier(username, "MECHANIC", ledger)
    print(f"HM for Apprentice MECHANIC: {hm_apprentice}")
    assert hm_apprentice == 1.4 # 1.4 * 1.0 * 1.0
    
    # 5. Simulate Growth (Frictionless Progression)
    print("Simulating 120 verified hours...")
    identity.add_verified_hours(username, 120.0)
    
    # 6. Check HM - Journeyman Stage
    hm_journeyman = identity.get_holistic_multiplier(username, "MECHANIC", ledger)
    print(f"HM for Journeyman MECHANIC: {hm_journeyman}")
    assert hm_journeyman == 1.68 # 1.4 * 1.2 * 1.0
    
    # 7. Check Safety Grade Penalty
    print("Simulating Justice Penalty (Safety Grade 80%)...")
    identity.users[username]['safety_grade'] = 80.0
    identity.save()
    
    hm_flagged = identity.get_holistic_multiplier(username, "MECHANIC", ledger)
    print(f"HM for Flagged Journeyman: {hm_flagged}")
    # 1.4 * 1.2 * 0.8 = 1.344 -> rounded to 1.34
    assert hm_flagged == 1.34
    
    print("--- ✅ INTEGRATED HUMAN PATH VERIFIED ---")
    
    # Cleanup
    if os.path.exists(ledger_file): os.remove(ledger_file)
    if os.path.exists(users_file): os.remove(users_file)

if __name__ == "__main__":
    test_integrated_human_path()
