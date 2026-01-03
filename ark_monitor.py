import time
import urllib.request
import subprocess
import os
import signal

# ARK OS WATCHDOG
# Monitor health and auto-restart if system hangs

HEALTH_URL = "http://localhost:3000/api/health"
START_CMD = "./ark_start.sh"
CHECK_INTERVAL = 30 # Seconds
PORT = 3000

def check_health():
    try:
        with urllib.request.urlopen(HEALTH_URL, timeout=5) as r:
            if r.getcode() == 200:
                return True
    except:
        return False
    return False

def restart_ark():
    print(f"⚠️  ARK OS unresponsive at {time.ctime()}. Triggering self-healing...")
    # Kill any zombie python server
    subprocess.run(["pkill", "-f", "python3 server.py"])
    time.sleep(2)
    # Run startup script
    subprocess.run([START_CMD], shell=True)
    print("✅ Self-healing sequence complete.")

def main():
    print(f"🛡️  Ark Watchdog Active. Monitoring {HEALTH_URL} every {CHECK_INTERVAL}s")
    while True:
        if not check_health():
            # Double check before restart to avoid false positives
            print("❓ Health check missed. Retrying in 5s...")
            time.sleep(5)
            if not check_health():
                restart_ark()
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main()
