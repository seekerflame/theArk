#!/usr/bin/env python3
import sqlite3
import json
import os

LEDGER_FILE = "village_ledger_py.json"
DB_FILE = "village_ledger.db"

def migrate():
    if not os.path.exists(LEDGER_FILE):
        print("❌ JSON ledger not found.")
        return

    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Ensure schema exists (Genesis-compatible)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            block_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER,
            block_hash TEXT UNIQUE NOT NULL,
            previous_hash TEXT,
            parents TEXT,
            block_type TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)

    print(f"📦 Migrating {len(ledger)} blocks...")
    migrated = 0
    errors = 0

    for i, block in enumerate(ledger):
        try:
            # Map variable block structure
            b_hash = block.get('hash', block.get('block_hash', f"hash_{i}"))
            b_index = block.get('index', block.get('block_index', i))
            b_type = block.get('block_type', block.get('data', {}).get('block_type', 'UNKNOWN'))
            b_time = block.get('timestamp', 0)
            b_prev = block.get('previous_hash', '0')
            b_parents = json.dumps(block.get('parents', [b_prev] if b_prev != '0' else []))
            b_data = json.dumps(block.get('data', {}))

            cursor.execute("""
                INSERT OR IGNORE INTO blocks (block_index, block_hash, previous_hash, parents, block_type, timestamp, data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (b_index, b_hash, b_prev, b_parents, b_type, b_time, b_data))
            migrated += 1
        except Exception as e:
            errors += 1
            if errors < 10:
                print(f"⚠️  Error migrating block {i}: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Migration complete. {migrated} blocks processed.")

if __name__ == "__main__":
    migrate()
