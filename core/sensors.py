import json
import os
import time
import logging
import threading

logger = logging.getLogger("ArkOS.Sensors")

class SensorRegistry:
    def __init__(self, registry_file):
        self.registry_file = registry_file
        self.sensors = {}
        self.command_queue = {} # device_id -> [commands]
        self.lock = threading.Lock()
        self.load()

    def load(self):
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f: self.sensors = json.load(f)
            except: pass

    def save(self):
        directory = os.path.dirname(self.registry_file)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(self.registry_file, 'w') as f: json.dump(self.sensors, f, indent=2)

    def update(self, s_id, s_type, value):
        with self.lock:
            self.sensors[s_id] = {
                "type": s_type,
                "last_value": value,
                "last_seen": time.time(),
                "status": "ONLINE"
            }
            self.save()

    def queue_command(self, device_id, command):
        with self.lock:
            if device_id not in self.command_queue:
                self.command_queue[device_id] = []
            self.command_queue[device_id].append(command)

    def get_pending_commands(self, device_id):
        with self.lock:
            if device_id in self.command_queue and self.command_queue[device_id]:
                cmds = self.command_queue[device_id]
                self.command_queue[device_id] = [] # Clear after reading
                return cmds
            return []

    def poll(self):
        """
        Checks for stale sensors and marks them OFFLINE.
        This constitutes 'polling' the state of the sensor network.
        """
        now = time.time()
        changed = False

        with self.lock:
            for s_id, data in list(self.sensors.items()):
                if now - data['last_seen'] > 60 and data['status'] == 'ONLINE':
                    data['status'] = 'OFFLINE'
                    changed = True

            if changed:
                self.save()

    def get_metabolic_yield(self):
        if not self.sensors: return 0.0
        now = time.time()
        active = [s for s in self.sensors.values() if now - s['last_seen'] < 60]
        if not active: return 0.0
        return len(active) / max(len(self.sensors), 1) * 0.95
