import os
import time
import threading
import logging

logger = logging.getLogger("ArkOS.Steward")

class StewardNexus:
    def __init__(self, ledger, sensors, identity_manager, server_file='server.py'):
        self.ledger = ledger
        self.sensors = sensors
        self.identity = identity_manager
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
            if size_kb > 40: # Increased threshold as server grows
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

    def create_proposal(self, title, description, requested_amount=0, creator_id='anonymous'):
        """
        Hardened: Requires minimum 5.0 verified hours to create a proposal.
        """
        user_data = self.identity.users.get(creator_id, {})
        verified_hours = user_data.get('verified_hours', 0.0)
        
        if creator_id != 'admin' and verified_hours < 5.0:
            return None, f"Insufficient verified hours to propose ({verified_hours}/5.0). Build more, then lead."

        proposal_id = f"prop_{int(time.time())}"
        data = {
            "id": proposal_id,
            "title": title,
            "description": description,
            "requested_amount": requested_amount,
            "creator": creator_id,
            "votes_for": 0,
            "votes_against": 0,
            "voters": [],
            "status": "OPEN",
            "timestamp": time.time()
        }
        self.ledger.add_block('PROPOSAL', data)
        return proposal_id, "Proposal submitted to the Ark."

    def vote_on_proposal(self, proposal_id, vote_type='YES', voter_id='anonymous'):
        """
        Hardened: Requires minimum 1.0 verified hour to vote.
        """
        user_data = self.identity.users.get(voter_id, {})
        verified_hours = user_data.get('verified_hours', 0.0)

        if voter_id != 'admin' and verified_hours < 1.0:
            return False, "You must be an Ark Citizen (1.0 verified hour) to vote."

        for block in self.ledger.blocks:
            if block['type'] == 'PROPOSAL' and block['data']['id'] == proposal_id:
                prop = block['data']
                if voter_id in prop.get('voters', []):
                    return False, "Already voted"
                
                if vote_type.upper() == 'YES':
                    prop['votes_for'] += 1
                else:
                    prop['votes_against'] += 1
                
                prop.setdefault('voters', []).append(voter_id)
                
                if prop['votes_for'] >= 3 and prop['status'] != 'VETOED':
                    prop['status'] = "APPROVED"
                
                # --- The People's Veto (Anti-Oligarch Logic) ---
                # For critical assets or mass wealth transfers, HUMAN consensus overrides capital.
                is_critical = prop.get('title', '').startswith('BUY') or prop.get('requested_amount', 0) > 1000
                
                if is_critical:
                    # Count total active citizens (denominator is humans, not tokens)
                    total_citizens = len([u for u_name, u in self.identity.users.items() if u.get('verified_hours', 0) >= 1.0])
                    
                    # If > 50% of ALL citizens vote NO, it is vetoed.
                    if total_citizens > 0 and (prop['votes_against'] / total_citizens) > 0.5:
                        prop['status'] = 'VETOED'
                        return True, "Vote recorded. PROPOSAL VETOED by the People (>50% Opposition)."

                return True, "Vote recorded"
        return False, "Proposal not found"

    def start(self):
        threading.Thread(target=self.audit_system, daemon=True).start()
