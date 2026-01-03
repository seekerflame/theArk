import sys
import os
import json
import hashlib
import time

# Ensure we run from scripting dir
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Import Server Logic to reuse VillageLedger
# We'll just copy the class essence or import if possible. 
# Importing server might trigger the server loop if not careful.
# Let's just append to the JSON directly to avoid side effects or port conflicts.

DATA_FILE = 'village_ledger_py.json'

def mint_wiki_block(page, content_file):
    if not os.path.exists(DATA_FILE):
        print("Error: Ledger not found")
        return

    with open(DATA_FILE, 'r') as f:
        blocks = json.load(f)

    with open(content_file, 'r') as f:
        content = f.read()

    content_hash = hashlib.md5(content.encode()).hexdigest()
    
    # Block Payload
    payload = {
        "block_type": "WIKI",
        "page": page,
        "content_hash": content_hash,
        "action": "UPDATE",
        "verified": True
    }

    # Hash Calculation
    parents = [blocks[-1]['hash']] if blocks else []
    raw_str = f"WIKI{json.dumps(payload)}{time.time()}"
    block_hash = hashlib.md5(raw_str.encode()).hexdigest()

    block = {
        "hash": block_hash,
        "parents": parents,
        "data": payload,
        "timestamp": int(time.time())
    }

    blocks.append(block)

    with open(DATA_FILE, 'w') as f:
        json.dump(blocks, f, indent=2)

    print(f"✅ Minted WIKI Block: {block_hash} for {page}")

if __name__ == "__main__":
    mint_wiki_block(
        "User:Seeker/Future_Builders_Crash_Course_Operations_Manual", 
        "Future_Builders_Crash_Course_SOP.md"
    )
