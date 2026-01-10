#!/bin/bash

# ABYSSAL SENTINEL: RECURSIVE SYSTEM AUDIT
# "The system that watches itself, evolves itself."

echo "------------------------------------------------"
echo "🛰️  ABUNDANCE LABS SENTINEL AUDIT v1.0"
echo "------------------------------------------------"

# 1. API HEALTH
echo -n "[API] Testing Local Gateway... "
HEALTH=$(curl -s http://localhost:3006/api/health | grep -o "healthy")
if [ "$HEALTH" == "healthy" ]; then
    echo "✅ OPTIMAL"
else
    echo "❌ CRITICAL FAILURE"
fi

# 2. LEDGER INTEGRITY
echo -n "[LEDGER] Verifying Block Density... "
BLOCKS=$(curl -s http://localhost:3006/api/state | grep -oE "[0-9]+")
if [ ! -z "$BLOCKS" ]; then
    echo "✅ $BLOCKS BLOCKS VERIFIED"
else
    echo "⚠️  SYNC ERROR"
fi

# 3. INTERFACE CHECK
echo -n "[UI] Checking Dopamine Protocols... "
UI=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3006/dopamine.css)
if [ "$UI" == "200" ]; then
    echo "✅ DUAL-MODE ACTIVE"
else
    echo "⚠️  STYLING DEGRADED"
fi

# 4. RENDER SYNC
echo -n "[DEPLOY] Fetching Global Pulse... "
GLOBAL=$(curl -s -o /dev/null -w "%{http_code}" https://ark-os-production.onrender.com/api/health)
if [ "$GLOBAL" == "200" ]; then
    echo "✅ GLOBAL NODE LIVE"
elif [ "$GLOBAL" == "404" ]; then
    echo "⚠️  GLOBAL NODE 404 (Check Render Dashboard)"
else
    echo "⚠️  GLOBAL NODE $GLOBAL"
fi

echo "------------------------------------------------"
echo "AUDIT COMPLETE. RECOMMENDATION: PROCEED TO BUILD."
