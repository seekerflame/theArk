import time
import json
import os

class SwarmEngine:
    def __init__(self, ledger, storage_path='ledger/swarm_state.json'):
        self.ledger = ledger
        self.storage_path = storage_path
        self.projects = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.projects = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.projects, f, indent=2)

    def create_project(self, title, blueprint_id, total_blocks):
        project_id = f"swarm_{int(time.time())}"
        self.projects[project_id] = {
            "id": project_id,
            "title": title,
            "blueprint_id": blueprint_id,
            "status": "ACTIVE",
            "blocks": {
                f"block_{i}": {
                    "id": f"block_{i}",
                    "description": f"Atomic Assembly Task {i+1} for {title}",
                    "status": "AVAILABLE",
                    "claimed_by": None,
                    "reward_at": 1.0,
                    "verified": False
                } for i in range(total_blocks)
            }
        }
        self.save()
        return project_id

    def claim_block(self, project_id, block_id, user_id):
        if project_id not in self.projects:
            return False, "Project not found"
        
        project = self.projects[project_id]
        if block_id not in project['blocks']:
            return False, "Block not found"
            
        block = project['blocks'][block_id]
        if block['status'] != "AVAILABLE":
            return False, f"Block is already {block['status']}"

        block['status'] = "CLAIMED"
        block['claimed_by'] = user_id
        self.save()
        return True, "Block claimed successfully"

    def complete_block(self, project_id, block_id, user_id):
        if project_id not in self.projects:
            return False, "Project not found"
        
        project = self.projects[project_id]
        block = project['blocks'].get(block_id)
        
        if not block or block['claimed_by'] != user_id:
            return False, "Unauthorized completion attempt"

        block['status'] = "COMPLETED"
        
        # Auto-verify for demo, normally triggers Triple Verification
        block['verified'] = True
        
        # Reward AT
        self.ledger.add_block('SWARM_BLOCK_REWARD', {
            "user": user_id,
            "project_id": project_id,
            "block_id": block_id,
            "reward_at": block['reward_at'],
            "timestamp": time.time()
        })
        
        self.save()
        return True, f"Block completed. Received {block['reward_at']} AT."
