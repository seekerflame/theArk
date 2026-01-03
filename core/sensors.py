import json
import os
import time
import logging

logger = logging.getLogger("ArkOS.Sensors")

class SensorRegistry:
    def __init__(self, registry_file):
        self.registry_file = registry_file
        self.sensors = {}
        self.load()

    def load(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f: self.sensors = json.load(f)
            except: pass

    def save(self):
        os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
        with open(self.registry_file, 'w') as f: json.dump(self.sensors, f, indent=2)

    def update(self, s_id, s_type, value):
        self.sensors[s_id] = {
            "type": s_type,
            "last_value": value,
            "last_seen": time.time(),
            "status": "ONLINE"
        }
        self.save()

    def get_metabolic_yield(self):
        if not self.sensors: return 0.0
        now = time.time()
        active = [s for s in self.sensors.values() if now - s['last_seen'] < 60]
        if not active: return 0.0
        return len(active) / max(len(self.sensors), 1) * 0.95
