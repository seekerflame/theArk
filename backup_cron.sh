#!/bin/bash
# Cron job for automated backups
# Add to crontab: 0 * * * * /path/to/backup_cron.sh

cd "$(dirname "$0")"

# Run backup
python3 backup_ledger.py >> backup.log 2>&1

# Sync to remote (if configured)
# rsync -avz village_ledger_py.json user@backup-server:/backups/

echo "[$(date)] Backup complete" >> backup.log
