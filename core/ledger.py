import sqlite3
import json
import time
import hashlib
import os
import logging

logger = logging.getLogger("ArkOS.Ledger")

class VillageLedger:
    def __init__(self, db_file):
        self.db_file = db_file
        self.blocks = []
        self.init_db()
        self.load()

    def init_db(self):
        db_dir = os.path.dirname(self.db_file)
        if db_dir:
            os.makedirs(db_dir, exist_ok=True)
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blocks (
                block_id INTEGER PRIMARY KEY AUTOINCREMENT,
                block_hash TEXT UNIQUE NOT NULL,
                block_type TEXT NOT NULL,
                timestamp INTEGER NOT NULL,
                data TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()

    def load(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM blocks ORDER BY block_id ASC")
        rows = cursor.fetchall()
        self.blocks = []
        for row in rows:
            self.blocks.append({
                "id": row['block_id'],
                "index": row['block_index'],
                "hash": row['block_hash'],
                "prev": row['previous_hash'],
                "parents": json.loads(row['parents']) if row['parents'] else [],
                "type": row['block_type'],
                "timestamp": row['timestamp'],
                "data": json.loads(row['data'])
            })
        conn.close()

    def add_block(self, block_type, data):
        timestamp = int(time.time())
        last_block = self.blocks[-1] if self.blocks else {"index": -1, "hash": "0"}
        
        # Safe fallback for NULL columns in existing DB
        last_index = last_block.get('index')
        if last_index is None: last_index = 0
        
        new_index = last_index + 1
        prev_hash = last_block.get('hash', "0")
        if prev_hash is None: prev_hash = "0"
        
        block_string = json.dumps(data, sort_keys=True) + str(timestamp) + block_type + prev_hash
        block_hash = hashlib.sha256(block_string.encode()).hexdigest()
        
        return self._persist_block(block_hash, block_type, timestamp, data, index=new_index, prev=prev_hash)

    def _persist_block(self, b_hash, b_type, timestamp, data, index=0, prev="0"):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            parents = json.dumps([prev])
            cursor.execute("""
                INSERT OR IGNORE INTO blocks 
                (block_index, block_hash, previous_hash, parents, block_type, timestamp, data) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (index, b_hash, prev, parents, b_type, timestamp, json.dumps(data)))
            
            block_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            if block_id:
                res_block = {
                    "id": block_id, "index": index, "hash": b_hash, 
                    "prev": prev, "parents": [prev], "type": b_type, 
                    "timestamp": timestamp, "data": data
                }
                self.blocks.append(res_block)
                return b_hash
            return None
        except Exception as e:
            logger.error(f"Ledger Error: {e}")
            return None

    def get_balance(self, username):
        balance = 0
        for b in self.blocks:
            d = b['data']
            if b['type'] == 'TX':
                if d.get('sender') == username: balance -= d.get('amount', 0)
                if d.get('receiver') == username: balance += d.get('amount', 0)
            elif b['type'] in ['LABOR', 'HARDWARE_PROOF', 'PROOF', 'CODE_MINT', 'MINT', 'GRANT']:
                if d.get('minter') == username or d.get('worker') == username or d.get('recipient') == username:
                    balance += d.get('reward', d.get('at', d.get('amount', 10)))
            elif b['type'] == 'PURCHASE':
                if d.get('buyer') == username: balance -= d.get('amount', 0)
        return balance

    def get_bounties(self):
        return [b['data'] for b in self.blocks if b['type'] == 'BOUNTY']

    def get_inventory(self, username):
        inventory = []
        for b in self.blocks:
            if b['type'] == 'PURCHASE' and b['data'].get('buyer') == username:
                inventory.append(b['data'].get('item'))
        return inventory
