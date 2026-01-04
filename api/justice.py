import time

def register_justice_routes(router, ledger, justice, requires_auth):

    @router.post('/api/justice/dispute')
    @requires_auth
    def h_dispute(h, user, p):
        """End-user flags a block as fraudulent or mistaken."""
        block_hash = p.get('block_hash')
        reason = p.get('reason')
        
        if not block_hash or not reason:
            return h.send_error("Block Hash and Reason required")
            
        success, msg = justice.dispute_block(block_hash, user['sub'], reason)
        if success:
            h.send_json({"status": "disputed", "message": msg})
        else:
            h.send_error(msg)

    @router.post('/api/justice/resolve')
    @requires_auth
    def h_resolve(h, user, p):
        """Oracle resolves a dispute."""
        # Simple permission check for now
        u_roles = justice.identity.users.get(user['sub'], {}).get('roles', [])
        if user['role'] != 'ADMIN' and 'ORACLE' not in u_roles:
            return h.send_error("Only Oracles can resolve disputes", status=403)
            
        dispute_hash = p.get('dispute_hash')
        resolution = p.get('resolution') # VALID | MISTAKE | MALICE
        findings = p.get('findings')
        
        if not dispute_hash or not resolution:
            return h.send_error("Dispute Hash and Resolution required")
            
        success, msg = justice.resolve_dispute(dispute_hash, resolution, user['sub'], findings)
        if success:
            h.send_json({"status": "resolved", "message": msg})
        else:
            h.send_error(msg)

    @router.get('/api/justice/grade')
    @requires_auth
    def h_get_grade(h, user, p):
        """Endpoint for users to see their own safety grade."""
        grade = justice.get_safety_grade(user['sub'])
        h.send_json({"username": user['sub'], "safety_grade": grade})
