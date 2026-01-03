#!/bin/bash
# ABSOLUTE PATH - No cd tricks
ARK_DIR="/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"

echo "🔧 ABUNDANCE TOKEN: FIX & LAUNCH"
echo "-------------------------------------------"

# 1. Kill Zombies
echo "💀 Killing old servers..."
pkill -f "python3 server.py" 2>/dev/null
pkill -f "python server.py" 2>/dev/null
pkill -f "village_node_mac" 2>/dev/null

# 2. Start Backend (log to /tmp to avoid SSD permission issues)
echo "🚀 Starting The Ark Server..."
cd "$ARK_DIR"
nohup python3 -u server.py > /tmp/ark_server.log 2>&1 &
SERVER_PID=$!
echo "✅ Server PID: $SERVER_PID"

# 3. Wait for boot
echo "⏳ Waiting for server..."
sleep 3

# 4. Verify server is running
if ps -p $SERVER_PID > /dev/null 2>&1; then
    echo "✅ Server is running"
else
    echo "❌ Server crashed! Check /tmp/ark_server.log"
    cat /tmp/ark_server.log
    exit 1
fi

# 5. Trigger Wiki Sync
echo "🔄 Running Wiki Sync..."
cd "$ARK_DIR"
python3 wiki_sync.py

# 6. Launch Interface
echo "🌍 Opening GAIA..."
open "http://localhost:3000/web/gaia.html"

echo "-------------------------------------------"
echo "✅ SYSTEM IS LIVE."
echo "Server log: /tmp/ark_server.log"
