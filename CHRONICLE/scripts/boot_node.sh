#!/bin/bash
# boot_node.sh - OSE Sovereign Node Bootloader

PROJECT_ROOT="/Volumes/Extreme SSD/Antigrav/OSE"
ARK_DIR="$PROJECT_ROOT/abundancetoken/07_Code/The_Ark"

echo "--- OSE NODE BOOTLOADER ---"

# 1. Check NetBird Status
echo "[+] Checking Mesh Connectivity..."
if netbird status | grep -q "Connected"; then
    echo "✅ Mesh Online."
else
    echo "⚠️ Mesh Offline. Attempting to connect..."
    netbird up
fi

# 2. Check for Friend's Node (Optional Ping)
# if [ ! -z "$FRIEND_IP" ]; then
#     ping -c 1 "$FRIEND_IP" > /dev/null 2>&1
#     if [ $? -eq 0 ]; then echo "✅ Peer Node detected."; else echo "⚠️ Peer Node unreachable."; fi
# fi

# 3. Start The Ark Server
echo "[+] Launching The Ark (PORT 3000)..."
cd "$ARK_DIR"
python3 server.py &
SERVER_PID=$!

echo "🚀 System is LIVE at http://localhost:3000"
echo "Press Ctrl+C to shutdown node."

# 4. Handle Shutdown
trap "kill $SERVER_PID; echo '--- NODE SHUTDOWN ---'; exit" INT
wait
