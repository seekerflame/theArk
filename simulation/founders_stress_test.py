import sys
import os
import time
import random
import threading
import json

# Add core path
script_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(script_dir)
sys.path.append(root_dir)

try:
    from core.foundry import OSEFoundry, FoundryMachine
    from core.ledger import VillageLedger
    from core.identity import IdentityManager
    from core.roles import ROLE_DEFINITIONS
except ImportError:
    print("Error: Could not import core modules. Ensure you are running from the simulation directory.")
    sys.exit(1)

class FoundersStressTest:
    def __init__(self, num_founders=50, num_admins=5):
        self.db_file = 'simulation_ledger.db'
        if os.path.exists(self.db_file): os.remove(self.db_file)
        
        self.ledger = VillageLedger(self.db_file)
        self.identity = IdentityManager('sim_users.json', 'sim_secret')
        self.foundry = OSEFoundry(self.ledger)
        
        self.num_founders = num_founders
        self.num_admins = num_admins
        self.users = []
        
        # Setup static assets for Founders Node
        self.foundry.add_machine(FoundryMachine("HARDWARE-LAB-001", "LAB", 50.0, is_static=True))
        self.foundry.add_machine(FoundryMachine("MEDIA-STUDIO-001", "STUDIO", 30.0, is_static=True))
        self.foundry.add_machine(FoundryMachine("QUIET-ROOM-001", "SPACE", 10.0, is_static=True))

    def setup_users(self):
        print(f"Setting up {self.num_founders} Founders and {self.num_admins} Admins...")
        for i in range(self.num_founders):
            uid = f"founder_{i}"
            res, msg = self.identity.register(uid, "pass123")
            # Grant FOUNDER role
            self.identity.users[uid]["role"] = "FOUNDER"
            self.identity.users[uid]["roles"] = ["FOUNDER", "WORKER"]
            self.identity.save()
            # Give starting balance
            self.ledger.add_block('MINT', {"minter": uid, "amount": 1000.0, "memo": "Genesis Grant"})
            self.users.append({"id": uid, "role": "FOUNDER"})
            
        for i in range(self.num_admins):
            uid = f"admin_{i}"
            res, msg = self.identity.register(uid, "pass123")
            self.identity.users[uid]["role"] = "ADMIN"
            self.identity.users[uid]["roles"] = ["ADMIN", "WORKER"]
            self.identity.save()
            self.ledger.add_block('MINT', {"minter": uid, "amount": 1000.0, "memo": "Admin Grant"})
            self.users.append({"id": uid, "role": "ADMIN"})

    def simulate_reservations(self):
        print("\n--- Simulating High-Concurrency Reservations ---")
        threads = []
        results = []

        def worker(user_id):
            asset = random.choice(["HARDWARE-LAB-001", "MEDIA-STUDIO-001", "QUIET-ROOM-001"])
            duration = random.randint(1, 4)
            res = self.foundry.reserve_asset(user_id, asset, duration)
            results.append(res)

        for user in self.users:
            t = threading.Thread(target=worker, args=(user['id'],))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        successes = len([r for r in results if r['status'] == 'success'])
        failures = [r for r in results if r['status'] == 'error']
        print(f"Results: {successes} Successes, {len(failures)} Failures")
        if failures:
            print(f"Sample Failure Error: {failures[0]['message']}")

    def verify_multipliers(self):
        print("\n--- Verifying Role Multipliers ---")
        # In Ark OS, multipliers are often applied at the API or Justice level 
        # In this sim, we check if the FOUNDER role exists and has the correct base_multiplier
        founder_role = ROLE_DEFINITIONS.get("FOUNDER")
        print(f"FOUNDER Role Definition: {founder_role['title']} | Multiplier: {founder_role['base_multiplier']}x")
        
        if founder_role['base_multiplier'] == 3.0:
            print("✅ Multiplier verification: SUCCESS")
        else:
            print("❌ Multiplier verification: FAILURE")

    def run(self):
        start = time.time()
        self.setup_users()
        self.verify_multipliers()
        self.simulate_reservations()
        
        # Cleanup
        if os.path.exists(self.db_file): os.remove(self.db_file)
        if os.path.exists('sim_users.json'): os.remove('sim_users.json')
        if os.path.exists('foundry_state.json'): os.remove('foundry_state.json')
        
        print(f"\nSimulation complete in {time.time() - start:.2f}s")

if __name__ == "__main__":
    sim = FoundersStressTest(num_founders=100, num_admins=10)
    sim.run()
