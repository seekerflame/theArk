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

    def start(self):
        threading.Thread(target=self.audit_system, daemon=True).start()
