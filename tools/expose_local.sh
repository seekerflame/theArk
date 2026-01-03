#!/bin/bash

# expose_local.sh - Civilization OS Global Exposure Tool
# A wrapper for cloudflared and ngrok to quickly share the Ark.

PORT=3000
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}🌍 Civilization OS: Global Exposure Tool${NC}"
echo "----------------------------------------"

# 1. Check for Cloudflared (Preferred)
if command -v cloudflared &> /dev/null; then
    echo "Found cloudflared. Starting tunnel..."
    cloudflared tunnel --url http://localhost:$PORT
    exit 0
fi

# 2. Check for Ngrok (Fallback)
if command -v ngrok &> /dev/null; then
    echo "Found ngrok. Starting portal..."
    ngrok http $PORT
    exit 0
fi

# 3. Instruction if none found
echo -e "${RED}Error: Neither 'cloudflared' nor 'ngrok' was found.${NC}"
echo ""
echo "To share your site, we recommend installing Cloudflare Tunnels:"
echo "  brew install cloudflared"
echo ""
echo "Or Ngrok:"
echo "  brew install ngrok"
echo ""
echo "Please refer to the Global_Access_Guide.md for detailed setup instructions."
