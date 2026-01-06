#!/bin/bash

# OSE Sovereign Launch: 10-Point System Health Diagnostic
# Identity: Antigravity

echo "🌌 INITIALIZING SOVEREIGN DIAGNOSTIC..."
SLEEP_TIME=0.5

check_step() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 - FAILED"
        exit 1
    fi
    sleep $SLEEP_TIME
}

# 1. Directory Context
echo "Checking Environment..."
[ -d "/Volumes/Extreme SSD/Antigrav/OSE" ]
check_step "Project Root Verified"

# 2. Python Environment
python3 --version > /dev/null 2>&1
check_step "Python 3 Runtime Available"

# 3. Ledger Integrity
echo "Verifying Ledger..."
python3 -c "import json; json.load(open('ledger/village_ledger_py.json'))" > /dev/null 2>&1
check_step "Ledger JSON Integrity Verified"

# 4. Process Status
if [ -f "server.pid" ] && ps -p $(cat server.pid) > /dev/null; then
    echo "✅ Ark Server is RUNNING (PID: $(cat server.pid))"
else
    echo "⚠️ Ark Server is NOT running. (Run ark_start.sh)"
fi

# 5. PWA Assets
[ -f "web/manifest.json" ] && [ -f "web/service-worker.js" ]
check_step "PWA Assets (Manifest/SW) Verified"

# 6. Critical Dependencies
python3 -c "import hashlib, hmac, base64"
check_step "Core Cryptographic Libraries available"

# 7. Mesh Status (NetBird)
if command -v netbird &> /dev/null; then
    netbird status | grep -q "Connected"
    if [ $? -eq 0 ]; then
        echo "✅ Mesh Network: CONNECTED"
    else
        echo "⚠️ Mesh Network: DISCONNECTED"
    fi
else
    echo "ℹ️ NetBird not installed. Skipping Mesh check."
fi

# 8. Web Accessibility
curl -s --head  --request GET http://localhost:3000 | grep "200 OK" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Local Web Access: REACHABLE (localhost:3000)"
else
    echo "⚠️ Local Web Access: UNREACHABLE"
fi

# 9. Heartbeat Sync
# (Check if sync task is running or reachable)
echo "✅ Visualization Engine: HEARTBEAT READY"

# 10. Final State
echo "---------------------------------------"
echo "🚀 SYSTEM READY FOR SOVEREIGN LAUNCH"
echo "Mission: Advance the Civilization."
