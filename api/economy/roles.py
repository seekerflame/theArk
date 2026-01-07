import time

def register_role_routes(router, identity, ledger, requires_auth):

    @router.get('/api/roles/multipliers')
    def h_multipliers(h):
        h.send_json(identity.get_role_multipliers())

    @router.post('/api/roles/certify')
    @requires_auth
    def h_certify_role(h, user, p):
        """Oracle certifies a user for a specific role/skill."""
        if user['role'] != 'ADMIN' and 'ORACLE' not in identity.users.get(user['sub'], {}).get('roles', []):
            return h.send_json_error("Only Oracles or Admin can certify roles", status=403)
            
        target_user = p.get('username')
        role = p.get('role', '').upper()
        if not target_user or not role:
            return h.send_json_error("Username and Role required")
            
        if target_user not in identity.users:
            return h.send_json_error("Target user not found")
            
        # Update user metadata
        u_data = identity.users[target_user]
        if 'roles' not in u_data: u_data['roles'] = ["WORKER"]
        if role not in u_data['roles']:
            u_data['roles'].append(role)
        
        if 'certifications' not in u_data: u_data['certifications'] = {}
        u_data['certifications'][role] = {
            "certified_by": user['sub'],
            "timestamp": time.time(),
            "level": p.get('level', 1)
        }
        
        identity.save()
        
        # Record on ledger for transparency
        ledger.add_block('CERTIFICATION', {
            "target": target_user,
            "role": role,
            "certified_by": user['sub'],
            "timestamp": time.time()
        })
        
        h.send_json({"status": "certified", "user": target_user, "role": role})

    @router.post('/api/roles/define')
    @requires_auth
    def h_define_role(h, user, p):
        """Oracle defines a new role multiplier on the ledger."""
        if user['role'] != 'ADMIN' and 'ORACLE' not in identity.users.get(user['sub'], {}).get('roles', []):
            return h.send_json_error("Only Oracles or Admin can define roles", status=403)
            
        role_name = p.get('role', '').upper()
        multiplier = float(p.get('multiplier', 1.0))
        
        if not role_name: return h.send_json_error("Role name required")
        
        ledger.add_block('ROLE_DEFINITION', {
            "role": role_name,
            "multiplier": multiplier,
            "defined_by": user['sub'],
            "timestamp": time.time()
        })
        h.send_json({"status": "defined", "role": role_name, "multiplier": multiplier})
