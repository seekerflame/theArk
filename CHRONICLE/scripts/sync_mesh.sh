#!/bin/bash
# sync_mesh.sh - Autonomous Sync for OSE Federation Nodes
# Usage: ./sync_mesh.sh <REMOTE_USER> <FRIEND_IP> <REMOTE_PATH> [--live]

REMOTE_USER=$1
REMOTE_IP=$2
REMOTE_PATH=$3
LIVE_MODE=$4

if [ -z "$REMOTE_USER" ] || [ -z "$REMOTE_IP" ] || [ -z "$REMOTE_PATH" ]; then
    echo "Usage: ./sync_mesh.sh <REMOTE_USER> <FRIEND_NETBIRD_IP> <REMOTE_OSE_PATH> [--live]"
    exit 1
fi

LOCAL_PATH="/Volumes/Extreme SSD/Antigrav/OSE"
OUTBOX="$LOCAL_PATH/CHRONICLE/MESH_COMMS/outbox.md"
INBOX="$LOCAL_PATH/CHRONICLE/MESH_COMMS/inbox.md"
CLIPBOARD="$LOCAL_PATH/CHRONICLE/MESH_COMMS/CLIPBOARD.md"
SHARED_LOCAL="$LOCAL_PATH/CHRONICLE/SHARED_FILES/"

sync_once() {
    echo "$(date) [+] Synchronizing..."
    
    # 1. Sync Box (Push/Pull)
    scp "$OUTBOX" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/MESH_COMMS/inbox.md" 2>/dev/null
    scp "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/MESH_COMMS/outbox.md" "$INBOX" 2>/dev/null
    
    # 2. Sync Clipboard (Bidirectional Mirror)
    # Note: This is a simple overwrite sync, last save wins
    scp "$CLIPBOARD" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/MESH_COMMS/CLIPBOARD.md" 2>/dev/null
    scp "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/MESH_COMMS/CLIPBOARD.md" "$CLIPBOARD" 2>/dev/null

    # 3. Sync Shared Files (Bidirectional)
    rsync -avz -e ssh "$SHARED_LOCAL" "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/SHARED_FILES/" 2>/dev/null
    rsync -avz -e ssh "$REMOTE_USER@$REMOTE_IP:$REMOTE_PATH/CHRONICLE/SHARED_FILES/" "$SHARED_LOCAL" 2>/dev/null
}

if [ "$LIVE_MODE" == "--live" ]; then
    echo "--- OSE MESH LIVE SYNC ACTIVE (5s Interval) ---"
    while true; do
        sync_once
        sleep 5
    done
else
    sync_once
    echo "--- OSE MESH SYNC COMPLETE ---"
fi
