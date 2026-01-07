"""
Economy API - The Central Nervous System of Ark OS
Handles Minting, Roles, Quests, and Verification.
"""

import time
import json
import logging

def register_economy_routes(router, ledger, sensors, identity, justice, requires_auth, quest_system, verification):
    logger = logging.getLogger("ArkOS.Economy")

    # === MINTING (Labor -> AT) ===
    
    @router.post('/api/mint')
    @requires_auth
    def h_mint(h, user, p):
        """Mint AT for verified labor."""
        amount = float(p.get('amount', 0))
        memo = p.get('memo', 'Labor')
        
        # Rate limit / Sanity check
        if amount > 100:
            return h.send_json_error("Mint limit exceeded (Max 100/tx)")
            
        # Create block
        block = {
            "action": "MINT",
            "amount": amount,
            "minter": user['sub'],
            "memo": memo,
            "timestamp": time.time()
        }
        
        # Verify with Justice (Holistic Multiplier)
        audit_score = justice.get_user_score(user['sub'])
        final_amount = amount * audit_score
        block['final_amount'] = final_amount
        block['audit_score'] = audit_score
        
        tx = ledger.add_block('MINT', block)
        h.send_json({"status": "minted", "tx": tx, "amount": final_amount})

    # === TRANSFERS (P2P) ===

    @router.post('/api/transfer')
    @requires_auth
    def h_transfer(h, user, p):
        """Send AT to another user."""
        recipient = p.get('to')
        amount = float(p.get('amount', 0))
        memo = p.get('memo', '')
        
        if amount <= 0: return h.send_json_error("Invalid amount")
        
        balance = ledger.get_balance(user['sub'])
        if balance < amount:
            return h.send_json_error("Insufficient funds")
            
        tx = ledger.add_block('TX', {
            "sender": user['sub'],
            "receiver": recipient,
            "amount": amount,
            "memo": memo,
            "timestamp": time.time()
        })
        
        h.send_json({"status": "sent", "tx": tx})

    # === ROLES & MULTIPLIERS ===

    @router.get('/api/roles/certify')
    @requires_auth
    def h_certify_role(h, user, p):
        """Oracle certifies a user for a role."""
        # 1. Check if requester is Oracle
        if not identity.has_role(user['sub'], 'ORACLE'):
            return h.send_json_error("Only Oracles can certify roles", status=403)
            
        target_user = p.get('user_id')
        role = p.get('role')
        
        ledger.add_block('ROLE_GRANT', {
            "oracle": user['sub'],
            "target": target_user,
            "role": role,
            "timestamp": time.time()
        })
        
        h.send_json({"status": "certified", "role": role})

    # === QUESTS ===

    @router.get('/api/quests/available')
    def h_quests_list(h):
        """Get open quests."""
        quests = quest_system.get_open_quests()
        h.send_json({"quests": quests})

    @router.post('/api/quests/claim')
    @requires_auth
    def h_quest_claim(h, user, p):
        """Claim a quest."""
        quest_id = p.get('quest_id')
        success, msg = quest_system.claim_quest(quest_id, user['sub'])
        if success:
            h.send_json({"status": "claimed"})
        else:
            h.send_json_error(msg)
            
    # === VERIFICATION (The Pyramid) ===
    
    @router.post('/api/verification/request')
    @requires_auth
    def h_verify_req(h, user, p):
        """Request 3 verifiers for a completed task."""
        task_id = p.get('task_id')
        evidence = p.get('evidence_link')
        
        req_id = verification.request_verification(user['sub'], task_id, evidence)
        h.send_json({"status": "requested", "request_id": req_id})
        
    @router.get('/api/verification/pending')
    @requires_auth
    def h_verify_pending(h, user, p):
        """Get tasks needing verification (for Oracles/Verifiers)."""
        tasks = verification.get_pending_for_user(user['sub'])
        h.send_json({"tasks": tasks})
        
    @router.post('/api/verification/submit')
    @requires_auth
    def h_verify_submit(h, user, p):
        """Submit a verification decision."""
        req_id = p.get('request_id')
        decision = p.get('decision') # approve/reject
        notes = p.get('notes', '')
        
        success = verification.submit_verification(user['sub'], req_id, decision, notes)
        if success:
            h.send_json({"status": "submitted"})
        else:
            h.send_json_error("Verification failed (already verified or invalid)")
