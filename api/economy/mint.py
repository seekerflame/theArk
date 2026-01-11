import time

def register_mint_routes(router, ledger, identity, justice, requires_auth):

    @router.post('/api/mint')
    @requires_auth
    def h_mint(h, user, p):
        data = p.get('data', p)
        data['minter'] = user['sub']
        data['timestamp'] = time.time()
        
        # Apply Holistic Multiplier
        role = p.get('role', 'WORKER')
        hours = float(p.get('hours', 0))
        hm = identity.get_holistic_multiplier(user['sub'], role, ledger)
        
        reward = hours * 10 * hm
        data['reward'] = reward
        data['hm_applied'] = hm
        
        block_hash = ledger.add_block('LABOR', data)
        if block_hash: 
            identity.add_verified_hours(user['sub'], hours) # Progress tiers
            h.send_json({"hash": block_hash, "reward": reward, "hm": hm})
        else: h.send_json_error("Failed to mint block")

    @router.post('/api/mint/code')
    @requires_auth
    def h_mint_code(h, user, p):
        """Mint AT for code contributions. Audited by JusticeSteward."""
        BASE_RATE = 0.1  # AT per line changed
        COMPLEXITY = {
            'trivial': 0.5,
            'standard': 1.0,
            'complex': 2.0,
            'expert': 3.0
        }
        
        lines = p.get('lines_changed', 0)
        complexity_level = p.get('complexity', 'standard')
        pr_url = p.get('pr_url', '')
        commit_hash = p.get('commit_hash', '')
        diff_content = p.get('diff', None) # Optional but recommended for audit
        
        # 1. Justice Audit
        is_valid, score, reason = justice.audit_code_contribution(user['sub'], lines, diff_content)
        if not is_valid:
            return h.send_json_error(f"Justice Audit Failed: {reason} (Score: {score:.2f})")
        
        # 2. Reward Calculation with HM Integration
        multiplier = COMPLEXITY.get(complexity_level, 1.0)
        hm = identity.get_holistic_multiplier(user['sub'], 'CODE_MINT', ledger)
        
        reward = max(1, lines * BASE_RATE * multiplier * score * hm)
        
        data = {
            'minter': user['sub'],
            'lines_changed': lines,
            'complexity': complexity_level,
            'reward': reward,
            'audit_score': score,
            'hm_applied': hm,
            'pr_url': pr_url,
            'commit_hash': commit_hash,
            'timestamp': time.time()
        }
        
        block_hash = ledger.add_block('CODE_MINT', data)
        if block_hash: 
            # Code work also counts towards tiers (100 lines = 1h simulation)
            identity.add_verified_hours(user['sub'], lines / 100.0)
            h.send_json({"hash": block_hash, "reward": reward, "audit_score": score, "hm": hm})
        else: 
            h.send_json_error("Failed to mint code block")

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
        if xp > (verified_hours * 100) + 1000:
            return 0.5 # Slashing multiplier for "all talk, no action"
        return 1.0

    @router.post('/api/economy/focus/start')
    @requires_auth
    def h_focus_start(h, user, p):
        """Initialize a focus session."""
        import os
        session_id = f"focus_{user['sub']}_{int(time.time())}"
        h.send_json({
            "status": "started", 
            "session_id": session_id, 
            "challenge": os.urandom(8).hex()
        })

    @router.post('/api/economy/focus/claim')
    @requires_auth
    def h_focus_claim(h, user, p):
        """Claim AT for completed focus session."""
        duration = float(p.get('duration_sec', 0))
        if duration < 300: # 5 min minimum for demo
            return h.send_json_error("Incomplete session.")
            
        multiplier = _vibe_check(user['sub'])
        final_mint = 1.0 * multiplier
        
        tx = ledger.add_block('MINT', {
            "action": "FOCUS_MINT",
            "amount": final_mint,
            "minter": user['sub'],
            "memo": "Deep Focus Session",
            "timestamp": time.time()
        })
        
        identity.add_xp(user['sub'], 50)
        h.send_json({"status": "minted", "tx": tx, "amount": final_mint})

    # === MISSION ESCROW (Oracle-led Funding) ===

    @router.post('/api/economy/mission/escrow')
    @requires_auth
    def h_mint_escrow(h, user, p):
        """Oracle mints AT directly into a mission escrow."""
        if not identity.has_role(user['sub'], 'ORACLE'):
            return h.send_json_error("Oracle level access required", status=403)
            
        title = p.get('title')
        amount = float(p.get('amount', 0))
        
        if not title or amount <= 0:
            return h.send_json_error("Title and positive amount required")
            
        tx = ledger.add_block('MISSION_ESCROW', {
            "title": title,
            "amount": amount,
            "funder": user['sub'],
            "timestamp": time.time()
        })
        
        h.send_json({"status": "mission_funded", "tx": tx, "amount": amount})
