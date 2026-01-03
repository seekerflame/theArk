import pytest
import os
import sqlite3
import json
import time
from core.ledger import VillageLedger

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_ledger.db"
    return str(db_file)

@pytest.fixture
def ledger(temp_db):
    return VillageLedger(temp_db)

def test_init_db(ledger, temp_db):
    assert os.path.exists(temp_db)
    conn = sqlite3.connect(temp_db)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='blocks'")
    assert cursor.fetchone() is not None
    conn.close()

def test_add_block(ledger):
    data = {"sender": "alice", "receiver": "bob", "amount": 10}
    block_hash = ledger.add_block("TX", data)
    assert block_hash is not None
    assert len(ledger.blocks) == 1
    assert ledger.blocks[0]["type"] == "TX"
    assert ledger.blocks[0]["data"] == data
    assert ledger.blocks[0]["hash"] == block_hash

def test_load_blocks(ledger, temp_db):
    data = {"sender": "alice", "receiver": "bob", "amount": 10}
    ledger.add_block("TX", data)

    # Create a new ledger instance pointing to the same DB
    new_ledger = VillageLedger(temp_db)
    assert len(new_ledger.blocks) == 1
    assert new_ledger.blocks[0]["data"] == data

def test_reconcile_block(ledger):
    block_data = {
        "hash": "test_hash_123",
        "type": "TX",
        "timestamp": 1234567890,
        "data": {"sender": "alice", "receiver": "bob", "amount": 5}
    }
    result_hash = ledger.reconcile_block(block_data)
    assert result_hash == "test_hash_123"
    assert len(ledger.blocks) == 1
    assert ledger.blocks[0]["hash"] == "test_hash_123"

def test_reconcile_existing_block(ledger):
    block_data = {
        "hash": "test_hash_123",
        "type": "TX",
        "timestamp": 1234567890,
        "data": {"sender": "alice", "receiver": "bob", "amount": 5}
    }
    ledger.reconcile_block(block_data)

    # Try to reconcile the same block again
    result_hash = ledger.reconcile_block(block_data)
    assert result_hash is False
    assert len(ledger.blocks) == 1

def test_get_balance_tx(ledger):
    ledger.add_block("TX", {"receiver": "alice", "amount": 100})
    ledger.add_block("TX", {"sender": "alice", "receiver": "bob", "amount": 30})

    assert ledger.get_balance("alice") == 70
    assert ledger.get_balance("bob") == 30

def test_get_balance_labor(ledger):
    ledger.add_block("LABOR", {"worker": "alice", "at": 10}) # 'at' is used in code
    ledger.add_block("LABOR", {"worker": "alice", "reward": 5}) # 'reward' is also checked

    assert ledger.get_balance("alice") == 15

def test_get_balance_hardware_proof(ledger):
    ledger.add_block("HARDWARE_PROOF", {"worker": "alice", "reward": 20})
    assert ledger.get_balance("alice") == 20

def test_get_balance_purchase(ledger):
    ledger.add_block("TX", {"receiver": "alice", "amount": 50})
    ledger.add_block("PURCHASE", {"buyer": "alice", "amount": 20, "item": "hoe"})

    assert ledger.get_balance("alice") == 30

def test_get_balance_mixed(ledger):
    ledger.add_block("LABOR", {"worker": "alice", "at": 10})
    ledger.add_block("TX", {"sender": "alice", "receiver": "bob", "amount": 5})
    ledger.add_block("PURCHASE", {"buyer": "alice", "amount": 2, "item": "seeds"})

    assert ledger.get_balance("alice") == 3 # 10 - 5 - 2 = 3

def test_get_bounties(ledger):
    ledger.add_block("BOUNTY", {"title": "Fix fence", "reward": 50})
    ledger.add_block("TX", {"sender": "alice", "receiver": "bob", "amount": 10})
    ledger.add_block("BOUNTY", {"title": "Water plants", "reward": 10})

    bounties = ledger.get_bounties()
    assert len(bounties) == 2
    assert bounties[0]["title"] == "Fix fence"
    assert bounties[1]["title"] == "Water plants"

def test_get_inventory(ledger):
    ledger.add_block("PURCHASE", {"buyer": "alice", "item": "shovel"})
    ledger.add_block("PURCHASE", {"buyer": "bob", "item": "rake"})
    ledger.add_block("PURCHASE", {"buyer": "alice", "item": "gloves"})

    inventory = ledger.get_inventory("alice")
    assert len(inventory) == 2
    assert "shovel" in inventory
    assert "gloves" in inventory
    assert "rake" not in inventory

def test_persistence(ledger, temp_db):
    ledger.add_block("TX", {"receiver": "alice", "amount": 100})

    # Reload from DB
    new_ledger = VillageLedger(temp_db)
    assert new_ledger.get_balance("alice") == 100

def test_get_balance_unknown_user(ledger):
    assert ledger.get_balance("unknown") == 0

def test_add_block_invalid_data(ledger):
    # This is a bit of a stretch since the code doesn't strictly validate types,
    # but let's ensure it handles arbitrary JSON serializable data
    data = {"some": "random", "data": [1, 2, 3]}
    block_hash = ledger.add_block("MISC", data)
    assert block_hash is not None
    assert ledger.blocks[0]["type"] == "MISC"
