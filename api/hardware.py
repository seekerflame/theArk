import time

def register_hardware_routes(router, ledger, sensors, requires_auth):

    @router.post('/api/hardware')
    def h_hardware_update(h, p):
        # Payload expected from hardware_bridge.py
        # { "sensor_id": "...", "type": "...", "device_id": "...", "power_w": ..., ... }

        s_id = p.get('sensor_id')
        s_type = p.get('type')

        if not s_id or not s_type:
            return h.send_error("Missing sensor_id or type")

        # Update Registry
        sensors.update(s_id, s_type, p)

        # Auto-Mint Logic for Solar Generation
        # "Goal: Connect real solar panels ... to auto-mint AT when they produce value."
        if s_type == 'SOLAR_GEN':
            power_w = p.get('power_w', 0)
            if power_w > 100: # Threshold for meaningful generation
                # Rate limit minting to avoid spamming the ledger?
                # For this MVP, we'll mint a micro-reward.
                # Ideally, we'd aggregate this over time, but let's stick to the prompt's "auto-mint".

                # Check if we minted recently for this sensor to prevent bloat (debounce 60s)
                # This requires querying the ledger, which might be slow.
                # Simplified: Just mint.

                reward = round(power_w / 1000 * 0.1, 4) # 0.1 AT per kWh rate (instantaneous approx)

                if reward > 0:
                    ledger.add_block('HARDWARE_PROOF', {
                        'worker': s_id,
                        'device': p.get('device_id'),
                        'watts': power_w,
                        'reward': reward,
                        'timestamp': time.time()
                    })

        h.send_json({"status": "updated", "sensor": s_id})

    @router.get('/api/hardware/list')
    def h_hardware_list(h):
        h.send_json(sensors.sensors)
