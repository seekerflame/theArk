import json
import time
from core.ledger import VillageLedger

def test_code_mint():
    print("--- VERIFYING CODE MINT AT FLOW ---")
    
    # 1. Setup Ledger
    ledger = VillageLedger('ledger/village_ledger.db')
    username = 'eternalflame'
    
    # 2. Add CODE_MINT Block
    data = {
        'minter': username,
        'description': 'Test code contribution',
        'lines_changed': 100,
        'complexity': 'standard',
        'reward': 10.0,
        'commit_hash': 'abcdef1234567890abcdef1234567890abcdef12',
        'timestamp': time.time()
    }
    
    print(f"Adding CODE_MINT block for {username}...")
    b_hash = ledger.add_block('CODE_MINT', data)
    
    if b_hash:
        print(f"SUCCESS: Block added with hash {b_hash}")
    else:
        print("FAILURE: Block not added")
        return

    # 3. Verify Balance
    balance = ledger.get_balance(username)
    print(f"Current Balance for {username}: {balance} AT")
    
    # 4. Test Duplicate Prevention (Logic is in API, but let's check ledger content)
    # Since duplicate check is in economy.py, we'll verify the block exists
    blocks = [b for b in ledger.blocks if b['type'] == 'CODE_MINT']
    print(f"Total CODE_MINT blocks in ledger: {len(blocks)}")
    
    for b in blocks:
        d = b['data']
        if d.get('commit_hash') == data['commit_hash']:
            print(f"Found block with expected commit hash: {d.get('commit_hash')}")

    # 5. Test Duplicate Prevention (Simulating API logic)
    print("\n--- TESTING DUPLICATE PREVENTION ---")
    new_data = data.copy()
    new_data['description'] = 'Duplicate attempt'
    
    is_duplicate = False
    if new_data.get('commit_hash') or new_data.get('pr_url'):
        for b in ledger.blocks:
            if b['type'] == 'CODE_MINT':
                d = b['data']
                if (new_data.get('commit_hash') and d.get('commit_hash') == new_data.get('commit_hash')) or \
                   (new_data.get('pr_url') and d.get('pr_url') == new_data.get('pr_url')):
                    is_duplicate = True
                    break
    
    if is_duplicate:
        print("SUCCESS: Duplicate contribution proof detected (Simulated API check).")
    else:
        print("FAILURE: Duplicate check failed.")


if __name__ == "__main__":
    test_code_mint()
