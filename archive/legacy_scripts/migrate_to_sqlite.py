#!/usr/bin/env python3
"""
Sprint 1: SQLite Migration (PostgreSQL alternative for local dev)
Migrate JSON ledger to SQLite for better performance and concurrent access
"""

import sqlite3
import json
import os
from datetime import datetime

LEDGER_FILE = "village_ledger_py.json"
DB_FILE = "village_ledger.db"

def create_schema(conn):
    """Create database schema"""
    cursor = conn.cursor()
    
    # Blocks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocks (
            block_id INTEGER PRIMARY KEY AUTOINCREMENT,
            block_index INTEGER NOT NULL,
            block_hash TEXT UNIQUE NOT NULL,
            previous_hash TEXT,
            block_type TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            data JSON NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_hash ON blocks(block_hash)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_block_type ON blocks(block_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON blocks(timestamp)")
    
    conn.commit()
    print("✅ Schema created")

def migrate_ledger(conn):
    """Migrate JSON ledger to SQLite"""
    if not os.path.exists(LEDGER_FILE):
        print("❌ Ledger file not found")
        return
    
    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)
    
    cursor = conn.cursor()
    
    print(f"📦 Migrating {len(ledger)} blocks...")
    migrated = 0
    
    for block in ledger:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO blocks (block_index, block_hash, previous_hash, block_type, timestamp, data)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                block['index'],
                block['hash'],
                block.get('previous_hash', '0'),
                block['block_type'],
                block['timestamp'],
                json.dumps(block['data'])
            ))
            migrated += 1
        except Exception as e:
            print(f"⚠️  Error migrating block {block.get('index')}: {e}")
    
    conn.commit()
    print(f"✅ Migrated {migrated}/{len(ledger)} blocks")

def verify_migration(conn):
    """Verify migration success"""
    cursor = conn.cursor()
    
    # Count blocks
    cursor.execute("SELECT COUNT(*) FROM blocks")
    db_count = cursor.fetchone()[0]
    
    with open(LEDGER_FILE, 'r') as f:
        json_count = len(json.load(f))
    
    print(f"\n📊 Verification:")
    print(f"   JSON ledger: {json_count} blocks")
    print(f"   SQLite DB:   {db_count} blocks")
    
    if db_count == json_count:
        print("✅ Migration verified - counts match")
    else:
        print("⚠️  Warning - count mismatch!")
    
    # Show sample data
    cursor.execute("SELECT block_type, COUNT(*) FROM blocks GROUP BY block_type")
    print("\n📈 Block Types:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}")

if __name__ == "__main__":
    print("=" * 70)
    print("SPRINT 1: DATABASE MIGRATION (SQLite)")
    print("=" * 70)
    
    # Connect to SQLite
    conn = sqlite3.connect(DB_FILE)
    
    # Run migration
    create_schema(conn)
    migrate_ledger(conn)
    verify_migration(conn)
    
    conn.close()
    
    print("\n✅ Migration complete! Database ready at:", DB_FILE)
    print("Next: Update server.py to use SQLite instead of JSON")
