#!/usr/bin/env python3
"""
Sprint 1: SQLite Migration - Fixed Version
Handles variable block structures from JSON ledger
"""

import sqlite3
import json
import os

LEDGER_FILE = "village_ledger_py.json"
DB_FILE = "village_ledger.db"

def create_schema(conn):
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            block_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER NOT NULL,
            block_hash TEXT UNIQUE NOT NULL,
            previous_hash TEXT,
            block_type TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            data TEXT NOT NULL
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_hash ON blocks(block_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_type ON blocks(block_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON blocks(timestamp)")
    conn.commit()
    print("✅ Schema created")

def migrate_ledger(conn):
    if not os.path.exists(LEDGER_FILE):
        print("❌ Ledger file not found")
        return 0
    
    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)
    
    cursor = conn.cursor()
    print(f"📦 Migrating {len(ledger)} blocks...")
    migrated = 0
    
    for i, block in enumerate(ledger):
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO blocks (block_index, block_hash, previous_hash, block_type, timestamp, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                block.get('index', i),
                block.get('hash', f"hash_{i}"),
                block.get('previous_hash', '0'),
                block.get('block_type', 'UNKNOWN'),
                block.get('timestamp', 0),
                json.dumps(block.get('data', {}))
            ))
            migrated += 1
        except Exception as e:
            print(f"⚠️  Block {i}: {e}")
    
    conn.commit()
    return migrated

# Main
conn = sqlite3.connect(DB_FILE)
create_schema(conn)
migrated = migrate_ledger(conn)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM blocks")
db_count = cursor.fetchone()[0]

print(f"✅ Migrated {migrated} blocks")
print(f"📊 Database contains: {db_count} blocks")

cursor.execute("SELECT block_type, COUNT(*) FROM blocks GROUP BY block_type")
print("\n📈 Block Types:")
for row in cursor.fetchall():
    print(f"   {row[0]}: {row[1]}")

conn.close()
print(f"\n✅ Migration complete! Database at: {DB_FILE}")
