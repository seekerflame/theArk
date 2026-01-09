def register_hardware_routes(router, sensors, foundry, requires_auth):

    @router.post('/api/hardware/register')
    @requires_auth
    def h_hardware_register(h, p, user):
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
        s_id = p.get('id')
        value = p.get('value')

        if not s_id or value is None:
            return h.send_json_error("Missing 'id' or 'value'")

        s_type = p.get('type', 'unknown')
        meta = p.get('meta')

        sensor = sensors.update(s_id, s_type, value, meta)
        h.send_json({"status": "updated", "sensor": sensor})

    @router.get('/api/hardware/list')
    def h_hardware_list(h):
        h.send_json(sensors.get_all())

    # === FOUNDRY & RESERVATIONS ===

    @router.get('/api/hardware/foundry')
    def h_foundry_list(h):
        """List all machines in the foundry."""
        machines = [
            {
                "name": m.name,
                "type": m.machine_type,
                "at_cost_per_hour": m.at_cost_per_hour,
                "status": m.status,
                "is_static": m.is_static
            }
            for m in foundry.machines.values()
        ]
        h.send_json({"machines": machines})

    @router.post('/api/hardware/foundry/reserve')
    @requires_auth
    def h_foundry_reserve(h, p, user):
        """Reserve a static asset."""
        asset_name = p.get('asset_name')
        duration = p.get('duration_hours', 1)

        if not asset_name:
            return h.send_json_error("Missing 'asset_name'")

        result = foundry.reserve_asset(user['sub'], asset_name, duration)
        if result.get('status') == 'success':
            h.send_json(result)
        else:
            h.send_json_error(result.get('message', 'Reservation failed'))
