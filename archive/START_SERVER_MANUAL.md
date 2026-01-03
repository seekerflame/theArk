# Manual Server Start Instructions

## Step 1: Open Terminal

Open Terminal app and navigate to The Ark:
```bash
cd "/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
```

## Step 2: Start Server

```bash
python3 server.py
```

**DO NOT CLOSE THIS TERMINAL WINDOW**

You should see:
```
🐍 Python Village Node active on port 3000
📂 Serving UI from: /path/to/web
```

## Step 3: Open Gaia (New Terminal Window)

Open a NEW terminal window and run:
```bash
open "http://localhost:3000/web/gaia.html"
```

## Step 4: Run Wiki Sync (Optional, in another terminal)

```bash
cd "/Volumes/Extreme SSD/Antigrav/OSE/abundancetoken/07_Code/The_Ark"
python3 wiki_sync.py
```

This will sync your docs to the OSE wiki with your credentials.

## Troubleshooting

### If server.py fails

Check error message. Common issues:

- Port 3000 already in use: `lsof -ti:3000 | xargs kill -9`
- Python not found: Install Python 3 from python.org

### If Wiki Sync fails

Check credentials are embedded in wiki_sync.py (they should be)
