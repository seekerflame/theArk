import json
import time
import hashlib

def register_exodus_routes(router, ledger, identity, requires_auth):
    
    @router.post('/api/exodus/verify')
    @requires_auth
    def h_verify_world_id(h, user, payload):
        """
        Receives World ID proof and issues a Liberation Grant (AT).
        The proof is verified (mocked for now), and a pseudonym is stored
        to prevent double-claiming without storing the biometric hash itself.
        """
        proof = payload.get('proof')
        nullifier_hash = payload.get('nullifier_hash') # World ID unique user ID (pseudonym)

        if not proof or not nullifier_hash:
            return h.send_json_error("Missing World ID proof or nullifier hash")

        # 1. Verify "Exodus" status (Check if already claimed)
        for b in ledger.blocks:
            if b['type'] == 'EXODUS_GRANT' and b['data'].get('nullifier_hash') == nullifier_hash:
                return h.send_json_error("Exodus Grant already claimed for this World ID", status=403)

        # 2. Check "Exodus Wave" Status (Timed 'Nuke' Strategy)
        # Waves are stored in the ledger as 'EXODUS_WAVE_CONFIG'
        current_wave = 1
        wave_config = None
        for b in ledger.blocks:
            if b['type'] == 'EXODUS_WAVE_CONFIG':
                wave_config = b['data']
        
        if not wave_config or not wave_config.get('active', False):
             return h.send_json_error("Project Exodus is in MENTAL phase. Enrollment is pending activation signal.")

        # 3. Mock Verification of World ID Proof
        # In production, this would call Worldcoin's verification API
        is_valid = _mock_verify_world_id(proof, nullifier_hash)
        
        if not is_valid:
            return h.send_json_error("Invalid World ID proof")

        # 4. Issue Liberation Grant (AT)
        grant_amount = wave_config.get('grant_amount', 100.0)
        grant_data = {
            "nullifier_hash": nullifier_hash,
            "recipient": user['username'],
            "amount": grant_amount,
            "timestamp": time.time(),
            "wave": wave_config.get('wave_id', 1),
            "memo": f"Project Exodus: Wave {wave_config.get('wave_id', 1)} Liberation"
        }

        # 5. Record to Ledger
        ledger.add_block('EXODUS_GRANT', grant_data)
        
        labor_data = {
            "minter": user['username'],
            "task": "Exodus Migration Grant",
            "hours": grant_amount / 10.0,
            "timestamp": time.time(),
            "verifier": "SYSTEM_EXODUS_ORACLE"
        }
        ledger.add_block('LABOR', labor_data)

        h.send_json({
            "status": "success",
            "message": f"Liberation Grant issued. {grant_amount} AT added to your balance.",
            "grant_id": hashlib.sha256(nullifier_hash.encode()).hexdigest()[:12]
        })

def _mock_verify_world_id(proof, nullifier_hash):
    """
    Placeholder for World ID SDK verification.
    For the MVP, we assume the proof is valid if it's longer than 32 chars.
    """
    return len(proof) > 32 and len(nullifier_hash) > 32
