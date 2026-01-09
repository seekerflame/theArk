import os
import json
import logging

logger = logging.getLogger("ArkOS.NodeAPI")

def register_node_routes(router, ledger, identity, foundry, verification, auth_decorator):
    
    @router.get('/api/nodes/templates')
    @auth_decorator
    def h_list_templates(h, user):
        templates_dir = 'templates'
        if not os.path.exists(templates_dir):
            return h.send_json([])
        
        templates = []
        for f in os.listdir(templates_dir):
            if f.endswith('.json'):
                templates.append(f.replace('.json', ''))
        h.send_json(templates)

    @router.post('/api/nodes/apply_template')
    @auth_decorator
    def h_apply_template(h, p, user):
        if user.get('role') != 'admin' and user.get('role') != 'NODE_ADMIN':
            return h.send_json_error("Unauthorized", status=403)
            
        template_name = p.get('template')
        template_path = f'templates/{template_name}.json'
        
        if not os.path.exists(template_path):
            return h.send_json_error("Template not found")
            
        try:
            with open(template_path, 'r') as f:
                config = json.load(f)
                
            overrides = config.get('overrides', {})
            
            # 1. Apply Verification Overrides
            if 'core.verification_pyramid.ORACLE_STAKE_REQUIRED' in overrides:
                verification.ORACLE_STAKE_REQUIRED = overrides['core.verification_pyramid.ORACLE_STAKE_REQUIRED']
                
            # 2. Apply Foundry Machines
            if 'core.foundry.DEFAULT_MACHINES' in overrides:
                for m_data in overrides['core.foundry.DEFAULT_MACHINES']:
                    from core.foundry import FoundryMachine
                    m = FoundryMachine(
                        m_data['name'], 
                        m_data['type'], 
                        m_data['at_cost_per_hour'],
                        is_static=m_data.get('is_static', False)
                    )
                    foundry.add_machine(m)
            
            # 3. Roles are inherently updated if logic uses the core roles.py
            # But we might need a way to dynamically reload if they were in-memory differently.
            
            h.send_json({"status": "success", "message": f"Template {template_name} applied."})
            logger.info(f"Node Template Applied: {template_name} by {user.get('username')}")
        except Exception as e:
            h.send_json_error(f"Failed to apply template: {str(e)}")
