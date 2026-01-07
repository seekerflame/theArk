from core.governance import GovernanceEngine
import json

class MockLedger:
    def __init__(self):
        self.blocks = []
    def add_block(self, b_type, data):
        self.blocks.append({"type": b_type, "data": data})
        return "mock_hash"

class MockIdentity:
    def __init__(self):
        self.users = {}

def test_governance_logic():
    print("🧪 Unit Testing Governance Logic...")
    ledger = MockLedger()
    identity = MockIdentity()
    gov = GovernanceEngine(ledger, identity)
    
    # 1. Test Violence Screening
    clean_text = "I love this community and want to help build the ark."
    allowed, score, reason = gov.screen_content(clean_text)
    assert allowed == True
    print("✅ Clean content allowed")
    
    threat_text = "I'm going to kill everyone who disagrees with me."
    allowed, score, reason = gov.screen_content(threat_text)
    assert allowed == False
    assert "NAP violation" in reason
    print(f"✅ Threat flagged: {reason}")
    
    grey_text = "bomb shoot violence" # 3 keywords, no NAP stems
    allowed, score, reason = gov.screen_content(grey_text)
    assert allowed == False
    assert "High concentration" in reason
    print(f"✅ Grey content flagged: {reason}")
    
    # 2. Test Inverted Incentive
    identity.users["small_oracle"] = {"verified_count": 5}
    identity.users["big_oracle"] = {"verified_count": 500}
    identity.users["god_oracle"] = {"verified_count": 5000}
    
    assert gov.calculate_audit_frequency("small_oracle") == 0.1
    assert gov.calculate_audit_frequency("big_oracle") == 0.9
    assert gov.calculate_audit_frequency("god_oracle") == 1.0
    print("✅ Inverted incentive logic confirmed (Power = Scrutiny)")

if __name__ == "__main__":
    test_governance_logic()
