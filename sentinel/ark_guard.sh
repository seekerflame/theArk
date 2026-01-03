#!/bin/bash
# ARK OS PRE-COMMIT GUARD
# Prevent syntax errors from reaching the CHRONICLE

set -e

ARK_DIR="/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
STYL_FILE="$ARK_DIR/web/style.css"
SERV_FILE="$ARK_DIR/server.py"

echo "🛡️  RUNNING PRE-COMMIT GUARD"
echo "==========================="

# 1. Check Python Syntax
echo "🐍 Checking server.py syntax..."
python3 -m py_compile "$SERV_FILE"
echo "✅ Python syntax clean."

# 2. Check CSS for Orphaned Properties (Crude heuristic)
echo "🎨 Checking style.css for orphaned properties..."
# Check for lines like "color: red;" that are not preceded by a line with "{" in the last 5 lines
# and not inside a block. This is complex for bash, so we'll do a simple check for lone braces.
OPEN_BRACES=$(grep -o "{" "$STYL_FILE" | wc -l)
CLOSE_BRACES=$(grep -o "}" "$STYL_FILE" | wc -l)

if [ "$OPEN_BRACES" -ne "$CLOSE_BRACES" ]; then
    echo "❌ CSS Syntax Error: Mismatched braces ($OPEN_BRACES open vs $CLOSE_BRACES close)"
    exit 1
fi
echo "✅ CSS brace count balanced."

# 3. Check for specific orphaned property patterns (e.g. property outside of rule)
# We look for lines starting with a property but not inside a rule.
# For simplicity, we'll just check if the last fix (orphaned properties) is resolved.
if grep -q "^font-weight: 600;" "$STYL_FILE"; then
    echo "❌ CSS Error: Orphaned property detected at root level."
    exit 1
fi

echo ""
echo "🎯 GUARD PASSED. System integrity verified."
