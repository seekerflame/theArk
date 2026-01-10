from core.swarm import SwarmEngine

def register_swarm_routes(router, ledger, auth_decorator):
    swarm = SwarmEngine(ledger)

    @router.get('/api/swarm/projects')
    def list_projects(h):
        h.send_json({"projects": list(swarm.projects.values())})

    @router.post('/api/swarm/claim')
    @auth_decorator
    def claim_block(h, user, p):
        project_id = p.get('project_id')
        block_id = p.get('block_id')
        success, message = swarm.claim_block(project_id, block_id, user['sub'])
        
        if success:
            h.send_json({"status": "success", "message": message})
        else:
            h.send_json_error(message)

    @router.post('/api/swarm/complete')
    @auth_decorator
    def complete_block(h, user, p):
        project_id = p.get('project_id')
        block_id = p.get('block_id')
        success, message = swarm.complete_block(project_id, block_id, user['sub'])
        
        if success:
            h.send_json({"status": "success", "message": message})
        else:
            h.send_json_error(message)

    # Demo tool to seed a project
    @router.post('/api/swarm/seed_demo')
    @auth_decorator
    def seed_demo(h, user, p):
        # Only for testing/demo
        pid = swarm.create_project("SEED Eco-Home v7", "blueprint_01", 10)
        h.send_json({"status": "success", "project_id": pid})
