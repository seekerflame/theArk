import os
import json
import time
import sqlite3

def register_system_routes(router, ledger, identity, peers, sensors, energy, fishery, hw_bridge, requires_auth):

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
        if not u or not pwd: return h.send_json_error("Missing username or password")
        ok, res = identity.register(u, pwd)
        if ok: h.send_json({"token": identity.generate_token(u), "mnemonic": res['mnemonic'], "message": res['message']})
        else: h.send_json_error(res)

    @router.post('/api/restore')
    def h_restore(h, p):
        u, m, pwd = p.get('username'), p.get('mnemonic'), p.get('password')
        if not u or not m or not pwd: return h.send_json_error("Username, Mnemonic, and New Password required")
        ok, msg = identity.restore(u, m, pwd)
        if ok: h.send_json({"message": msg})
        else: h.send_json_error(msg)

    @router.post('/api/login')
    def h_login(h, p):
        u, pwd = p.get('username'), p.get('password')
        ok, res = identity.login(u, pwd)
        if ok: 
            user_data = identity.users.get(u, {})
            # Detect Roles (including ephemeral NODE_HOST)
            roles = identity.get_user_roles(u, ledger=ledger, hw_bridge=hw_bridge)
            hm = identity.get_holistic_multiplier(u, ledger=ledger)
            
            h.send_json({
                "token": identity.generate_token(u), 
                "user": {
                    "username": u, 
                    "pseudoname": user_data.get('pseudoname'),
                    "role": res['role'],
                    "roles": roles, # Detailed roles list
                    "is_host": "NODE_HOST" in roles,
                    "balance": ledger.get_balance(u),
                    "verified_hours": user_data.get('verified_hours', 0),
                    "safety_grade": user_data.get('safety_grade', 100),
                    "hm": hm
                }
            })
        else: 
            fishery.report_auth_failure()
            h.send_json_error("Invalid credentials")

    @router.post('/api/identity/pseudoname')
    @requires_auth
    def h_update_pseudoname(h, user, p):
        u, pseudo = user['sub'], p.get('pseudoname')
        if not pseudo: return h.send_json_error("Pseudoname required")
        ok, msg = identity.update_pseudoname(u, pseudo)
        if ok: h.send_json({"message": msg, "pseudoname": pseudo})
        else: h.send_json_error(msg)

    @router.get('/api/fishery/status')
    @requires_auth
    def h_fishery_status(h, user, p=None):
        # Admin or Oracle only
        user_roles = identity.users.get(user['sub'], {}).get('roles', [])
        if user['role'] != 'ADMIN' and 'ORACLE' not in user_roles:
            return h.send_json_error("Unauthorized access to safety systems", status=403)
        h.send_json(fishery.get_status())


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

    @router.get('/api/users')
    @requires_auth
    def h_users(h, user, p=None):
        """Returns scrubbed user data for Oracle/Admin visualization."""
        user_roles = identity.users.get(user['sub'], {}).get('roles', [])
        if user['role'] != 'ADMIN' and 'ORACLE' not in user_roles:
            return h.send_json_error("Oracle level access required", status=403)
            
        scrubbed = {}
        for username, data in identity.users.items():
            scrubbed[username] = {
                "roles": data.get('roles', []),
                "verified_hours": data.get('verified_hours', 0),
                "safety_grade": data.get('safety_grade', 100),
                "created_at": data.get('created_at')
            }
    @router.post('/api/wiki/sync')
    @requires_auth
    def h_wiki_sync(h, user, p):
        """Triggers the Wiki Sync script (Admins only)"""
        if user['role'] != 'ADMIN':
            return h.send_json_error("Admin access required", status=403)
            
        import subprocess
        try:
            # Run the sync script in a separate process to avoid blocking
            script_path = os.path.join(os.getcwd(), 'wiki', 'wiki_sync.py')
            if not os.path.exists(script_path):
                return h.send_json_error(f"Sync script not found at {script_path}")
                
            # Use sys.executable to ensure we use the same python environment
            import sys
            subprocess.Popen([sys.executable, script_path])
            
            h.send_json({"status": "sync_started", "message": "Wiki synchronization initiated in background"})
        except Exception as e:
            h.send_json_error(f"Failed to start sync: {str(e)}")

    @router.post('/api/ark/privacy')
    @requires_auth
    def h_update_privacy(h, user, p):
        """Toggle Ghost Mode (Identity Shielding)"""
        u, ghost_mode = user['sub'], p.get('ghost_mode', False)
        # In a real system, this would modify how the user appears in the federation
        # For v1.0, we just persist the intent in the identity state
        if 'settings' not in identity.users[u]:
            identity.users[u]['settings'] = {}
        identity.users[u]['settings']['ghost_mode'] = ghost_mode
        h.send_json({"status": "success", "ghost_mode": ghost_mode})

    @router.get('/api/wiki/status')
    def h_wiki_status(h):
        """Returns the last known wiki sync status"""
        path = os.path.join("web", "wiki_status.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                h.send_json(json.load(f))
        else:
            h.send_json({"status": "OFFLINE", "message": "No sync history found"})

