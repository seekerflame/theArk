# Sprint 1: Database Migration - PostgreSQL Setup

## JSON → PostgreSQL for Production Scale

### Prerequisites

- PostgreSQL 14+ installed
- psycopg2 Python library
- Database credentials configured

### Schema Design

```sql
-- Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE,
    wallet_address VARCHAR(128) UNIQUE NOT NULL,
    seed_phrase_hash VARCHAR(256) NOT NULL,
    role VARCHAR(20) DEFAULT 'USER',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Blocks table (ledger)
CREATE TABLE blocks (
    block_id SERIAL PRIMARY KEY,
    block_index INTEGER NOT NULL,
    block_hash VARCHAR(64) UNIQUE NOT NULL,
    previous_hash VARCHAR(64),
    block_type VARCHAR(20) NOT NULL,
    timestamp BIGINT NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_block_hash ON blocks(block_hash);
CREATE INDEX idx_block_type ON blocks(block_type);
CREATE INDEX idx_timestamp ON blocks(timestamp);

-- Quests table
CREATE TABLE quests (
    quest_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50),
    bounty_at INTEGER NOT NULL,
    estimated_time VARCHAR(20),
    status VARCHAR(20) DEFAULT 'OPEN',
    location VARCHAR(100),
    icon VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User achievements
CREATE TABLE achievements (
    achievement_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    achievement_type VARCHAR(50) NOT NULL,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    at_reward INTEGER DEFAULT 0
);

CREATE INDEX idx_user_achievements ON achievements(user_id);
```

### Migration Script

```python

#!/usr/bin/env python3

"""
Migrate JSON ledger to PostgreSQL
"""

import json
import psycopg2
from psycopg2.extras import Json

# Load JSON ledger

with open('village_ledger_py.json', 'r') as f:
    ledger = json.load(f)

# Connect to PostgreSQL

conn = psycopg2.connect(
    host="localhost",
    database="abundance_token",
    user="postgres",
    password="your_password"
)
cur = conn.cursor()

# Migrate blocks

print(f"Migrating {len(ledger)} blocks...")
for block in ledger:
    cur.execute("""
        INSERT INTO blocks (block_index, block_hash, previous_hash, block_type, timestamp, data)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (block_hash) DO NOTHING
    """, (
        block['index'],
        block['hash'],
        block.get('previous_hash', '0'),
        block['block_type'],
        block['timestamp'],
        Json(block['data'])
    ))

conn.commit()
print("Migration complete!")
```

### Server.py Updates

```python
import psycopg2
from psycopg2.extras import RealDictCursor

# Connection pool

from psycopg2 import pool
db_pool = psycopg2.pool.SimpleConnectionPool(
    1, 10,
    host="localhost",
    database="abundance_token",
    user="postgres",
    password="your_password"
)

def get_ledger():
    """Fetch ledger from PostgreSQL"""
    conn = db_pool.getconn()
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT * FROM blocks ORDER BY block_index")
        blocks = cur.fetchall()
        return [dict(b) for b in blocks]
    finally:
        db_pool.putconn(conn)

def add_block(block):
    """Add block to PostgreSQL"""
    conn = db_pool.getconn()
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO blocks (block_index, block_hash, previous_hash, block_type, timestamp, data)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            block['index'],
            block['hash'],
            block['previous_hash'],
            block['block_type'],
            block['timestamp'],
            Json(block['data'])
        ))
        conn.commit()
    finally:
        db_pool.putconn(conn)
```

### Performance Targets

- Query time: < 100ms for `/api/graph`
- Write time: < 50ms for `/api/mint`
- Concurrent connections: 100+
- Database size: 1GB for 100k blocks

### Rollback Plan

- Keep JSON ledger as backup during transition
- Dual-write to both systems for 1 week
- Verify data consistency before cutover

---

**Status:** Ready to execute. Requires user approval for production database setup.
