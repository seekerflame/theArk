import os
import time
import threading
import logging

logger = logging.getLogger("ArkOS.Steward")

class StewardNexus:
    def __init__(self, ledger, sensors, server_file='server.py'):
        self.ledger = ledger
        self.sensors = sensors
        self.server_file = server_file
        self.stop_event = threading.Event()
        self.last_audit = 0

    def audit_system(self):
        while not self.stop_event.is_set():
            now = time.time()
            if now - self.last_audit > 300: # Audit every 5 minutes
                self.perform_technical_audit()
                self.perform_metabolic_audit()
                self.last_audit = now
            time.sleep(10)

    def perform_technical_audit(self):
        try:
            stats = os.stat(self.server_file)
            size_kb = stats.st_size / 1024
            if size_kb > 30:
                self.ledger.add_block('CHRONICLE', {
                    'event': 'TECH_DEBT_ALERT',
                    'message': f'System core density at {size_kb:.1f}KB. Modularization mission recommended.',
                    'source': 'STEWARD'
                })
        except: pass

    def perform_metabolic_audit(self):
        now = time.time()
        for s_id, s in self.sensors.sensors.items():
            if now - s['last_seen'] > 300 and s['status'] == 'ONLINE':
                s['status'] = 'OFFLINE'
                self.ledger.add_block('CHRONICLE', {
                    'event': 'METABOLIC_FAULT',
                    'message': f'Sensor {s_id} ({s["type"]}) has flatlined. Dispatching repair proposal.',
                    'source': 'STEWARD'
                })
                self.ledger.add_block('QUEST', {
                    'quest_id': f'repair_{s_id}_{int(now)}',
                    'title': f'🔧 Repair Sensor {s_id}',
                    'reward': 25.0,
                    'owner': 'STEWARD',
                    'status': 'OPEN',
                    'created_at': now
                })
        self.sensors.save()

    def create_proposal(self, title, description, cost_at=0):
        proposal_id = f"prop_{int(time.time())}"
        data = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "cost_at": cost_at,
            "votes_for": 0,
            "votes_against": 0,
            "status": "OPEN",
            "timestamp": time.time()
        }
        self.ledger.add_block('PROPOSAL', data)
        return proposal_id

    def vote_on_proposal(self, proposal_id, vote_type='for'):
        for block in self.ledger.blocks:
            if block['type'] == 'PROPOSAL' and block['data']['id'] == proposal_id:
                if vote_type == 'for':
                    block['data']['votes_for'] += 1
                else:
                    block['data']['votes_against'] += 1
                
                # Simple auto-approve logic for demo
                if block['data']['votes_for'] >= 5:
                    block['data']['status'] = "APPROVED"
                
                return True
        return False

    def start(self):
        threading.Thread(target=self.audit_system, daemon=True).start()
