"""
Moderation API - Routes for governance and safety
"""

def register_moderation_routes(router, governance, identity, requires_auth):
    
    # === PUBLIC TRANSPARENCY ===
    
    @router.get('/api/moderation/log')
    def h_transparency_log(h):
        """Get public transparency log."""
        # Parse query params
        from urllib.parse import parse_qs, urlparse
        query = parse_qs(urlparse(h.path).query)
        limit = int(query.get('limit', [50])[0])
        offset = int(query.get('offset', [0])[0])
        
        logs = governance.get_public_logs(limit, offset)
        h.send_json(logs)

    # === REPORTING ===

    @router.post('/api/moderation/report')
    @requires_auth
    def h_report_content(h, user, p):
        """Submit a report."""
        content_id = p.get('content_id')
        reason = p.get('reason')
        category = p.get('category', 'other')
        
        if not content_id or not reason:
            return h.send_json_error("content_id and reason required")
            
        success, result = governance.submit_report(user['sub'], content_id, reason, category)
        
        if success:
            h.send_json({"status": "reported", "report_id": result})
        else:
            h.send_json_error(result)

    # === PRE-SCREENING (Used by client before post) ===
    
    @router.post('/api/moderation/check')
    @requires_auth
    def h_check_content(h, user, p):
        """Pre-screen content for violence."""
        text = p.get('text', '')
        is_safe, severity, triggers, rec = governance.check_content(text, user_id=user['sub'])
        
        h.send_json({
            "is_safe": is_safe,
            "recommendation": rec,
            "triggers": triggers if not is_safe else []
        })

    # === ORACLE ACTIONS ===
    
    @router.get('/api/moderation/queue')
    @requires_auth
    def h_mod_queue(h, user, p):
        """Get pending reports for oracle."""
        # Check if oracle
        u_data = identity.users.get(user['sub'], {})
        if 'ORACLE' not in u_data.get('roles', []) and user['role'] != 'ADMIN':
            return h.send_json_error("Access denied: Oracles only", status=403)
            
        queue = governance.get_report_queue()
        h.send_json({"queue": queue, "count": len(queue)})
