import json
import os
import datetime

WEB_DIR = 'web'
DATA_FILE = 'village_ledger_py.json'
USERS_FILE = 'users.json'
QUESTS_FILE = os.path.join(WEB_DIR, 'quests.json')

def load_json(path):
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            return None
    return None

def main():
    print("=== 📊 CLASSIFIED OPERATIVE REPORT 📊 ===\n")
    
    # 1. USERS
    users = load_json(USERS_FILE)
    if users:
        print(f"## 👥 Operatives ({len(users)})")
        for username, data in users.items():
            role = data.get('role', 'UNKNOWN')
            created = datetime.datetime.fromtimestamp(data.get('created_at', 0)).strftime('%Y-%m-%d %H:%M')
            print(f"  - **{username}** [{role}] (Joined: {created})")
    else:
        print("## 👥 Operatives: None Found (System Empty)")
    
    print()

    # 2. LEDGER ACTIVITY
    ledger = load_json(DATA_FILE)
    if ledger:
        print(f"## 📒 Ledger Status ({len(ledger)} Blocks)")
        
        # Analyze Blocks
        counts = {}
        quests_completed = []
        recent_activity = []
        
        for block in ledger:
            data = block.get('data', {})
            btype = data.get('block_type', 'UNKNOWN')
            counts[btype] = counts.get(btype, 0) + 1
            
            # Quest Completion
            if btype == 'QUEST_COMPLETE' or (btype == 'QUEST' and data.get('status') == 'COMPLETED'):
                quests_completed.append(data)
            
            # Recent (last 5)
            ts = block.get('timestamp', 0)
            date = datetime.datetime.fromtimestamp(ts).strftime('%m-%d %H:%M')
            recent_activity.append(f"[{date}] {btype}: {str(data)}")

        print("### Activity Distribution")
        for k, v in counts.items():
            print(f"  - {k}: {v}")
            
        print("\n### Recent Events (Last 5)")
        for activity in recent_activity[-5:]:
            print(f"  {activity}")

    else:
        print("## 📒 Ledger: No Data")

    print()

    # 3. QUESTS
    quests = load_json(QUESTS_FILE)
    if quests:
        print(f"## ⚔️ Active Quests ({len(quests)})")
        for q in quests:
            # Check if likely done
            status = q.get('status', 'OPEN')
            print(f"  - [{status}] {q.get('title')} ({q.get('reward')} tokens)")
            if 'claimed_by' in q:
                print(f"    -> Claimed by: {q['claimed_by']}")
    else:
        print("## ⚔️ Quests: None On Board")

if __name__ == "__main__":
    main()
