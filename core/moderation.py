import json
import time
import logging
import os

logger = logging.getLogger("ArkOS.Moderation")

class ModerationQueue:
    def __init__(self, db_file):
        self.db_file = db_file
        self.queue = []
        self.log = []
        self.load()

    def load(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r') as f:
                    data = json.load(f)
                    self.queue = data.get('queue', [])
                    self.log = data.get('log', [])
            except: pass

    def save(self):
        os.makedirs(os.path.dirname(self.db_file), exist_ok=True)
        with open(self.db_file, 'w') as f:
            json.dump({'queue': self.queue, 'log': self.log}, f, indent=2)

    def add_report(self, reporter, target_id, reason, proof=None):
        report = {
            "id": f"rep_{int(time.time())}_{len(self.queue)}",
            "reporter": reporter,
            "target_id": target_id,
            "reason": reason,
            "proof": proof,
            "status": "PENDING",
            "timestamp": time.time()
        }
        self.queue.append(report)
        self.save()
        return report['id']

    def resolve_report(self, report_id, resolver, action, notes=None):
        # Find report
        report = next((r for r in self.queue if r['id'] == report_id), None)
        if not report: return False

        # Move to Log
        self.queue = [r for r in self.queue if r['id'] != report_id]
        report['status'] = 'RESOLVED'
        report['resolution'] = action # BAN, DISMISS, WARN
        report['resolver'] = resolver
        report['notes'] = notes
        report['resolved_at'] = time.time()

        self.log.insert(0, report) # Newest first
        self.log = self.log[:100] # Keep last 100
        self.save()
        return True

    def get_queue(self):
        return self.queue

    def get_log(self):
        return self.log
