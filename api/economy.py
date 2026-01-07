import time
import json
import os
import random

def register_economy_routes(router, ledger, sensors, identity, justice, requires_auth, quest_system=None, verification=None):

    @router.get('/api/roles/multipliers')
    def h_multipliers(h):
        h.send_json(identity.get_role_multipliers())

        h.send_json({"status": "certified", "user": target_user, "role": role})

    @router.post('/api/roles/certify')
    @requires_auth
    def h_certify_role(h, user, p):
        """Oracle certifies a user for a specific role/skill."""
        if user['role'] != 'ADMIN' and 'ORACLE' not in identity.users.get(user['sub'], {}).get('roles', []):
            return h.send_json_error("Only Oracles or Admin can certify roles", status=403)
            
        target_user = p.get('username')
        role = p.get('role', '').upper()
        if not target_user or not role:
            return h.send_json_error("Username and Role required")
            
        if target_user not in identity.users:
            return h.send_json_error("Target user not found")
            
        # Update user metadata
        u_data = identity.users[target_user]
        if 'roles' not in u_data: u_data['roles'] = ["WORKER"]
        if role not in u_data['roles']:
            u_data['roles'].append(role)
        
        if 'certifications' not in u_data: u_data['certifications'] = {}
        u_data['certifications'][role] = {
            "certified_by": user['sub'],
            "timestamp": time.time(),
            "level": p.get('level', 1)
        }
        
        identity.save()
        
        # Record on ledger for transparency
        ledger.add_block('CERTIFICATION', {
            "target": target_user,
            "role": role,
            "certified_by": user['sub'],
            "timestamp": time.time()
        })
        
        h.send_json({"status": "certified", "user": target_user, "role": role})

    @router.post('/api/roles/define')

    @requires_auth
    def h_define_role(h, user, p):
        """Oracle defines a new role multiplier on the ledger."""
        if user['role'] != 'ADMIN' and 'ORACLE' not in identity.users.get(user['sub'], {}).get('roles', []):
            return h.send_json_error("Only Oracles or Admin can define roles", status=403)
            
        role_name = p.get('role', '').upper()
        multiplier = float(p.get('multiplier', 1.0))
        
        if not role_name: return h.send_json_error("Role name required")
        
        ledger.add_block('ROLE_DEFINITION', {
            "role": role_name,
            "multiplier": multiplier,
            "defined_by": user['sub'],
            "timestamp": time.time()
        })
        h.send_json({"status": "defined", "role": role_name, "multiplier": multiplier})




    @router.get('/api/evolution')
    def h_evolution(h):
        blocks = ledger.blocks
        v_mints = len([b for b in blocks if b['type'] in ['LABOR', 'HARDWARE_PROOF', 'PROOF', 'CODE_MINT']])
        active_missions = [b['data'] for b in blocks if b['type'] == 'MISSION'][-3:]
        h.send_json({
            "total_mints": v_mints,
            "metabolic_yield": sensors.get_metabolic_yield() if hasattr(sensors, 'get_metabolic_yield') else 0,
            "evolution_cycles": len(blocks),
            "active_missions": active_missions,
            "sensors": getattr(sensors, 'sensors', {}),
            "uptime": "99.9%"
        })

    @router.get('/api/marketing/prompts')
    def h_marketing_prompts(h):
        """Get a random marketing prompt for Veo3 video generation."""
        try:
            prompts_file = os.path.join(os.path.dirname(__file__), '..', 'web', 'marketing_prompts.json')
            with open(prompts_file, 'r') as f:
                data = json.load(f)
            prompts = data.get('prompts', [])
            if prompts:
                selected = random.choice(prompts)
                h.send_json(selected)
            else:
                h.send_json_error("No prompts available")
        except Exception as e:
            h.send_json_error(f"Error loading prompts: {str(e)}")

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


    @router.post('/api/transfer')
    @requires_auth
    def h_transfer(h, user, p):
        sender = user['sub']
        recv, amt = p.get('receiver'), float(p.get('amount', 0))
        if ledger.get_balance(sender) < amt: return h.send_json_error("Insufficient life wealth (AT)")
        h_res = ledger.add_block('TX', {'sender': sender, 'receiver': recv, 'amount': amt, 'timestamp': time.time()})
        h.send_json({"hash": h_res})

    @router.get('/api/store')
    def h_store(h):
        h.send_json([
            {"id": "ose_fbcc", "name": "FBCC Godzilla Ticket", "price": 2100, "icon": "🏎️", "desc": "2-for-1 Immersive Truck Build (Includes Food & Onsite Living)"},
            {"id": "ose_consult", "name": "AI/Lead Architect Consult", "price": 100, "icon": "🧠", "desc": "1 Hour technical strategy session"},
            {"id": "ose_cad", "name": "Ironworker CAD (Full)", "price": 50, "icon": "🛠️", "desc": "Complete technical design files"},
            {"id": "ose_seh", "name": "Seed Eco-Home Blueprints", "price": 150, "icon": "🏡", "desc": "Modular structural designs"},
            {"id": "ose_sticker", "name": "Civ-OS Sticker", "price": 10, "icon": "🏷️", "desc": "Proclaim your sovereignty"}
        ])

    @router.post('/api/purchase')
    def h_purchase(h, p):
        u = h.get_auth_user()
        if not u: return h.send_json_error("Auth Required", status=401)
        sender = u['sub']
        item_id = p.get('item_id')
        prices = {
            "ose_fbcc": 2100,
            "ose_consult": 100,
            "ose_cad": 50,
            "ose_seh": 150,
            "ose_sticker": 10
        }
        price = prices.get(item_id)
        if not price: return h.send_json_error("Item not found")
        if ledger.get_balance(sender) < price: return h.send_json_error("Insufficient AT")
        
        h_res = ledger.add_block('PURCHASE', {'buyer': sender, 'item': item_id, 'amount': price, 'timestamp': time.time()})
        h.send_json({"hash": h_res, "status": "success"})

    # === COMMUNITY QUEST SYSTEM ===
    
    @router.post('/api/quests/post')
    @requires_auth
    def h_post_quest(h, user, p):
        """Post a new community quest."""
        if not quest_system:
            return h.send_json_error("Quest system not available")
        
        success, result = quest_system.post_quest(user['sub'], p)
        if success:
            h.send_json({"quest_id": result, "status": "posted"})
        else:
            h.send_json_error(result)
    
    @router.get('/api/quests/available')
    def h_available_quests(h):
        """Get all available quests (optionally filtered)."""
        if not quest_system:
            return h.send_json_error("Quest system not available")
        
        # TODO: Parse query params for filters
        user = h.get_auth_user()
        username = user['sub'] if user else "guest"
        
        quests = quest_system.get_available_quests(username)
        h.send_json({"quests": quests, "count": len(quests)})
    
    @router.post('/api/quests/claim')
    @requires_auth
    def h_claim_quest(h, user, p):
        """Claim a quest to work on it."""
        if not quest_system:
            return h.send_json_error("Quest system not available")
        
        quest_id = p.get('quest_id')
        if not quest_id:
            return h.send_json_error("quest_id required")
        
        success, message = quest_system.claim_quest(quest_id, user['sub'])
        if success:
            h.send_json({"status": "claimed", "message": message})
        else:
            h.send_json_error(message)
    
    @router.get('/api/quests/detail')
    def h_quest_detail(h):
        """Get details of a specific quest."""
        if not quest_system:
            return h.send_json_error("Quest system not available")
        
        # Parse query param
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(h.path).query)
        quest_id = query.get('quest_id', [None])[0]
        
        if not quest_id:
            return h.send_json_error("quest_id required")
        
        quest = quest_system.get_quest(quest_id)
        if quest:
            h.send_json(quest)
        else:
            h.send_json_error("Quest not found", status=404)
    
    # === VERIFICATION SYSTEM ===
    
    @router.post('/api/verification/request')
    @requires_auth
    def h_request_verification(h, user, p):
        """Request 3-witness verification after completing a quest."""
        if not verification:
            return h.send_json_error("Verification system not available")
        
        quest_id = p.get('quest_id')
        witnesses = p.get('witnesses', [])
        proof = p.get('proof', {})
        
        if not quest_id or not witnesses or not proof:
            return h.send_json_error("quest_id, witnesses, and proof required")
        
        success, result = verification.request_verification(
            quest_id, user['sub'], witnesses, proof
        )
        
        if success:
            h.send_json({
                "verification_id": result,
                "status": "pending",
                "message": "Verification request sent to witnesses"
            })
        else:
            h.send_json_error(result)
    
    @router.post('/api/verification/submit')
    @requires_auth
    def h_submit_verification(h, user, p):
        """Witness submits their verification decision."""
        if not verification:
            return h.send_json_error("Verification system not available")
        
        verification_id = p.get('verification_id')
        approved = p.get('approved', False)
        note = p.get('note', '')
        
        if not verification_id:
            return h.send_json_error("verification_id required")
        
        success, message = verification.submit_verification(
            verification_id, user['sub'], approved, note
        )
        
        if success:
            h.send_json({"status": "recorded", "message": message})
        else:
            h.send_json_error(message)
    
    @router.get('/api/verification/pending')
    @requires_auth
    def h_pending_verifications(h, user, p):
        """Get all pending verifications where user is a witness."""
        if not verification:
            return h.send_json_error("Verification system not available")
        
        pending = verification.get_pending_verifications_for_user(user['sub'])
        h.send_json({"verifications": pending, "count": len(pending)})
    
    # === QUEST TEMPLATES ===
    
    @router.get('/api/quests/templates')
    def h_quest_templates(h):
        """Get pre-built quest templates."""
        from core.quest_system import QuestTemplates
        
        templates = {
            "bar_crawl_bingo": QuestTemplates.bar_crawl_bingo(),
            "photo_scavenger_hunt": QuestTemplates.photo_scavenger_hunt("Downtown"),
            "art_walk_discovery": QuestTemplates.art_walk_discovery(),
            "skill_exchange": QuestTemplates.skill_exchange("Knitting", "Spanish"),
            "local_shop_support": QuestTemplates.local_shop_support("Joe's Coffee", "Organize stockroom")
        }
        
        h.send_json({"templates": templates})

