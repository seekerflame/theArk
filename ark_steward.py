
import time
import subprocess
import os
import datetime

# Configuration
SYNC_INTERVAL = 600 # 10 Minutes
LOG_FILE = "ark_steward.log"

def log(msg):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {msg}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def run_sync():
    log("🔄 Ark Steward: Initiating Gaia Sync Sequence...")
    try:
        # Run the sync script
        result = subprocess.run(["python3", "wiki_sync.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            log("✅ Sync Successful.")
            if result.stdout:
                log(f"Sync Results:\n{result.stdout}") 
            if result.stderr:
                log(f"Sync Warnings/Errors:\n{result.stderr}")
        else:
            log(f"❌ Sync Failed with code {result.returncode}")
            log(f"Error: {result.stderr}")
            
    except Exception as e:
        log(f"🚨 Critical Failure in Sync Dispatch: {e}")

def main():
    log("🚀 Ark Steward Online. Monitoring for Abundance...")
    while True:
        run_sync()
        log(f"💤 Sleeping for {SYNC_INTERVAL} seconds...")
        time.sleep(SYNC_INTERVAL)

if __name__ == "__main__":
    main()
