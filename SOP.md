# 🛠️ Standard Operating Procedures (SOP)

> **"Systems save you. Procedures protect you."**

## 1. System Maintenance

### 1.1 Daily Health Check
1.  **Check API Health**: `curl http://localhost:3000/api/health`
2.  **Verify Ledger Sync**: `curl http://localhost:3000/api/state`
3.  **Monitor Sensors**: Check `http://localhost:3000/api/hardware/list` for STALE sensors.

### 1.2 Backups
*   **Ledger**: `cp ledger/village_ledger.db backups/ledger_$(date +%F).db`
*   **Identity**: `cp core/users.json backups/users_$(date +%F).json`
*   **Frequency**: Automated daily at 03:00 UTC.

## 2. Emergency Protocols

### 2.1 Power Failure
1.  **Hardware Bridge**: The bridge will auto-restart when power is restored.
2.  **Server**: Run `python3 server.py` manually if auto-start fails.
3.  **Data Integrity**: Run `sqlite3 ledger/village_ledger.db "PRAGMA integrity_check;"` to verify DB health.

### 2.2 Security Breach (Physical)
1.  **Trigger**: `SECURITY` sensor detects unauthorized motion in protected zones.
2.  **Action**:
    *   System logs event to ledger (`HARDWARE_PROOF`).
    *   Notification sent to admin (future feature).
    *   Activate lockout mode (future feature).

### 2.3 Economic Anomaly
1.  **Trigger**: Unusual minting volume or massive transfers.
2.  **Action**:
    *   Review `core/ledger.py` logs.
    *   Freeze minting endpoint via environment variable `ARK_MINT_FREEZE=1` (to be implemented).

## 3. Development Standards

*   **Code Style**: Python PEP8.
*   **Testing**: All core changes must be verified with `pytest tests/`.
*   **AI Collaboration**: Follow `AI_COLLABORATION_GUIDE.md` for multi-agent changes.
