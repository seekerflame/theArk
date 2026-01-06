"""
Role API Endpoints
Provides role information and user role management
"""

def register_role_routes(router, ledger, identity, requires_auth):
    
    @router.get('/api/roles')
    def h_list_roles(h):
        """List all available roles with their definitions"""
        try:
            from core.roles import ROLE_DEFINITIONS
            roles = []
            for role_name, role_info in ROLE_DEFINITIONS.items():
                roles.append({
                    'role': role_name,
                    'title': role_info['title'],
                    'base_multiplier': role_info['base_multiplier'],
                    'capabilities': role_info.get('capabilities', []),
                    'quest_tags': role_info.get('quest_tags', []),
                    'onboarding': role_info.get('onboarding', ''),
                    'sops': role_info.get('sops', []),
                    'requires_certification': role_info.get('requires_certification', False)
                })
            h.send_json(roles)
        except ImportError:
            h.send_error("Role system not available", status=500)
    
    @router.get('/api/roles/my')
    @requires_auth
    def h_my_roles(h, user, p):
        """Get current user's roles and certifications"""
        username = user['sub']
        
        # Get user roles from ledger
        user_roles = identity.get_user_roles(username, ledger)
        
        # Get detailed info for each role
        try:
            from core.roles import get_role_info, get_progression_path
            role_details = []
            for role in user_roles:
                info = get_role_info(role)
                role_details.append({
                    'role': role,
                    'title': info['title'],
                    'multiplier': info['base_multiplier'],
                    'capabilities': info.get('capabilities', []),
                    'quest_tags': info.get('quest_tags', []),
                    'progression_options': get_progression_path(role)
                })
            
            # Get verified hours for tier info
            verified_hours = identity.users.get(username, {}).get('verified_hours', 0.0)
            tier = 'Apprentice'
            if verified_hours >= 500:
                tier = 'Master'
            elif verified_hours >= 100:
                tier = 'Journeyman'
            
            h.send_json({
                'username': username,
                'roles': role_details,
                'verified_hours': verified_hours,
                'tier': tier
            })
        except ImportError:
            h.send_json({
                'username': username,
                'roles': user_roles,
                'verified_hours': 0.0,
                'tier': 'Worker'
            })
    
    @router.get('/api/roles/sops/<sop_code>')
    def h_roles_for_sop(h, sop_code):
        """Get which roles are responsible for a specific SOP"""
        try:
            from core.roles import get_roles_for_sop
            roles = get_roles_for_sop(sop_code)
            h.send_json({'sop': sop_code, 'responsible_roles': roles})
        except ImportError:
            h.send_json({'sop': sop_code, 'responsible_roles': []})
