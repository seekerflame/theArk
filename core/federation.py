import json
import os
import time
import threading
import subprocess
import logging

logger = logging.getLogger("ArkOS.Federation")

class PeerManager:
    def __init__(self, registry_file, port):
        self.registry_file = registry_file
        self.port = port
        self.peers = []
        self.load()

    def load(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    data = json.load(f)
                    self.peers = data.get('villages', data) if isinstance(data, dict) else data
            except: pass
        else:
            self.peers = [{"id": "V-001", "name": "The Ark (Local)", "url": f"http://localhost:{self.port}", "status": "ONLINE"}]
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, 'w') as f: json.dump(self.peers, f, indent=2)

    def add_peer(self, name, url):
        p_id = f"V-{len(self.peers)+1:03d}"
        self.peers.append({"id": p_id, "name": name, "url": url, "status": "PENDING"})
        self.save()
        return p_id

class FederationSyncer:
    def __init__(self, ledger, peers, port):
        self.ledger = ledger
        self.peers = peers
        self.port = port
        self.stop_event = threading.Event()

    def sync_cycle(self):
        while not self.stop_event.is_set():
            for peer in self.peers.peers:
                if not isinstance(peer, dict) or 'url' not in peer: continue
                if peer['url'].endswith(str(self.port)): continue 
                try:
                    last_id = self.ledger.blocks[-1]['id'] if self.ledger.blocks else 0
                    url = f"{peer['url']}/api/graph?since={last_id}"
                    logger.info(f"Syncing from peer: {peer['name']} ({url})")
                    
                    res = subprocess.check_output(["curl", "-s", url])
                    data = json.loads(res)
                    
                    if data.get('status') == 'success':
                        new_blocks = data.get('data', [])
                        for b in new_blocks:
                            if self.ledger.reconcile_block(b):
                                logger.info(f"Synced new block {b['hash'][:8]} from {peer['name']}")
                        peer['status'] = 'ONLINE'
                    else:
                        peer['status'] = 'ERROR'
                except Exception as e:
                    logger.warning(f"Failed to sync from {peer['name']}: {e}")
                    peer['status'] = 'OFFLINE'
            
            self.peers.save()
            time.sleep(30)

    def start(self):
        threading.Thread(target=self.sync_cycle, daemon=True).start()
