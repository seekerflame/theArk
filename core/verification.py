import time
import json
import hashlib
from typing import Dict, List, Tuple

class ProofOfPhysics:
    """
    Verification Engine for the Value Delta.
    Ensures Physical Value exists before minting High-Density AT.
    """
    
    def __init__(self, ledger):
        self.ledger = ledger
        self.pending_claims = {} # claim_id -> verification data
        
    def submit_value_claim(self, user: str, manifest: Dict) -> str:
        """
        Submit a claim for value produced (e.g., "Built 1 SEH Wall").
        
        manifest:
            type: str (SEH, FOOD, POWER)
            value_delta_usd: float
            sensor_payload: dict (GPS, Video Hash, IoT logs)
            witnesses: list (Peer Node IDs)
        """
        claim_id = hashlib.sha256(f"{user}{time.time()}".encode()).hexdigest()[:12]
        
        self.pending_claims[claim_id] = {
            "user": user,
            "manifest": manifest,
            "signatures": [],
            "sensor_verified": False,
            "timestamp": time.time(),
            "status": "AWAITING_PHYSICS"
        }
        
        return claim_id

    def verify_sensor_payload(self, claim_id: str, hardware_signature: str) -> bool:
        """
        Validate sensor data from the Hardware Bridge (IoT sensors).
        """
        if claim_id not in self.pending_claims:
            return False
            
        # mock validation: In production, checks hardware key and data consistency
        print(f"[PoP] Verifying Hardware Payload for {claim_id}...")
        self.pending_claims[claim_id]["sensor_verified"] = True
        return True

    def toggle_peer_signature(self, claim_id: str, peer_id: str) -> bool:
        """
        Add a peer signature (Dunbar Witness).
        """
        if claim_id not in self.pending_claims:
            return False
            
        claim = self.pending_claims[claim_id]
        if peer_id not in claim["signatures"]:
            claim["signatures"].append(peer_id)
            
        # Check for consensus (3 signatures standard for small nodes)
        if len(claim["signatures"]) >= 3 and claim["sensor_verified"]:
            claim["status"] = "VERIFIED_PHYSICS"
            return True
            
        return False

    def finalize_verification(self, claim_id: str) -> Tuple[bool, float]:
        """
        Finalize and return the validated AT amount to mint.
        """
        if claim_id not in self.pending_claims:
            return False, 0.0
            
        claim = self.pending_claims[claim_id]
        if claim["status"] == "VERIFIED_PHYSICS":
            # 1 AT = $70. If value produced = $700, mint 10 AT.
            at_to_mint = claim["manifest"]["value_delta_usd"] / 70.0
            return True, at_to_mint
            
        return False, 0.0

# Protocol Integration
if __name__ == "__main__":
    pop = ProofOfPhysics(ledger=None)
    cid = pop.submit_value_claim("User123", {
        "type": "SEH_BUILD",
        "value_delta_usd": 700.0,
        "witnesses": ["PeerA", "PeerB", "PeerC"]
    })
    
    pop.verify_sensor_payload(cid, "HW_SIGNED_7788")
    pop.toggle_peer_signature(cid, "PeerA")
    pop.toggle_peer_signature(cid, "PeerB")
    pop.toggle_peer_signature(cid, "PeerC")
    
    success, amount = pop.finalize_verification(cid)
    print(f"Verification Success: {success} | Minted: {amount} AT")
