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

    @router.get('/api/economy/ppp')
    def h_ppp(h):
        """Get current Purchasing Power Parity (PPP) metrics."""
        # Baseline: 1960 Silver Standard (5 Silver Quarters for 8 hours)
        # 1 AT target = ~$70 USD (2026 inflation-adjusted)
        # This is a dynamic metric used for the Admin Deck
        ppp_data = {
            "target_unit_value_usd": 70.0,
            "parity_standard": "1960 Silver Standard",
            "daily_labor_parity_usd": 560.0,
            "labor_density_index": 1.0, # Target 1.0
            "fiat_dilution_factor": 8.0, # How much more an hour SHOULD be worth vs fiat current
            "timestamp": time.time()
        }
        h.send_json(ppp_data)

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

    # === ANTI-GRIFT (Vibe Check) ===

    def _vibe_check(user_id):
        """
        Verify if knowledge (XP) aligns with real-world action (Labor).
        Prevents AI farming of levels without physical output.
        """
        user_data = identity.get_user(user_id)
        xp = user_data.get('xp', 0)
        verified_hours = user_data.get('verified_hours', 0)
        
        # Heuristic: 1 hour labor should roughly equal 100 XP worth of learning
        # If XP is 10x higher than labor-equivalent, trigger a 'Deep Research' audit
        if xp > (verified_hours * 100) + 1000: # Grant 1000 XP grace for newcomers
            logger.warning(f"⚠️  User {user_id} triggered Anti-Grift: XP({xp}) >> Labor({verified_hours})")
            return 0.5 # Slashing multiplier for being "all talk, no action"
        return 1.0

    @router.post('/api/economy/focus/start')
    @requires_auth
    def h_focus_start(h, user, p):
        """Initialize a focus session."""
        session_id = f"focus_{user['sub']}_{int(time.time())}"
        focus_sessions[session_id] = {
            "user": user['sub'],
            "start_time": time.time(),
            "entropy_challenge": os.urandom(8).hex() # Proof-of-Attention seed
        }
        h.send_json({"status": "started", "session_id": session_id, "challenge": focus_sessions[session_id]['entropy_challenge']})

    @router.post('/api/economy/focus/claim')
    @requires_auth
    def h_focus_claim(h, user, p):
        """Claim AT for completed focus session."""
        session_id = p.get('session_id')
        session = focus_sessions.get(session_id)
        
        if not session or session['user'] != user['sub']:
            return h.send_json_error("Invalid session")
            
        duration = time.time() - session['start_time']
        
        # Minimum 60 minutes (3600 seconds)
        MIN_DURATION = 3600 
        if Config.get('ENVIRONMENT') == 'development':
            MIN_DURATION = 10
            
        if duration < MIN_DURATION:
            return h.send_json_error(f"Incomplete session. Remaining: {int((MIN_DURATION - duration)/60)}m")
            
        # Anti-Grift Multiplier
        multiplier = _vibe_check(user['sub'])
        final_mint = 1.0 * multiplier
        
        # Mint AT
        tx = ledger.add_block('MINT', {
            "action": "FOCUS_MINT",
            "amount": final_mint,
            "minter": user['sub'],
            "memo": f"Deep Focus Session (Efficiency: {int(multiplier*100)}%)",
            "duration_sec": duration,
            "timestamp": time.time()
        })
        
        # Reward XP for the attention
        identity.add_xp(user['sub'], 50) # Focus = 50 XP
        
        del focus_sessions[session_id]
        h.send_json({"status": "minted", "tx": tx, "amount": final_mint, "multiplier": multiplier})
