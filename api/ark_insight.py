from core.ark_insight import ArkAnalytics
from core.passport import ArkPassport

def register_ark_insight_routes(router, ledger, identity, bridge, requires_auth):
    
    analytics = ArkAnalytics(ledger)
    passport = ArkPassport(ledger, identity, bridge)

    @router.get('/api/ark/analytics')
    @requires_auth
    def h_get_analytics(h, user, p=None):
        """Returns abundance-focused intelligence."""
        h.send_json({
            "metrics": analytics.get_abundance_metrics(),
            "recommendation": analytics.generate_recommendation()
        })

    @router.post('/api/ark/passport/at_token')
    def h_get_presence(h, payload):
        """Returns current presence token (Publicly scanable locally)."""
        h.send_json({"presence_token": bridge.read_telemetry().get('presence_token')})

    @router.post('/api/ark/passport/request')
    @requires_auth
    def h_request_passport(h, user, payload):
        """Initiates decentralized identity verification."""
        result = passport.request_passport(user['sub'])
        h.send_json(result)

    @router.post('/api/ark/passport/attest')
    @requires_auth
    def h_attest(h, user, payload):
        """Peer-attestation for Ark Citizenship."""
        target = payload.get('target')
        presence_token = payload.get('presence_token')
        if not target: return h.send_json_error("Missing target username")
        if not presence_token: return h.send_json_error("Proof of Presence required (token missing)")
        
        result = passport.attest_citizen(user['sub'], target, presence_token)
        h.send_json(result)
        
    @router.post('/api/ark/passport/grant')
    @requires_auth
    def h_grant_passport(h, user, payload):
        """Admin bootstrapping of an Ark Citizen."""
        if user['role'] != 'ADMIN':
            return h.send_json_error("Admin only", status=403)
        target = payload.get('target')
        if not target: return h.send_json_error("Missing target")
        result = passport.grant_emergency_passport(user['sub'], target)
        h.send_json(result)

    @router.get('/api/ark/passport/status')
    @requires_auth
    def h_status(h, user, p=None):
        """Checks passport status."""
        p_data = passport.get_passport(user['sub'])
        h.send_json(p_data or {"status": "PENDING", "message": "No active passport."})
