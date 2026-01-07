import time

def register_economy_routes(router, ledger, sensors, requires_auth):

    @router.get('/api/evolution')
    def h_evolution(h):
        blocks = ledger.blocks
        v_mints = len([b for b in blocks if b['type'] in ['LABOR', 'HARDWARE_PROOF', 'PROOF']])
        active_missions = [b['data'] for b in blocks if b['type'] == 'MISSION'][-3:]
        h.send_json({
            "total_mints": v_mints,
            "metabolic_yield": sensors.get_metabolic_yield() if hasattr(sensors, 'get_metabolic_yield') else 0,
            "evolution_cycles": len(blocks),
            "active_missions": active_missions,
            "sensors": getattr(sensors, 'sensors', {}),
            "uptime": "99.9%"
        })

    @router.post('/api/mint')
    @requires_auth
    def h_mint(h, user, p):
        data = p.get('data', p)
        data['minter'] = user['sub']
        data['timestamp'] = time.time()
        block_hash = ledger.add_block('LABOR', data)
        if block_hash: h.send_json({"hash": block_hash})
        else: h.send_error("Failed to mint block")

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

    @router.get('/api/verification/pending')
    @requires_auth
    def h_verify_pending(h, user, p=None):
        # Fetch blocks that need verification.
        # In this simplified model, we scan the ledger for unverified blocks (simulated by a flag or separate list).
        # For MVP, let's scan recent blocks of type 'LABOR' or 'PROOF'.
        # Real impl would filter by `verified: false` in block data.

        pending = []
        for b in ledger.blocks[-50:]: # Scan last 50
            if b['type'] in ['LABOR', 'PROOF'] and not b['data'].get('verified'):
                pending.append(b)
        h.send_json(pending)

    @router.post('/api/verification/submit')
    @requires_auth
    def h_verify_submit(h, user, p):
        # Oracle submits verification
        block_hash = p.get('hash')
        verdict = p.get('verdict') # VALID, INVALID

        if not block_hash or not verdict:
            return h.send_error("Missing hash or verdict")

        # In a real blockchain, we'd append a VERIFICATION block referencing the target.
        # Here we just emit a block.
        ledger.add_block('VERIFICATION', {
            "target_hash": block_hash,
            "oracle": user['username'],
            "verdict": verdict,
            "timestamp": time.time()
        })

        # Also could update local state if we had a mutable DB, but we are append-only.
        # The frontend will re-read the graph and see the verification block.

        h.send_json({"status": "verified"})
