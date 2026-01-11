import pytest
import os
from pathlib import Path
from federation.file_bridge import FileBridge
from core.ledger import VillageLedger

@pytest.fixture
def temp_env(tmp_path):
    ledger_file = tmp_path / "test_ledger.db"
    return VillageLedger(str(ledger_file)), tmp_path

def test_file_registration(temp_env):
    ledger, tmp_path = temp_env
    bridge = FileBridge(ledger)
    
    # Create a dummy file
    test_file = tmp_path / "test_artifact.txt"
    test_file.write_text("Sovereign data content")
    
    # Register it
    file_hash = bridge.register_file(str(test_file))
    
    assert file_hash is not None
    assert file_hash in bridge.manifest
    
    # Check ledger for announcement
    announcements = [b for b in ledger.blocks if b["type"] == "FILE_ANNOUNCEMENT"]
    assert len(announcements) == 1
    assert announcements[0]["data"]["hash"] == file_hash
    assert announcements[0]["data"]["name"] == "test_artifact.txt"

def test_config_paths():
    from core.config import BASE_DIR, STORAGE_DIR
    assert BASE_DIR.name == "The_Ark"
    assert STORAGE_DIR.exists()
