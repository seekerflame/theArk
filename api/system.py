import os
import json
import time
import sqlite3

def register_system_routes(router, ledger, identity, peers, sensors, energy, requires_auth):

    @router.get('/api/system/energy')
    def h_energy(h):
        h.send_json(energy.get_status())

    @router.get('/api/health')
    def h_health(h): 
        h.send_json({"status": "healthy", "timestamp": time.time(), "agent": "Antigravity"})

    @router.get('/api/state')
    def h_state(h):
        h.send_json({
            "status": "operational",
            "blocks": len(ledger.blocks),
            "version": "1.2.0",
            "codename": "The Ark Modular"
        })

    @router.post('/api/register')
    def h_register(h, p):
        u, pwd = p.get('username'), p.get('password')
        if not u or not pwd: return h.send_error("Missing username or password")
        ok, msg = identity.register(u, pwd)
        if ok: h.send_json({"token": identity.generate_token(u), "mnemonic": "seed-phrase-simulated"})
        else: h.send_error(msg)

    @router.post('/api/login')
    def h_login(h, p):
        u, pwd = p.get('username'), p.get('password')
        ok, res = identity.login(u, pwd)
        if ok: h.send_json({"token": identity.generate_token(u), "user": {"username": u, "role": res['role'], "balance": ledger.get_balance(u)}})
        else: h.send_error("Invalid credentials")

    @router.get('/api/logs')
    @requires_auth
    def h_logs(h, user, p=None):
        logs = {"auto_operator.log": [], "ark_steward.log": [], "agent_uplink.log": []}
        mappings = {"auto_operator.log": "auto_operator.log", "ark_steward.log": "ark_steward.log", "agent_uplink.log": "server.log"}
        for key, filename in mappings.items():
            path = os.path.join("logs", filename)
            if os.path.exists(path):
                with open(path, 'r') as f: logs[key] = f.readlines()[-50:]
        h.send_json(logs)
        
    @router.get('/api/graph')
    def h_graph(h):
        from urllib.parse import urlparse, parse_qs
        since_id = 0
        try:
            query = urlparse(h.path).query
            params = parse_qs(query)
            since_id = int(params.get('since', [0])[0])
        except: pass
        
        if since_id > 0:
            h.send_json([b for b in ledger.blocks if b['id'] > since_id])
        else:
            h.send_json(ledger.blocks)
