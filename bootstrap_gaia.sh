#!/bin/bash
# Bootstrap GAIA NEXUS - Complete AI activation

echo "🌌 GAIA NEXUS ACTIVATION SEQUENCE"
echo "=================================="
echo ""

# Set environment
export ARK_API_URL="http://localhost:3000"
export AI_USERNAME="antigravity_ai"

# Generate a simple token for testing (in production, use real auth)
export AI_AGENT_TOKEN="gaia_nexus_bootstrap_token_$(date +%s)"

echo "📝 Configuration:"
echo "   ARK_API_URL: $ARK_API_URL"
echo "   AI_USERNAME: $AI_USERNAME"
echo ""

# Test server connectivity
echo "🔍 Testing server connectivity..."
if curl -s http://localhost:3000/api/health > /dev/null; then
    echo "✅ Server is reachable"
else
    echo "❌ Server not reachable!"
    echo "💡 Start the server first: python3 server.py"
    exit 1
fi

echo ""
echo "🧠 Testing AI Memory System..."
# Test AI endpoints
if curl -s http://localhost:3000/api/ai/patterns > /dev/null 2>&1; then
    echo "✅ AI Memory API is active"
else
    echo "⚠️  AI Memory API not found (server may need restart)"
fi

echo ""
echo "🚀 Running first autonomous cycle..."
echo ""

# Run AI orchestrator
python3 ai_orchestrator.py

echo ""
echo "=================================="
echo "✅ GAIA NEXUS ACTIVATION COMPLETE"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Deploy to Render for 24/7 operation"
echo "2. Import n8n workflow for 6-hour cycles"
echo "3. Watch AI earn its first AT"
echo ""
echo "The future is autonomous. 🌌"
