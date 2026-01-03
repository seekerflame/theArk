import json
import os
import time
import hashlib
import glob

# Configuration
LEDGER_FILE = 'village_ledger_py.json'
LIBRARY_DIR = 'library'

# Load Ledger
if os.path.exists(LEDGER_FILE):
    with open(LEDGER_FILE, 'r') as f:
        ledger = json.load(f)
else:
    print("❌ Critical: Ledger not found.")
    exit(1)

def mint_block(block_type, payload):
    parents = [ledger[-1]['hash']] if ledger else []
    
    # Create Hash
    content = f"{block_type}{json.dumps(payload)}{time.time()}"
    block_hash = hashlib.md5(content.encode()).hexdigest()
    
    # Block Structure
    block = {
        "hash": block_hash,
        "parents": parents,
        "data": {
            "block_type": block_type,
            "verified": True,
            **payload
        },
        "timestamp": int(time.time())
    }
    
    ledger.append(block)
    print(f"🧱 Minted: [{block_type}] {payload.get('page', 'Unknown')}")

# Scan Library
print("📜 Scanning Knowledge Library for Genesis...")
files = glob.glob(f"{LIBRARY_DIR}/*.md")

for filepath in files:
    filename = os.path.basename(filepath)
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Create Payload
    payload = {
        "page": filename,
        "content_hash": hashlib.md5(content.encode()).hexdigest(),
        "size_bytes": len(content),
        "author": "Antigravity (Genesis)",
        "message": "Initial Knowledge Seeding"
    }
    
    mint_block("WIKI", payload)

# Save Ledger
with open(LEDGER_FILE, 'w') as f:
    json.dump(ledger, f, indent=2)

print("✅ Knowledge Genesis Complete. The Library is on-chain.")
