from core.sovereign_analytics import SovereignAnalytics
from core.passport import SovereignPassport

def register_sovereign_intel_routes(router, ledger, identity, requires_auth):
    
    analytics = SovereignAnalytics(ledger)
    passport = SovereignPassport(ledger, identity)

    @router.get('/api/sovereign/analytics')
    @requires_auth
    def h_get_analytics(h, user):
        """Returns abundance-focused intelligence."""
        h.send_json({
            "metrics": analytics.get_abundance_metrics(),
            "recommendation": analytics.generate_recommendation()
        })

    @router.post('/api/sovereign/passport/request')
    @requires_auth
    def h_request_passport(h, user, payload):
        """Initiates decentralised identity verification."""
        result = passport.request_passport(user['username'])
        h.send_json(result)

    @router.post('/api/sovereign/passport/attest')
    @requires_auth
    def h_attest(h, user, payload):
        """Peer-attestation for Sovereign Citizenship."""
        target = payload.get('target')
        if not target: return h.send_json_error("Missing target username")
        
        result = passport.attest_citizen(user['username'], target)
        h.send_json(result)
        
    @router.get('/api/sovereign/passport/status')
    @requires_auth
    def h_status(h, user):
        """Checks passport status."""
        p_data = passport.get_passport(user['username'])
        h.send_json(p_data or {"status": "PENDING", "message": "No active passport."})
