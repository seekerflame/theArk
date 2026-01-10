import time
import random
from core.swarm import SwarmEngine
from core.care import CareCircle
from core.ledger import VillageLedger

class GaiaDaemon:
    def __init__(self, ledger, hardware_bridge=None):
        self.ledger = ledger
        self.swarm = SwarmEngine(ledger)
        self.care = CareCircle(ledger)
        self.bridge = hardware_bridge
        self.node_id = "node_001"
        self.history = []

    def run_cycle(self):
        # 1. Monitor Hardware Sensors
        if self.bridge:
            telemetry = self.bridge.read_telemetry()
            solar_efficiency = telemetry.get('solar_amps', 0) / 10.0 # Approximate efficiency based on max amps
            battery_level = telemetry.get('battery_level', 50.0)
            social_entropy = random.uniform(0.0, 1.0) # Still simulated for now
        else:
            # Fallback to pure random simulation if no bridge
            solar_efficiency = random.uniform(0.7, 1.0)
            battery_level = random.uniform(50.0, 100.0)
            social_entropy = random.uniform(0.0, 1.0)
        
        # 2. Identify Critical Path Issues
        if solar_efficiency < 0.8:
            self.generate_repair_swarm("Solar Array Panel Cleaning", "blueprint_solar_maint")

        # 3. Monitor Community Morale (Simulated)
        social_entropy = random.uniform(0.0, 1.0)
        if social_entropy > 0.7:
            self.generate_care_quest("Inter-Node Mentorship", "Community fragmentation risk detected.")

        # 4. Generate Thrive Messages for Radio
        thrive_msgs = [
            f"[GAIA] Solar Efficiency: {solar_efficiency*100:.1f}%",
            f"[GAIA] Node Energy: {battery_level:.1f} kWh",
            f"[GAIA] Social Entropy: {social_entropy:.2f}"
        ]
        
        if social_entropy < 0.3:
            thrive_msgs.append("🌟 Community synchronization reaching optimal levels.")
        if solar_efficiency > 0.9:
            thrive_msgs.append("☀️ Maximum photonic harvest detected.")

        # 5. Log Gaia's thoughts to the Ledger
        log_entry = {
            "type": "GAIA_THOUGHT",
            "solar_eff": f"{solar_efficiency:.2f}",
            "entropy": f"{social_entropy:.2f}",
            "messages": thrive_msgs,
            "timestamp": time.time()
        }
        self.ledger.add_block('GAIA_PULSE', log_entry)
        return log_entry

    def generate_repair_swarm(self, title, blueprint):
        # Check if already active
        existing = any(p['title'] == title for p in self.swarm.projects.values())
        if not existing:
            pid = self.swarm.create_project(f"[AUTO] {title}", blueprint, 5)
            self.ledger.add_block('GAIA_AUTONOMY', {
                "action": "AUTO_SWARM_GEN",
                "project_id": pid,
                "reason": "Efficiency dropped below 80%"
            })

    def generate_care_quest(self, title, reason):
        # Check if already active
        existing = any(t['title'] == title for t in self.care.tasks.values())
        if not existing:
            tid = self.care.add_task(f"[GAIA] {title}", reason, 3.0)
            self.ledger.add_block('GAIA_AUTONOMY', {
                "action": "AUTO_CARE_GEN",
                "task_id": tid,
                "reason": reason
            })
