#!/bin/bash
# Ark OS - Automated Startup Script
# Usage: ./ark_start.sh

set -e

# Get actual script location to be portable
ARK_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
LOG_FILE="$ARK_DIR/logs/server.log"
PID_FILE="$ARK_DIR/server.pid"

echo "🚀 ARK OS STARTUP SEQUENCE"
echo "=========================="

# Ensure Environment is set up
echo "🛠️  Initializing environment..."
python3 "$ARK_DIR/setup.py"

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

# Default PORT if not set (or load from .env.local if needed)
PORT=${PORT:-3000}

# Start server in background
echo "🔧 Starting Python server on port $PORT..."
mkdir -p "$ARK_DIR/logs"
nohup python3 server.py > "$LOG_FILE" 2>&1 &
SERVER_PID=$!
echo $SERVER_PID > "$PID_FILE"

# Wait for startup
echo "⏳ Waiting for server initialization..."
sleep 3

# Health check
echo "🩺 Running health check on port $PORT..."
HEALTH=$(curl -s http://localhost:$PORT/api/health 2>/dev/null || echo '{"status":"error"}')

if echo "$HEALTH" | grep -q "healthy"; then
    echo "✅ SERVER ONLINE"
    echo "   PID: $SERVER_PID"
    echo "   URL: http://localhost:$PORT"
    echo "   Log: $LOG_FILE"
    echo ""
    echo "🎯 Ark OS is operational. Advance the mission."
else
    echo "❌ HEALTH CHECK FAILED"
    echo "   Check logs: tail -f $LOG_FILE"
    exit 1
fi
