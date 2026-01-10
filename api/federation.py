from core.federation import FederationMesh

def register_federation_routes(router, ledger, auth_decorator):
    fed = FederationMesh(ledger)

    @router.get('/api/federation/mesh')
    def list_nodes(h):
        # Trigger growth/mitosis simulation heartbeats
        fed.heartbeat()
        h.send_json({"nodes": list(fed.nodes.values())})

    @router.post('/api/federation/ping')
    @auth_decorator
    def ping_node(h, user, p):
        # Placeholder for inter-node comms
        h.send_json({"status": "pong", "origin": "node_001"})
