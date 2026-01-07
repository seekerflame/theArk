def register_hardware_routes(router, sensors, requires_auth):

    @router.post('/api/hardware/register')
    @requires_auth
    def h_hardware_register(h, p):
        # Expected: id, type, meta (optional)
        s_id = p.get('id')
        s_type = p.get('type')
        meta = p.get('meta', {})

        if not s_id or not s_type:
            return h.send_json_error("Missing sensor 'id' or 'type'")

        sensor = sensors.register(s_id, s_type, meta)
        h.send_json({"status": "registered", "sensor": sensor})

    @router.post('/api/hardware/update')
    def h_hardware_update(h, p):
        # Allow unauthenticated updates? Maybe with a secret key in future.
        # For now, let's keep it open but maybe we should check a header or shared secret.
        # But the plan didn't specify strict auth for sensors yet, and README implies easy integration.
        # We'll allow it for now.

        s_id = p.get('id')
        value = p.get('value')

        if not s_id or value is None:
            return h.send_json_error("Missing 'id' or 'value'")

        # Optional: update type/meta on fly
        s_type = p.get('type', 'unknown')
        meta = p.get('meta')

        # If sensor doesn't exist, we might want to reject or auto-register.
        # Current sensors.update logic auto-registers if needed.
        sensor = sensors.update(s_id, s_type, value, meta)
        h.send_json({"status": "updated", "sensor": sensor})

    @router.get('/api/hardware/list')
    def h_hardware_list(h):
        h.send_json(sensors.get_all())
