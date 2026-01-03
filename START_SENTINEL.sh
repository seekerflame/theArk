#!/bin/bash
# START_SENTINEL.sh
# Starts the Sentinel in the background, detached from the terminal.

# 1. Kill existing sentinel if running
pkill -f "python3 sentinel.py"

# 2. Start Sentinel with nohup
echo "🛡️ Deploying Sentinel..."
nohup python3 sentinel.py > sentinel_nohup.log 2>&1 &

# 3. Save PID
echo $! > sentinel.pid
echo "✅ Sentinel running in background (PID: $!)."
echo "📜 Logs: tail -f sentinel.log"
