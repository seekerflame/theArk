import subprocess
import time
import urllib.request
import urllib.error
import json
import os
import sys
import signal
import datetime
import random


# --- Configuration ---
SERVER_SCRIPT = "server.py"
PORT = 3000
CHECK_INTERVAL = 10  # Seconds between checks
TRAFFIC_INTERVAL = 30 # Seconds between simulated transactions
LOG_FILE = "sentinel.log"

server_process = None
last_traffic_time = 0

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] [SENTINEL] {message}"
    print(entry)
    with open(LOG_FILE, "a") as f:
        f.write(entry + "\n")

def is_server_running():
    # Simple check: Can we connect to the port?
    try:
        with urllib.request.urlopen(f"http://localhost:{PORT}/api/health", timeout=2) as response:
            return response.getcode() == 200
    except:
        return False

def start_server():
    global server_process
    log(f"🚀 Starting {SERVER_SCRIPT}...")
    # direct output to separate logs or inherit? Let's hide it to keep sentinel clean, 
    # but capturing it would be better for debugging. 
    # For now, let's let it spew to stdout if run manually, or redirect if needed.
    # We'll redirect to a file.
    
    with open("ark_steward.log", "a") as out_log:
        server_process = subprocess.Popen(
            [sys.executable, SERVER_SCRIPT],
            cwd=os.getcwd(),
            stdout=out_log, 
            stderr=out_log
        )
    log(f"✅ Server Process PID: {server_process.pid}")

def stop_server():
    global server_process
    if server_process:
        log("🛑 Stopping Server Process...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            server_process.kill()
        server_process = None
    else:
        # Fallback: Try to kill by port/name if we didn't start it but found it dead? 
        # Actually if we didn't start it, we might not have the handle.
        # But for 'Local' sentinel, we assume we own it.
        pass

def generate_traffic():
    # Simulate a "Heartbeat" Mint
    try:
        # User requested: LABOR, ECO, TOOLS
        category = random.choice(["LABOR", "ECO", "TOOLS"])
        payload = {
            "minter": "Sentinel_AI", 
            "task": f"System Heartbeat ({category})", 
            "hours": 0.1,
            "category": category,
            "verified": True # Sentinel heartbeats are auto-verified
        }
        req = urllib.request.Request(
            f"http://localhost:{PORT}/api/mint", 
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'abundance'
            }
        )
        with urllib.request.urlopen(req, timeout=2) as resp:
            if resp.getcode() == 200:
                log("💓 Heartbeat Minted (Traffic Simulation)")
    except Exception as e:
        log(f"⚠️ Traffic Gen Failed: {e}")

def main():
    global server_process, last_traffic_time
    
    log("🛡️ Sentinel Active. Monitoring The Ark.")
    
    # 1. Cleanup existing? (Optional)
    
    try:
        while True:
            # WATCHDOG
            if not is_server_running():
                log("⚠️ Server appears DOWN or Unresponsive.")
                stop_server() # Safety cleanup
                start_server()
                # Give it time to boot
                time.sleep(5) # Increased from 2s to 5s for slower hardware/DB init
            
            # TRAFFIC GEN
            if time.time() - last_traffic_time > TRAFFIC_INTERVAL:
                if is_server_running():
                    generate_traffic()
                    last_traffic_time = time.time()
            
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        log("👋 Sentinel shutting down.")
        stop_server()
        sys.exit(0)

if __name__ == "__main__":
    # Ensure we are in the right dir
    if not os.path.exists(SERVER_SCRIPT):
        log(f"❌ Error: {SERVER_SCRIPT} not found in {os.getcwd()}")
        sys.exit(1)
        
    main()
