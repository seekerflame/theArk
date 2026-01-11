#!/bin/bash
# Ark OS - Automated Shutdown Script
# Usage: ./ark_stop.sh

set -e

# Get actual script location
ARK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PID_FILE="$ARK_DIR/server.pid"
CHRONICLE_DIR="/Volumes/Extreme SSD/Antigrav/OSE/CHRONICLE"

echo "🛑 ARK OS SHUTDOWN SEQUENCE"
echo "==========================="

if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found. Server might already be stopped."
    # Fallback to pkill if user really wants it stopped
    echo "🔍 Checking for zombie processes..."
    if pgrep -f "python3 server.py" > /dev/null; then
        echo "🧟 Found zombie process. Terminating..."
        pkill -f "python3 server.py"
    fi
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE")

echo "⏳ Terminating server (PID: $SERVER_PID)..."
if kill "$SERVER_PID" 2>/dev/null; then
    # Wait for it to actually die
    for i in {1..5}; do
        if ps -p "$SERVER_PID" > /dev/null; then
            sleep 1
        else
            break
        fi
    done

    if ps -p "$SERVER_PID" > /dev/null; then
        echo "⚠️  Server didn't stop. Forcing shutdown..."
        kill -9 "$SERVER_PID" 2>/dev/null
    fi

    echo "✅ Server stopped."
else

# Cleanup PID file
rm -f "$PID_FILE"

# Run Integrity Guard
if [ -f "$ARK_DIR/ark_guard.sh" ]; then
    echo "🛡️  Checking system integrity..."
    bash "$ARK_DIR/ark_guard.sh" || { echo "❌ INTEGRITY CHECK FAILED. Aborting snapshot."; exit 1; }
fi

# Auto-snapshot using CHRONICLE
if [ -f "$CHRONICLE_DIR/scripts/snapshot.sh" ]; then
    echo "📦 Creating CHRONICLE snapshot..."
    cd "/Volumes/Extreme SSD/Antigrav/OSE"
    bash "$CHRONICLE_DIR/scripts/snapshot.sh" || echo "⚠️  Snapshot failed (non-critical)"
fi

echo ""
echo "🌙 Ark OS shutdown complete. State preserved."
echo "   Next startup: ./ark_start.sh"
