import time
import json
import os
import random

class FederationMesh:
    def __init__(self, ledger, storage_path='ledger/federation_registry.json'):
        self.ledger = ledger
        self.storage_path = storage_path
        self.nodes = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.nodes = json.load(f)
        else:
            # Seed Genesis Node
            self.nodes = {
                "node_001": {
                    "id": "node_001",
                    "name": "Factor E Farm",
                    "population": 142,
                    "kardashev": 0.7241,
                    "status": "STABLE",
                    "location": [39.0, -91.0] # Kansas
                }
            }
            self.save()

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.nodes, f, indent=2)

    def heartbeat(self):
        # Simulate mitosis across the federation
        for node_id, node in list(self.nodes.items()):
            # Growth simulation
            node['population'] += random.randint(0, 2)
            node['kardashev'] += random.uniform(0.0001, 0.0005)
            
            if node['population'] >= 150:
                self.mitosis(node_id)

    def mitosis(self, node_id):
        parent = self.nodes[node_id]
        new_node_id = f"node_{len(self.nodes) + 1:03d}"
        
        # Split population
        new_pop = parent['population'] // 2
        parent['population'] -= new_pop
        parent['status'] = "RECOVERING"
        
        self.nodes[new_node_id] = {
            "id": new_node_id,
            "name": f"Spore Node {new_node_id}",
            "population": new_pop,
            "kardashev": 0.5,
            "status": "COLONIZING",
            "location": [
                parent['location'][0] + random.uniform(-1.0, 1.0),
                parent['location'][1] + random.uniform(-1.0, 1.0)
            ],
            "parent_id": node_id
        }
        
        self.ledger.add_block('FEDERATION_MITOSIS', {
            "parent": node_id,
            "child": new_node_id,
            "timestamp": time.time()
        })
        self.save()

    def register_node(self, node_data):
        """Register a real peer node in the mesh"""
        node_id = node_data.get('node_id')
        if not node_id: return False, "No node_id provided"
        
        # Standardize node format
        self.nodes[node_id] = {
            "id": node_id,
            "name": node_data.get('name', f"Peer {node_id}"),
            "url": node_data.get('url'),
            "ip": node_data.get('ip'),
            "port": node_data.get('port'),
            "kardashev": node_data.get('kardashev', 0.5),
            "status": "CONNECTED",
            "last_seen": time.time(),
            "location": node_data.get('location', [0, 0])
        }
        self.save()
        return True, "Node registered"

    def get_node_info(self, node_id):
        return self.nodes.get(node_id)

    def get_public_manifest(self):
        """Returns data about this node for handshakes"""
        return {
            "node_id": "node_001", # Should be configurable
            "name": "Factor E Farm",
            "kardashev": 0.7241,
            "location": [39.0, -91.0]
        }

class PeerManager:
    def __init__(self, registry_path, port):
        self.registry_path = registry_path
        self.port = port
        self.mesh = FederationMesh(None, storage_path=registry_path)

    def get_nodes(self):
        return self.mesh.nodes

class FederationSyncer:
    def __init__(self, ledger, peers, port):
        self.ledger = ledger
        self.peers = peers
        self.port = port
        self.running = False

    def start(self):
        self.running = True
        # Background simulation loop could go here
        print(f"🌐 Federation Syncer active on port {self.port}")
