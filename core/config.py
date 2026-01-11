import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
LIBRARY_DIR = BASE_DIR / "library"
CORE_DIR = BASE_DIR / "core"
LEDGER_DIR = BASE_DIR / "ledger"
LOGS_DIR = BASE_DIR / "logs"
WEB_DIR = BASE_DIR / "web"

# Ensure critical directories exist
for d in [LEDGER_DIR, LOGS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Ledger Config
LEDGER_FILE = os.environ.get("ARK_LEDGER_FILE", str(BASE_DIR / "village_ledger_py.json"))
LEDGER_DB = os.environ.get("ARK_LEDGER_DB", str(BASE_DIR / "village_ledger.db"))

# Server Config
PORT = int(os.environ.get("PORT", 3000))
HOST = os.environ.get("HOST", "0.0.0.0")

# Agent Config
AI_AGENT_TOKEN = os.environ.get("AI_AGENT_TOKEN", "")
ARK_API_URL = os.environ.get("ARK_API_URL", f"http://localhost:{PORT}")

# File Sharing Config
STORAGE_DIR = BASE_DIR / "storage"
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
INBOX_DIR = STORAGE_DIR / "inbox"
INBOX_DIR.mkdir(parents=True, exist_ok=True)
