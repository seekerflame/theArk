import time
import json
import os
import random

def register_economy_routes(router, ledger, sensors, identity, requires_auth):

    @router.get('/api/roles/multipliers')
    def h_multipliers(h):
        h.send_json(identity.get_role_multipliers())

    @router.post('/api/roles/certify')
    @requires_auth
    def h_certify_role(h, user, p):
        """Oracle certifies a user for a specific role/skill."""
        if user['role'] != 'ADMIN' and 'ORACLE' not in identity.users.get(user['sub'], {}).get('roles', []):
            return h.send_error("Only Oracles or Admin can certify roles", status=403)
            
        target_user = p.get('username')
        role = p.get('role', '').upper()
        if not target_user or not role:
            return h.send_error("Username and Role required")
            
        if target_user not in identity.users:
            return h.send_error("Target user not found")
            
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
                h.send_error("No prompts available")
        except Exception as e:
            h.send_error(f"Error loading prompts: {str(e)}")

    @router.post('/api/mint')
    @requires_auth
    def h_mint(h, user, p):
        data = p.get('data', p)
        data['minter'] = user['sub']
        data['timestamp'] = time.time()
        block_hash = ledger.add_block('LABOR', data)
        if block_hash: h.send_json({"hash": block_hash})
        else: h.send_error("Failed to mint block")


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
            return h.send_error(f"Justice Audit Failed: {reason} (Score: {score:.2f})")
        
        # 2. Reward Calculation
        multiplier = COMPLEXITY.get(complexity_level, 1.0)
        reward = max(1, lines * BASE_RATE * multiplier * score)  # Score scales the reward
        
        data = {
            'minter': user['sub'],
            'lines_changed': lines,
            'complexity': complexity_level,
            'reward': reward,
            'audit_score': score,
            'pr_url': pr_url,
            'commit_hash': commit_hash,
            'timestamp': time.time()
        }
        
        block_hash = ledger.add_block('CODE_MINT', data)
        if block_hash: 
            h.send_json({"hash": block_hash, "reward": reward, "audit_score": score})
        else: 
            h.send_error("Failed to mint code block")

    @router.post('/api/transfer')
    @requires_auth
    def h_transfer(h, user, p):
        sender = user['sub']
        recv, amt = p.get('receiver'), float(p.get('amount', 0))
        if ledger.get_balance(sender) < amt: return h.send_error("Insufficient life wealth (AT)")
        h_res = ledger.add_block('TX', {'sender': sender, 'receiver': recv, 'amount': amt, 'timestamp': time.time()})
        h.send_json({"hash": h_res})

    @router.get('/api/store')
    def h_store(h):
        h.send_json([
            {"id": "s1", "name": "Sol-Module X", "price": 50, "icon": "🔋", "desc": "High-density energy storage"},
            {"id": "s2", "name": "Bio-Seed Pack", "price": 10, "icon": "🌱", "desc": "Heirloom diverse seeds"},
            {"id": "s3", "name": "Aqua-Filter Pro", "price": 30, "icon": "💧", "desc": "Type 6 water purification"},
            {"id": "s4", "name": "Civ-OS Sticker", "price": 2, "icon": "🏷️", "desc": "Proclaim your sovereignty"}
        ])

    @router.post('/api/purchase')
    def h_purchase(h, p):
        u = h.get_auth_user()
        if not u: return h.send_error("Auth Required", status=401)
        sender = u['sub']
        item_id = p.get('item_id')
        prices = {"s1": 50, "s2": 10, "s3": 30, "s4": 2}
        price = prices.get(item_id)
        if not price: return h.send_error("Item not found")
        if ledger.get_balance(sender) < price: return h.send_error("Insufficient AT")
        
        h_res = ledger.add_block('PURCHASE', {'buyer': sender, 'item': item_id, 'amount': price, 'timestamp': time.time()})
        h.send_json({"hash": h_res, "status": "success"})

