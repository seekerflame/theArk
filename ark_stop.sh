#!/bin/bash
# Ark OS - Automated Shutdown Script  
# Usage: ./ark_stop.sh

set -e

ARK_DIR="/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
PID_FILE="$ARK_DIR/server.pid"
CHRONICLE_DIR="/Volumes/Extreme SSD/Antigrav/OSE/CHRONICLE"

echo "🛑 ARK OS SHUTDOWN SEQUENCE"
echo "==========================="

# Check if server is running
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  No PID file found. Checking for orphaned processes..."
    pkill -f "python3 server.py" && echo "✅ Killed orphaned server" || echo "ℹ️  No server processes found"
    exit 0
fi

SERVER_PID=$(cat "$PID_FILE")

# Graceful shutdown
if ps -p "$SERVER_PID" > /dev/null 2>&1; then
    echo "📡 Sending shutdown signal to PID $SERVER_PID..."
    kill -TERM "$SERVER_PID" 2>/dev/null || true
    
    # Wait for graceful shutdown (max 10 seconds)
    for i in {1..10}; do
        if ! ps -p "$SERVER_PID" > /dev/null 2>&1; then
            echo "✅ Server stopped gracefully"
            break
        fi
        sleep 1
    done
    
    # Force kill if still running
    if ps -p "$SERVER_PID" > /dev/null 2>&1; then
        echo "⚠️  Force killing stubborn process..."
        kill -9 "$SERVER_PID"
    fi
else
    echo "ℹ️  Server not running"
fi

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
