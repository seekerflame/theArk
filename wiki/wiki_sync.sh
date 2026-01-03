#!/bin/bash
# Wrapper to run wiki_sync.py from the correct directory
cd "$(dirname "$0")"

# Check if Python is available
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

echo "🔄 executing wiki_sync.py..."
$PYTHON_CMD wiki_sync.py "$@"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ Wiki Sync Success"
else
    echo "❌ Wiki Sync Failed (Exit Code: $EXIT_CODE)"
fi

exit $EXIT_CODE
