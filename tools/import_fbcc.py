import json
import os
import time
import sys

# Ensure we can import core modules
sys.path.append(os.getcwd())

from core.ledger import VillageLedger

def import_fbcc_tasks():
    print("🏗️  Initializing FBCC Task Importer...")

    # Load Ledger
    ledger_path = os.path.join(os.getcwd(), 'ledger', 'village_ledger.db')
    ledger = VillageLedger(ledger_path)

    # Load FBCC Roles
    fbcc_path = os.path.join(os.getcwd(), 'web', 'fbcc_roles.json')
    try:
        with open(fbcc_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: {fbcc_path} not found.")
        return

    roles = data.get('roles', [])
    print(f"📋 Found {len(roles)} roles. Scanning for tasks...")

    # Get existing quests to prevent duplicates
    existing_quests = {b['data']['title'] for b in ledger.blocks if b['type'] == 'QUEST'}

    added_count = 0

    for role in roles:
        print(f"   > Processing {role['name']}...")
        for task in role.get('default_tasks', []):
            if task['title'] in existing_quests:
                continue

            # Create Quest Block
            quest_data = {
                "quest_id": f"fbcc_{int(time.time())}_{added_count}",
                "title": task['title'],
                "description": f"[{role['name']}] {task['description']}",
                "reward": task.get('bounty_at', 10),
                "owner": "Maslow_Prime_System",
                "category": role.get('category', 'MAINTENANCE'),
                "status": "OPEN",
                "created_at": time.time(),
                "frequency": task.get('frequency', 'daily')
            }

            ledger.add_block('QUEST', quest_data)
            existing_quests.add(task['title']) # Prevent dupes in same run
            added_count += 1
            print(f"     + Added: {task['title']}")

    print(f"✅ Import Complete. {added_count} new tasks added to Ledger.")

if __name__ == "__main__":
    import_fbcc_tasks()
