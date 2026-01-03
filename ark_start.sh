#!/bin/bash
# Ark OS - Automated Startup Script
# Usage: ./ark_start.sh

set -e

ARK_DIR="/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
LOG_FILE="$ARK_DIR/server.log"
PID_FILE="$ARK_DIR/server.pid"

echo "🚀 ARK OS STARTUP SEQUENCE"
echo "=========================="

# Check if already running
if [ -f "$PID_FILE" ]; then
    OLD_PID=$(cat "$PID_FILE")
    if ps -p "$OLD_PID" > /dev/null 2>&1; then
        echo "⚠️  Server already running (PID: $OLD_PID)"
        exit 1
    else
        echo "🧹 Cleaning stale PID file..."
        rm "$PID_FILE"
    fi
fi

# Navigate to Ark directory
cd "$ARK_DIR" || exit 1

# Start server in background
echo "🔧 Starting Python server..."
nohup python3 server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait for startup
echo "⏳ Waiting for server initialization..."
sleep 3

# Health check
echo "🩺 Running health check..."
HEALTH=$(curl -s http://localhost:3000/api/health 2>/dev/null || echo '{"status":"error"}')

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ SERVER ONLINE"
    echo "   PID: $SERVER_PID"
    echo "   URL: http://localhost:3000"
    echo "   Log: $LOG_FILE"
    echo ""
    echo "🎯 Ark OS is operational. Advance the mission."
else
    echo "❌ HEALTH CHECK FAILED"
    echo "   Check logs: tail -f $LOG_FILE"
    exit 1
fi
