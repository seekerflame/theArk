
import time
from typing import Dict, List

class EvolutionAPI:
    def __init__(self, ledger):
        self.ledger = ledger
        self.proposals = []
        self._load_proposals()

    def _load_proposals(self):
        # Scan ledger for past proposals to rebuild state
        for block in self.ledger.blocks:
            if block['type'] == 'EVOLUTION_PROPOSAL':
                self.proposals.append(block['data'])

    def propose(self, entry: Dict):
        """Submit a new evolution proposal"""
        proposal = entry.copy()
        proposal['id'] = f"evo_{int(time.time())}"
        proposal['status'] = 'approved' # Auto-approve for MVP/Demo
        proposal['timestamp'] = time.time()
        
        # Persist to ledger
        self.ledger.add_block('EVOLUTION_PROPOSAL', proposal)
        self.proposals.append(proposal)
        
        return proposal

    def get_proposals(self, status=None):
        if status:
            return [p for p in self.proposals if p.get('status') == status]
        return self.proposals

    def review_proposal(self, proposal_id, decision, note):
        # Update status in memory
        for p in self.proposals:
            if p['id'] == proposal_id:
                p['status'] = decision
                p['review_note'] = note
                
                # Persist review
                self.ledger.add_block('EVOLUTION_REVIEW', {
                    'proposal_id': proposal_id,
                    'decision': decision,
                    'note': note,
                    'timestamp': time.time()
                })
                return True
        return False

def register_evolution_routes(router, ledger, auth_decorator):
    evolution = EvolutionAPI(ledger)

    @router.post('/api/evolution/propose')
    def h_propose(h, p):
        # Open endpoint for "Right Brain" (internal trusted process)
        # In prod, this should be auth-gated
        proposal = evolution.propose(p)
        h.send_json({"status": "success", "proposal": proposal})

    @router.get('/api/evolution/proposals')
    def h_get_proposals(h):
        # Extract query params manually if needed, or just default to all
        # Simple implementation: /api/evolution/proposals?status=approved
        path = h.path
        status = None
        if 'status=' in path:
            status = path.split('status=')[1].split('&')[0]
            
        proposals = evolution.get_proposals(status)
        h.send_json({"status": "success", "proposals": proposals})

    @router.post('/api/evolution/review')
    def h_review(h, p):
        # Left Brain reporting back execution
        success = evolution.review_proposal(p.get('proposal_id'), p.get('decision'), p.get('note'))
        if success:
            h.send_json({"status": "success"})
        else:
            h.send_json_error("Proposal not found")
