#!/usr/bin/env python3
"""
Dunbar Mitosis Protocol - Phase 9
Automates node replication when population exceeds 150 (Dunbar's Number).

Logic:
1. Monitor registered user count
2. When count > 150, trigger "Mitosis" event
3. Generate new node seed (configuration package)
4. Export ledger snapshot for new node
5. Register new node in federation
"""

import os
import json
import time
import hashlib
import sqlite3
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "village_ledger.db")
REGISTRY_FILE = os.path.join(BASE_DIR, "federation_registry.json")
NODE_SEED_DIR = os.path.join(BASE_DIR, "node_seeds")

DUNBAR_LIMIT = 150
NODE_PREFIX = "ose-child"

class MitosisEngine:
    def __init__(self):
        self.db_file = DB_FILE
        self.node_id = self._get_current_node_id()
        
    def _get_current_node_id(self):
        """Get current node ID from config or generate one."""
        try:
            with open(os.path.join(BASE_DIR, "node_config.json"), 'r') as f:
                return json.load(f).get('node_id', 'ark_primary')
        except:
            return 'ark_primary'
    
    def get_user_count(self):
        """Count unique active users in the ledger."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            # Count unique minters/users
            cursor.execute("""
                SELECT COUNT(DISTINCT json_extract(data, '$.minter')) 
                FROM blocks 
                WHERE json_extract(data, '$.minter') IS NOT NULL
            """)
            count = cursor.fetchone()[0] or 0
            conn.close()
            return count
        except Exception as e:
            print(f"[MITOSIS] Error counting users: {e}")
            return 0
    
    def check_mitosis_trigger(self):
        """Check if node population exceeds Dunbar limit."""
        user_count = self.get_user_count()
        print(f"[MITOSIS] Current population: {user_count}/{DUNBAR_LIMIT}")
        
        if user_count > DUNBAR_LIMIT:
            print(f"[MITOSIS] ⚠️ DUNBAR LIMIT EXCEEDED. Initiating mitosis protocol...")
            return True
        return False
    
    def generate_node_seed(self, child_name=None):
        """Generate a new node configuration package."""
        timestamp = int(time.time())
        child_id = child_name or f"{NODE_PREFIX}-{timestamp}"
        seed_dir = os.path.join(NODE_SEED_DIR, child_id)
        
        os.makedirs(seed_dir, exist_ok=True)
        
        # Create node config
        node_config = {
            "node_id": child_id,
            "parent_node": self.node_id,
            "created_at": timestamp,
            "dunbar_limit": DUNBAR_LIMIT,
            "genesis_block": self._get_latest_block_hash()
        }
        
        with open(os.path.join(seed_dir, "node_config.json"), 'w') as f:
            json.dump(node_config, f, indent=2)
        
        # Export ledger snapshot (last 100 blocks for reference)
        self._export_ledger_snapshot(seed_dir)
        
        # Copy essential files
        essential_files = [
            "web/index.html",
            "web/app.js", 
            "web/style.css",
            "web/ui_config.json",
            "web/manifest.json",
            "server.py"
        ]
        
        for file in essential_files:
            src = os.path.join(BASE_DIR, file)
            if os.path.exists(src):
                dst_dir = os.path.dirname(os.path.join(seed_dir, file))
                os.makedirs(dst_dir, exist_ok=True)
                shutil.copy2(src, os.path.join(seed_dir, file))
        
        print(f"[MITOSIS] 🌱 Node seed created: {seed_dir}")
        return child_id, seed_dir
    
    def _get_latest_block_hash(self):
        """Get hash of latest block for genesis reference."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM blocks ORDER BY block_id DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else "genesis"
        except:
            return "genesis"
    
    def _export_ledger_snapshot(self, seed_dir, limit=100):
        """Export recent ledger blocks for new node."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM blocks ORDER BY block_id DESC LIMIT {limit}")
            blocks = cursor.fetchall()
            conn.close()
            
            snapshot = {
                "exported_at": time.time(),
                "parent_node": self.node_id,
                "block_count": len(blocks),
                "blocks": [{"id": b[0], "hash": b[1], "prev_hash": b[2], "data": json.loads(b[3]), "timestamp": b[4]} for b in blocks]
            }
            
            with open(os.path.join(seed_dir, "ledger_snapshot.json"), 'w') as f:
                json.dump(snapshot, f, indent=2)
                
            print(f"[MITOSIS] 📦 Exported {len(blocks)} blocks to snapshot")
        except Exception as e:
            print(f"[MITOSIS] Error exporting snapshot: {e}")
    
    def register_child_node(self, child_id, ip="TBD", port=3000, lat=0, lng=0):
        """Register new child node in federation registry."""
        try:
            registry = {"villages": []}
            if os.path.exists(REGISTRY_FILE):
                with open(REGISTRY_FILE, 'r') as f:
                    registry = json.load(f)
            
            new_node = {
                "village_id": child_id,
                "name": f"Child Node ({child_id})",
                "ip": ip,
                "port": port,
                "lat": lat,
                "lng": lng,
                "parent": self.node_id,
                "status": "pending_deploy",
                "created_at": time.time()
            }
            
            registry['villages'].append(new_node)
            
            with open(REGISTRY_FILE, 'w') as f:
                json.dump(registry, f, indent=2)
            
            print(f"[MITOSIS] ✅ Child node registered in federation: {child_id}")
            return True
        except Exception as e:
            print(f"[MITOSIS] Error registering node: {e}")
            return False
    
    def execute_mitosis(self):
        """Full mitosis protocol execution."""
        if not self.check_mitosis_trigger():
            return {"status": "not_needed", "population": self.get_user_count()}
        
        child_id, seed_dir = self.generate_node_seed()
        self.register_child_node(child_id)
        
        return {
            "status": "mitosis_complete",
            "child_node": child_id,
            "seed_location": seed_dir,
            "parent_node": self.node_id
        }
    
    def status(self):
        """Get current mitosis status."""
        user_count = self.get_user_count()
        return {
            "node_id": self.node_id,
            "population": user_count,
            "dunbar_limit": DUNBAR_LIMIT,
            "headroom": DUNBAR_LIMIT - user_count,
            "mitosis_triggered": user_count > DUNBAR_LIMIT
        }


if __name__ == "__main__":
    import sys
    
    engine = MitosisEngine()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "status":
            status = engine.status()
            print(json.dumps(status, indent=2))
        
        elif cmd == "check":
            if engine.check_mitosis_trigger():
                print("[MITOSIS] ⚠️ Mitosis REQUIRED")
            else:
                print("[MITOSIS] ✅ Population within limits")
        
        elif cmd == "execute":
            result = engine.execute_mitosis()
            print(json.dumps(result, indent=2))
        
        elif cmd == "seed":
            name = sys.argv[2] if len(sys.argv) > 2 else None
            child_id, seed_dir = engine.generate_node_seed(name)
            print(f"Seed created: {child_id} at {seed_dir}")
        
        else:
            print("Usage: mitosis.py [status|check|execute|seed [name]]")
    else:
        # Default: status
        print(json.dumps(engine.status(), indent=2))
