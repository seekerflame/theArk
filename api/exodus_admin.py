import time

def register_exodus_admin_routes(router, ledger, identity, admin_only):
    
    @router.post('/api/exodus/admin/trigger')
    @admin_only
    def h_trigger_wave(h, user, payload):
        """
        Triggers a new Exodus migration wave.
        Payload: { "wave_id": 1, "grant_amount": 100.0, "active": true }
        """
        wave_id = payload.get('wave_id')
        grant_amount = payload.get('grant_amount', 100.0)
        active = payload.get('active', True)

        if wave_id is None:
            return h.send_json_error("Missing wave_id")

        wave_data = {
            "wave_id": wave_id,
            "grant_amount": grant_amount,
            "active": active,
            "timestamp": time.time(),
            "triggered_by": user['username']
        }

        # Add to ledger as a configuration block
        ledger.add_block('EXODUS_WAVE_CONFIG', wave_data)

        h.send_json({
            "status": "success",
            "message": f"Exodus Wave {wave_id} activated with {grant_amount} AT grant.",
            "wave_data": wave_data
        })

    @router.get('/api/exodus/admin/status')
    @admin_only
    def h_get_wave_status(h, user):
        """Returns the current wave configuration."""
        wave_config = None
        for b in ledger.blocks:
            if b['type'] == 'EXODUS_WAVE_CONFIG':
                wave_config = b['data']
        
        h.send_json(wave_config or {"active": False, "message": "No active wave."})
