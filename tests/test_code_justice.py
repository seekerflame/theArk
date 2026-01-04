import pytest
import sys
import os

# Add the project root to sys.path
sys.path.append(os.path.join(os.getcwd()))

from core.ledger import VillageLedger
from core.identity import IdentityManager
from core.justice import JusticeSteward

@pytest.fixture
def justice_env(tmp_path):
    db_file = tmp_path / "test_village.db"
    users_file = tmp_path / "test_users.json"
    
    # Create a dummy users.json
    with open(users_file, "w") as f:
        f.write("{}")
        
    ledger = VillageLedger(str(db_file))
    identity = IdentityManager(str(users_file), "test_secret")
    justice = JusticeSteward(ledger, identity)
    
    # Add a test user
    identity.users["jules"] = {"name": "Jules", "roles": ["WORKER"], "safety_grade": 100.0}
    identity.save()
    
    return justice, identity

def test_audit_bs_code(justice_env):
    justice, _ = justice_env
    
    # Diff with only comments
    bs_diff = """
    # This is a comment
    # Another comment
    // Still just comments
    # No logic here
    """
    
    # Try auditing with 5 lines of comments
    is_valid, score, reason = justice.audit_code_contribution("jules", 5, bs_diff)
    
    assert is_valid is False
    assert "Low value density" in reason
    assert score < 0.2

def test_audit_legit_code(justice_env):
    justice, _ = justice_env
    
    # Diff with actual logic
    legit_diff = """
    import os
    def hello_world():
        print("Hello")
        x = 1 + 2
        return x
    """
    
    # Try auditing legit code
    is_valid, score, reason = justice.audit_code_contribution("jules", 6, legit_diff)
    
    assert is_valid is True
    assert score > 0.5
    assert "Logic audit passed" in reason

def test_audit_large_diff_rejection(justice_env):
    justice, _ = justice_env
    
    # Try a massive diff count
    is_valid, score, reason = justice.audit_code_contribution("jules", 6000, None)
    
    assert is_valid is False
    assert "Massive diff rejected" in reason

def test_reputation_penalty(justice_env):
    justice, identity = justice_env
    
    # Create a "bad" user
    identity.users["hacker"] = {"name": "Hacker", "safety_grade": 40.0}
    identity.save()
    
    legit_diff = "x = 10\ny = 20\nz = x + y"
    
    # Audit legit code for the "bad" user
    is_valid, score, reason = justice.audit_code_contribution("hacker", 3, legit_diff)
    
    # For a flagged user, the score should be halved. 
    # Logic density here is high (1.0), so score should be around 0.5
    assert is_valid is True
    assert score < 0.6 
