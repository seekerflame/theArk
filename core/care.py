import time
import json
import os

class CareCircle:
    def __init__(self, ledger, storage_path='ledger/care_state.json'):
        self.ledger = ledger
        self.storage_path = storage_path
        self.tasks = {}
        self.load()

    def load(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, 'r') as f:
                self.tasks = json.load(f)

    def save(self):
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, title, description, reward_at=1.0):
        task_id = f"care_{int(time.time() * 1000)}"
        self.tasks[task_id] = {
            "id": task_id,
            "title": title,
            "description": description,
            "reward_at": reward_at,
            "status": "OPEN",
            "completions": []
        }
        self.save()
        return task_id

    def verify_care_labor(self, task_id, provider_id, quantity=1.0):
        if task_id not in self.tasks:
            return False, "Care task not found"
        
        task = self.tasks[task_id]
        
        # In a real scenario, this would require verification from the recipient
        # or social consensus. For the demo, we log the intent.
        
        reward = task['reward_at'] * quantity
        
        # Process Reward
        self.ledger.add_block('CARE_LABOR_MINT', {
            "provider": provider_id,
            "task_id": task_id,
            "task_title": task['title'],
            "reward_at": reward,
            "timestamp": time.time()
        })

        task['completions'].append({
            "provider": provider_id,
            "timestamp": time.time(),
            "reward": reward
        })
        
        self.save()
        return True, reward
