import hashlib
import time

class SovereignPassport:
    """
    Sovereign Passport (Anti-Worldcoin).
    Decentralized Proof of Personhood via Peer-Attestation.
    Zero Biometrics. 100% Cryptographic.
    """
    def __init__(self, ledger, identity_manager):
        self.ledger = ledger
        self.identity = identity_manager

    def request_passport(self, username):
        """
        Starts the attestation process.
        Requires 3 existing Sovereign Citizens to sign off.
        """
        passport_req = {
            "username": username,
            "status": "PENDING_ATTESTATION",
            "approvals": [],
            "timestamp": time.time()
        }
        
        # Check if already exists
        if self.get_passport(username):
             return {"status": "error", "message": "Passport already exists or pending."}

        self.ledger.add_block('PASSPORT_REQUEST', passport_req)
        return {"status": "success", "message": "Passport request initiated. Seek 3 attestations."}

    def attest_citizen(self, verifier_username, target_username):
        """
        A Sovereign Citizen vouches for a new user.
        """
        # 1. Verify verifier has a valid passport
        if not self.is_sovereign(verifier_username):
            return {"status": "error", "message": "Verifier must have a Sovereign Passport."}

        # 2. Add attestation to the record
        attest_data = {
            "target": target_username,
            "verifier": verifier_username,
            "timestamp": time.time()
        }
        
        self.ledger.add_block('PASSPORT_ATTESTATION', attest_data)
        
        # 3. Check for completion (3 approvals)
        approvals = [b for b in self.ledger.blocks if b['type'] == 'PASSPORT_ATTESTATION' and b['data']['target'] == target_username]
        
        if len(approvals) >= 3:
            passport_id = hashlib.sha256(f"{target_username}:{time.time()}".encode()).hexdigest()[:16]
            self.ledger.add_block('SOVEREIGN_PASSPORT', {
                "username": target_username,
                "passport_id": f"SOV-{passport_id.upper()}",
                "level": "CITIZEN",
                "issued_at": time.time()
            })
            return {"status": "success", "message": "Sovereign Passport ISSUED."}

        return {"status": "success", "message": f"Attestation recorded ({len(approvals)}/3)."}

    def get_passport(self, username):
        for b in reversed(self.ledger.blocks):
            if b['type'] == 'SOVEREIGN_PASSPORT' and b['data']['username'] == username:
                return b['data']
        return None

    def is_sovereign(self, username):
        return self.get_passport(username) is not None
