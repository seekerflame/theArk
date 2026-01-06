import json
import os
import time

USERS_FILE = "core/users.json"

def inject_admin():
    if not os.path.exists(USERS_FILE):
        users = {}
    else:
        with open(USERS_FILE, 'r') as f:
            users = json.load(f)
            
    users["superadmin"] = {
        "password": "superpassword",
        "role": "ADMIN",
        "roles": ["ADMIN", "ORACLE"],
        "certifications": {},
        "verified_hours": 1000,
        "safety_grade": 100,
        "created_at": time.time(),
        "mnemonic": "ark seed node labor mint value gaia tribe build grid power earth"
    }
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)
    print("✅ Injected user 'superadmin' with password 'superpassword'")

if __name__ == "__main__":
    inject_admin()
