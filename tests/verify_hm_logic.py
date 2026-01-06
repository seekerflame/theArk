import sys
import os
import json
import time

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd()))

from core.ledger import VillageLedger
from core.identity import IdentityManager

def test_hm_boosts():
    db_file = "test_hm.db"
    users_file = "test_hm_users.json"
    
    if os.path.exists(db_file): os.remove(db_file)
    if os.path.exists(users_file): os.remove(users_file)
    
    ledger = VillageLedger(db_file)
    identity = IdentityManager(users_file, "secret")
    
    # 1. Register User
    identity.register("oscar", "password")
    user = identity.users["oscar"]
    
    # Base HM should be 1.0 (1.0 Role * 1.0 Tier * 1.0 Safety)
    hm_base = identity.get_holistic_multiplier("oscar", "WORKER", ledger)
    print(f"Base HM: {hm_base}")
    assert hm_base == 1.0
    
    # 2. Add dynamic ROLE_DEFINITION
    ledger.add_block('ROLE_DEFINITION', {"role": "WELDER", "multiplier": 2.5})
    hm_welder = identity.get_holistic_multiplier("oscar", "WELDER", ledger)
    print(f"Welder HM: {hm_welder}")
    assert hm_welder == 2.5
    
    # 3. Add Tier Boost (Journeyman > 100 hours)
    identity.add_verified_hours("oscar", 150)
    hm_journeyman = identity.get_holistic_multiplier("oscar", "WELDER", ledger)
    print(f"Journeyman Welder HM: {hm_journeyman}")
    # 2.5 Role * 1.2 Tier = 3.0
    assert hm_journeyman == 3.0
    
    # 4. Apply Safety Penalty
    user['safety_grade'] = 50.0
    hm_flagged = identity.get_holistic_multiplier("oscar", "WELDER", ledger)
    print(f"Flagged Journeyman Welder HM: {hm_flagged}")
    # 2.5 Role * 1.2 Tier * 0.5 Safety = 1.5
    assert hm_flagged == 1.5
    
    print("\n✅ Holistic Multiplier Logic Verified!")
    
    # Cleanup
    os.remove(db_file)
    os.remove(users_file)

if __name__ == "__main__":
    test_hm_boosts()
