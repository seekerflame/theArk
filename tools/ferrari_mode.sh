#!/bin/bash
# Keep Ollama Alive & Looping
# "Get Ollama to be running like a Ferrari"

echo "🏎️  Starting Ollama Imagination Turbo Loop..."

# 1. Ensure Ollama is running
if ! pgrep -x "ollama" > /dev/null
then
    echo "⚠️  Ollama not running. Starting..."
    ollama serve > ollama.log 2>&1 &
    sleep 5
fi

# 2. Infinite Loop: Imagine -> Post -> Sleep -> Repeat
while true
do
    echo "🧠 Imagining..."
    python3 tools/imagination_loop.py
    
    # 3. Check if server is healthy
    if curl -s http://localhost:3000/api/health > /dev/null
    then
        echo "✅ Health Check: OK"
    else
        echo "⚠️  Ark Server Down! Restarting..."
        pkill -f "python3 server.py"
        python3 server.py > server.log 2>&1 &
    fi
    
    echo "💤 Sleeping 60s..."
    sleep 60
done
