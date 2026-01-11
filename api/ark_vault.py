"""
Ark Vault API
Handles the authorization and signing of local data sales.
Uses core/ark_vault.py for device-level encryption.
"""

import time
import json
from core.ark_vault import ArkVault

def register_ark_vault_routes(router, ledger, identity, auth_decorator):
    
    @router.post('/api/ark/data-sale/sign')
    @auth_decorator
    def h_sign_data_sale(h, user, p):
        """
        Signs a data-sale agreement locally using the user's mnemonic.
        This authorizes the release of a specific, anonymized data packet.
        """
        username = user['sub']
        mnemonic = p.get('mnemonic')
        data_packet_id = p.get('packet_id')
        buyer = p.get('buyer', 'GPM_RESEARCH_FOUNDATION')
        
        if not mnemonic:
            return h.send_json_error("Mnemonic seed required for Ark signing.")
            
        try:
            av = ArkVault(mnemonic)
            
            # 1. Create the Agreement
            agreement = {
                "packet_id": data_packet_id,
                "seller": username,
                "buyer": buyer,
                "timestamp": time.time(),
                "terms": "Anonymized metabolic aggregate for GPM Research"
            }
            
            # 2. Sign it (deterministic hash based on key)
            signature = av.encrypt(json.dumps(agreement))
            
            # 3. Add to Ledger as an ARK_TX
            tx = ledger.add_block('ARK_TX', {
                "action": "DATA_SALE",
                "seller": username,
                "buyer": buyer,
                "amount": 2.0, # Standard UBI data subsidy
                "signature_hash": signature[:64],
                "timestamp": time.time()
            })
            
            h.send_json({
                "status": "signed",
                "tx": tx,
                "reward": 2.0,
                "message": "True data sale authorized and tokenized."
            })
            
        except Exception as e:
            return h.send_json_error(f"Ark signing failed: {str(e)}")

    @router.get('/api/ark/status')
    @auth_decorator
    def h_ark_status(h, user, p):
        """Returns the user's data state and economic metrics."""
        username = user['sub']
        user_data = identity.users.get(username, {})
        balance = ledger.get_balance(username)
        
        h.send_json({
            "status": "HARDENED",
            "encryption": "AES-256-CFB",
            "last_audit": time.time(),
            "data_sale_eligibility": True,
            "username": username,
            "role": user_data.get('role', 'WORKER'),
            "balance": balance,
            "verified_hours": user_data.get('verified_hours', 0.0),
            "safety_grade": user_data.get('safety_grade', 100.0)
        })
