import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent

class Config:
    @staticmethod
    def get(key, default=None):
        return os.environ.get(key, default)

    @staticmethod
    def get_jwt_key():
        return os.environ.get("JWT_TOKEN_KEY", "dev_only_key_change_in_production")

    # Path Resolution Constants
    LIBRARY_DIR = BASE_DIR / "library"
    CORE_DIR = BASE_DIR / "core"
    LEDGER_DIR = BASE_DIR / "ledger"
    LOGS_DIR = BASE_DIR / "logs"
    WEB_DIR = BASE_DIR / "web"
    STORAGE_DIR = BASE_DIR / "storage"
    INBOX_DIR = STORAGE_DIR / "inbox"

# Ensure critical directories exist
for d in [Config.LEDGER_DIR, Config.LOGS_DIR, Config.STORAGE_DIR, Config.INBOX_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Ledger Config (legacy variables for modules not using class)
LEDGER_FILE = os.environ.get("ARK_LEDGER_FILE", str(BASE_DIR / "village_ledger_py.json"))
LEDGER_DB = os.environ.get("ARK_LEDGER_DB", str(BASE_DIR / "village_ledger.db"))
