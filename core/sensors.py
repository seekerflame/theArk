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

    def register(self, s_id, s_type, meta=None):
        if meta is None: meta = {}
        if s_id not in self.sensors:
            self.sensors[s_id] = {
                "id": s_id,
                "type": s_type,
                "meta": meta,
                "last_value": 0,
                "last_seen": 0,
                "status": "OFFLINE"
            }
        else:
            # Update meta if provided
            self.sensors[s_id]["meta"].update(meta)
            self.sensors[s_id]["type"] = s_type # Allow type update
        self.save()
        return self.sensors[s_id]

    def update(self, s_id, s_type, value, meta=None):
        if s_id not in self.sensors:
             self.register(s_id, s_type, meta)

        self.sensors[s_id]["last_value"] = value
        self.sensors[s_id]["last_seen"] = time.time()
        self.sensors[s_id]["status"] = "ONLINE"
        if meta:
            self.sensors[s_id].setdefault("meta", {}).update(meta)

        self.save()
        return self.sensors[s_id]

    def get_sensor(self, s_id):
        return self.sensors.get(s_id)

    def get_all(self):
        return self.sensors

    def get_aggregate_value(self, s_type):
        total = 0.0
        # Only count sensors seen in last 5 minutes
        cutoff = time.time() - 300
        for s in self.sensors.values():
            if s.get('type') == s_type and s.get('last_seen', 0) > cutoff:
                try:
                    total += float(s.get('last_value', 0))
                except (ValueError, TypeError):
                    pass
        return total

    def get_metabolic_yield(self):
        if not self.sensors: return 0.0
        now = time.time()
        active = [s for s in self.sensors.values() if now - s['last_seen'] < 60]
        if not active: return 0.0
        return len(active) / max(len(self.sensors), 1) * 0.95
