#!/bin/bash

# verify_security.sh - Sovereign Security Audit Script
# Part of the Civilization OS / The Ark

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🛡️ Starting Sovereign Security Audit...${NC}"
echo "------------------------------------------"

# 1. Check for Local Data Sovereignty
echo -ne "SEC_01: Checking Sensitive Data Locations... "
if [ -f "secrets.json" ] || [ -f "users.json" ] || [ -f "village_ledger.db" ]; then
    echo -e "${GREEN}PASS${NC} (Stored locally)"
else
    echo -e "${RED}FAIL${NC} (Critical files missing from local directory!)"
fi

# 2. Check for Open Network Ports (Internal Only)
echo -ne "SEC_02: Checking for Publicly Exposed Ports... "
LSOF_OUT=$(lsof -i -P -n | grep LISTEN | grep -v "127.0.0.1" | grep -v "::1")
if [ -z "$LSOF_OUT" ]; then
    echo -e "${GREEN}PASS${NC} (Only listening on localhost)"
else
    echo -e "${RED}WARNING${NC} (Non-local listening ports detected!)"
    echo "$LSOF_OUT"
fi

# 3. Check for External Phoning Home (Simplified)
echo -ne "SEC_03: Checking for Active External Connections... "
NETSTAT_OUT=$(netstat -an | grep ESTABLISHED | grep -v "127.0.0.1")
if [ -z "$NETSTAT_OUT" ]; then
     echo -e "${GREEN}PASS${NC} (No active external connections)"
else
     echo -e "${BLUE}NOTE${NC} (Active external connections found - verify if these are expected, e.g., NetBird/SSH)"
     echo "$NETSTAT_OUT" | head -n 5
fi

# 4. Audit Sentinel Liveness
echo -ne "SEC_04: Verifying Gaia Sentinel Status... "
if pgrep -f "sentinel.py" > /dev/null; then
    echo -e "${GREEN}RUNNING${NC}"
else
    echo -e "${RED}NOT RUNNING${NC} (System watchdog is inactive!)"
fi

echo "------------------------------------------"
echo -e "${BLUE}Audit Complete.${NC} Please review the command logs in your IDE for full agent transparency."
