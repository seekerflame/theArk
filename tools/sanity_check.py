import sys
import os
import json
import time

# Add core paths
base_path = '/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark'
sys.path.append(base_path)

from core.ledger import VillageLedger

def run_sanity_check():
    print("--- 🩺 ARK OS SYSTEM SANITY CHECK ---")
    
    # 1. Ledger Verification
    db_file = os.path.join(base_path, 'village_ledger.db')
    print(f"[1/3] Ledger Integrity Check (DB: {db_file})...")
    ledger = VillageLedger(db_file)
    blocks = ledger.blocks
    print(f"Current Blocks in Memory: {len(blocks)}")
    
    # Check if DB has blocks
    if len(blocks) > 0:
        print("✅ Ledger has existing blocks.")
    else:
        print("ℹ️  Ledger is currently empty or new.")

    # 2. Add Block Test
    print("[2/3] Adding Test Block...")
    test_data = {"test": "sanity_check", "val": 100}
    tx_hash = ledger.add_block('SANITY_TEST', test_data)
    if tx_hash:
        print(f"✅ Block added. Hash: {tx_hash}")
    else:
        print("❌ Failed to add block.")

    # 3. Balance Logic Check
    print("[3/3] Checking Balance Logic...")
    test_user = "pilot_user_001"
    # Add a MINT block for testing balance
    mint_data = {"minter": test_user, "reward": 50, "memo": "Sanity Mint"}
    ledger.add_block('LABOR', mint_data)
    balance = ledger.get_balance(test_user)
    print(f"User {test_user} Balance: {balance} AT")
    if balance >= 50:
        print("✅ Balance calculation consistent.")
    else:
        print(f"❌ Balance calculation discrepancy (Expected >= 50, Got {balance}).")

    print("--- 🩺 SANITY CHECK COMPLETE ---")

if __name__ == "__main__":
    run_sanity_check()

if __name__ == "__main__":
    run_sanity_check()
