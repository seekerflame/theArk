def register_federation_routes(router, peers):

    @router.get('/api/federation/villages')
    def h_villages(h):
        # Return list of active peers + Simulation peers
        # In a real scenario, this would come from `peers.get_active_peers()`

        sim_villages = [
            {"village_id": "ose-missouri-001", "name": "Factor e Farm (HQ)", "lat": 39.914, "lng": -94.525, "status": "ONLINE"},
            {"village_id": "ose-europe-001", "name": "OSE Europe", "lat": 51.165, "lng": 10.451, "status": "ONLINE"},
            {"village_id": "sim-mars-001", "name": "Mars Sovereign", "lat": 40.0, "lng": -95.0, "status": "OFFLINE"}
        ]

        # Merge with actual peers if any
        # peers_list = peers.list_peers() ...

        h.send_json({"villages": sim_villages})
