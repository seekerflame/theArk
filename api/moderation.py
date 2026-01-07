def register_moderation_routes(router, mod_queue, requires_auth):

    @router.get('/api/moderation/queue')
    @requires_auth
    def h_mod_queue(h, user, p=None):
        # In future, check if user is ORACLE or MODERATOR
        # if user['role'] not in ['ADMIN', 'ORACLE']: return h.send_error("Access Denied", 403)
        h.send_json(mod_queue.get_queue())

    @router.post('/api/moderation/report')
    @requires_auth
    def h_report(h, user, p):
        target = p.get('target_id')
        reason = p.get('reason')
        proof = p.get('proof')

        if not target or not reason:
            return h.send_error("Missing target or reason")

        rid = mod_queue.add_report(user['username'], target, reason, proof)
        h.send_json({"status": "reported", "report_id": rid})

    @router.get('/api/moderation/log')
    def h_mod_log(h):
        h.send_json(mod_queue.get_log())

    @router.post('/api/moderation/resolve')
    @requires_auth
    def h_resolve(h, user, p):
        # if user['role'] not in ['ADMIN', 'ORACLE']: return h.send_error("Access Denied", 403)
        rid = p.get('report_id')
        action = p.get('action') # DISMISS, BAN, WARN
        notes = p.get('notes', '')

        if not rid or not action:
            return h.send_error("Missing report_id or action")

        success = mod_queue.resolve_report(rid, user['username'], action, notes)
        if success:
            h.send_json({"status": "resolved"})
        else:
            h.send_error("Report not found")
