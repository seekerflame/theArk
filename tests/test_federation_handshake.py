
import requests
import time
import threading
import os
import signal
import subprocess
import pytest

# Configuration for simulated nodes
NODE_A_PORT = 3006
NODE_B_PORT = 3007

def test_federation_handshake():
    """
    Simulates a handshake between Node A (The Ark) and Node B (Simulated Peer).
    Requires Node A to be running on 3006.
    """
    print("🚀 Starting Federation Handshake Test")
    
    # 1. Verify Node A is alive
    try:
        r = requests.get(f"http://localhost:{NODE_A_PORT}/api/health")
        if r.status_code != 200:
            pytest.fail("Node A is not running")
    except:
        pytest.fail(f"Node A unreachable on port {NODE_A_PORT}")
        
    print("✅ Node A Online")

    # 2. Simulate Node B (Just a mock endpoint or a minimal server?)
    # For a true handshake, we need to hit the /api/federation/handshake endpoint on Node A
    # pretending to be Node B.
    
    node_b_identity = {
        "node_id": "node_002",
        "name": "Friend_Village",
        "ip": "127.0.0.1",
        "port": NODE_B_PORT,
        "public_key": "mock_pub_key_b"
    }
    
    print("🤝 Sending Handshake from Node B -> Node A...")
    try:
        r = requests.post(
            f"http://localhost:{NODE_A_PORT}/api/federation/handshake",
            json=node_b_identity,
            timeout=5
        )
        
        if r.status_code == 200:
            resp = r.json()
            print(f"✅ Handshake Accepted! Response: {resp}")
            assert resp.get('status') == 'success'
            assert resp.get('node_id') == 'node_001' # Node A's ID
        else:
            pytest.fail(f"Handshake failed: {r.text}")
            
    except Exception as e:
        pytest.fail(f"Handshake request error: {e}")

if __name__ == "__main__":
    test_federation_handshake()
