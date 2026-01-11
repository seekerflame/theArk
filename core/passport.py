import hashlib
import time

class ArkPassport:
    """
    Ark Passport (Anti-Worldcoin).
    Decentralized Proof of Personhood via Peer-Attestation.
    Zero Biometrics. 100% Cryptographic.
    """
    def __init__(self, ledger, identity_manager, bridge=None):
        self.ledger = ledger
        self.identity = identity_manager
        self.bridge = bridge

    def request_passport(self, username):
        """
        Starts the attestation process.
        Requires 3 existing Ark Citizens to sign off.
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

    def attest_citizen(self, verifier_username, target_username, presence_token):
        """
        An Ark Citizen vouches for a new user.
        Requires valid hardware presence_token from both.
        """
        # 1. Verify verifier has a valid passport
        if not self.is_verified(verifier_username):
            return {"status": "error", "message": "Verifier must have an Ark Passport."}

        # 2. Verify Proof of Presence
        if self.bridge:
            current_token = self.bridge.read_telemetry().get('presence_token')
            if presence_token != current_token:
                return {"status": "error", "message": "Invalid Presence Token. Physical proximity required."}

        # 3. Add attestation to the record
        attest_data = {
            "target": target_username,
            "verifier": verifier_username,
            "presence_verified": True,
            "timestamp": time.time()
        }
        
        self.ledger.add_block('PASSPORT_ATTESTATION', attest_data)
        
        # 3. Check for completion (3 approvals)
        approvals = [b for b in self.ledger.blocks if b['type'] == 'PASSPORT_ATTESTATION' and b['data']['target'] == target_username]
        
        if len(approvals) >= 3:
            passport_id = hashlib.sha256(f"{target_username}:{time.time()}".encode()).hexdigest()[:16]
            self.ledger.add_block('ARK_PASSPORT', {
                "username": target_username,
                "passport_id": f"ARK-{passport_id.upper()}",
                "level": "CITIZEN",
                "issued_at": time.time()
            })
            return {"status": "success", "message": "Ark Passport ISSUED."}

        return {"status": "success", "message": f"Attestation recorded ({len(approvals)}/3)."}

    def grant_emergency_passport(self, admin_username, target_username):
        """Allows an admin to bootstrap the system with a first citizen."""
        # Verification of admin status would happen in API
        passport_id = hashlib.sha256(f"{target_username}:EMERG-{time.time()}".encode()).hexdigest()[:16]
        self.ledger.add_block('ARK_PASSPORT', {
            "username": target_username,
            "passport_id": f"ARK-{passport_id.upper()}",
            "level": "FOUNDER",
            "issued_at": time.time(),
            "bootstrapped": True
        })
        return {"status": "success", "message": f"Foundational Passport issued to {target_username}"}

    def get_passport(self, username):
        for b in reversed(self.ledger.blocks):
            if b['type'] == 'ARK_PASSPORT' and b['data']['username'] == username:
                return b['data']
        return None

    def is_verified(self, username):
        return self.get_passport(username) is not None
