#!/usr/bin/env python3
"""
Federation Client - Village-to-Village Synchronization
Enables this village node to sync with other OSE villages
"""

import urllib.request
import urllib.parse
import json
import time
from datetime import datetime
from pathlib import Path

# Configuration
LOCAL_VILLAGE_ID = "ose-missouri-001"  # Customize per deployment
FEDERATION_REGISTRY = "federation_registry.json"
LEDGER_FILE = "village_ledger_py.json"
SYNC_INTERVAL = 300  # 5 minutes

class FederationClient:
    def __init__(self):
        self.registry = self.load_registry()
        self.last_sync = {}
        
    def load_registry(self):
        """Load known federated villages"""
        if Path(FEDERATION_REGISTRY).exists():
            with open(FEDERATION_REGISTRY, 'r') as f:
                return json.load(f)
        return {"villages": []}
    
    def save_registry(self):
        """Save federation registry"""
        with open(FEDERATION_REGISTRY, 'w') as f:
            json.dump(self.registry, f, indent=2)
    
    def register_village(self, village_data):
        """Add a new village to federation"""
        self.registry['villages'].append(village_data)
        self.save_registry()
        print(f"[FEDERATION] Registered {village_data['name']}")
    
    def sync_with_village(self, village):
        """Sync ledger blocks with another village"""
        try:
            # Get their latest blocks
            url = f"http://{village['ip']}:{village['port']}/api/graph"
            with urllib.request.urlopen(url, timeout=10) as response:
                their_blocks = json.loads(response.read().decode())
                
                # Load our blocks
                if not Path(LEDGER_FILE).exists():
                     with open(LEDGER_FILE, 'w') as f: json.dump([], f)
                
                with open(LEDGER_FILE, 'r') as f:
                    our_blocks = json.load(f)
                
                # Find new blocks (simple hash comparison)
                our_hashes = {b['hash'] for b in our_blocks}
                new_blocks = [b for b in their_blocks if b['hash'] not in our_hashes]
                
                if new_blocks:
                    print(f"[FEDERATION] Received {len(new_blocks)} new blocks from {village['name']}")
                    
                    # Merge (append-only for now, no conflict resolution)
                    our_blocks.extend(new_blocks)
                    
                    # Save merged ledger
                    with open(LEDGER_FILE, 'w') as f:
                        json.dump(our_blocks, f, indent=2)
                    
                    self.last_sync[village['village_id']] = time.time()
                else:
                    print(f"[FEDERATION] Already in sync with {village['name']}")
                
                return True
                
        except Exception as e:
            print(f"[FEDERATION] Error syncing with {village['name']}: {e}")
            return False
    
    def heartbeat(self):
        """Send heartbeat to all federated villages"""
        for village in self.registry.get('villages', []):
            if not village.get('enabled', True):
                continue
            
            try:
                url = f"http://{village['ip']}:{village['port']}/federation/heartbeat"
                data = json.dumps({
                    "village_id": LOCAL_VILLAGE_ID,
                    "timestamp": int(time.time())
                }).encode()
                
                req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=5) as response:
                    pass # Heartbeat success
            except:
                pass  # Heartbeat failure is non-critical
    
    def run_sync_cycle(self):
        """Execute full federation sync"""
        print(f"[FEDERATION] Starting sync cycle at {datetime.now()}")
        
        for village in self.registry.get('villages', []):
            if village.get('enabled', True):
                self.sync_with_village(village)
        
        self.heartbeat()
        print(f"[FEDERATION] Sync cycle complete")

def main():
    client = FederationClient()
    
    # Example: Add a test village (comment out after first run)
    # client.register_village({
    #     "village_id": "ose-california-001",
    #     "name": "OSE West Coast",
    #     "ip": "192.168.1.100",
    #     "port": 3000,
    #     "enabled": True
    # })
    
    print(f"""
    ╔═══════════════════════════════════════╗
    ║   FEDERATION CLIENT - VILLAGE SYNC    ║
    ║   {LOCAL_VILLAGE_ID:^37} ║
    ╚═══════════════════════════════════════╝
    """)
    
    while True:
        try:
            client.run_sync_cycle()
        except KeyboardInterrupt:
            print("[FEDERATION] Shutting down...")
            break
        except Exception as e:
            print(f"[FEDERATION] Error in sync cycle: {e}")
        
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
