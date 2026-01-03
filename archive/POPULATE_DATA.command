#!/bin/bash
# Quick script to populate system data

cd "/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"

echo "🔄 Running Wiki Sync..."
python3 wiki_sync.py

echo ""
echo "✅ Data population complete!"
echo ""
echo "Check the status:"
echo "  - Wiki Status: http://localhost:3000/wiki_status.json"
echo "  - Auditor Report: http://localhost:3000/auditor_report.json"
echo "  - Gaia Dashboard: http://localhost:3000/web/gaia.html"
