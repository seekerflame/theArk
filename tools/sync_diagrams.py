import os
import argparse
import time
from core.config import Config

# The Shared Map URL (from "fren of dev")
SHARED_MAP_URL = "https://www.mermaidchart.com/app/projects/164728d4-dd49-4384-a326-9f40aac9af0a/diagrams/5368504b-2af9-4b26-bbd6-6f8a4f7faf86/version/v0.1/edit"

def get_api_key():
    return Config.get_mermaid_key()

def scan_local_diagrams():
    """Scans the repo for .mermaid and .md files with diagrams."""
    diagrams = []
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs: dirs.remove('.git')
        for file in files:
            if file.endswith('ARCHITECTURE.mermaid'):
                diagrams.append(os.path.join(root, file))
    return diagrams

def monitor_mode():
    """
    Watches local file for changes and prompts user to sync.
    Since we don't have WRITE access to the API key yet, we guide the user to the URL.
    """
    print(f"👁️  Visual DevOps Monitor Active")
    print(f"🔗 Shared Map: {SHARED_MAP_URL}")
    print("---------------------------------------------------")
    
    last_mtime = 0
    target_file = './ARCHITECTURE.mermaid'
    
    if not os.path.exists('docs/master_architecture.md'):
        print(f"❌ Target map not found: docs/master_architecture.md")
        return

    try:
        current_mtime = os.path.getmtime('docs/master_architecture.md')
        if current_mtime > last_mtime:
            print(f"\n[DETECTED CHANGE] {time.ctime(current_mtime)}")
            print(f"👉 ACTION: Copy content from docs/master_architecture.md")
            print(f"👉 PASTE TO: {SHARED_MAP_URL}")
            last_mtime = current_mtime
            
            time.sleep(2)
    except KeyboardInterrupt:
        print("\n🛑 Monitor stopped.")

def push_to_cloud():
    """Manual push guidance."""
    print("🚀 Pushing to Cloud...")
    print(f"⚠️  API Key read-only or missing. Manual Sync Required.")
    print(f"1. Open: {SHARED_MAP_URL}")
    print(f"2. Copy content from: ./ARCHITECTURE.mermaid")
    print(f"3. Paste into Web Editor")
    print("✅ Done.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync Mermaid diagrams with Mermaid Chart API")
    parser.add_argument("--monitor", action="store_true", help="Watch for changes and prompt sync")
    parser.add_argument("--push", action="store_true", help="Push logic")
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_mode()
    else:
        push_to_cloud()
