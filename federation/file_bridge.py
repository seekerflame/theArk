import os
import hashlib
import shutil
import json
import time
from pathlib import Path
from core.config import STORAGE_DIR, INBOX_DIR, LEDGER_FILE

class FileBridge:
    def __init__(self, ledger):
        self.ledger = ledger
        self.storage = STORAGE_DIR
        self.inbox = INBOX_DIR
        self.manifest_file = self.storage / "file_manifest.json"
        self.manifest = self._load_manifest()

    def _load_manifest(self):
        if self.manifest_file.exists():
            with open(self.manifest_file, "r") as f:
                return json.load(f)
        return {}

    def _save_manifest(self):
        with open(self.manifest_file, "w") as f:
            json.dump(self.manifest, f, indent=2)

    def hash_file(self, file_path):
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def register_file(self, file_path, metadata=None):
        """Register a local file in the manifest and the ledger"""
        path = Path(file_path)
        if not path.exists():
            return False
            
        file_hash = self.hash_file(path)
        file_info = {
            "name": path.name,
            "hash": file_hash,
            "size": path.stat().st_size,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # Store in local manifest
        self.manifest[file_hash] = str(path.resolve())
        self._save_manifest()
        
        # Log to ledger for discovery
        self.ledger.add_block("FILE_ANNOUNCEMENT", file_info)
        print(f"📦 File registered: {path.name} ({file_hash[:8]})")
        return file_hash

    def request_file(self, file_hash, peer_url):
        """Placeholder for P2P file request logic via NetBird/HTTP"""
        print(f"📡 Requesting file {file_hash[:8]} from {peer_url}...")
        # In a real implementation, this would use requests to fetch from peer_url/api/files/{hash}
        return False

if __name__ == "__main__":
    from core.ledger import VillageLedger
    from core.config import LEDGER_DB
    
    ledger = VillageLedger(LEDGER_DB)
    bridge = FileBridge(ledger)
    
    # Example: Register a log file for testing
    log_path = Path(__file__).parent.parent / "logs" / "server.log"
    if log_path.exists():
        bridge.register_file(log_path)
