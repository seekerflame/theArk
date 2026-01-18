#!/bin/bash
# OSE Session Snapshot Script

PROJECT_ROOT="/Volumes/Extreme SSD/Antigrav/OSE"
CHRONICLE_DIR="$PROJECT_ROOT/CHRONICLE"
SESSION_DATE=$(date +"%Y%m%d_%H%M%S")

echo "--- OSE CHRONICLE SNAPSHOT ---"
echo "Session Date: $SESSION_DATE"

# Ask for Session ID or Task Summary if possible, otherwise use date
TASK_SUMMARY=$1
if [ -z "$TASK_SUMMARY" ]; then
    TASK_SUMMARY="Automated Session Snapshot"
fi

# Add changes in CHRONICLE and root documentation
git -C "$PROJECT_ROOT" add "$CHRONICLE_DIR"
git -C "$PROJECT_ROOT" add "$PROJECT_ROOT/*.md"

# Commit if there are changes
if ! git -C "$PROJECT_ROOT" diff --cached --quiet; then
    git -C "$PROJECT_ROOT" commit -m "CHRONICLE: $TASK_SUMMARY [$SESSION_DATE]"
    echo "✅ Snapshot created and committed."
else
    echo "📭 No changes detected in CHRONICLE or root documentation."
fi
