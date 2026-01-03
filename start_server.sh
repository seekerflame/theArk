#!/bin/bash
cd "$(dirname "$0")"
echo "Starting server at $(date)" > startup.log
echo "Current directory: $(pwd)" >> startup.log
echo "Python version: $(python3 --version 2>&1)" >> startup.log

# Kill existing
pkill -f "python3 server.py" || echo "No process found" >> startup.log

# Start
nohup python3 -u server.py > server.log 2>&1 &
PID=$!
echo "Server started with PID $PID" >> startup.log
