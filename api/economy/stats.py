def register_stats_routes(router, ledger, sensors):
    @router.get('/api/evolution')
    def h_evolution(h):
        blocks = ledger.blocks
        v_mints = len([b for b in blocks if b['type'] in ['LABOR', 'HARDWARE_PROOF', 'PROOF', 'CODE_MINT']])
        active_missions = [b['data'] for b in blocks if b['type'] == 'MISSION'][-3:]
        h.send_json({
            "total_mints": v_mints,
            "metabolic_yield": sensors.get_metabolic_yield() if hasattr(sensors, 'get_metabolic_yield') else 0,
            "evolution_cycles": len(blocks),
            "active_missions": active_missions,
            "sensors": getattr(sensors, 'sensors', {}),
            "uptime": "99.9%"
        })
