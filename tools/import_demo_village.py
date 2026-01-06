#!/usr/bin/env python3
"""
Import demo village blocks into SQLite ledger
"""
import json
import sqlite3
import sys
import os

def import_demo_blocks():
    """Import JSON blocks into SQLite ledger"""
    
    # Load demo blocks
    with open('ledger/demo_village_blocks.json', 'r') as f:
        demo_blocks = json.load(f)
    
    print(f"📦 Loaded {len(demo_blocks)} demo blocks")
    
    # Connect to ledger database
    db_file = 'ledger/village_ledger.db'
    if not os.path.exists(db_file):
        print(f"❌ Ledger database not found: {db_file}")
        print("💡 Make sure The Ark has been run at least once to initialize the database")
        return False
    
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    # Import each block
    imported = 0
    skipped = 0
    
    for block in demo_blocks:
        try:
            cursor.execute(
                "INSERT OR IGNORE INTO blocks (block_hash, block_type, timestamp, data) VALUES (?, ?, ?, ?)",
                (
                    block['hash'],
                    block['type'],
                    block['timestamp'],
                    json.dumps(block['data'])
                )
            )
            if cursor.rowcount > 0:
                imported += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"⚠️  Error importing block {block['hash'][:8]}: {e}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Import complete!")
    print(f"   Imported: {imported} blocks")
    print(f"   Skipped:  {skipped} blocks (already exist)")
    print(f"\n🚀 Restart The Ark to see demo village active!")
    
    return True

if __name__ == '__main__':
    try:
        if not os.path.exists('ledger/demo_village_blocks.json'):
            print("❌ Demo blocks not found. Run init_demo_village.py first")
            sys.exit(1)
        
        success = import_demo_blocks()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
