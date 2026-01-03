import sqlite3
import json
import os
import sys

# ARK OS - Chronicle Export Tool
# Used to generate training data for Sovereign AI (Digital Twin)

DB_FILE = 'village_ledger.db'
EXPORT_FILE = 'sovereign_context.jsonl'

def export():
    if not os.path.exists(DB_FILE):
        print(f"Error: {DB_FILE} not found.")
        sys.exit(1)

    print(f"🛰️  Synchronizing Chronicle from {DB_FILE}...")
    
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # We export all blocks that represent "intelligence" or "metabolic action"
    cursor.execute("SELECT * FROM blocks ORDER BY timestamp ASC")
    rows = cursor.fetchall()
    
    exported_count = 0
    with open(EXPORT_FILE, 'w', encoding='utf-8') as f:
        for row in rows:
            data = json.loads(row['data'])
            block_type = row['block_type']
            timestamp = row['timestamp']
            
            # Format for LLM fine-tuning or RAG (JSONL)
            record = {
                "type": block_type,
                "timestamp": timestamp,
                "content": data
            }
            
            # Special formatting for messages to preserve conversational history
            if block_type == 'MESSAGE':
                record["formatted"] = f"[{data.get('sender', 'Unknown')}]: {data.get('content', '')}"
            elif block_type == 'LABOR':
                record["formatted"] = f"[MINT]: {data.get('minter')} logged {data.get('hours')}h of {data.get('task')}"
            
            f.write(json.dumps(record) + '\n')
            exported_count += 1

    print(f"🚀 Export Complete: {exported_count} records saved to {EXPORT_FILE}")
    print("💡 You can now feed this to your local model script to advance the Mission.")

if __name__ == "__main__":
    export()
