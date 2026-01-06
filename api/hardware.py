import time

def register_hardware_routes(router, ledger, sensors, requires_auth):

    @router.post('/api/hardware')
    def h_hardware_update(h, p):
        # Authenticate if needed (currently hardware bridge uses a secret or sim token)
        # Check for X-Hardware-Secret header if we want to enforce security, but for now we follow the pattern
        # Actually ark_hardware_sim sends X-Hardware-Secret.

        # Extract data
        s_id = p.get('sensor_id')
        s_type = p.get('type')
        value = p.get('value')
        # Note: hardware_bridge.py sends specific fields like 'power_w', etc.
        # It sends: { "sensor_id": ..., "type": ..., "device_id": ..., **data }
        # ark_hardware_sim.py sends: { "sensor_id": ..., "type": ..., "value": ... }

        if not s_id or not s_type:
             return h.send_error("Missing sensor_id or type")

        # If value is missing, maybe it's the other format (hardware_bridge.py)
        if value is None:
             # Store the whole payload as value minus the metadata
             value = {k: v for k, v in p.items() if k not in ['sensor_id', 'type', 'device_id']}

        # Update registry
        sensors.update(s_id, s_type, value)

        # Optional: Mint AT for energy generation (from ark_hardware_sim logic)
        if s_type in ['ENERGY', 'SOLAR_GEN']:
            # Check if we should mint
            pass # Logic for minting can be added here or kept in simulation logic

        # Check for pending commands
        device_id = p.get('device_id')
        cmds = []
        if device_id:
            cmds = sensors.get_pending_commands(device_id)

        h.send_json({"status": "received", "sensor_id": s_id, "commands": cmds})

    @router.post('/api/hardware/command')
    @requires_auth
    def h_hardware_command(h, user, p):
        device_id = p.get('device_id')
        cmd = p.get('command')

        if not device_id or not cmd:
            return h.send_error("Missing device_id or command")

        sensors.queue_command(device_id, cmd)
        h.send_json({"status": "queued", "device_id": device_id, "command": cmd})
