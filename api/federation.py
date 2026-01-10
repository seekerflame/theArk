from core.federation import FederationMesh

def register_federation_routes(router, ledger, auth_decorator):
    fed = FederationMesh(ledger)

    @router.get('/api/federation/peers')
    def list_nodes(h):
        # Trigger growth/mitosis simulation heartbeats
        fed.heartbeat()
        
        # Format for frontend (lat/lng/village_id)
        formatted = []
        for n_id, n in fed.nodes.items():
            formatted.append({
                "village_id": n_id,
                "id": n_id,
                "name": n.get('name'),
                "lat": n.get('location', [0, 0])[0],
                "lng": n.get('location', [0, 0])[1],
                "status": n.get('status', 'OFFLINE'),
                "url": n.get('url', 'local')
            })
        h.send_json(formatted)

    @router.post('/api/federation/peers/add')
    def add_peer(h, p):
        """Manually trigger a handshake with a new node"""
        url = p.get('url')
        if not url: return h.send_json_error("No URL provided")
        
        # 1. Reach out to peer and perform handshake
        try:
            import requests
            # We send our manifest
            my_manifest = fed.get_public_manifest()
            r = requests.post(f"{url}/api/federation/handshake", json=my_manifest, timeout=5)
            
            if r.status_code == 200:
                peer_data = r.json().get('data', {}).get('node_info', {})
                # 2. Register peer
                peer_data['url'] = url
                fed.register_node(peer_data)
                h.send_json({"status": "success", "peer": peer_data})
            else:
                h.send_json_error(f"Peer handshake failed: {r.text}")
        except Exception as e:
            h.send_json_error(f"Handshake Error: {str(e)}")

    @router.post('/api/federation/ping')
    @auth_decorator
    def ping_node(h, user, p):
        # Placeholder for inter-node comms
        h.send_json({"status": "pong", "origin": "node_001"})

    @router.post('/api/federation/handshake')
    def handshake(h, p):
        """Incoming handshake from a peer node"""
        success, message = fed.register_node(p)
        if success:
            h.send_json({
                "status": "success",
                "message": "Handshake mutual",
                "node_info": fed.get_public_manifest()
            })
        else:
            h.send_json_error(message)
