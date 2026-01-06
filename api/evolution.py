"""
Evolution API - Receives proposals from the local 'Right Brain' (Ollama)
Enables the Perpetual Imagination Loop
"""

import time
import json
from typing import Dict, List, Tuple

class EvolutionEngine:
    """
    Handles incoming evolution proposals from local AI nodes (Ollama).
    Proposals are recorded on the ledger and can be reviewed by the user.
    """
    
    def __init__(self, ledger, identity):
        self.ledger = ledger
        self.identity = identity
        self.proposals = {}  # proposal_id -> data
        
    def submit_proposal(self, source: str, data: Dict) -> Tuple[bool, str]:
        """
        Submit a new evolution proposal.
        
        data:
            title: str
            description: str
            type: technical | economic | social | hardware
            impact: 1-10
            estimated_labor: float (AT)
            logic_proof: str (reasoning)
        """
        required = ["title", "description", "type", "impact"]
        for field in required:
            if field not in data:
                return False, f"Missing field: {field}"
                
        proposal_id = f"evo_{int(time.time())}_{source[:4]}"
        
        proposal = {
            "id": proposal_id,
            "source": source,
            "title": data["title"],
            "description": data["description"],
            "type": data["type"],
            "impact": data["impact"],
            "estimated_labor": data.get("estimated_labor", 0.0),
            "logic_proof": data.get("logic_proof", ""),
            "status": "proposed",  # proposed, reviewed, implementation_planned, executed, rejected
            "created_at": time.time(),
            "votes": []
        }
        
        # Record to ledger
        self.ledger.add_block('EVOLUTION_PROPOSAL', {
            "proposal_id": proposal_id,
            "source": source,
            "type": data["type"],
            "title": data["title"],
            "timestamp": time.time()
        })
        
        self.proposals[proposal_id] = proposal
        return True, proposal_id

    def get_proposals(self, status: str = None) -> List[Dict]:
        """List incoming proposals."""
        if status:
            return [p for p in self.proposals.values() if p["status"] == status]
        return list(self.proposals.values())

    def review_proposal(self, proposal_id: str, reviewer: str, 
                        decision: str, note: str = "") -> Tuple[bool, str]:
        """User reviews a proposal."""
        if proposal_id not in self.proposals:
            return False, "Proposal not found"
            
        proposal = self.proposals[proposal_id]
        proposal["status"] = decision
        proposal["review_note"] = note
        proposal["reviewed_by"] = reviewer
        proposal["reviewed_at"] = time.time()
        
        self.ledger.add_block('EVOLUTION_REVIEW', {
            "proposal_id": proposal_id,
            "decision": decision,
            "reviewer": reviewer,
            "timestamp": time.time()
        })
        
        return True, f"Proposal {decision}"

def register_evolution_routes(router, evolution, auth_decorator):
    """Register evolution API routes."""
    
    @router.get('/api/evolution/proposals')
    def h_get_evo(h, p):
        status = p.get('status')
        h.send_json({"proposals": evolution.get_proposals(status)})
        
    @router.post('/api/evolution/propose')
    def h_submit_evo(h, p):
        # Source can be 'ollama_local' or 'jules_remote' etc.
        source = p.get('source', 'unknown_agent')
        success, result = evolution.submit_proposal(source, p)
        if success:
            h.send_json({"status": "success", "proposal_id": result})
        else:
            h.send_error(result)
            
    @router.post('/api/evolution/review')
    @auth_decorator
    def h_review_evo(h, user, p):
        proposal_id = p.get('proposal_id')
        decision = p.get('decision')
        note = p.get('note', "")
        success, msg = evolution.review_proposal(proposal_id, user['sub'], decision, note)
        if success:
            h.send_json({"status": "success", "message": msg})
        else:
            h.send_error(msg)
