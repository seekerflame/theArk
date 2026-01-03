#!/usr/bin/env python3
"""
Geographic Ledger Backup System
Automatically copies ledger to multiple physical locations for disaster recovery
"""

import json
import shutil
import os
from datetime import datetime
from pathlib import Path

# Backup locations (customize per deployment)
BACKUP_LOCATIONS = [
    "/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/BACKUPS",  # Local SSD
    os.path.expanduser("~/Documents/AT_Backups"),  # User docs
    # Add: USB drives, network shares, cloud sync folders
]

LEDGER_FILE = "village_ledger_py.json"

def create_backup():
    """Create timestamped backup in all locations"""
    if not os.path.exists(LEDGER_FILE):
        print(f"[BACKUP] Ledger not found: {LEDGER_FILE}")
        return
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"ledger_backup_{timestamp}.json"
    
    # Also create a "human-readable" markdown version
    md_name = f"ledger_archive_{timestamp}.md"
    
    for location in BACKUP_LOCATIONS:
        try:
            Path(location).mkdir(parents=True, exist_ok=True)
            
            # Copy JSON
            dest_json = os.path.join(location, backup_name)
            shutil.copy2(LEDGER_FILE, dest_json)
            
            # Create Markdown archive
            dest_md = os.path.join(location, md_name)
            create_markdown_archive(LEDGER_FILE, dest_md)
            
            print(f"[BACKUP] ✅ Saved to {location}")
        except Exception as e:
            print(f"[BACKUP] ❌ Failed {location}: {e}")
    
    # Keep only last 100 backups per location (prevent bloat)
    cleanup_old_backups()

def create_markdown_archive(ledger_path, output_path):
    """Create human-readable Markdown version of ledger"""
    with open(ledger_path, 'r') as f:
        ledger = json.load(f)
    
    with open(output_path, 'w') as f:
        f.write("# Abundance Token Ledger Archive\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Total Blocks:** {len(ledger)}\n\n")
        f.write("---\n\n")
        
        for block in ledger:
            block_type = block.get('block_type', 'UNKNOWN')
            timestamp = block.get('timestamp', 0)
            date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
            
            f.write(f"## Block {block.get('index', '?')} - {block_type}\n\n")
            f.write(f"**Date:** {date}  \n")
            f.write(f"**Hash:** `{block.get('hash', 'N/A')}`  \n")
            f.write(f"**Previous:** `{block.get('previous_hash', 'N/A')}`  \n\n")
            
            # Extract key data
            data = block.get('data', {})
            if block_type == 'MINT':
                f.write(f"- **User:** {data.get('username', '?')}  \n")
                f.write(f"- **Hours:** {data.get('hours', 0)}  \n")
                f.write(f"- **Task:** {data.get('task', 'N/A')}  \n")
            elif block_type == 'TX':
                f.write(f"- **From:** {data.get('from', '?')}  \n")
                f.write(f"- **To:** {data.get('to', '?')}  \n")
                f.write(f"- **Amount:** {data.get('amount', 0)} AT  \n")
            
            f.write("\n---\n\n")

def cleanup_old_backups():
    """Keep only last 100 backups in each location"""
    for location in BACKUP_LOCATIONS:
        if not os.path.exists(location):
            continue
        
        backups = sorted([
            os.path.join(location, f) 
            for f in os.listdir(location) 
            if f.startswith('ledger_backup_')
        ], key=os.path.getmtime)
        
        # Delete oldest if >100
        while len(backups) > 100:
            oldest = backups.pop(0)
            try:
                os.remove(oldest)
                print(f"[CLEANUP] Removed old backup: {oldest}")
            except:
                pass

if __name__ == "__main__":
    create_backup()
    print("[BACKUP] Ledger backup complete.")
