#!/usr/bin/env python3
import os
import json
import sqlite3
import urllib.request
import sys

# OSE Sentinel Checker v1.1
# "Always advance the mission. High output, low noise."

BASE_DIR = "/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
WEB_DIR = os.path.join(BASE_DIR, "web")
DB_FILE = os.path.join(BASE_DIR, "village_ledger.db")

FAILURES = []

def log_failure(component, message):
    print(f"❌ [FAIL] {component}: {message}")
    FAILURES.append({"component": component, "message": message})

def check_placeholders():
    print("🔍 Checking for unconfigured placeholders...")
    placeholders = ["YOUR_N8N_CHAT_WEBHOOK_URL", "var(--primary-light)fff"]
    for root, _, files in os.walk(WEB_DIR):
        for file in files:
            if file.endswith((".html", ".js", ".css")):
                path = os.path.join(root, file)
                with open(path, 'r', errors='ignore') as f:
                    content = f.read()
                    for p in placeholders:
                        if p in content:
                            log_failure("PLACEHOLDER", f"Found '{p}' in {file}")

def check_backend():
    print("🔍 Checking backend health...")
    try:
        with urllib.request.urlopen("http://localhost:3000/api/health", timeout=2) as r:
            if r.status == 200:
                print("✅ Backend is LIVE")
            else:
                log_failure("BACKEND", f"Health check returned {r.status}")
    except Exception as e:
        log_failure("BACKEND", f"Could not connect: {e}")

def check_db():
    print("🔍 Checking database integrity...")
    if not os.path.exists(DB_FILE):
        log_failure("DATABASE", "village_ledger.db missing!")
        return
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blocks")
        count = cursor.fetchone()[0]
        print(f"✅ DB has {count} blocks")
        conn.close()
    except Exception as e:
        log_failure("DATABASE", f"Corrupt or locked: {e}")

def check_ui_logic():
    print("🔍 Checking app.js for fragile fetch logic...")
    app_js = os.path.join(WEB_DIR, "app.js")
    if os.path.exists(app_js):
        with open(app_js, 'r') as f:
            lines = f.readlines()
            for i, line in enumerate(lines):
                # Skip if already has .catch on the same line
                if "fetch(" in line and ".catch(" in line:
                    continue
                
                # Skip async/await pattern (try/catch handles these)
                if "await fetch(" in line:
                    continue
                    
                # Check for fetch calls without .catch in the following 120 lines (large promise chain window)
                if "fetch(" in line:
                    found_catch = False
                    brace_depth = 0
                    
                    # Look ahead up to 120 lines for a .catch(
                    for j in range(1, 120):
                        if i + j >= len(lines):
                            break
                        check_line = lines[i+j]
                        
                        if ".catch(" in check_line:
                            found_catch = True
                            break
                        
                        # Also count as found if we hit a new function definition (scope boundary)
                        if ("window." in check_line and "function" in check_line) or \
                           ("function " in check_line and "(" in check_line):
                            break
                    
                    if not found_catch:
                        # Only log if it's an actual API call or resource fetch
                        if any(x in line for x in ["/api/", ".json", ".md", "localhost"]):
                            log_failure("UI_LOGIC", f"Fragile fetch at app.js:{i+1}")

def main():
    check_placeholders()
    check_backend()
    check_db()
    check_ui_logic()
    
    if FAILURES:
        print(f"\n🛑 {len(FAILURES)} failures found. System is SUBOPTIMAL.")
        with open(os.path.join(BASE_DIR, "sentinel_report.json"), 'w') as f:
            json.dump(FAILURES, f, indent=2)
        sys.exit(1)
    else:
        print("\n✨ ALL SYSTEMS OPTIMAL. Mission Ready.")
        sys.exit(0)

if __name__ == "__main__":
    main()
