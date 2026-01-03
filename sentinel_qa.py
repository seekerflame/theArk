#!/usr/bin/env python3
"""
Sentinel: Automated QA Background Service
Runs every 5 minutes to verify server health, routes, and database integrity.
"""

import time
import urllib.request
import json
import os
import sqlite3

BASE_URL = "http://localhost:3000"
LOG_FILE = "sentinel_qa.json"
CHECK_INTERVAL = 300 # 5 minutes

ROUTES = [
    "/api/health",
    "/api/state",
    "/api/graph",
    "/api/store",
    "/web/index.html",
    "/web/app.js"
]

def check_route(route):
    try:
        url = BASE_URL + route
        response = urllib.request.urlopen(url)
        return response.getcode() == 200, None
    except Exception as e:
        return False, str(e)

def check_db():
    try:
        db_path = os.path.join(os.getcwd(), 'village_ledger.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM blocks")
        count = cursor.fetchone()[0]
        conn.close()
        return count >= 0, None
    except Exception as e:
        return False, str(e)

def run_checks():
    status = {
        "timestamp": time.time(),
        "routes": {},
        "database": {"ok": True, "error": None},
        "overall": "PASS"
    }
    
    # Check Routes
    for route in ROUTES:
        ok, err = check_route(route)
        status["routes"][route] = {"ok": ok, "error": err}
        if not ok: status["overall"] = "FAIL"
    
    # Check DB
    db_ok, db_err = check_db()
    status["database"] = {"ok": db_ok, "error": db_err}
    if not db_ok: status["overall"] = "FAIL"
    
    # Write result
    with open(LOG_FILE, 'w') as f:
        json.dump(status, f, indent=2)
    
    print(f"[{time.ctime()}] Sentinel QA: {status['overall']}")

if __name__ == "__main__":
    print("🚀 Sentinel QA Service Starting...")
    while True:
        try:
            run_checks()
        except Exception as e:
            print(f"⚠️ Sentinel Error: {e}")
        time.sleep(CHECK_INTERVAL)
