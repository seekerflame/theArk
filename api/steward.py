import json
import subprocess
import time

def register_steward_routes(router, ledger, energy, steward, requires_auth):
    
    @router.post('/api/steward/think')
    def h_steward_think(h, p):
        # ... logic for AI thinking ...
        pass

    @router.post('/api/steward/propose')
    @requires_auth
    def h_steward_propose(h, user, p):
        title = p.get('title')
        desc = p.get('description')
        requested_amount = float(p.get('requested_amount', p.get('cost_at', 0)))
        if not title: return h.send_json_error("Title required")
        
        prop_id, msg = steward.create_proposal(title, desc, requested_amount, creator_id=user['sub'])
        if not prop_id:
            return h.send_json_error(msg)
            
        h.send_json({"id": prop_id, "message": msg})

    @router.get('/api/steward/proposals')
    def h_steward_proposals(h):
        props = [b['data'] for b in ledger.blocks if b['type'] == 'PROPOSAL']
        h.send_json(props)

    @router.post('/api/steward/vote')
    @requires_auth
    def h_steward_vote(h, user, p):
        prop_id = p.get('id')
        vote_type = p.get('vote', 'YES')
        if not prop_id: return h.send_json_error("Proposal ID required")
        
        success, msg = steward.vote_on_proposal(prop_id, vote_type, voter_id=user['sub'])
        if success:
            h.send_json({"message": msg})
        else:
            h.send_json_error(msg)

    @router.post('/api/steward/chat')
    def h_steward_chat(h, p):
        msg = p.get('message', '')
        h.send_json({"output": f"[STEWARD] Intelligence received. Analyzing: '{msg[:20]}...'. Directive: Continue Evolution Cycle."})
