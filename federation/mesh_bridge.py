import json
import time
import os
import gzip
import base64
import random

# CONFIG
LEDGER_FILE = 'village_ledger_py.json'
INBOX_DIR = 'mesh_inbox'
OUTBOX_LOG = 'mesh_outbox.log'

# Ensure Dirs
if not os.path.exists(INBOX_DIR):
    os.makedirs(INBOX_DIR)

print("📡 [MESH BRIDGE] Initializing LoRa Interface...")
print("Checking for Meshtastic hardware... (SIMULATION MODE)")

def load_ledger():
    try:
        with open(LEDGER_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def compress_block(block):
    # Minify JSON
    json_str = json.dumps(block, separators=(',', ':'))
    # Gzip
    compressed = gzip.compress(json_str.encode('utf-8'))
    # Base64 for Text Transmission
    b64 = base64.b64encode(compressed).decode('utf-8')
    return b64

def broadcast(packet):
    # Simulate LoRa Broadcast
    print(f"📡 [TX] Broadcasting Packet ({len(packet)} bytes)...")
    with open(OUTBOX_LOG, 'a') as f:
        f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} | TX | {packet}\n")
    # Simulate airtime delay
    time.sleep(random.uniform(0.5, 2.0))
    print("✅ [TX] Sent.")

def listen():
    # Check Inbox for new packets (File drop simulation)
    # In real Meshtastic, this would be serial.read()
    pass

# MAIN LOOP
last_count = 0

while True:
    ledger = load_ledger()
    current_count = len(ledger)
    
    if current_count > last_count:
        # New Blocks Detected!
        new_blocks = ledger[last_count:]
        print(f"🆕 [MESH] Found {len(new_blocks)} new blocks to sync.")
        
        for block in new_blocks:
            # ONLY Sync WIKI or CRITICAL Transaction blocks to save bandwidth
            btype = block['data'].get('block_type', 'UNKNOWN')
            
            if btype in ['WIKI', 'TX', 'GENESIS']:
                packet = compress_block(block)
                broadcast(packet)
            else:
                print(f"⏭️ [SKIP] ignoring heavy block {btype}")
        
        last_count = current_count
    
    time.sleep(10)
